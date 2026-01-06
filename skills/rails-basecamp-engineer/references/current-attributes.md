# CurrentAttributes Pattern

## Overview

`Current` is a singleton class using Rails' `ActiveSupport::CurrentAttributes` to provide thread-safe, request-scoped context throughout the application. It stores session, user, account, and request metadata that can be accessed anywhere without passing parameters.

## Basic Implementation

```ruby
# app/models/current.rb
class Current < ActiveSupport::CurrentAttributes
  attribute :session, :user, :account
  attribute :request_id, :user_agent, :ip_address, :http_method, :referrer
end
```

## Key Features

### Thread-Safe Request Isolation

Each request gets its own isolated `Current` instance. Values set in one request don't leak to others:

```ruby
# Request A sets Current.user = alice
# Request B sets Current.user = bob
# They don't interfere with each other
```

### Automatic Reset

Rails automatically resets all `Current` attributes after each request. No manual cleanup needed.

### Global Access

Access current context from anywhere - models, controllers, views, jobs, mailers:

```ruby
# In a model
belongs_to :creator, default: -> { Current.user }

# In a controller
@boards = Current.user.boards

# In a view
<%= Current.user.name %>

# In a job (with proper setup)
Current.with_account(account) { perform_work }
```

## Multi-Tenant Implementation

For multi-tenant applications, `Current` manages account context:

```ruby
class Current < ActiveSupport::CurrentAttributes
  attribute :session, :user, :account
  attribute :request_id, :user_agent, :ip_address

  delegate :identity, to: :session, allow_nil: true

  # Automatically derive user when session is set
  def session=(value)
    super(value)
    if value.present? && account.present?
      self.user = identity.users.find_by(account: account)
    end
  end

  # Helper for scoped execution
  def with_account(value, &block)
    with(account: value, &block)
  end

  def without_account(&block)
    with(account: nil, &block)
  end
end
```

### Setting Account Context

Account context is typically set by middleware before the request reaches controllers:

```ruby
# In middleware
def call(env)
  account = resolve_account_from_request(env)

  if account
    Current.with_account(account) { @app.call(env) }
  else
    Current.without_account { @app.call(env) }
  end
end
```

### Cascading Derivation

When session is set, user is automatically derived based on account:

```ruby
Current.account = accounts(:acme)
Current.session = session  # session.identity has multiple users
# Current.user is now automatically set to identity's user in acme account
```

## Request Context Attributes

Track request metadata for logging, debugging, and auditing:

```ruby
class Current < ActiveSupport::CurrentAttributes
  attribute :request_id, :user_agent, :ip_address, :http_method, :referrer
end

# Set in controller concern
module CurrentRequest
  extend ActiveSupport::Concern

  included do
    before_action :set_request_context
  end

  private
    def set_request_context
      Current.request_id  = request.uuid
      Current.user_agent  = request.user_agent
      Current.ip_address  = request.ip
      Current.http_method = request.method
      Current.referrer    = request.referrer
    end
end
```

## Delegation Pattern

Delegate through `Current` for cleaner access:

```ruby
class Current < ActiveSupport::CurrentAttributes
  attribute :session

  delegate :identity, to: :session, allow_nil: true
  delegate :email_address, to: :identity, allow_nil: true, prefix: true
end

# Usage
Current.identity           # => Identity object
Current.identity_email_address  # => "user@example.com"
```

## Using Current in Models

### Default Association Values

```ruby
class Comment < ApplicationRecord
  belongs_to :creator, class_name: "User", default: -> { Current.user }
  belongs_to :account, default: -> { Current.account }
end

# When creating comments, creator and account are automatically set
Comment.create!(body: "Hello")  # creator = Current.user, account = Current.account
```

### Derived Defaults via Chain

```ruby
class Card < ApplicationRecord
  belongs_to :board
  belongs_to :account, default: -> { board.account }
  belongs_to :creator, class_name: "User", default: -> { Current.user }
end

class Comment < ApplicationRecord
  belongs_to :card
  belongs_to :account, default: -> { card.account }
  belongs_to :creator, class_name: "User", default: -> { Current.user }
end
```

