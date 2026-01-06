# Hotwire Patterns (Turbo + Stimulus)

> **Stimulus Controller Catalog:** See `stimulus/index.md` for a decision table to find the right controller, or browse by category:
> - `stimulus/utility-controllers.md` - copy-to-clipboard, hotkey, toggle-class, beacon
> - `stimulus/form-controllers.md` - auto-submit, autoresize, local-save, character-counter
> - `stimulus/ui-controllers.md` - dialog, lightbox, navigable-list, local-time
> - `stimulus/interaction-controllers.md` - drag-and-drop, sortable, resize

## Turbo Frames

### Basic Frame Usage

```erb
<%# Wrap content in a named frame %>
<%= turbo_frame_tag @card, :edit do %>
  <%= form_with model: @card do |form| %>
    <%= form.text_field :title %>
    <%= form.submit %>
  <% end %>
<% end %>

<%# Frame with lazy loading %>
<%= turbo_frame_tag @board, :cards, src: board_cards_path(@board), loading: :lazy do %>
  <div class="loading-placeholder">Loading...</div>
<% end %>
```

### Frame Naming Conventions

```erb
<%# Object + descriptor %>
<%= turbo_frame_tag @card, :card_container %>
<%= turbo_frame_tag @card, :edit %>
<%= turbo_frame_tag @board, :columns %>

<%# DOM ID helper %>
<%= turbo_frame_tag dom_id(@card, :comments) %>
```

### Targeting Different Frames

```erb
<%# Link targets a specific frame %>
<%= link_to "Edit", edit_card_path(@card), data: { turbo_frame: dom_id(@card, :edit) } %>

<%# Link breaks out of frame to full page %>
<%= link_to "View Full", card_path(@card), data: { turbo_frame: "_top" } %>
```

## Turbo Streams

### Stream Actions

```erb
<%# Replace element %>
<%= turbo_stream.replace [@card, :card_container] do %>
  <%= render "cards/container", card: @card %>
<% end %>

<%# Append to container %>
<%= turbo_stream.append :comments do %>
  <%= render "comments/comment", comment: @comment %>
<% end %>

<%# Prepend to container %>
<%= turbo_stream.prepend :notifications do %>
  <%= render "notifications/notification", notification: @notification %>
<% end %>

<%# Insert before element %>
<%= turbo_stream.before [@card, :new_comment] do %>
  <%= render "comments/comment", comment: @comment %>
<% end %>

<%# Update content %>
<%= turbo_stream.update [@card, :new_comment] do %>
  <%= render "comments/new", card: @card %>
<% end %>

<%# Remove element %>
<%= turbo_stream.remove @comment %>
```

### Morphing for UX Preservation

Use `method: :morph` to preserve form state and focus:

```ruby
def render_card_replacement
  render turbo_stream: turbo_stream.replace(
    [@card, :card_container],
    partial: "cards/container",
    method: :morph,
    locals: { card: @card.reload }
  )
end
```

### Multiple Stream Responses

```ruby
def create
  @comment = @card.comments.create!(comment_params)

  render turbo_stream: [
    turbo_stream.before([@card, :new_comment], partial: "comments/comment", locals: { comment: @comment }),
    turbo_stream.update([@card, :new_comment], partial: "comments/new", locals: { card: @card }),
    turbo_stream_flash(notice: "Comment added")
  ]
end
```

### Broadcasting

```ruby
# Model broadcasting
module Card::Broadcastable
  extend ActiveSupport::Concern

  included do
    broadcasts_refreshes
    broadcasts_refreshes_to ->(card) { [card.account, :all_cards] }
  end
end

# Manual broadcast in controller
def create
  @pin = @card.pin_by(Current.user)
  @pin.broadcast_prepend_to([Current.user, :pins_tray], target: "pins", partial: "pins/pin")
end
```

### Stream Subscriptions in Views

```erb
<%# Subscribe to model updates %>
<%= turbo_stream_from @card %>
<%= turbo_stream_from @card, :activity %>

<%# Subscribe to multiple boards %>
<% @boards.each do |board| %>
  <%= turbo_stream_from board %>
<% end %>

<%# Account-wide subscription %>
<%= turbo_stream_from [Current.account, :all_boards] %>
```

## Stimulus Controllers

### Controller Structure

```javascript
// app/javascript/controllers/form_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["submit", "cancel", "input"]
  static values = {
    debounceTimeout: { type: Number, default: 300 }
  }

  submit() {
    this.element.requestSubmit()
  }

  cancel() {
    this.cancelTarget?.click()
  }

  disableSubmitWhenInvalid() {
    if (this.element.checkValidity()) {
      this.submitTarget.removeAttribute("disabled")
    } else {
      this.submitTarget.toggleAttribute("disabled", true)
    }
  }
}
```

