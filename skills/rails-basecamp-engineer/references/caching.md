# Caching Patterns

> **Related:** For `touch: true` association patterns, see `models.md`. For Solid Cache configuration, see `configuration.md`.

## HTTP Caching with ETags

### Global ETags in ApplicationController

```ruby
class ApplicationController < ActionController::Base
  etag { "v1" }  # Bump to bust all caches on deploy
  etag { Current.session.id if authenticated? }
end
```

### Concern-Level ETags

```ruby
module CurrentTimezone
  included do
    etag { timezone_from_cookie }
  end
end
```

**Why timezone affects caching:** Pages display times like "Created 2 hours ago". These are rendered server-side in the user's timezone. Different timezones need different cached responses.

### `fresh_when` for Conditional GET

Controllers declare cache dependencies:

```ruby
class Cards::AssignmentsController < ApplicationController
  def new
    @assigned_to = @card.assignees.active.alphabetically
    @users = @board.users.active.alphabetically.where.not(id: @card.assignees)
    fresh_when etag: [@users, @card.assignees]  # Returns 304 if unchanged
  end
end

class Cards::WatchesController < ApplicationController
  def show
    fresh_when etag: @card.watch_for(Current.user) || "none"
  end
end

class Boards::ColumnsController < ApplicationController
  def show
    set_page_and_extract_portion_from @column.cards.active.latest
    fresh_when etag: @page.records
  end
end
```

### Complex ETags

```ruby
fresh_when etag: [@board, @page.records, @user_filtering]
fresh_when etag: [@filters, @boards, @tags, @users]
```

## Fragment Caching

### Basic Fragment Cache

```erb
<%# app/views/cards/_container.html.erb %>
<% cache card do %>
  <%= render "cards/card", card: card %>
<% end %>
```

### Collection Caching

```erb
<%# Automatic cache key per item, cached: true enables collection caching %>
<%= render partial: "cards/comments/comment",
           collection: card.comments.preloaded.chronologically,
           cached: true %>
```

### Turbo Cache Exemptions

```erb
<%# Pages that shouldn't be restored from Turbo's page cache %>
<% turbo_exempts_page_from_cache %>
```

## Cache Invalidation via `touch: true`

Instead of granular cache keys, use `touch: true` extensively:

```ruby
# When a comment is created, card.updated_at changes → card cache invalidates
belongs_to :card, touch: true    # Comment, Step, Closure, Assignment, Watch
belongs_to :board, touch: true   # Column, Access
belongs_to :comment, touch: true # Reaction
```

This is intentionally simple:
- **Accept the cache churn** - cards change often anyway
- **No Russian doll complexity** - whole card cached, not nested fragments
- **Predictable invalidation** - any child change busts parent cache

## Model Cache Keys

Models automatically generate cache keys via `cache_key_with_version`:

```ruby
cache card  # => "cards/abc123-20241214120000"
```

## Avatar Caching Pattern

Avatars use a redirect pattern for HTTP caching:

```ruby
# app/controllers/users/avatars_controller.rb
def show
  if @user.avatar.attached?
    # Redirect to blob URL (which has its own caching)
    redirect_to rails_blob_url(@user.avatar_thumbnail, disposition: "inline")
  elsif stale? @user, cache_control: cache_control
    # Render SVG initials, cached via ETags
    render_initials
  end
end

def cache_control
  if @user == Current.user
    {}  # No caching for your own avatar (might change it)
  else
    { max_age: 30.minutes, stale_while_revalidate: 1.week }
  end
end
```

Avatar variants are pre-processed on upload:

```ruby
# app/models/user/avatar.rb
has_one_attached :avatar do |attachable|
  attachable.variant :thumb, resize_to_fill: [256, 256], process: :immediately
end
```

## Dynamic SVG with ERB

Initials are rendered as SVG - cacheable and dynamic:

```erb
<%# app/views/users/avatars/show.svg.erb %>
<svg viewBox="0 0 512 512" class="avatar" aria-hidden="true">
  <rect width="100%" height="100%" rx="50"
        fill="<%= avatar_background_color(@user) %>" />
  <text x="50%" y="50%" fill="#FFFFFF" text-anchor="middle" dy="0.35em"
        font-size="230" font-weight="800">
    <%= @user.initials %>
  </text>
</svg>
```

Benefits:
- **Cacheable** - HTTP caching works (ETags from user record)
- **Dynamic** - Color computed from user ID via CRC32
- **No image processing** - pure vector graphics

## Public Cache Expiration

```ruby
class Public::BaseController < ApplicationController
  before_action :set_public_cache_expiration

  private
    def set_public_cache_expiration
      expires_in 30.seconds, public: true
    end
end
```

## Solid Cache Configuration

Database-backed caching (no Redis):

```yaml
# config/solid_cache.yml
default: &default
  database: cache
  store_options:
    max_age: <%= 1.week.to_i %>
    max_size: <%= 256.megabytes %>
    namespace: <%= Rails.env %>
```

## Summary

| Layer | Technique |
|-------|-----------|
| HTTP | ETags via `fresh_when`, global etags in ApplicationController |
| Fragment | `cache` helper with model cache keys |
| Collection | `cached: true` on render partial collection |
| Invalidation | `touch: true` on associations |
| Public | `expires_in` with `public: true` |
| Store | Solid Cache (database-backed) |