### Event Tracking with Current Context

```ruby
module Eventable
  def track_event(action, **particulars)
    events.create!(
      action: action,
      creator: Current.user,  # Automatically use current user
      account: Current.account,
      particulars: particulars
    )
  end
end
```

## Using Current in Background Jobs

Jobs run outside request context, so `Current` must be explicitly managed:

### Capture and Restore Account

```ruby
module TenantedActiveJobExtensions
  extend ActiveSupport::Concern

  prepended do
    attr_reader :account
  end

  def initialize(...)
    super
    @account = Current.account  # Capture at enqueue time
  end

  def serialize
    super.merge("account" => @account&.to_gid)
  end

  def deserialize(job_data)
    super
    if gid = job_data["account"]
      @account = GlobalID::Locator.locate(gid)
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

### Manual Context in Jobs

For jobs that need different context:

```ruby
class CrossAccountReportJob < ApplicationJob
  def perform(account_ids)
    account_ids.each do |account_id|
      account = Account.find(account_id)
      Current.with_account(account) do
        generate_report_for_account
      end
    end
  end
end
```

## Using Current in ActionCable

WebSocket connections need explicit context setup:

```ruby
module ApplicationCable
  class Connection < ActionCable::Connection::Base
    identified_by :current_user

    def connect
      if session = find_session
        account = resolve_account_from_request
        Current.account = account
        self.current_user = session.identity.users.find_by(account: account)
      else
        reject_unauthorized_connection
      end
    end
  end
end
```

## Using Current in Mailers

Mailers may run in job context, so verify Current is set:

```ruby
class NotificationMailer < ApplicationMailer
  def weekly_digest(user)
    # Ensure account context for URL generation
    Current.with_account(user.account) do
      @user = user
      @notifications = user.notifications.recent
      mail(to: user.email)
    end
  end
end
```

## ETags with Current

Include session in ETags for cache invalidation:

```ruby
class ApplicationController < ActionController::Base
  etag { Current.session&.id }
  etag { Current.account&.id }
end
```

## Testing with Current

### Setting Context in Tests

```ruby
setup do
  Current.account = accounts(:acme)
  Current.session = sessions(:david)
end

teardown do
  Current.reset_all
end
```

### Helper for Temporary Context

```ruby
def with_current_user(user)
  old_session = Current.session
  Current.session = Session.new(identity: user.identity)
  yield
ensure
  Current.session = old_session
end

test "user can create comments" do
  with_current_user(users(:david)) do
    comment = Comment.create!(body: "Hello", card: cards(:first))
    assert_equal users(:david), comment.creator
  end
end
```

## Common Patterns

### Convenience Methods

```ruby
class Current < ActiveSupport::CurrentAttributes
  attribute :session, :user, :account

  def admin?
    user&.admin?
  end

  def authenticated?
    session.present?
  end

  def account_slug
    account&.slug
  end
end
```

### Lazy Loading

```ruby
class Current < ActiveSupport::CurrentAttributes
  attribute :session, :_user, :account

  def user
    @_user ||= identity&.users&.find_by(account: account)
  end
end
```

## Best Practices

1. **Keep it minimal** - Only store truly request-scoped data
2. **Avoid business logic** - Current is for context, not computation
3. **Always nil-safe** - Use `&.` or `try` when accessing nested attributes
4. **Document dependencies** - Make clear what sets each attribute
5. **Test context setup** - Verify Current is properly set in different contexts
6. **Use `with` for scoped changes** - Don't mutate Current directly in nested contexts

## Anti-Patterns

```ruby
# BAD: Complex business logic in Current
def user_dashboard_data
  user.boards.with_recent_activity  # Move to presenter/service
end

# BAD: Storing non-request data
attribute :cached_settings  # Use Rails.cache instead

# BAD: Mutating in nested context without scoping
def nested_operation
  old_account = Current.account
  Current.account = other_account  # Dangerous! Use with() instead
  # ...
  Current.account = old_account
end

# GOOD: Use with() for scoped changes
def nested_operation
  Current.with(account: other_account) do
    # ...
  end
end
```
