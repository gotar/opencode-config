# Model Patterns

## Directory Structure

Organize models by domain with nested concerns:

```
app/models/
├── application_record.rb
├── current.rb                   # CurrentAttributes
├── concerns/                    # Cross-cutting concerns
│   ├── attachments.rb
│   ├── searchable.rb
│   ├── notifiable.rb
│   └── mentions.rb
├── card.rb
├── card/                        # Card-specific concerns
│   ├── assignable.rb
│   ├── closeable.rb
│   ├── eventable.rb
│   └── taggable.rb
├── board.rb
├── board/
│   ├── accessible.rb
│   └── publishable.rb
└── user/
    ├── role.rb
    └── accessor.rb
```

## ApplicationRecord

```ruby
class ApplicationRecord < ActiveRecord::Base
  primary_abstract_class

  # UUID primary keys with automatic generation
  attribute :id, :uuid, default: -> { ActiveRecord::Type::Uuid.generate }
end
```

## Concerns - Feature-Based Composition

Heavy use of concerns to compose behavior - models include 10-20+ concerns:

```ruby
class Card < ApplicationRecord
  include Assignable, Closeable, Eventable, Taggable,
          Watchable, Searchable, Notifiable, Mentions
end
```

### Concern Structure

```ruby
module Card::Assignable
  extend ActiveSupport::Concern

  included do
    has_many :assignments, dependent: :delete_all
    has_many :assignees, through: :assignments

    scope :assigned_to, ->(users) {
      joins(:assignments).where(assignments: { assignee: users }).distinct
    }
  end

  def toggle_assignment(user)
    assigned_to?(user) ? unassign(user) : assign(user)
  end

  def assigned_to?(user)
    assignees.include?(user)
  end

  private
    def assign(user)
      assignments.create!(assignee: user, assigner: Current.user)
      track_event :assigned, assignee_ids: [user.id]
    rescue ActiveRecord::RecordNotUnique
      # Already assigned - idempotent
    end

    def unassign(user)
      assignments.find_by(assignee: user)&.destroy
      track_event :unassigned, assignee_ids: [user.id]
    end
end
```

### Cross-Cutting Concerns

```ruby
# app/models/concerns/notifiable.rb
module Notifiable
  extend ActiveSupport::Concern

  included do
    has_many :notifications, as: :source, dependent: :destroy
    after_create_commit :notify_recipients_later
  end

  def notify_recipients
    Notifier.for(self)&.notify
  end

  private
    def notify_recipients_later
      NotifyRecipientsJob.perform_later(self)
    end
end
```

## Associations

### Default Values from Context

```ruby
belongs_to :creator, class_name: "User", default: -> { Current.user }
belongs_to :account, default: -> { board.account }
belongs_to :board
```

### Touch for Cache Invalidation

```ruby
belongs_to :card, touch: true
belongs_to :user, touch: true
```

### Dependent Strategies

```ruby
has_many :comments, dependent: :destroy      # Delete with callbacks
has_many :assignments, dependent: :delete_all # Bulk delete, no callbacks
has_one :closure, dependent: :destroy
```

### Through Associations with Scopes

```ruby
has_many :tags, -> { distinct }, through: :cards
has_many :watchers, -> { active.merge(Watch.watching) }, through: :watches, source: :user
```

## Validations and Normalizations

```ruby
# Presence and format
validates :name, presence: true
validates :title, format: { without: /\A#/ }

# Normalization (prefer over validation for data cleaning)
normalizes :email_address, with: ->(value) { value.strip.downcase.presence }
normalizes :subscribed_actions, with: ->(value) {
  Array.wrap(value).map(&:to_s).uniq & PERMITTED_ACTIONS
}
```

## Callbacks (Used Sparingly)

Callbacks are used but not overused - prefer explicit method calls over implicit callbacks.

### What to Avoid

- No complex callback chains
- No `before_validation` for business logic
- No callbacks that call external services synchronously
- Prefer explicit method calls over implicit callbacks

### Organize in Concerns

```ruby
module Card::Statuses
  extend ActiveSupport::Concern

  included do
    enum :status, %w[drafted published].index_by(&:itself)

    before_save :update_created_at_on_publication
    before_save :remember_initial_status
    after_create -> { track_event :published }, if: :published?
  end
end
```

### Use after_create_commit for Async Work

```ruby
after_create_commit :notify_recipients_later
after_create_commit :dispatch_webhooks
after_commit :relay_later, on: :create
after_save_commit -> { cards.touch_all }, if: :saved_change_to_name?
```

### Before Save for Derived Data

```ruby
before_save :set_defaults
before_save :calculate_position
```

### Inline Lambdas for Simple Callbacks

```ruby
after_save   -> { board.touch }, if: :published?
after_touch  -> { board.touch }, if: :published?
```

## Scopes

