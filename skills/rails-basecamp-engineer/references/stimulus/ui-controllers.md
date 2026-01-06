# UI Stimulus Controllers

Controllers for dialogs, lists, and visual components.

## Dialog Controller

Native HTML `<dialog>` management with modal/non-modal support:

```javascript
// app/javascript/controllers/dialog_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = [ "dialog" ]
  static values = { modal: { type: Boolean, default: false } }

  connect() {
    this.dialogTarget.setAttribute("aria-hidden", "true")
  }

  open() {
    if (this.modalValue) {
      this.dialogTarget.showModal()
    } else {
      this.dialogTarget.show()
    }
    this.dialogTarget.setAttribute("aria-hidden", "false")
    this.dispatch("show")
  }

  toggle() {
    this.dialogTarget.open ? this.close() : this.open()
  }

  close() {
    this.dialogTarget.close()
    this.dialogTarget.setAttribute("aria-hidden", "true")
    this.dispatch("close")
  }

  closeOnClickOutside({ target }) {
    if (target === this.dialogTarget) {
      this.close()
    }
  }

  closeOnEscape(event) {
    if (event.key === "Escape") {
      this.close()
    }
  }
}
```

Usage:
```html
<div data-controller="dialog">
  <button data-action="dialog#open">Open Menu</button>

  <dialog data-dialog-target="dialog"
          data-action="click->dialog#closeOnClickOutside keydown.escape->dialog#closeOnEscape">
    <nav>Menu content</nav>
  </dialog>
</div>
```

## Lightbox Controller

Simple image lightbox using native `<dialog>`:

```javascript
// app/javascript/controllers/lightbox_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = [ "caption", "dialog", "zoomedImage" ]

  open(event) {
    event.preventDefault()
    this.dialogTarget.showModal()
    this.#set(event.target.closest("a"))
  }

  close() {
    this.dialogTarget.close()
  }

  handleTransitionEnd(event) {
    if (event.target === this.dialogTarget && !this.dialogTarget.open) {
      this.reset()
    }
  }

  reset() {
    this.zoomedImageTarget.src = ""
    this.captionTarget.innerText = ""
  }

  #set(target) {
    this.zoomedImageTarget.src = target.href
    const caption = target.dataset.lightboxCaptionValue
    if (caption) this.captionTarget.innerText = caption
  }
}
```

Usage:
```html
<div data-controller="lightbox">
  <a href="/large-image.jpg"
     data-lightbox-caption-value="Photo caption"
     data-action="click->lightbox#open">
    <img src="/thumbnail.jpg" alt="Thumbnail">
  </a>

  <dialog data-lightbox-target="dialog"
          data-action="click->lightbox#close transitionend->lightbox#handleTransitionEnd">
    <img data-lightbox-target="zoomedImage">
    <figcaption data-lightbox-target="caption"></figcaption>
  </dialog>
</div>
```

## Local Time Controller

Format UTC timestamps in the user's timezone:

```javascript
// app/javascript/controllers/local_time_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = {
    datetime: String,
    format: { type: String, default: "time-or-date" }
  }

  connect() {
    this.render()
  }

  render() {
    const datetime = new Date(this.datetimeValue)
    this.element.textContent = this.#format(datetime)
  }

  #format(datetime) {
    const now = new Date()
    const isToday = datetime.toDateString() === now.toDateString()

    switch (this.formatValue) {
      case "time-or-date":
        return isToday ? this.#formatTime(datetime) : this.#formatDate(datetime)
      case "time":
        return this.#formatTime(datetime)
      case "date":
        return this.#formatDate(datetime)
      case "relative":
        return this.#formatRelative(datetime)
      default:
        return datetime.toLocaleString()
    }
  }

  #formatTime(datetime) {
    return datetime.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" })
  }

  #formatDate(datetime) {
    return datetime.toLocaleDateString(undefined, { month: "short", day: "numeric" })
  }

  #formatRelative(datetime) {
    const diff = Date.now() - datetime
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(minutes / 60)
    const days = Math.floor(hours / 24)

    if (minutes < 1) return "just now"
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    return `${days}d ago`
  }
}
```

