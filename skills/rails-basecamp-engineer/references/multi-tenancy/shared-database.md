# Shared Database, Shared Schema Multi-Tenancy

This pattern uses a single shared database with all tenants sharing the same tables. Tenant isolation is achieved via `account_id` filtering on every query.

**Also known as:** Row-level multi-tenancy, tenant_id filtering

**Used by:** Fizzy, Basecamp, HEY (37signals)

## When to Use

- Most SaaS applications (recommended default)
- Simpler ops: one database to backup, migrate, monitor
- Cost-effective: single database instance
- Cross-tenant queries needed (analytics, admin dashboards)

## Trade-offs

**Pros:**
- Single schema to maintain
- Simpler deployment and migrations
- Lower infrastructure costs
- Easy cross-tenant operations

**Cons:**
- Risk of data leakage if WHERE clause missed
- "Noisy neighbor" potential (one tenant's load affects others)
- Tenant-specific customizations are harder

## Implementation

### Account Slug Middleware

Extract account from URL path (`/{account_id}/boards/...`):

```ruby
# config/initializers/tenanting/account_slug.rb
module AccountSlug
  PATTERN = /(\d{7,})/
  FORMAT = "%07d"
  PATH_INFO_MATCH = /\A(\/#{PATTERN})/

  def self.decode(slug) slug.to_i end
  def self.encode(id) FORMAT % id end

  class Extractor
    def initialize(app)
      @app = app
    end

    def call(env)
      request = ActionDispatch::Request.new(env)

      # Extract account ID from URL path
      if request.path_info =~ PATH_INFO_MATCH
        # Move slug from PATH_INFO to SCRIPT_NAME
        request.engine_script_name = request.script_name = $1
        request.path_info = $'.empty? ? "/" : $'

        env["app.external_account_id"] = AccountSlug.decode($2)
      end

      if env["app.external_account_id"]
        account = Account.find_by(external_account_id: env["app.external_account_id"])
        Current.with_account(account) { @app.call(env) }
      else
        Current.without_account { @app.call(env) }
      end
    end
  end
end

# Insert after Rack middleware
Rails.application.config.middleware.insert_after Rack::TempfileReaper, AccountSlug::Extractor
```

### CurrentAttributes

```ruby
class Current < ActiveSupport::CurrentAttributes
  attribute :session, :user, :account
  attribute :request_id, :user_agent, :ip_address

  delegate :identity, to: :session, allow_nil: true

  def session=(value)
    super(value)
    if value.present? && account.present?
      self.user = identity.users.find_by(account: account)
    end
  end

  def with_account(value, &block)
    with(account: value, &block)
  end

  def without_account(&block)
    with(account: nil, &block)
  end
end
```

### Model Scoping via Defaults

All models derive `account_id` from associations - no explicit filtering needed:

```ruby
class Board < ApplicationRecord
  belongs_to :creator, class_name: "User", default: -> { Current.user }
  belongs_to :account, default: -> { creator.account }
end

class Card < ApplicationRecord
  belongs_to :account, default: -> { board.account }
  belongs_to :board
end

class Comment < ApplicationRecord
  belongs_to :account, default: -> { card.account }
  belongs_to :card, touch: true
end

# For top-level models without a parent
class Tag < ApplicationRecord
  belongs_to :account, default: -> { Current.account }
end
```

### Account Model

```ruby
class Account < ApplicationRecord
  has_many :users, dependent: :destroy
  has_many :boards, dependent: :destroy
  has_many :cards, dependent: :destroy

  before_create :assign_external_account_id

  def slug
    "/#{external_account_id}"
  end

  private
    def assign_external_account_id
      self.external_account_id ||= ExternalIdSequence.next
    end
end
```

### Background Job Context Preservation

```ruby
# config/initializers/active_job.rb
module TenantedActiveJobExtensions
  extend ActiveSupport::Concern

  prepended do
    attr_reader :account
    self.enqueue_after_transaction_commit = true
  end

  def initialize(...)
    super
    @account = Current.account
  end

  def serialize
    super.merge({ "account" => @account&.to_gid })
  end

  def deserialize(job_data)
    super
    if _account = job_data.fetch("account", nil)
      @account = GlobalID::Locator.locate(_account)
    end
  end

  def perform_now
    if account.present?
      Current.with_account(account) { super }
    else
      super
    end
  end
end

ActiveSupport.on_load(:active_job) do
  prepend TenantedActiveJobExtensions
end
```

### ActionCable Multi-Tenancy

```ruby
# app/channels/application_cable/connection.rb
module ApplicationCable
  class Connection < ActionCable::Connection::Base
    identified_by :current_user

    def connect
      set_current_user || reject_unauthorized_connection
    end

    private
      def set_current_user
        if session = find_session_by_cookie
          account = Account.find_by(external_account_id: request.env["app.external_account_id"])
          Current.account = account
          self.current_user = session.identity.users.find_by!(account: account) if account
        end
      end
  end
end
```

### Turbo Streams with Multi-Tenancy

```ruby
# config/initializers/tenanting/turbo.rb
module TurboStreamsJobExtensions
  extend ActiveSupport::Concern

  class_methods do
    def render_format(format, **rendering)
      if Current.account.present?
        ApplicationController.renderer.new(
          script_name: Current.account.slug
        ).render(formats: [format], **rendering)
      else
        super
      end
    end
  end
end

Rails.application.config.after_initialize do
  Turbo::StreamsChannel.prepend TurboStreamsJobExtensions
end
```

## Testing

```ruby
class ActionDispatch::IntegrationTest
  setup do
    integration_session.default_url_options[:script_name] =
      "/#{ActiveRecord::FixtureSet.identify("37signals")}"
  end
end

def untenanted(&block)
  original = integration_session.default_url_options[:script_name]
  integration_session.default_url_options[:script_name] = ""
  yield
ensure
  integration_session.default_url_options[:script_name] = original
end
```