### Naming Conventions

**Ordering scopes** - use adverbs:

```ruby
scope :chronologically,         -> { order created_at: :asc }
scope :reverse_chronologically, -> { order created_at: :desc }
scope :alphabetically,          -> { order name: :asc }
scope :latest,                  -> { order last_active_at: :desc }
```

**Preloading scopes** - use `preloaded` as standard name:

```ruby
scope :with_users, -> {
  preload(creator: [:avatar_attachment, :account],
          assignees: [:avatar_attachment, :account])
}

scope :preloaded, -> {
  with_users
    .preload(:column, :tags, :steps, :closure,
             board: [:entropy, :columns])
    .with_rich_text_description_and_embeds
}
```

### Simple Scopes

```ruby
scope :alphabetically, -> { order("lower(title)") }
scope :chronologically, -> { order(created_at: :asc, id: :asc) }
scope :reverse_chronologically, -> { order(created_at: :desc, id: :desc) }
```

### Parameterized Scopes with Case Statements

```ruby
scope :indexed_by, ->(index) do
  case index
  when "stalled" then stalled
  when "closed" then closed
  when "not_now" then postponed.latest
  when "golden" then golden
  else all
  end
end

scope :sorted_by, ->(sort) do
  case sort
  when "newest" then reverse_chronologically
  when "oldest" then chronologically
  else latest
  end
end
```

### Preload Scopes for N+1 Prevention

```ruby
scope :preloaded, -> {
  preload(:column, :tags, :steps, :closure,
          creator: [:avatar_attachment, :account],
          assignees: [:avatar_attachment, :account],
          board: [:entropy, :columns])
    .with_rich_text_description_and_embeds
}

scope :with_users, -> {
  preload(creator: [:avatar_attachment, :account],
          assignees: [:avatar_attachment, :account])
}
```

## Enums

```ruby
enum :role, %i[owner admin member system].index_by(&:itself), scopes: false
enum :status, %w[drafted published].index_by(&:itself)
enum :involvement, %i[access_only watching].index_by(&:itself), default: :access_only
```

## State via Relationships (Instead of Soft Deletes)

```ruby
module Card::Closeable
  extend ActiveSupport::Concern

  included do
    has_one :closure, dependent: :destroy

    scope :closed, -> { joins(:closure) }
    scope :open, -> { where.missing(:closure) }
  end

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

  def closed?
    closure.present?
  end
end
```

## Event Tracking Pattern

```ruby
module Eventable
  extend ActiveSupport::Concern

  included do
    has_many :events, as: :eventable, dependent: :destroy
  end

  def track_event(action, creator: Current.user, board: self.board, **particulars)
    board.events.create!(
      action: "#{eventable_prefix}_#{action}",
      creator: creator,
      eventable: self,
      particulars: particulars
    )
  end

  private
    def eventable_prefix
      self.class.name.underscore
    end
end
```

## Service Objects with Factory Pattern

```ruby
class Notifier
  attr_reader :source

  class << self
    def for(source)
      case source
      when Event
        "Notifier::#{source.eventable.class}EventNotifier".safe_constantize&.new(source)
      when Mention
        MentionNotifier.new(source)
      end
    end
  end

  def initialize(source)
    @source = source
  end

  def notify
    return unless should_notify?

    recipients.map do |recipient|
      Notification.create!(user: recipient, source: source, creator: creator)
    end
  end
end
```

## Form Objects

```ruby
class Signup
  include ActiveModel::Model
  include ActiveModel::Attributes
  include ActiveModel::Validations

  attribute :full_name, :string
  attribute :email_address, :string

  with_options on: :completion do
    validates :full_name, presence: true
    validates :email_address, presence: true
  end

  def complete
    return false unless valid?(:completion)

    transaction do
      @account = Account.create_with_owner(
        account: { name: generate_account_name },
        owner: { name: full_name, identity: identity }
      )
      @user = @account.users.find_by!(role: :owner)
      true
    end
  rescue => error
    errors.add(:base, error.message)
    false
  end
end
```

## Delegation

```ruby
# In Card model
delegate :accessible_to?, to: :board

# In Comment model
delegate :board, :watch_by, to: :card

# In User::Filtering presenter
delegate :as_params, :single_board, to: :filter
```

## Transaction Patterns

```ruby
def handle_board_change
  old_board = account.boards.find_by(id: board_id_before_last_save)

  transaction do
    update!(column: nil)
    track_board_change_event(old_board.name)
    grant_access_to_assignees unless board.all_access?
  end

  remove_inaccessible_notifications_later
end
```

## Idempotent Operations

```ruby
def assign(user)
  assignments.create!(assignee: user, assigner: Current.user)
  track_event :assigned
rescue ActiveRecord::RecordNotUnique
  # Already assigned - idempotent operation
end
```
