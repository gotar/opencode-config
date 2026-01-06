# Background Jobs Patterns (Solid Queue)

## Overview

Solid Queue is a database-backed job queue (no Redis required). Jobs are stored in the database and processed by worker processes.

## Directory Structure

```
app/jobs/
├── application_job.rb
├── notify_recipients_job.rb
├── export_account_data_job.rb
├── card/
│   ├── activity_spike/
│   │   └── detection_job.rb
│   └── remove_inaccessible_notifications_job.rb
├── event/
│   └── webhook_dispatch_job.rb
└── notification/
    └── bundle/
        ├── deliver_all_job.rb
        └── deliver_job.rb
```

## ApplicationJob

Keep it minimal:

```ruby
class ApplicationJob < ActiveJob::Base
  # Automatically retry jobs that encountered a deadlock
  # retry_on ActiveRecord::Deadlocked

  # Most jobs are safe to ignore if records no longer exist
  # discard_on ActiveJob::DeserializationError
end
```

## Account Context Preservation

Automatically capture and restore account context in jobs:

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

## Job Patterns

### Simple Job

```ruby
class NotifyRecipientsJob < ApplicationJob
  def perform(notifiable)
    notifiable.notify_recipients
  end
end
```

### Queue-Specific Job

```ruby
class ExportAccountDataJob < ApplicationJob
  queue_as :backend  # Heavy operation

  def perform(export)
    export.build
  end
end
```

### Webhook Dispatch Job

```ruby
class Event::WebhookDispatchJob < ApplicationJob
  queue_as :webhooks

  def perform(event)
    Webhook.active.triggered_by(event).find_each do |webhook|
      webhook.trigger(event)
    end
  end
end
```

### Batch Delivery Pattern

```ruby
class Notification::Bundle::DeliverAllJob < ApplicationJob
  queue_as :backend

  def perform
    Notification::Bundle.due.in_batches do |batch|
      jobs = batch.collect { |bundle| DeliverJob.new(bundle) }
      ActiveJob.perform_all_later(jobs)  # Bulk enqueue
    end
  end
end

class Notification::Bundle::DeliverJob < ApplicationJob
  def perform(bundle)
    bundle.deliver
  end
end
```

### Cleanup Job

```ruby
class DeleteUnusedTagsJob < ApplicationJob
  def perform
    Tag.unused.find_each(&:destroy)
  end
end
```

## Enqueuing Jobs

### From Model Callbacks

```ruby
module Notifiable
  extend ActiveSupport::Concern

  included do
    after_create_commit :notify_recipients_later
  end

  private
    def notify_recipients_later
      NotifyRecipientsJob.perform_later(self)
    end
end
```

### From Controllers

```ruby
def create
  @export = Current.account.exports.create!
  ExportAccountDataJob.perform_later(@export)
  redirect_to account_exports_path, notice: "Export started"
end
```

### Batch Enqueuing

```ruby
def deliver_all
  due.in_batches do |batch|
    jobs = batch.collect { |item| DeliverJob.new(item) }
    ActiveJob.perform_all_later(jobs)
  end
end
```

## Queue Configuration

```yaml
# config/queue.yml
default: &default
  dispatchers:
    - polling_interval: 1
      batch_size: 500
  workers:
    - queues: ["default", "solid_queue_recurring", "backend", "webhooks"]
      threads: 3
      processes: <%= ENV.fetch("JOB_CONCURRENCY", Concurrent.physical_processor_count) %>
      polling_interval: 0.1

production: *default
development: *default
test: *default
```

## Recurring Jobs

```yaml
# config/recurring.yml
production: &production
  # Application functionality
  deliver_bundled_notifications:
    command: "Notification::Bundle.deliver_all_later"
    schedule: every 30 minutes

  auto_postpone_all_due:
    command: "Card.auto_postpone_all_due"
    schedule: every hour at minute 50

  # Cleanup tasks
  delete_unused_tags:
    class: DeleteUnusedTagsJob
    schedule: every day at 04:02

  clear_solid_queue_finished_jobs:
    command: "SolidQueue::Job.clear_finished_in_batches(sleep_between_batches: 0.3)"
    schedule: every hour at minute 12

  cleanup_webhook_deliveries:
    command: "Webhook::Delivery.cleanup"
    schedule: every 4 hours at minute 51

  cleanup_magic_links:
    command: "MagicLink.cleanup"
    schedule: every 4 hours

development:
  <<: *production
```

## Error Handling

### State Tracking

```ruby
class Webhook::Delivery < ApplicationRecord
  enum :state, %i[pending in_progress completed errored]

  def deliver
    in_progress!
    self.response = perform_request
    self.state = :completed
    save!
  rescue => error
    errored!
    raise  # Re-raise for job framework retry
  end
end
```

### Classified Errors

```ruby
def perform_request
  # ... HTTP request ...
rescue Resolv::ResolvTimeout, Resolv::ResolvError
  { error: :dns_lookup_failed }
rescue Net::OpenTimeout, Net::ReadTimeout
  { error: :connection_timeout }
rescue Errno::ECONNREFUSED, Errno::EHOSTUNREACH
  { error: :destination_unreachable }
rescue OpenSSL::SSL::SSLError
  { error: :failed_tls }
end
```

### Retry Configuration

```ruby
class WebhookDeliveryJob < ApplicationJob
  retry_on Net::OpenTimeout, wait: :polynomially_longer, attempts: 5
  discard_on ActiveRecord::RecordNotFound
end
```

## Idempotency Patterns

### State Guards

```ruby
def deliver
  return if delivered?  # Guard against double delivery

  in_progress!
  # ... perform work ...
  delivered!
end
```

### Database Constraints

```ruby
def assign(user)
  assignments.create!(assignee: user)
rescue ActiveRecord::RecordNotUnique
  # Already assigned - idempotent
end
```

## Transaction Safety

Always use `enqueue_after_transaction_commit`:

```ruby
prepended do
  self.enqueue_after_transaction_commit = true
end
```

This prevents jobs from being enqueued before the transaction commits, avoiding race conditions where the job runs before the record is visible.

## Testing Jobs

```ruby
class DeleteUnusedTagsJobTest < ActiveJob::TestCase
  test "deletes tags not used by any cards" do
    unused = Tag.create!(title: "unused")

    assert_changes -> { Tag.count }, -1 do
      DeleteUnusedTagsJob.perform_now
    end

    assert_not Tag.exists?(unused.id)
  end
end

# Controller test with job assertions
test "creates export and enqueues job" do
  assert_enqueued_with(job: ExportAccountDataJob) do
    post account_exports_path
  end
end

# Perform jobs inline
test "delivers notification after creation" do
  perform_enqueued_jobs only: NotifyRecipientsJob do
    Comment.create!(body: "Hello", card: cards(:logo))
  end

  assert_equal 1, Notification.count
end
```

## Database Configuration

```yaml
# config/database.yml
production:
  primary:
    <<: *default
    database: app_production
  queue:
    <<: *default
    database: app_queue_production
    migrations_paths: db/queue_migrate
```

```ruby
# Connect Solid Queue to separate database
class SolidQueue::Record < ActiveRecord::Base
  self.abstract_class = true
  connects_to database: { writing: :queue, reading: :queue }
end
```

## Running Workers

```bash
# Development
bin/jobs start

# Production (via Procfile)
worker: bundle exec rails solid_queue:start

# Or in Puma process
# config/puma.rb
plugin :solid_queue if ENV["SOLID_QUEUE_IN_PUMA"]
```
