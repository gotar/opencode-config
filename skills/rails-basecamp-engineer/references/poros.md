# PORO Patterns (Plain Old Ruby Objects)

POROs are used for logic that doesn't fit in models or controllers, but they're **not service objects**. They're model-adjacent, namespaced under their parent model.

## Directory Structure

POROs live in the model directory, nested under their parent:

```
app/models/
├── event.rb
├── event/
│   ├── description.rb      # PORO - presentation logic
│   ├── particulars.rb      # Concern
│   └── promptable.rb       # Concern
├── card.rb
├── card/
│   ├── eventable/
│   │   └── system_commenter.rb  # PORO - business logic
│   ├── closeable.rb        # Concern
│   └── goldness.rb         # ActiveRecord model
```

## When to Use POROs

| Use Case | Example |
|----------|---------|
| Presentation logic | `Event::Description` formats events for display |
| Complex operations | `SystemCommenter` creates comments from events |
| View context bundling | `User::Filtering` collects filter UI state |
| NOT service objects | POROs are model-adjacent, not controller-adjacent |

## PORO for Presentation Logic

Formatting data for display:

```ruby
# app/models/event/description.rb
class Event::Description
  include ActionView::Helpers::TagHelper
  include ERB::Util

  attr_reader :event, :user

  def initialize(event, user)
    @event, @user = event, user
  end

  def to_html
    to_sentence(creator_tag, card_title_tag).html_safe
  end

  def to_plain_text
    to_sentence(creator_name, card.title)
  end

  private
    def action_sentence(creator, card_title)
      case event.action
      when "card_closed"
        %(#{creator} moved #{card_title} to "Done")
      when "card_reopened"
        "#{creator} reopened #{card_title}"
      when "card_assigned"
        "#{creator} assigned #{card_title} to #{assignee_names}"
      else
        "#{creator} updated #{card_title}"
      end
    end

    def creator_tag
      tag.strong(h(creator_name))
    end

    def creator_name
      event.creator == user ? "You" : event.creator.name
    end

    def card_title_tag
      tag.em(h(card.title))
    end

    def card
      event.eventable
    end
end
```

Usage:
```ruby
Event::Description.new(event, Current.user).to_html
```

## PORO for Business Logic

Encapsulating a specific operation:

```ruby
# app/models/card/eventable/system_commenter.rb
class Card::Eventable::SystemCommenter
  include ERB::Util

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
      when "card_closed"
        "<strong>Moved</strong> to \"Done\" by #{creator_name}"
      when "card_reopened"
        "<strong>Reopened</strong> by #{creator_name}"
      when "card_assigned"
        "<strong>Assigned</strong> to #{assignee_names} by #{creator_name}"
      when "card_board_changed"
        "<strong>Moved</strong> from #{old_board_name} by #{creator_name}"
      end
    end

    def creator_name
      h event.creator.name
    end

    def assignee_names
      event.assignees.map { |a| h(a.name) }.to_sentence
    end
end
```

Usage in concern:
```ruby
# app/models/card/eventable.rb
module Card::Eventable
  def event_was_created(event)
    transaction do
      SystemCommenter.new(self, event).comment
      touch_last_active_at unless was_just_published?
    end
  end
end
```

## PORO for View Context

Bundling data for complex views:

```ruby
# app/models/user/filtering.rb
class User::Filtering
  attr_reader :user, :filter, :expanded

  delegate :as_params, :single_board, to: :filter

  def initialize(user, filter, expanded: false)
    @user, @filter, @expanded = user, filter, expanded
  end

  def boards
    @boards ||= user.boards.ordered_by_recently_accessed
  end

  def tags
    @tags ||= user.tags.alphabetically
  end

  def users
    @users ||= user.accessible_users.active.alphabetically
  end

  def filters
    @filters ||= user.filters.alphabetically
  end

  def expanded?
    expanded
  end

  def cache_key
    ActiveSupport::Cache.expand_cache_key(
      [user, filter, expanded?, boards, tags, users, filters],
      "user-filtering"
    )
  end
end
```

Usage in controller:
```ruby
# app/controllers/concerns/filter_scoped.rb
module FilterScoped
  def set_user_filtering
    @user_filtering = User::Filtering.new(Current.user, @filter, expanded: expanded_param)
  end
end
```

## NOT Service Objects

POROs are **not** service objects. Compare:

```ruby
# BAD: Service object pattern (don't do this)
class CloseCardService
  def initialize(card, user)
    @card = card
    @user = user
  end

  def call
    @card.transaction do
      @card.create_closure!(user: @user)
      @card.track_event(:closed)
    end
  end
end

# Called from controller
CloseCardService.new(@card, Current.user).call

# GOOD: Method on model (do this)
class Card < ApplicationRecord
  def close(user: Current.user)
    transaction do
      create_closure!(user: user)
      track_event :closed, creator: user
    end
  end
end

# Called from controller
@card.close
```

## Design Guidelines

1. **Namespace under parent model**: `Event::Description`, not `EventDescriptionService`
2. **Initialize with data**: Pass objects in constructor
3. **Single responsibility**: One focused purpose
4. **No external side effects**: Don't call external services
5. **Testable in isolation**: No dependencies on request/controller
6. **Include helpers as needed**: `ActionView::Helpers`, `ERB::Util`
7. **Return values, not void**: Methods should return useful data

## When NOT to Use POROs

- **Simple transformations**: Use model methods
- **Controller orchestration**: Keep in controller
- **Cross-model transactions**: Use model method with explicit transaction
- **External API calls**: Use dedicated client classes (not POROs)
