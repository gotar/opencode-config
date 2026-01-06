# Authorization Patterns

## Role System

Define account-level roles with implicit permissions:

```ruby
module User::Role
  extend ActiveSupport::Concern

  included do
    enum :role, %i[owner admin member system].index_by(&:itself), scopes: false

    scope :owner, -> { where(active: true, role: :owner) }
    scope :admin, -> { where(active: true, role: %i[owner admin]) }
    scope :member, -> { where(active: true, role: :member) }
    scope :active, -> { where(active: true, role: %i[owner admin member]) }
  end

  # Owner implicitly has admin permissions
  def admin?
    super || owner?
  end

  # Permission helpers
  def can_change?(other)
    (admin? && !other.owner?) || other == self
  end

  def can_administer?(other)
    admin? && !other.owner? && other != self
  end

  def can_administer_board?(board)
    admin? || board.creator == self
  end
end
```

## Board-Level Access Control

Use explicit Access records for fine-grained permissions:

### Access Model

```ruby
class Access < ApplicationRecord
  belongs_to :account, default: -> { user.account }
  belongs_to :board, touch: true
  belongs_to :user, touch: true

  enum :involvement, %i[access_only watching].index_by(&:itself), default: :access_only

  scope :ordered_by_recently_accessed, -> { order(accessed_at: :desc) }

  def accessed
    touch(:accessed_at)
  end
end
```

### Board Accessible Concern

```ruby
module Board::Accessible
  extend ActiveSupport::Concern

  included do
    has_many :accesses, dependent: :delete_all do
      def revise(granted: [], revoked: [])
        transaction do
          grant_to granted
          revoke_from revoked
        end
      end

      def grant_to(users)
        Access.insert_all Array(users).collect { |user|
          {
            id: ActiveRecord::Type::Uuid.generate,
            board_id: proxy_association.owner.id,
            user_id: user.id,
            account_id: proxy_association.owner.account.id
          }
        }
      end

      def revoke_from(users)
        destroy_by user: users unless proxy_association.owner.all_access?
      end
    end

    has_many :users, through: :accesses
    has_many :access_only_users, -> { merge(Access.access_only) }, through: :accesses, source: :user

    scope :all_access, -> { where(all_access: true) }

    after_create :grant_access_to_creator
    after_save_commit :grant_access_to_everyone
  end

  def accessed_by(user)
    access_for(user).accessed
  end

  def access_for(user)
    accesses.find_by(user: user)
  end

  def accessible_to?(user)
    access_for(user).present?
  end

  def watchers
    users.active.where(accesses: { involvement: :watching })
  end

  private
    def grant_access_to_creator
      accesses.create(user: creator, involvement: :watching)
    end

    def grant_access_to_everyone
      accesses.grant_to(account.users.active) if all_access_previously_changed?(to: true)
    end
end
```

### User Accessor Concern

Define which boards users can access:

```ruby
module User::Accessor
  extend ActiveSupport::Concern

  included do
    has_many :accesses, dependent: :destroy
    has_many :boards, through: :accesses
    has_many :accessible_cards, through: :boards, source: :cards

    after_create_commit :grant_access_to_all_access_boards, unless: :system?
  end

  private
    def grant_access_to_all_access_boards
      all_access_board_ids = account.boards.all_access.pluck(:id)

      Access.insert_all(
        all_access_board_ids.map { |board_id|
          {
            id: ActiveRecord::Type::Uuid.generate,
            board_id: board_id,
            user_id: id,
            account_id: account.id
          }
        }
      ) if all_access_board_ids.any?
    end
end
```

## Controller Authorization

### Authorization Concern

```ruby
module Authorization
  extend ActiveSupport::Concern

  included do
    before_action :ensure_can_access_account,
                  if: -> { Current.account.present? && authenticated? }
  end

  class_methods do
    def allow_unauthorized_access(**options)
      skip_before_action :ensure_can_access_account, **options
    end
  end

  private
    def ensure_admin
      head :forbidden unless Current.user.admin?
    end

    def ensure_staff
      head :forbidden unless Current.identity.staff?
    end

    def ensure_can_access_account
      redirect_to session_menu_url(script_name: nil) if Current.user.blank? || !Current.user.active?
    end
end
```

### Board Scoping Concern

```ruby
module BoardScoped
  extend ActiveSupport::Concern

  included do
    before_action :set_board
  end

  private
    def set_board
      @board = Current.user.boards.find(params[:board_id])
    end

    def ensure_permission_to_admin_board
      head :forbidden unless Current.user.can_administer_board?(@board)
    end
end
```

