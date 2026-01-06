# Database Per Tenant Multi-Tenancy

This pattern creates a separate database for each tenant. Tenant identification is typically done via subdomain.

**Also known as:** Database-level isolation, database sharding by tenant

**Implemented via:** `activerecord-tenanted` gem

## When to Use

- Strict compliance requirements (HIPAA, SOC2, data residency)
- Enterprise customers requiring complete data isolation
- Per-tenant backup/restore requirements
- Heavy per-tenant customization needs

## Trade-offs

**Pros:**
- Complete tenant isolation
- Easy tenant data export/restore/deletion
- No WHERE clause risks
- Per-tenant performance tuning possible

**Cons:**
- Complex schema migrations (N databases to update)
- Higher infrastructure costs
- Cross-tenant queries difficult
- More ops overhead

## Implementation

### Setup

```ruby
# Gemfile
gem "activerecord-tenanted", "~> 0.5.0"
```

### Configuration

```ruby
# config/initializers/tenancy.rb
Rails.application.configure do
  config.active_record_tenanted.tenant_resolver = ->(request) {
    TenantNameValidator.resolve(request.subdomain)
  }
  config.active_record_tenanted.default_tenant = Rails.env.local? ? "dev" : nil
  config.active_record_tenanted.connection_class = "AccountRecord"
end
```

### Database Configuration

```yaml
# config/database.yml
default: &default
  adapter: sqlite3
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
  timeout: 5000

development:
  primary:
    <<: *default
    database: storage/development/primary.sqlite3
  account:
    <<: *default
    database: storage/development/account/%{tenant_id}.sqlite3
    migrations_paths: db/account_migrate
```

### Base Models

```ruby
# app/models/application_record.rb
class ApplicationRecord < ActiveRecord::Base
  primary_abstract_class
  # For shared/global data (accounts, identities, etc.)
end

# app/models/account_record.rb
class AccountRecord < ActiveRecord::Base
  self.abstract_class = true
  tenanted "account"  # Specifies tenant database connection
end
```

### Account Model with Database Lifecycle

```ruby
class Account < ApplicationRecord
  include WithDatabase

  validates :tenant_id, presence: true, uniqueness: true,
            format: { with: /\A[a-z0-9-]+\z/ }
end

module Account::WithDatabase
  extend ActiveSupport::Concern

  included do
    after_create :create_tenant_database
    after_destroy :destroy_tenant_database
  end

  private
    def create_tenant_database
      AccountRecord.create_tenant(tenant_id)
    end

    def destroy_tenant_database
      AccountRecord.destroy_tenant(tenant_id)
    end
end
```

### Tenant Models

Models that should be isolated per tenant inherit from `AccountRecord`:

```ruby
class User < AccountRecord
  # Automatically scoped to current tenant database
end

class Reflection < AccountRecord
  belongs_to :user
end

class Board < AccountRecord
  has_many :cards
end
```

### Current Context

```ruby
class Current < ActiveSupport::CurrentAttributes
  attribute :session, :account

  delegate :user, to: :session, allow_nil: true

  def account
    super || self.account = Account.find_by(tenant_id: AccountRecord.current_tenant)
  end
end
```

### Controller Concern

```ruby
module Tenancy
  extend ActiveSupport::Concern

  included do
    helper_method :current_tenant
  end

  def current_tenant
    AccountRecord.current_tenant
  end
end
```

### Background Jobs

Jobs must manually pass and restore tenant context:

```ruby
class UpdateStateJob < ApplicationJob
  def perform(tenant_id, user_id)
    AccountRecord.with_tenant(tenant_id) do
      user = User.find(user_id)
      user.update_state
    end
  end
end

# Enqueuing - must pass tenant explicitly
UpdateStateJob.perform_later(AccountRecord.current_tenant, user.id)
```

### ActionCable

```ruby
module ApplicationCable
  class Connection < ActiveRecord::Tenanted::CableConnection::Base
    identified_by :current_user

    def connect
      AccountRecord.with_tenant(tenant_id) do
        self.current_user = find_verified_user
      end
    end
  end
end
```

## Testing

```ruby
class ActionDispatch::IntegrationTest
  setup do
    host! "dev.app.localhost"
  end
end

def with_tenant(tenant_id, &block)
  AccountRecord.with_tenant(tenant_id, &block)
end
```

## Comparison with Shared Database

| Aspect | Shared Database | Database Per Tenant |
|--------|-----------------|---------------------|
| Database | Single, account_id filtering | Separate per tenant |
| Isolation | Row-level | Database-level |
| Query Scoping | Manual (default lambdas) | Automatic (inheritance) |
| Job Context | Automatic (extensions) | Manual (parameter) |
| Gem | None (custom) | activerecord-tenanted |
| URL Format | `/123456/boards` | `tenant.app.com/boards` |
| Scaling | Horizontal (row filtering) | Horizontal (database sharding) |
| Dev Setup | Simple (one database) | Complex (manage N databases) |
| Migrations | Simple (one schema) | Complex (N schemas to update) |
| Compliance | Shared storage | Isolated storage |
