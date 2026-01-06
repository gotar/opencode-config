# Utility Stimulus Controllers

Small, focused, reusable controllers for common tasks.

## Copy-to-Clipboard Controller

Simple async clipboard API wrapper with visual feedback:

```javascript
// app/javascript/controllers/copy_to_clipboard_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = { content: String }
  static classes = [ "success" ]

  async copy(event) {
    event.preventDefault()
    this.reset()

    try {
      await navigator.clipboard.writeText(this.contentValue)
      this.element.classList.add(this.successClass)
    } catch {}
  }

  reset() {
    this.element.classList.remove(this.successClass)
    this.#forceReflow()
  }

  #forceReflow() {
    this.element.offsetWidth
  }
}
```

Usage:
```html
<button data-controller="copy-to-clipboard"
        data-copy-to-clipboard-content-value="https://example.com/share"
        data-copy-to-clipboard-success-class="copied"
        data-action="click->copy-to-clipboard#copy">
  Copy Link
</button>
```

## Auto-Click Controller

Clicks an element when it connects. Perfect for auto-submitting forms:

```javascript
// app/javascript/controllers/auto_click_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  connect() {
    this.element.click()
  }
}
```

Usage:
```html
<button data-controller="auto-click" data-action="...">
  Auto-triggered
</button>
```

## Element Removal Controller

Removes any element on action:

```javascript
// app/javascript/controllers/element_removal_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  remove() {
    this.element.remove()
  }
}
```

Usage:
```html
<div data-controller="element-removal">
  <p>Dismissible content</p>
  <button data-action="element-removal#remove">Dismiss</button>
</div>
```

## Toggle Class Controller

Toggle, add, or remove CSS classes:

```javascript
// app/javascript/controllers/toggle_class_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static classes = [ "toggle" ]
  static targets = [ "checkbox" ]

  toggle() {
    this.element.classList.toggle(this.toggleClass)
  }

  add() {
    this.element.classList.add(this.toggleClass)
  }

  remove() {
    this.element.classList.remove(this.toggleClass)
  }

  checkAll() {
    this.checkboxTargets.forEach(checkbox => checkbox.checked = true)
  }

  checkNone() {
    this.checkboxTargets.forEach(checkbox => checkbox.checked = false)
  }
}
```

Usage:
```html
<div data-controller="toggle-class"
     data-toggle-class-toggle-class="expanded">
  <button data-action="toggle-class#toggle">Toggle</button>
  <div class="content">...</div>
</div>
```

## Hotkey Controller

Bind keyboard shortcuts to elements:

```javascript
// app/javascript/controllers/hotkey_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  click(event) {
    if (this.#isClickable && !this.#shouldIgnore(event)) {
      event.preventDefault()
      this.element.click()
    }
  }

  focus(event) {
    if (this.#isClickable && !this.#shouldIgnore(event)) {
      event.preventDefault()
      this.element.focus()
    }
  }

  #shouldIgnore(event) {
    return event.defaultPrevented || event.target.closest("input, textarea, [contenteditable]")
  }

  get #isClickable() {
    return getComputedStyle(this.element).pointerEvents !== "none"
  }
}
```

Usage:
```html
<button data-controller="hotkey"
        data-action="keydown.n@window->hotkey#click">
  New Card (N)
</button>

<input data-controller="hotkey"
       data-action="keydown.slash@window->hotkey#focus"
       placeholder="Search (/)">
```

## Beacon Controller

Track views/reads by sending beacon on connect:

```javascript
// app/javascript/controllers/beacon_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = { url: String }

  connect() {
    this.#sendBeacon()
  }

  #sendBeacon() {
    if (this.urlValue) {
      navigator.sendBeacon(this.urlValue)
    }
  }
}
```

Usage:
```html
<article data-controller="beacon"
         data-beacon-url-value="<%= card_reading_path(@card) %>">
  <!-- Card content - reading tracked when viewed -->
</article>
```

## Design Patterns

1. **Stimulus Values for Configuration**
   ```javascript
   static values = { content: String, delay: { type: Number, default: 300 } }
   ```

2. **Stimulus Classes for Styling**
   ```javascript
   static classes = [ "active", "loading" ]
   // Use: this.activeClass, this.loadingClass
   ```

3. **Private Methods with #**
   ```javascript
   #privateMethod() { ... }
   ```

4. **Early Returns for Guard Clauses**
   ```javascript
   if (!this.#isValid) return
   ```

5. **No Dependencies** - Vanilla JS, no jQuery
