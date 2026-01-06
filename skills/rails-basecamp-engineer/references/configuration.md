# Configuration Patterns

## ENV Pattern: Fetch with Defaults

Use `ENV.fetch` with sensible defaults:

```ruby
# Required with default
ENV.fetch("PORT", 3000)
ENV.fetch("SMTP_PORT", "587").to_i
ENV.fetch("MULTI_TENANT", "true")
ENV.fetch("DATABASE_ADAPTER", saas? ? "mysql" : "sqlite")

# Optional (no default)
ENV["MYSQL_PASSWORD"]
ENV["VAPID_PRIVATE_KEY"]
```

## Important ENV Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_ADAPTER` | `sqlite`/`mysql` | Database type |
| `MULTI_TENANT` | `true` | Enable multi-tenancy |
| `SMTP_ADDRESS` | - | SMTP server |
| `MAILER_FROM_ADDRESS` | `support@fizzy.do` | From address |
| `ACTIVE_STORAGE_SERVICE` | `local` | Storage backend |
| `DISABLE_SSL` | `false` | Disable SSL in prod |
| `SOLID_QUEUE_IN_PUMA` | - | Run jobs in web process |

## Multiple Databases

Separate databases for different concerns:

```yaml
# config/database.mysql.yml
default: &default
  adapter: trilogy
  host: <%= ENV.fetch("MYSQL_HOST", "127.0.0.1") %>
  port: <%= ENV.fetch("MYSQL_PORT", "3306") %>
  pool: 50
  timeout: 5000

production:
  primary:
    <<: *default
    database: fizzy_production
  cable:
    <<: *default
    database: fizzy_production_cable
  queue:
    <<: *default
    database: fizzy_production_queue
  cache:
    <<: *default
    database: fizzy_production_cache
```

- **Primary** - Main app data
- **Cable** - ActionCable/WebSocket messages (Solid Cable)
- **Queue** - Background jobs (Solid Queue)
- **Cache** - Rails cache (Solid Cache)

## SQLite for Simple Deployments

```yaml
# config/database.sqlite.yml
production:
  primary:
    adapter: sqlite3
    database: storage/production.sqlite3
    pool: 5
```

## Dynamic Database Selection

```ruby
# lib/fizzy.rb
module Fizzy
  def db_adapter
    @db_adapter ||= DbAdapter.new ENV.fetch("DATABASE_ADAPTER", saas? ? "mysql" : "sqlite")
  end

  def saas?
    ENV.fetch("MULTI_TENANT", "true") == "true"
  end
end
```

```yaml
# config/database.yml
<%= ERB.new(File.read("config/database.#{Fizzy.db_adapter}.yml")).result %>
```

## Minimal Logging

Almost no explicit logging in app code:

```ruby
# Only log actual errors, not routine operations
Rails.logger.error error
Rails.logger.error error.backtrace.join("\n")
```

Let Rails handle logging. Don't litter code with log statements.

## Configuration via Initializers

```ruby
# config/initializers/multi_tenant.rb
Rails.application.configure do
  config.after_initialize do
    Account.multi_tenant = ENV["MULTI_TENANT"] == "true" || config.x.multi_tenant.enabled == true
  end
end
```

## CSP Configuration

Extensible via ENV:

```ruby
# config/initializers/content_security_policy.rb
Rails.application.configure do
  config.content_security_policy do |policy|
    policy.default_src :self
    policy.script_src  :self, *sources.(:script_src)
    policy.style_src   :self, :unsafe_inline, *sources.(:style_src)
    policy.img_src     :self, :data, :blob, *sources.(:img_src)
    policy.connect_src :self, *sources.(:connect_src)
  end
end

# Helper to get additional CSP sources from ENV
sources = ->(directive) do
  env_key = "CSP_#{directive.to_s.upcase}"
  value = ENV[env_key]

  case value
  when nil then []
  when String then value.split
  else []
  end
end
```

Usage:
```bash
CSP_SCRIPT_SRC="https://cdn.example.com" rails server
```

## Solid Stack Configuration

### Solid Queue

```yaml
# config/solid_queue.yml
default: &default
  dispatchers:
    - polling_interval: 1
      batch_size: 500
  workers:
    - queues: "*"
      threads: 3
      processes: 1
      polling_interval: 0.1

production:
  <<: *default
```

### Solid Cache

```yaml
# config/solid_cache.yml
default: &default
  database: cache
  store_options:
    max_age: <%= 1.week.to_i %>
    max_size: <%= 256.megabytes %>
    namespace: <%= Rails.env %>

production:
  <<: *default
```

### Solid Cable

```yaml
# config/cable.yml
production:
  adapter: solid_cable
  connects_to:
    database:
      writing: cable
  polling_interval: 0.1.seconds
  message_retention: 1.day
```

## Recurring Jobs

```yaml
# config/recurring.yml
production:
  deliver_bundled_notifications:
    command: "Notification::Bundle.deliver_all_later"
    schedule: every 30 minutes

  auto_postpone_all_due:
    command: "Card.auto_postpone_all_due"
    schedule: every hour at minute 50

  cleanup_magic_links:
    command: "MagicLink.stale.delete_all"
    schedule: every 4 hours

  cleanup_sessions:
    command: "Session.stale.delete_all"
    schedule: every day at 3am
```

## Storage Configuration

```yaml
# config/storage.yml
local:
  service: Disk
  root: <%= Rails.root.join("storage") %>

amazon:
  service: S3
  access_key_id: <%= ENV["AWS_ACCESS_KEY_ID"] %>
  secret_access_key: <%= ENV["AWS_SECRET_ACCESS_KEY"] %>
  region: <%= ENV.fetch("AWS_REGION", "us-east-1") %>
  bucket: <%= ENV["AWS_BUCKET"] %>
```

```ruby
# config/environments/production.rb
config.active_storage.service = ENV.fetch("ACTIVE_STORAGE_SERVICE", "local").to_sym
```

## Summary

| Pattern | Example |
|---------|---------|
| Required with default | `ENV.fetch("PORT", 3000)` |
| Optional | `ENV["API_KEY"]` |
| Multiple databases | primary, cable, queue, cache |
| Database selection | Dynamic based on `DATABASE_ADAPTER` |
| CSP extension | Via `CSP_*` ENV vars |
| Logging | Minimal - let Rails handle it |
