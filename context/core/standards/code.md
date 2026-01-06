<!-- Context: standards/code | Priority: critical | Version: 2.0 | Updated: 2025-01-21 -->
# Code Standards

## Quick Reference

**Core Philosophy**: Rails-First, Composition over Inheritance, Rich Domain Models
**Golden Rule**: If you can't easily test it, refactor it

**Critical Patterns** (use these):
- ✅ Composition over inheritance (concerns)
- ✅ Rich domain models (business logic in models)
- ✅ Minimal controllers (push logic to models/concerns)
- ✅ Explicit transactions (wrap critical operations)
- ✅ Event tracking (audit trails for significant actions)
- ✅ Strong parameters (strict input validation)

**Anti-Patterns** (avoid these):
- ❌ Fat controllers, skinny models
- ❌ Deep inheritance hierarchies
- ❌ Complex callback chains
- ❌ Synchronous external service calls
- ❌ Missing transaction safety

---

## Core Philosophy

**Rails-First**: Prefer Rails conventions and native features over external gems
**Composition**: Build complex behavior through concern composition
**Domain-Driven**: Models are the heart of the application, rich with business logic
**Transactional**: Wrap critical operations in database transactions
**Event-Driven**: Track significant actions for audit trails and notifications

## Principles

### Model-Centric Design
- **Rich models**: Business logic lives in models and concerns
- **Composition over inheritance**: Use concerns to compose behavior
- **Transaction safety**: Wrap critical operations in transactions
- **Event tracking**: Record significant actions for audit trails

### Controller Minimalism
- **Thin controllers**: Push business logic to models and concerns
- **Strong parameters**: Strict input validation with `params.expect()`
- **Turbo Stream responses**: Real-time UI updates with Hotwire
- **Concern-based scoping**: Reusable controller logic via concerns

### Concern-Driven Architecture
- **Feature-based organization**: Group code by domain feature
- **Cross-cutting concerns**: Shared behavior across models/controllers
- **Single responsibility**: Each concern has one clear purpose
- **Composable**: Mix and match concerns to build complex behavior

### Directory Structure
```
app/
├── models/
│   ├── application_record.rb
│   ├── concerns/              # Cross-cutting concerns
│   │   ├── searchable.rb
│   │   ├── notifiable.rb
│   │   └── eventable.rb
│   ├── card.rb
│   └── card/                   # Card-specific concerns
│       ├── assignable.rb
│       └── closeable.rb
├── controllers/
│   ├── application_controller.rb
│   ├── concerns/              # Controller concerns
│   │   ├── board_scoped.rb
│   │   └── card_scoped.rb
│   ├── cards_controller.rb
│   └── cards/
│       └── comments_controller.rb
└── jobs/
    └── notify_recipients_job.rb
```

## Patterns

### Concern Composition
```ruby
# ✅ Composition over inheritance
class Card < ApplicationRecord
  include Assignable, Closeable, Eventable, Taggable,
          Watchable, Searchable, Notifiable, Mentions
end

# ❌ Deep inheritance
class TaggableCard < Card
  # ...
end
```

### Rich Domain Models
```ruby
# ✅ Business logic in models
class Card < ApplicationRecord
  def close(user: Current.user)
    return if closed?

    transaction do
      create_closure!(user: user)
      track_event :closed, creator: user
    end
  end

  def reopen(user: Current.user)
    return unless closed?

    transaction do
      closure.destroy
      track_event :reopened, creator: user
    end
  end
end

# ❌ Business logic in controllers
def close
  @card.closure = Closure.new(user: current_user)
  @card.save!
  Event.create!(action: 'closed', card: @card)
end
```

### Transaction Safety
```ruby
# ✅ Wrap critical operations
def handle_board_change
  old_board = account.boards.find_by(id: board_id_before_last_save)

  transaction do
    update!(column: nil)
    track_board_change_event(old_board.name)
    grant_access_to_assignees unless board.all_access?
  end

  remove_inaccessible_notifications_later
end

# ❌ Unprotected operations
def transfer_card
  update!(board: new_board)
  create_notification
  send_webhook
end
```

### Event Tracking
```ruby
# ✅ Track significant actions
module Eventable
  def track_event(action, creator: Current.user, **particulars)
    board.events.create!(
      action: "#{eventable_prefix}_#{action}",
      creator: creator,
      eventable: self,
      particulars: particulars
    )
  end
end

# Usage
card.close(user: user)  # Automatically tracks :closed event
```

### Strong Parameters
```ruby
# ✅ Strict parameter validation
def card_params
  params.expect(card: [:title, :description, tag_ids: []])
end

def webhook_params
  params.expect(webhook: [:name, :url, subscribed_actions: []])
        .merge(board_id: @board.id)
end

# ❌ Permissive parameters
def card_params
  params.require(:card).permit(:title, :description, tag_ids: [])
end
```

### Controller Concerns
```ruby
# ✅ Reusable scoping logic
module CardScoped
  extend ActiveSupport::Concern

  included do
    before_action :set_card, :set_board
  end

  private
    def set_card
      @card = Current.user.accessible_cards.find_by!(number: params[:card_id])
    end

    def set_board
      @board = @card.board
    end
end
```

## Naming Conventions

- **Models**: PascalCase (User, Card, Board)
- **Concerns**: AdjectiveVerb (Assignable, Closeable, Eventable)
- **Controllers**: PluralResourceController (CardsController)
- **Jobs**: VerbNounJob (NotifyRecipientsJob)
- **Scopes**: Adverbs (chronologically, alphabetically, reverse_chronologically)
- **Methods**: snake_case, verb phrases (create_with_owner, track_event)

## Error Handling

```ruby
# ✅ Let Rails handle validation errors
def create
  @card = Card.create!(card_params)  # Raises on validation failure
  redirect_to @card
end

# ✅ Rescue specific exceptions
def create
  @card = Card.create!(card_params)
  redirect_to @card
rescue ActiveRecord::RecordInvalid => e
  flash[:error] = e.message
  render :new
end

# ❌ Generic rescue
def create
  @card = Card.create(card_params)
  redirect_to @card
rescue => e
  flash[:error] = "Something went wrong"
  render :new
end
```

## Anti-Patterns

❌ **Fat controllers**: Business logic in controllers
❌ **Deep inheritance**: Complex class hierarchies
❌ **Callback chains**: Complex before/after_save chains
❌ **Synchronous external calls**: API calls in model callbacks
❌ **Missing transactions**: Unprotected multi-step operations
❌ **Permissive parameters**: Weak input validation
❌ **God models**: Models with too many responsibilities

## Best Practices

✅ **Composition over inheritance**: Use concerns to build behavior
✅ **Rich domain models**: Keep business logic in models
✅ **Transaction safety**: Wrap critical operations
✅ **Event tracking**: Audit significant actions
✅ **Strong parameters**: Strict input validation
✅ **Minimal controllers**: Thin controller actions
✅ **Concern organization**: Group related behavior
✅ **Rails conventions**: Follow Rails patterns and naming

**Golden Rule**: If you can't easily test it, refactor it.
