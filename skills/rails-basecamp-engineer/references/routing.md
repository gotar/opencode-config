# Routing Patterns

## Core Principle: Everything is CRUD

Every action maps to a CRUD verb. When something doesn't fit, **create a new resource**.

```ruby
# BAD: Custom actions on existing resource
resources :cards do
  post :close
  post :reopen
  post :archive
  post :gild
end

# GOOD: New resources for each state change
resources :cards do
  resource :closure      # POST to close, DELETE to reopen
  resource :goldness     # POST to gild, DELETE to ungild
  resource :not_now      # POST to postpone
  resource :pin          # POST to pin, DELETE to unpin
  resource :watch        # POST to watch, DELETE to unwatch
end
```

## Using `scope module` for Namespacing

Group related nested resources under the parent's module:

```ruby
# config/routes.rb

resources :cards do
  scope module: :cards do
    resource :board           # Moving card to different board
    resource :closure         # Closing/reopening
    resource :column          # Assigning to workflow column
    resource :goldness        # Highlighting as important
    resource :image           # Managing header image
    resource :not_now         # Postponing
    resource :pin             # Pinning to sidebar
    resource :publish         # Publishing draft
    resource :reading         # Marking as read
    resource :triage          # Triaging
    resource :watch           # Subscribing to updates

    resources :assignments    # Managing assignees
    resources :steps          # Checklist items
    resources :taggings       # Tags
    resources :comments do
      resources :reactions    # Emoji reactions
    end
  end
end
```

This creates controllers like:
- `Cards::ClosuresController`
- `Cards::AssignmentsController`
- `Cards::Comments::ReactionsController`

## Namespace for Context

Use `namespace` within `scope module` for logical groupings:

```ruby
# Board-specific resources
resources :boards do
  scope module: :boards do
    resource :publication    # Publishing publicly
    resource :entropy        # Auto-postpone settings
    resource :involvement    # User's involvement level

    namespace :columns do
      resource :not_now      # "Not Now" pseudo-column
      resource :stream       # Main stream view
      resource :closed       # Closed cards view
    end
  end
end
```

## Using `resolve` for Custom URL Generation

Make `polymorphic_url` work correctly for nested resources:

```ruby
# config/routes.rb

# Comment URLs should point to the card with an anchor
resolve "Comment" do |comment, options|
  options[:anchor] = ActionView::RecordIdentifier.dom_id(comment)
  route_for :card, comment.card, options
end

# Notification URLs should point to the notifiable target
resolve "Notification" do |notification, options|
  polymorphic_url(notification.notifiable_target, options)
end
```

Now you can use:
```ruby
url_for(@comment)  # => /12345/cards/42#comment_123
url_for(@notification)  # => wherever the notification points
```

## State Machine Controllers

Instead of adding actions to existing controllers, create dedicated controllers for state transitions:

```ruby
# config/routes.rb
resources :cards do
  scope module: :cards do
    resource :closure  # POST creates, DELETE destroys
  end
end
```

```ruby
# app/controllers/cards/closures_controller.rb
class Cards::ClosuresController < ApplicationController
  include CardScoped

  def create
    @card.close(user: Current.user)
    render_card_replacement
  end

  def destroy
    @card.reopen(user: Current.user)
    render_card_replacement
  end
end
```

## Singular vs Plural Resources

- Use `resource` (singular) when there's only one per parent
- Use `resources` (plural) when there can be many

```ruby
resources :cards do
  scope module: :cards do
    resource :closure        # One closure per card (singular)
    resources :comments      # Many comments per card (plural)
  end
end
```

## Public Routes (Outside Authentication)

```ruby
# Routes that work without authentication
scope module: :public do
  resources :boards, only: :show, param: :published_key
end

# Routes that work outside account context
resource :session, only: %i[new create destroy] do
  resource :magic_link, only: %i[show create], module: :sessions
end
```

## API Routes

Same controllers, different format:

```ruby
# No separate API namespace - just respond_to in controllers
def create
  @card.close

  respond_to do |format|
    format.turbo_stream { render_card_replacement }
    format.json { head :no_content }
  end
end
```

## Route Constraints

```ruby
# Constrain by format
resources :cards, constraints: { format: :html }

# Constrain by subdomain (for database-per-tenant)
constraints subdomain: /[a-z0-9-]+/ do
  resources :boards
end
```

## Testing Routes

```ruby
# test/routes_test.rb
class RoutesTest < ActionDispatch::IntegrationTest
  test "card closure routes" do
    assert_routing(
      { method: :post, path: "/12345/cards/42/closure" },
      { controller: "cards/closures", action: "create", card_id: "42" }
    )
  end
end
```

## Summary

| Instead of... | Do this... |
|---------------|------------|
| `post :close` on cards | `resource :closure` nested under cards |
| `post :assign` on cards | `resources :assignments` nested under cards |
| Custom action verbs | New singular/plural resources |
| Complex nested routes | `scope module:` for organization |
| Manual URL building | `resolve` for polymorphic URLs |