### Common Patterns

**Dialog Controller:**
```javascript
export default class extends Controller {
  static targets = ["dialog"]
  static values = { modal: { type: Boolean, default: false } }

  open() {
    if (this.modalValue) {
      this.dialogTarget.showModal()
    } else {
      this.dialogTarget.show()
    }
    this.loadLazyFrames()
  }

  close() {
    this.dialogTarget.close()
  }

  closeOnClickOutside({ target }) {
    if (!this.element.contains(target)) this.close()
  }

  loadLazyFrames() {
    this.dialogTarget.querySelectorAll("turbo-frame").forEach(frame => {
      frame.loading = "eager"
    })
  }
}
```

**Auto-Save Controller:**
```javascript
const AUTOSAVE_INTERVAL = 3000

export default class extends Controller {
  change(event) {
    if (event.target.form === this.element) {
      this.#scheduleSave()
    }
  }

  #scheduleSave() {
    clearTimeout(this.#timer)
    this.#timer = setTimeout(() => this.#save(), AUTOSAVE_INTERVAL)
  }

  async #save() {
    const request = new FetchRequest(this.element.method, this.element.action, {
      body: new FormData(this.element)
    })
    await request.perform()
  }
}
```

**Toggle Class Controller:**
```javascript
export default class extends Controller {
  static classes = ["active"]

  toggle() {
    this.element.classList.toggle(this.activeClass)
  }
}
```

### Data Attributes

```erb
<%# Controller and actions %>
<div data-controller="form dialog"
     data-action="turbo:submit-end->form#reset">

  <%# Targets %>
  <input data-form-target="input">
  <button data-form-target="submit">Save</button>

  <%# Values %>
  <div data-controller="local-save"
       data-local-save-key-value="card-<%= card.id %>">

  <%# Multiple actions %>
  <textarea data-action="input->autoresize#resize
                         keydown.enter->form#submit:prevent
                         keydown.esc->form#cancel">
</div>
```

### Keyboard Shortcuts

```erb
<%# Modifier keys %>
data-action="keydown.ctrl+enter->form#submit:prevent
             keydown.meta+enter->form#submit:prevent
             keydown.esc->form#cancel:stop"
```

## Form Patterns

### Form with Multiple Controllers

```erb
<%= form_with model: @card,
      data: {
        controller: "form auto-save local-save",
        local_save_key_value: "card-#{@card.id}",
        action: "turbo:submit-end->local-save#submit"
      } do |form| %>

  <%= form.text_area :title,
        data: {
          autoresize_target: "textarea",
          action: "input->autoresize#resize keydown.enter->form#submit:prevent"
        } %>

  <%= form.rich_textarea :description,
        data: {
          local_save_target: "input",
          action: "lexxy:change->local-save#save"
        } %>
<% end %>
```

### Turbo Form Submission

```erb
<%# Form submits via Turbo by default %>
<%= form_with model: @comment, url: card_comments_path(@card) do |form| %>
  <%= form.text_area :body %>
  <%= form.submit "Post" %>
<% end %>

<%# Disable Turbo for specific form %>
<%= form_with model: @export, data: { turbo: false } do |form| %>
  <%# Full page reload on submit %>
<% end %>
```

## Flash Messages

```erb
<%# app/views/layouts/shared/_flash.html.erb %>
<%= turbo_frame_tag :flash do %>
  <% if notice = flash[:notice] || flash[:alert] %>
    <div class="flash"
         data-controller="element-removal"
         data-action="animationend->element-removal#remove">
      <%= notice %>
    </div>
  <% end %>
<% end %>
```

```ruby
# Controller helper
def turbo_stream_flash(**flash_options)
  turbo_stream.replace(:flash, partial: "layouts/shared/flash", locals: { flash: flash_options })
end
```

## Pagination with Intersection Observer

```javascript
export default class extends Controller {
  static targets = ["paginationLink"]
  static values = { paginateOnIntersection: { type: Boolean, default: false } }

  connect() {
    if (this.paginateOnIntersectionValue) {
      this.observer = new IntersectionObserver(this.#intersect, {
        rootMargin: "300px",
        threshold: 1
      })
      this.observer.observe(this.paginationLinkTarget)
    }
  }

  #intersect = ([entry]) => {
    if (entry?.isIntersecting) {
      this.#loadPaginationLink(entry.target)
    }
  }

  #loadPaginationLink(link) {
    const frame = document.createElement("turbo-frame")
    frame.id = link.dataset.frame
    frame.src = link.href
    link.replaceWith(frame)
  }
}
```

