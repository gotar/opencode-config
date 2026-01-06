# Event Tracking Patterns

## Overview

Event tracking creates an audit trail of significant actions in the application. Events drive:
- Activity timelines and history
- Notifications to users
- Webhook dispatches to external systems
- System-generated comments for inline context

## Event Model

The central Event model records all trackable actions:

```ruby
class Event < ApplicationRecord
  include Notifiable, Particulars

  belongs_to :account, default: -> { board.account }
  belongs_to :board
  belongs_to :creator, class_name: "User"
  belongs_to :eventable, polymorphic: true

  has_many :webhook_deliveries, class_name: "Webhook::Delivery", dependent: :delete_all

  scope :chronologically, -> { order(created_at: :asc, id: :desc) }
  scope :preloaded, -> {
    includes(:creator, :board, {
      eventable: [
        :closure, :image_attachment,
        { rich_text_body: :embeds_attachments },
        { card: [:closure, :image_attachment] }
      ]
    })
  }

  after_create -> { eventable.event_was_created(self) }
  after_create_commit :dispatch_webhooks

  delegate :card, to: :eventable

  def action
    super.inquiry  # Returns StringInquirer for nice predicate methods
  end

  private
    def dispatch_webhooks
      Event::WebhookDispatchJob.perform_later(self)
    end
end
```

## Eventable Concern

Include this concern in any model that should track events:

```ruby
module Eventable
  extend ActiveSupport::Concern

  included do
    has_many :events, as: :eventable, dependent: :destroy
  end

  def track_event(action, creator: Current.user, board: self.board, **particulars)
    if should_track_event?
      board.events.create!(
        action: "#{eventable_prefix}_#{action}",
        creator: creator,
        board: board,
        eventable: self,
        particulars: particulars
      )
    end
  end

  # Override in model to respond to event creation
  def event_was_created(event)
  end

  private
    def should_track_event?
      true
    end

    def eventable_prefix
      self.class.name.demodulize.underscore
    end
end
```

## Model-Specific Eventable Concerns

Override the base Eventable in model-specific concerns:

### Card::Eventable

```ruby
module Card::Eventable
  extend ActiveSupport::Concern

  include ::Eventable

  included do
    before_create { self.last_active_at = Time.current }
    after_save :track_title_change, if: :saved_change_to_title?
  end

  def event_was_created(event)
    transaction do
      create_system_comment_for(event)
      touch_last_active_at
    end
  end

  def touch_last_active_at
    update!(last_active_at: Time.current)
    broadcast_activity
  end

  private
    def should_track_event?
      published?  # Only track events for published cards
    end

    def track_title_change
      if title_before_last_save.present?
        track_event "title_changed", particulars: {
          old_title: title_before_last_save,
          new_title: title
        }
      end
    end

    def create_system_comment_for(event)
      SystemCommenter.new(self, event).comment
    end

    def broadcast_activity
      broadcast_render_later_to self, :activity,
        partial: "card/display/refresh_activity",
        locals: { card: self }
    end
end
```

### Comment::Eventable

```ruby
module Comment::Eventable
  extend ActiveSupport::Concern

  include ::Eventable

  included do
    after_create_commit :track_creation
  end

  def event_was_created(event)
    card.touch_last_active_at
  end

  private
    def should_track_event?
      !creator.system?  # Don't track system-generated comments
    end

    def track_creation
      track_event("created", board: card.board, creator: creator)
    end
end
```

## Tracking Events from Actions

Call `track_event` from domain methods that represent significant actions:

### State Changes

```ruby
module Card::Closeable
  def close(user: Current.user)
    unless closed?
      transaction do
        create_closure!(user: user)
        track_event :closed, creator: user
      end
    end
  end

  def reopen(user: Current.user)
    if closed?
      transaction do
        closure&.destroy
        track_event :reopened, creator: user
      end
    end
  end
end
```

### Assignments

```ruby
module Card::Assignable
  private
    def assign(user)
      assignments.create! assignee: user, assigner: Current.user
      watch_by user
      track_event :assigned, assignee_ids: [user.id]
    rescue ActiveRecord::RecordNotUnique
      # Already assigned
    end

    def unassign(user)
      destructions = assignments.destroy_by assignee: user
      track_event :unassigned, assignee_ids: [user.id] if destructions.any?
    end
end
```

### Movement/Status Changes

```ruby
module Card::Triageable
  def triage_to(column, triager: Current.user)
    transaction do
      update! column: column, triaged_at: Time.current, triager: triager
      track_event :triaged, creator: triager, particulars: { column: column.name }
    end
  end

  def send_back_to_triage(user: Current.user)
    transaction do
      update! column: nil, triaged_at: nil, triager: nil
      track_event :sent_back_to_triage, creator: user
    end
  end
end
```

## Event Particulars

Store action-specific data in a JSON column:

```ruby
module Event::Particulars
  extend ActiveSupport::Concern

  included do
    store_accessor :particulars, :assignee_ids
  end

  def assignees
    @assignees ||= User.where(id: assignee_ids)
  end
end
```

Usage in events:

```ruby
# Tracking with particulars
track_event :assigned, assignee_ids: [user.id]
track_event :title_changed, particulars: { old_title: "Foo", new_title: "Bar" }
track_event :moved, particulars: { old_board: "Design", new_board: "Development" }

# Accessing particulars
event.assignee_ids              # => ["uuid-1", "uuid-2"]
event.assignees                 # => [User, User]
event.particulars["old_title"]  # => "Foo"
```

