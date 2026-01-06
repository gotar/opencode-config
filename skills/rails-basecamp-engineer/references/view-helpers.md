# View Helper Patterns

Helpers wrap Stimulus controllers for reusable UI patterns.

## Icon Helper

```ruby
# app/helpers/application_helper.rb
def icon_tag(name, **options)
  tag.span class: class_names("icon icon--#{name}", options.delete(:class)),
           "aria-hidden": true, **options
end
```

Usage:
```erb
<%= icon_tag("arrow-left") %>
<%= icon_tag("check", class: "icon--success") %>
```

## Clipboard Helper

```ruby
# app/helpers/clipboard_helper.rb
def button_to_copy_to_clipboard(url, &)
  tag.button class: "btn", data: {
    controller: "copy-to-clipboard tooltip",
    action: "copy-to-clipboard#copy",
    copy_to_clipboard_success_class: "btn--success",
    copy_to_clipboard_content_value: url
  }, &
end
```

Usage:
```erb
<%= button_to_copy_to_clipboard(share_url) do %>
  <%= icon_tag("link") %> Copy Link
<% end %>
```

## Auto-Submit Form Helper

```ruby
# app/helpers/forms_helper.rb
def auto_submit_form_with(**attributes, &)
  data = attributes.delete(:data) || {}
  data[:controller] = "auto-submit #{data[:controller]}".strip

  form_with **attributes, data: data, &
end
```

Usage:
```erb
<%= auto_submit_form_with model: @filter do |f| %>
  <%= f.select :sort_by, options, data: { action: "auto-submit#submit" } %>
<% end %>
```

## Avatar Helper

Deterministic colors based on user ID:

```ruby
# app/helpers/avatars_helper.rb
AVATAR_COLORS = %w[
  #AF2E1B #CC6324 #3B4B59 #2E5B8C #7A4B8C
  #8C4B5E #4B7A5E #5E4B7A #7A5E4B #4B5E7A
].freeze

def avatar_background_color(user)
  # Same user always gets same color via CRC32 hash
  AVATAR_COLORS[Zlib.crc32(user.to_param) % AVATAR_COLORS.size]
end

def avatar_tag(user, hidden_for_screen_reader: false, **options)
  link_to user_path(user),
    class: class_names("avatar btn btn--circle", options.delete(:class)),
    data: { turbo_frame: "_top" },
    aria: { hidden: hidden_for_screen_reader, label: user.name } do
    avatar_image_tag(user)
  end
end

def avatar_image_tag(user, size: :thumb)
  if user.avatar.attached?
    image_tag user.avatar.variant(size), alt: user.name, class: "avatar__image"
  else
    tag.span user.initials, class: "avatar__initials",
             style: "background-color: #{avatar_background_color(user)}"
  end
end
```

## Back Link Helper

```ruby
# app/helpers/navigation_helper.rb
def back_link_to(label, url, hotkey_action, **options)
  link_to url, class: "btn btn--back",
    data: { controller: "hotkey", action: hotkey_action }, **options do
    icon_tag("arrow-left") +
    tag.strong("Back to #{label}", class: "overflow-ellipsis") +
    tag.kbd("ESC", class: "txt-x-small hide-on-touch")
  end
end
```

Usage:
```erb
<%= back_link_to "Board", @board, "keydown.escape@window->hotkey#click" %>
```

## Dialog Helper

```ruby
# app/helpers/dialog_helper.rb
def dialog_tag(id:, modal: true, **options, &)
  data = options.delete(:data) || {}
  data[:controller] = "dialog #{data[:controller]}".strip
  data[:dialog_modal_value] = modal
  data[:dialog_target] = "dialog"

  tag.dialog id: id, **options, data: data, &
end

def dialog_trigger_tag(dialog_id, **options, &)
  data = options.delete(:data) || {}
  data[:action] = "dialog#open #{data[:action]}".strip

  tag.button **options, data: data, &
end
```

## Time Helper

```ruby
# app/helpers/time_helper.rb
def local_time_tag(datetime, format: "time-or-date", **options)
  tag.time datetime.iso8601,
    data: {
      controller: "local-time",
      local_time_datetime_value: datetime.iso8601,
      local_time_format_value: format
    },
    **options do
    datetime.strftime("%b %d, %Y")  # Fallback for no-JS
  end
end
```

Usage:
```erb
<%= local_time_tag(card.created_at) %>
<%= local_time_tag(event.created_at, format: "time") %>
```

## Card Article Helper

```ruby
# app/helpers/cards_helper.rb
def card_article_tag(card, **options, &block)
  classes = [
    options.delete(:class),
    ("golden-effect" if card.golden?),
    ("card--postponed" if card.postponed?),
    ("card--closed" if card.closed?)
  ].compact.join(" ")

  tag.article id: dom_id(card), class: classes, **options, &block
end
```

## Turbo Stream Flash Helper

```ruby
# app/helpers/turbo_helper.rb
def turbo_stream_flash(**flash_options)
  turbo_stream.replace(:flash, partial: "layouts/shared/flash", locals: { flash: flash_options })
end
```

Usage in controller:
```ruby
render turbo_stream: [
  turbo_stream.append(:comments, @comment),
  turbo_stream_flash(notice: "Comment added!")
]
```

## Conditional Class Helper

```ruby
# Built into Rails, but commonly used
class_names("btn", "btn--primary" => primary?, "btn--disabled" => disabled?)
```

## Summary

| Helper | Purpose |
|--------|---------|
| `icon_tag` | SVG icon with consistent classes |
| `button_to_copy_to_clipboard` | Clipboard API integration |
| `auto_submit_form_with` | Forms that submit on change |
| `avatar_tag` / `avatar_background_color` | Deterministic avatar colors |
| `back_link_to` | Back navigation with hotkey |
| `dialog_tag` | Native dialog with Stimulus |
| `local_time_tag` | Client-side time formatting |
| `card_article_tag` | Card element with state classes |
| `turbo_stream_flash` | Flash messages via Turbo |