### Permission Checks in Controllers

```ruby
class BoardsController < ApplicationController
  before_action :set_board, except: %i[new create]
  before_action :ensure_permission_to_admin_board, only: %i[update destroy]

  private
    def set_board
      @board = Current.user.boards.find(params[:id])
    end

    def ensure_permission_to_admin_board
      head :forbidden unless Current.user.can_administer_board?(@board)
    end
end

class Cards::CommentsController < ApplicationController
  include CardScoped

  before_action :set_comment, only: %i[edit update destroy]
  before_action :ensure_creatorship, only: %i[edit update destroy]

  private
    def ensure_creatorship
      head :forbidden if Current.user != @comment.creator
    end
end
```

### Admin-Only Controllers

```ruby
class Account::SettingsController < ApplicationController
  before_action :ensure_admin
end

class WebhooksController < ApplicationController
  before_action :ensure_admin
end

class AdminController < ApplicationController
  disallow_account_scope
  before_action :ensure_staff
end
```

## Query-Based Authorization

Authorization built into queries for automatic scoping:

```ruby
# Controllers use scoped queries
@board = Current.user.boards.find(params[:id])
@card = Current.user.accessible_cards.find(params[:id])
@comments = Current.user.accessible_comments.where(card: @card)

# Never use unscoped queries for user data
# BAD: Board.find(params[:id])
# GOOD: Current.user.boards.find(params[:id])
```

## View Authorization

Conditionally render UI based on permissions:

```erb
<%# Show admin controls only to authorized users %>
<% if Current.user.can_administer_board?(@board) %>
  <%= render "boards/edit/delete", board: @board %>
<% end %>

<%# Disable form inputs for non-admins %>
<%= form.check_box :all_access,
      disabled: !Current.user.can_administer_board?(@board) %>

<%# Show edit button only for creator or admin %>
<% if Current.user.can_administer_board?(card.board) %>
  <%= link_to "Edit", edit_card_path(card) %>
<% end %>

<%# Disable buttons when lacking permission %>
<%= button_to user, method: :delete,
      disabled: !Current.user.can_administer?(user) %>
```

## Access Cleanup on Revocation

When access is revoked, clean up related data:

```ruby
module Board::Accessible
  def clean_inaccessible_data_for(user)
    return if accessible_to?(user)

    mentions_for_user(user).destroy_all
    notifications_for_user(user).destroy_all
    watches_for(user).destroy_all
  end

  private
    def watches_for(user)
      Watch.where(card: cards, user: user)
    end
end
```

Call cleanup after access changes:

```ruby
class Boards::AccessesController < ApplicationController
  def update
    @board.accesses.revise(granted: granted_users, revoked: revoked_users)

    revoked_users.each do |user|
      CleanInaccessibleDataJob.perform_later(@board, user)
    end

    redirect_to edit_board_path(@board)
  end
end

class CleanInaccessibleDataJob < ApplicationJob
  def perform(board, user)
    Current.with_account(board.account) do
      board.clean_inaccessible_data_for(user)
    end
  end
end
```

## Authorization Summary

| Level | Check | Usage |
|-------|-------|-------|
| Account | `Current.user.admin?` | Account-wide admin operations |
| Account | `Current.identity.staff?` | Platform-level staff access |
| Board | `board.accessible_to?(user)` | Board visibility |
| Board | `user.can_administer_board?(board)` | Board settings/deletion |
| Card | `user.accessible_cards` | Card visibility via board access |
| Record | `user.can_administer?(other)` | User management |
| Creator | `record.creator == Current.user` | Creator-only actions |

## Testing Authorization

```ruby
test "users can only see cards in boards they have access to" do
  sign_in_as(:kevin)

  get card_path(cards(:logo))
  assert_response :success

  # Revoke access
  boards(:writebook).update!(all_access: false)
  boards(:writebook).accesses.revoke_from(users(:kevin))

  get card_path(cards(:logo))
  assert_response :not_found
end

test "only admins can update board settings" do
  sign_in_as(:member)  # Non-admin user

  patch board_path(boards(:writebook)), params: { board: { name: "Hacked" } }
  assert_response :forbidden
end

test "creators can administer their own boards" do
  sign_in_as(:member)
  board = boards(:created_by_member)

  patch board_path(board), params: { board: { name: "Updated" } }
  assert_response :success
end
```