Usage:
```html
<time data-controller="local-time"
      data-local-time-datetime-value="2024-12-14T15:30:00Z"
      data-local-time-format-value="time-or-date">
  Dec 14, 2024 <!-- Fallback for no-JS -->
</time>
```

## Fetch on Visible Controller

Lazy load content when element scrolls into view:

```javascript
// app/javascript/controllers/fetch_on_visible_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = {
    url: String,
    threshold: { type: Number, default: 0.1 }
  }

  connect() {
    this.observer = new IntersectionObserver(
      entries => entries.forEach(entry => {
        if (entry.isIntersecting) this.fetch()
      }),
      { threshold: this.thresholdValue }
    )
    this.observer.observe(this.element)
  }

  disconnect() {
    this.observer?.disconnect()
  }

  async fetch() {
    this.observer.disconnect()
    const response = await fetch(this.urlValue)
    this.element.innerHTML = await response.text()
  }
}
```

Usage:
```html
<div data-controller="fetch-on-visible"
     data-fetch-on-visible-url-value="/cards/123/details"
     data-fetch-on-visible-threshold-value="0.5">
  <div class="skeleton-loader">Loading...</div>
</div>
```

## Navigable List Controller

Keyboard navigation for lists - arrow keys, enter to select:

```javascript
// app/javascript/controllers/navigable_list_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = [ "item" ]
  static values = {
    orientation: { type: String, default: "vertical" },
    wrap: { type: Boolean, default: true }
  }

  #selectedIndex = -1

  navigate(event) {
    const isVertical = this.orientationValue === "vertical"
    const prevKey = isVertical ? "ArrowUp" : "ArrowLeft"
    const nextKey = isVertical ? "ArrowDown" : "ArrowRight"

    switch (event.key) {
      case prevKey:
        event.preventDefault()
        this.#selectPrevious()
        break
      case nextKey:
        event.preventDefault()
        this.#selectNext()
        break
      case "Enter":
        event.preventDefault()
        this.#activateSelected()
        break
    }
  }

  select({ params: { index } }) {
    this.#select(index)
  }

  #selectPrevious() {
    const newIndex = this.#selectedIndex - 1
    if (newIndex >= 0) {
      this.#select(newIndex)
    } else if (this.wrapValue) {
      this.#select(this.itemTargets.length - 1)
    }
  }

  #selectNext() {
    const newIndex = this.#selectedIndex + 1
    if (newIndex < this.itemTargets.length) {
      this.#select(newIndex)
    } else if (this.wrapValue) {
      this.#select(0)
    }
  }

  #select(index) {
    this.itemTargets.forEach((item, i) => {
      item.setAttribute("aria-selected", i === index)
    })
    this.#selectedIndex = index
    this.itemTargets[index]?.scrollIntoView({ block: "nearest" })
  }

  #activateSelected() {
    const selected = this.itemTargets[this.#selectedIndex]
    selected?.click()
  }
}
```

Usage:
```html
<ul data-controller="navigable-list"
    data-action="keydown->navigable-list#navigate"
    role="listbox">
  <% @items.each_with_index do |item, index| %>
    <li data-navigable-list-target="item"
        data-action="click->navigable-list#select"
        data-navigable-list-index-param="<%= index %>"
        role="option">
      <%= item.name %>
    </li>
  <% end %>
</ul>
```

## Tooltip Controller

Simple CSS-based tooltips:

```javascript
// app/javascript/controllers/tooltip_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = { text: String, position: { type: String, default: "top" } }

  connect() {
    this.element.setAttribute("data-tooltip", this.textValue)
    this.element.setAttribute("data-tooltip-position", this.positionValue)
  }
}
```

CSS handles the actual tooltip display using `::before`/`::after` pseudo-elements.