## Drag and Drop

```javascript
export default class extends Controller {
  static targets = ["item", "container"]
  static classes = ["draggedItem", "hoverContainer"]

  dragStart(event) {
    event.dataTransfer.effectAllowed = "move"
    this.dragItem = this.#itemContaining(event.target)
    this.sourceContainer = this.#containerContaining(this.dragItem)
    this.dragItem.classList.add(this.draggedItemClass)
  }

  dragOver(event) {
    event.preventDefault()
    const container = this.#containerContaining(event.target)
    if (container !== this.sourceContainer) {
      container.classList.add(this.hoverContainerClass)
    }
  }

  async drop(event) {
    const container = this.#containerContaining(event.target)
    if (container && container !== this.sourceContainer) {
      await this.#submitDropRequest(this.dragItem, container)
    }
  }

  async #submitDropRequest(item, container) {
    const url = container.dataset.dragAndDropUrl.replace("__id__", item.dataset.id)
    return post(url, { responseKind: "turbo-stream" })
  }
}
```

## Utility Helpers

```javascript
// Timing helpers
export function debounce(fn, delay = 1000) {
  let timeoutId = null
  return (...args) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn.apply(this, args), delay)
  }
}

export function nextFrame() {
  return new Promise(requestAnimationFrame)
}

export function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// Scroll helpers
export function scrollToBottom(element) {
  element.scrollTop = element.scrollHeight
}
```

## Frame Controller with Morph

```javascript
export default class extends Controller {
  morphRender({ detail }) {
    detail.render = function(currentElement, newElement) {
      Turbo.morphChildren(currentElement, newElement)
    }
  }

  reload() {
    this.element.reload()
  }
}
```

```erb
<turbo-frame id="card_123"
             data-controller="frame"
             data-action="turbo:before-frame-render->frame#morphRender">
```

## Advanced Patterns

### Turbo Stream Morphing

Use `method: :morph` for efficient DOM updates that preserve form state and focus:

```erb
<%# Replace with morphing to preserve user state %>
<%= turbo_stream.replace(dom_id(@column), partial: "boards/show/column", method: :morph) %>
```

### Lazy Loading Pagination

Pattern for infinite scroll with automatic page loading:

```erb
<%# Remove loading indicator and append next page %>
<%= turbo_stream.remove "#{params[:target]}-load-page-#{@page.number}" %>
<%= turbo_stream.append params[:target] do %>
  <%= render partial: "cards/display/preview", collection: @page.records %>
  <% unless @page.last? %>
    <%= cards_next_page_link params[:target], page: @page %>
  <% end %>
<% end %>
```

### Multi-Channel Broadcasting

Subscribe to multiple channels or account-wide broadcasts:

```erb
<%# Conditional channel subscription %>
<% if filter.boards.any? %>
  <% filter.boards.each do |board| %>
    <%= turbo_stream_from board %>
  <% end %>
<% else %>
  <%= turbo_stream_from [ Current.account, :all_boards ] %>
<% end %>
```

### Nested Activity Channels

Listen to both model updates and activity streams separately:

```erb
<%# Subscribe to card updates and its activity feed %>
<%= turbo_stream_from @card %>
<%= turbo_stream_from @card, :activity %>
```

### Frame Refresh with Morphing

Auto-refresh frames using morphing to preserve state:

```erb
<%# Frame auto-refreshes with morph strategy %>
<%= turbo_frame_tag "notifications", src: tray_notifications_path, refresh: "morph" %>
```

### Automatic Pagination with Intersection Observer

Helper pattern for automatic pagination when scrolling:

```erb
<%# Pagination wrapper with intersection observer %>
<%= with_automatic_pagination dom_id(@column, :cards), @page do %>
  <%= render "boards/columns/list", cards: @page.records %>
<% end %>
```

```javascript
// Stimulus controller for intersection-based pagination
export default class extends Controller {
  static targets = ["paginationLink"]
  static values = { paginateOnIntersection: { type: Boolean, default: false } }

  connect() {
    if (this.paginateOnIntersectionValue) {
      this.observer = new IntersectionObserver(this.#intersect, {
        rootMargin: "300px",
        threshold: 1
      })
      this.observer.observe(this.paginationLinkTarget)
    }
  }

  #intersect = ([entry]) => {
    if (entry?.isIntersecting) {
      this.#loadPaginationLink(entry.target)
    }
  }

  #loadPaginationLink(link) {
    const frame = document.createElement("turbo-frame")
    frame.id = link.dataset.frame
    frame.src = link.href
    link.replaceWith(frame)
  }
}
```
