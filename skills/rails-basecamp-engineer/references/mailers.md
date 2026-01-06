# Mailer Patterns

> **Related:** For SMTP and email delivery configuration, see `configuration.md`.

## Philosophy

Keep mailers minimal. The logic belongs in models.

## Minimal Mailers

```ruby
# app/mailers/application_mailer.rb
class ApplicationMailer < ActionMailer::Base
  default from: -> { ENV.fetch("MAILER_FROM_ADDRESS", "support@app.com") }
  layout "mailer"
end
```

```ruby
# app/mailers/magic_link_mailer.rb
class MagicLinkMailer < ApplicationMailer
  def sign_in_instructions(magic_link)
    @magic_link = magic_link
    @identity = @magic_link.identity

    mail to: @identity.email_address,
         subject: "Your code is #{@magic_link.code}"
  end
end
```

## Sending from Models

Models decide when to send emails:

```ruby
# app/models/identity.rb
class Identity < ApplicationRecord
  def send_magic_link(purpose: :sign_in)
    magic_links.create!(purpose: purpose).tap do |link|
      MagicLinkMailer.send("#{purpose}_instructions", link).deliver_later
    end
  end
end
```

## Bundled Notifications

Instead of sending emails immediately, bundle them:

```ruby
# app/models/notification/bundle.rb
class Notification::Bundle
  class << self
    def deliver_all_later
      Identity.with_undelivered_notifications.find_each do |identity|
        DeliverBundledNotificationsJob.perform_later(identity)
      end
    end
  end
end
```

```ruby
# app/jobs/deliver_bundled_notifications_job.rb
class DeliverBundledNotificationsJob < ApplicationJob
  def perform(identity)
    notifications = identity.notifications.undelivered.preloaded

    if notifications.any?
      NotificationMailer.bundled(identity, notifications).deliver_now
      notifications.update_all(delivered_at: Time.current)
    end
  end
end
```

```yaml
# config/recurring.yml
production:
  deliver_bundled_notifications:
    command: "Notification::Bundle.deliver_all_later"
    schedule: every 30 minutes
```

## Mailer Views

Keep views simple:

```erb
<%# app/views/magic_link_mailer/sign_in_instructions.html.erb %>
<h1>Your sign-in code</h1>

<p>Enter this code to sign in:</p>

<p style="font-size: 24px; font-weight: bold; letter-spacing: 4px;">
  <%= @magic_link.code %>
</p>

<p>This code expires in 15 minutes.</p>
```

## Preview Mailers

```ruby
# test/mailers/previews/magic_link_mailer_preview.rb
class MagicLinkMailerPreview < ActionMailer::Preview
  def sign_in_instructions
    magic_link = MagicLink.first || MagicLink.new(
      code: "ABC123",
      identity: Identity.first
    )
    MagicLinkMailer.sign_in_instructions(magic_link)
  end
end
```

## Testing Mailers

```ruby
# test/mailers/magic_link_mailer_test.rb
class MagicLinkMailerTest < ActionMailer::TestCase
  test "sign_in_instructions" do
    magic_link = magic_links(:david_sign_in)
    email = MagicLinkMailer.sign_in_instructions(magic_link)

    assert_equal [magic_link.identity.email_address], email.to
    assert_includes email.subject, magic_link.code
    assert_includes email.body.encoded, magic_link.code
  end
end
```

## What NOT to Do

```ruby
# BAD: Logic in mailer
class NotificationMailer < ApplicationMailer
  def notify(user, event)
    return if user.unsubscribed?  # Don't do this
    return if event.old?          # Don't do this

    @event = event
    mail to: user.email
  end
end

# GOOD: Logic in model, mailer just sends
class NotificationMailer < ApplicationMailer
  def notify(user, event)
    @event = event
    mail to: user.email_address
  end
end

# In model
def notify_recipients
  return unless should_notify?

  recipients.each do |recipient|
    NotificationMailer.notify(recipient, self).deliver_later
  end
end
```

## Summary

| Do | Don't |
|----|-------|
| Minimal mailer methods | Complex logic in mailers |
| Send from models | Send from controllers |
| Bundle notifications | Send immediately for each event |
| Use deliver_later | Use deliver_now (except in jobs) |
| Preview mailers | Skip mailer testing |