## Event Descriptions

Generate human-readable descriptions for display:

```ruby
class Event::Description
  include ActionView::Helpers::TagHelper
  include ERB::Util

  attr_reader :event, :user

  def initialize(event, user)
    @event = event
    @user = user
  end

  def to_html
    to_sentence(creator_tag, card_title_tag).html_safe
  end

  def to_plain_text
    to_sentence(creator_name, card.title)
  end

  private
    def to_sentence(creator, card_title)
      case event.action
      when "comment_created"
        "#{creator} commented on #{card_title}"
      when "card_assigned"
        assigned_sentence(creator, card_title)
      when "card_closed"
        %(#{creator} moved #{card_title} to "Done")
      when "card_reopened"
        "#{creator} reopened #{card_title}"
      when "card_title_changed"
        old_title = event.particulars.dig("particulars", "old_title")
        %(#{creator} renamed #{card_title} (was: "#{h old_title}"))
      end
    end

    def assigned_sentence(creator, card_title)
      if event.assignees.include?(user)
        "#{creator} will handle #{card_title}"
      else
        "#{creator} assigned #{h event.assignees.pluck(:name).to_sentence} to #{card_title}"
      end
    end

    # Personalized creator display
    def creator_tag
      tag.span data: { creator_id: event.creator.id } do
        tag.span("You", data: { only_visible_to_you: true }) +
        tag.span(event.creator.name, data: { only_visible_to_others: true })
      end
    end
end
```

Usage in views:

```erb
<%= event.description_for(Current.user).to_html %>
```

## System Comments

Auto-generate inline comments from events for context:

```ruby
class Card::Eventable::SystemCommenter
  attr_reader :card, :event

  def initialize(card, event)
    @card, @event = card, event
  end

  def comment
    return unless comment_body.present?

    card.comments.create!(
      creator: card.account.system_user,
      body: comment_body,
      created_at: event.created_at
    )
  end

  private
    def comment_body
      case event.action
      when "card_assigned"
        "#{event.creator.name} <strong>assigned</strong> this to #{event.assignees.pluck(:name).to_sentence}."
      when "card_closed"
        "<strong>Moved</strong> to \"Done\" by #{event.creator.name}"
      when "card_title_changed"
        old = event.particulars.dig('particulars', 'old_title')
        new = event.particulars.dig('particulars', 'new_title')
        "#{event.creator.name} <strong>changed the title</strong> from \"#{old}\" to \"#{new}\"."
      end
    end
end
```

## Notifications from Events

Events trigger notifications via the Notifiable concern:

```ruby
module Notifiable
  extend ActiveSupport::Concern

  included do
    has_many :notifications, as: :source, dependent: :destroy

    after_create_commit :notify_recipients_later
  end

  def notify_recipients
    Notifier.for(self)&.notify
  end

  def notifiable_target
    self
  end

  private
    def notify_recipients_later
      NotifyRecipientsJob.perform_later(self)
    end
end
```

## Webhook Dispatch

Events automatically dispatch to configured webhooks:

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

## Action Inquiry

Use Rails StringInquirer for clean action checks:

```ruby
class Event < ApplicationRecord
  def action
    super.inquiry
  end
end

# Usage
if event.action.card_closed?
  # ...
elsif event.action.comment_created?
  # ...
end
```

## Best Practices

1. **Track in transactions** - Always track events within the same transaction as the action:
   ```ruby
   transaction do
     create_closure!(user: user)
     track_event :closed, creator: user
   end
   ```

2. **Use after_create_commit for async work** - Notifications and webhooks should dispatch after commit:
   ```ruby
   after_create_commit :dispatch_webhooks
   ```

3. **Store context in particulars** - Capture data that may change later (like old titles):
   ```ruby
   track_event :moved, particulars: {
     old_board: board.name,  # Store name, not just ID
     new_board: new_board.name
   }
   ```

4. **Conditional tracking** - Override `should_track_event?` to skip tracking in certain states:
   ```ruby
   def should_track_event?
     published? && !creator.system?
   end
   ```

5. **Prefixed actions** - Actions are auto-prefixed with the model name for clarity:
   ```ruby
   # In Card model
   track_event :closed  # Creates action: "card_closed"

   # In Comment model
   track_event :created  # Creates action: "comment_created"
   ```

6. **Respond to events** - Use `event_was_created` to trigger side effects:
   ```ruby
   def event_was_created(event)
     transaction do
       create_system_comment_for(event)
       touch_last_active_at
     end
   end
   ```

## Testing Events

```ruby
test "closing a card tracks the closed event" do
  card = cards(:logo)

  assert_difference -> { Event.count } do
    card.close(user: users(:david))
  end

  event = card.events.last
  assert_equal "card_closed", event.action
  assert_equal users(:david), event.creator
end

test "tracking event creates system comment" do
  card = cards(:logo)

  assert_difference -> { card.comments.count } do
    card.close(user: users(:david))
  end

  comment = card.comments.last
  assert_equal card.account.system_user, comment.creator
  assert_includes comment.body, "Done"
end

test "events dispatch webhooks" do
  card = cards(:logo)
  webhook = webhooks(:card_events)

  assert_enqueued_with(job: Event::WebhookDispatchJob) do
    card.close(user: users(:david))
  end
end
```
