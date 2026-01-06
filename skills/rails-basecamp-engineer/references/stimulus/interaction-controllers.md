# Interaction Stimulus Controllers

Controllers for complex interactions like drag-and-drop.

## Drag and Drop Controller

Full drag-and-drop between containers with Turbo integration:

```javascript
// app/javascript/controllers/drag_and_drop_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = [ "item", "container" ]
  static classes = [ "dragging", "dragOver" ]
  static values = {
    url: String,
    paramName: { type: String, default: "position" }
  }

  #dragItem = null
  #placeholder = null

  // Item Events

  itemDragStart(event) {
    this.#dragItem = event.target.closest("[data-drag-and-drop-target='item']")
    this.#dragItem.classList.add(this.draggingClass)

    event.dataTransfer.effectAllowed = "move"
    event.dataTransfer.setData("text/plain", this.#dragItem.dataset.id)

    this.#createPlaceholder()
  }

  itemDragEnd(event) {
    this.#dragItem?.classList.remove(this.draggingClass)
    this.#removePlaceholder()
    this.#dragItem = null
  }

  // Container Events

  containerDragOver(event) {
    event.preventDefault()
    event.dataTransfer.dropEffect = "move"

    const container = event.target.closest("[data-drag-and-drop-target='container']")
    if (!container) return

    container.classList.add(this.dragOverClass)

    const afterElement = this.#getDragAfterElement(container, event.clientY)
    if (afterElement) {
      container.insertBefore(this.#placeholder, afterElement)
    } else {
      container.appendChild(this.#placeholder)
    }
  }

  containerDragLeave(event) {
    const container = event.target.closest("[data-drag-and-drop-target='container']")
    if (container && !container.contains(event.relatedTarget)) {
      container.classList.remove(this.dragOverClass)
    }
  }

  async containerDrop(event) {
    event.preventDefault()

    const container = event.target.closest("[data-drag-and-drop-target='container']")
    if (!container || !this.#dragItem) return

    container.classList.remove(this.dragOverClass)

    // Insert item at placeholder position
    this.#placeholder.replaceWith(this.#dragItem)

    // Calculate new position
    const items = [...container.querySelectorAll("[data-drag-and-drop-target='item']")]
    const position = items.indexOf(this.#dragItem)
    const containerId = container.dataset.containerId

    // Submit to server
    await this.#submitPosition(this.#dragItem.dataset.id, position, containerId)
  }

  // Private Methods

  #createPlaceholder() {
    this.#placeholder = document.createElement("div")
    this.#placeholder.classList.add("drag-placeholder")
    this.#placeholder.style.height = `${this.#dragItem.offsetHeight}px`
  }

  #removePlaceholder() {
    this.#placeholder?.remove()
    this.#placeholder = null
  }

  #getDragAfterElement(container, y) {
    const items = [...container.querySelectorAll(
      "[data-drag-and-drop-target='item']:not(.dragging)"
    )]

    return items.reduce((closest, child) => {
      const box = child.getBoundingClientRect()
      const offset = y - box.top - box.height / 2

      if (offset < 0 && offset > closest.offset) {
        return { offset, element: child }
      } else {
        return closest
      }
    }, { offset: Number.NEGATIVE_INFINITY }).element
  }

  async #submitPosition(itemId, position, containerId) {
    const url = this.urlValue.replace(":id", itemId)
    const body = new FormData()
    body.append(this.paramNameValue, position)
    if (containerId) body.append("container_id", containerId)

    const response = await fetch(url, {
      method: "PATCH",
      body,
      headers: {
        "Accept": "text/vnd.turbo-stream.html"
      }
    })

    if (response.ok) {
      const html = await response.text()
      Turbo.renderStreamMessage(html)
    }
  }
}
```

Usage:
```html
<div data-controller="drag-and-drop"
     data-drag-and-drop-url-value="/cards/:id/position"
     data-drag-and-drop-dragging-class="opacity-50"
     data-drag-and-drop-drag-over-class="bg-blue-100">

  <div data-drag-and-drop-target="container"
       data-container-id="column-1"
       data-action="dragover->drag-and-drop#containerDragOver
                    dragleave->drag-and-drop#containerDragLeave
                    drop->drag-and-drop#containerDrop">

    <% @column.cards.each do |card| %>
      <article data-drag-and-drop-target="item"
               data-id="<%= card.id %>"
               draggable="true"
               data-action="dragstart->drag-and-drop#itemDragStart
                           dragend->drag-and-drop#itemDragEnd">
        <%= card.title %>
      </article>
    <% end %>
  </div>
</div>
```

## Sortable List Controller

Simpler reordering within a single list:

```javascript
// app/javascript/controllers/sortable_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = [ "item" ]
  static values = { url: String }

  #dragItem = null

  dragStart(event) {
    this.#dragItem = event.target.closest("[data-sortable-target='item']")
    event.dataTransfer.effectAllowed = "move"
  }

  dragOver(event) {
    event.preventDefault()
    const target = event.target.closest("[data-sortable-target='item']")
    if (target && target !== this.#dragItem) {
      const rect = target.getBoundingClientRect()
      const midY = rect.top + rect.height / 2

      if (event.clientY < midY) {
        target.parentNode.insertBefore(this.#dragItem, target)
      } else {
        target.parentNode.insertBefore(this.#dragItem, target.nextSibling)
      }
    }
  }

  async dragEnd(event) {
    if (!this.#dragItem) return

    const items = this.itemTargets
    const position = items.indexOf(this.#dragItem)

    await fetch(this.urlValue.replace(":id", this.#dragItem.dataset.id), {
      method: "PATCH",
      body: JSON.stringify({ position }),
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      }
    })

    this.#dragItem = null
  }
}
```

## Resize Controller

Resizable panels:

```javascript
// app/javascript/controllers/resize_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = [ "handle", "panel" ]
  static values = {
    min: { type: Number, default: 200 },
    max: { type: Number, default: 600 },
    direction: { type: String, default: "horizontal" }
  }

  #startX = 0
  #startWidth = 0

  start(event) {
    event.preventDefault()
    this.#startX = event.clientX
    this.#startWidth = this.panelTarget.offsetWidth

    document.addEventListener("mousemove", this.resize)
    document.addEventListener("mouseup", this.stop)
  }

  resize = (event) => {
    const diff = event.clientX - this.#startX
    const newWidth = Math.min(
      Math.max(this.#startWidth + diff, this.minValue),
      this.maxValue
    )
    this.panelTarget.style.width = `${newWidth}px`
  }

  stop = () => {
    document.removeEventListener("mousemove", this.resize)
    document.removeEventListener("mouseup", this.stop)
    this.dispatch("resized", { detail: { width: this.panelTarget.offsetWidth } })
  }
}
```

## Design Patterns for Interaction Controllers

1. **Use Native Drag Events** - `dragstart`, `dragover`, `drop`, `dragend`
2. **Create Placeholders** - Visual feedback for drop position
3. **Calculate Position from DOM** - Count siblings to determine new position
4. **Turbo Integration** - Return Turbo Streams from server for UI updates
5. **Optimistic Updates** - Move DOM immediately, sync with server async
6. **Debounce Server Calls** - Don't hit server on every tiny movement
