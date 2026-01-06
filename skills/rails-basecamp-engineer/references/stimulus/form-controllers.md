# Form Stimulus Controllers

Controllers for form interactions and data persistence.

## Auto-Submit Controller

Auto-submit forms on input change:

```javascript
// app/javascript/controllers/auto_submit_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = { delay: { type: Number, default: 300 } }

  submit() {
    clearTimeout(this.timeout)
    this.timeout = setTimeout(() => {
      this.element.requestSubmit()
    }, this.delayValue)
  }

  submitNow() {
    clearTimeout(this.timeout)
    this.element.requestSubmit()
  }
}
```

Usage:
```html
<%= form_with model: @filter, data: { controller: "auto-submit" } do |f| %>
  <%= f.select :sort_by, options,
      data: { action: "change->auto-submit#submit" } %>
  <%= f.text_field :search,
      data: { action: "input->auto-submit#submit" } %>
<% end %>
```

## Auto-Resize Controller

Auto-expands textareas as you type:

```javascript
// app/javascript/controllers/autoresize_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = { minHeight: { type: Number, default: 0 } }

  connect() {
    this.resize()
  }

  resize() {
    this.element.style.height = "auto"
    const newHeight = Math.max(this.minHeightValue, this.element.scrollHeight)
    this.element.style.height = `${newHeight}px`
  }

  reset() {
    this.element.style.height = "auto"
  }
}
```

Usage:
```html
<textarea data-controller="autoresize"
          data-autoresize-min-height-value="100"
          data-action="input->autoresize#resize">
</textarea>
```

## Local Save Controller

Auto-save form content to localStorage, restore on page load:

```javascript
// app/javascript/controllers/local_save_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = { key: String }
  static targets = [ "input" ]

  connect() {
    this.restore()
  }

  save() {
    clearTimeout(this.saveTimeout)
    this.saveTimeout = setTimeout(() => {
      const content = this.inputTarget.value
      if (content) {
        localStorage.setItem(this.keyValue, content)
      } else {
        localStorage.removeItem(this.keyValue)
      }
    }, 300)
  }

  restore() {
    const saved = localStorage.getItem(this.keyValue)
    if (saved && !this.inputTarget.value) {
      this.inputTarget.value = saved
      this.dispatch("restored")
    }
  }

  clear() {
    localStorage.removeItem(this.keyValue)
  }

  submit({ detail: { success } }) {
    if (success) this.clear()
  }
}
```

Usage:
```html
<%= form_with model: @comment,
    data: {
      controller: "local-save",
      local_save_key_value: "comment-draft-#{@card.id}",
      action: "turbo:submit-end->local-save#submit"
    } do |f| %>
  <%= f.text_area :body,
      data: {
        local_save_target: "input",
        action: "input->local-save#save"
      } %>
<% end %>
```

## Form Controller

Form utilities including debounced submission and IME handling:

```javascript
// app/javascript/controllers/form_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = { debounce: { type: Number, default: 0 } }
  static targets = [ "submit" ]

  #composing = false

  connect() {
    this.element.addEventListener("compositionstart", () => this.#composing = true)
    this.element.addEventListener("compositionend", () => this.#composing = false)
  }

  submit(event) {
    // Don't submit during IME composition (CJK input)
    if (this.#composing) return

    clearTimeout(this.debounceTimeout)

    if (this.debounceValue > 0) {
      this.debounceTimeout = setTimeout(() => {
        this.element.requestSubmit()
      }, this.debounceValue)
    } else {
      this.element.requestSubmit()
    }
  }

  disableSubmit() {
    if (this.hasSubmitTarget) {
      this.submitTarget.disabled = true
    }
  }

  enableSubmit() {
    if (this.hasSubmitTarget) {
      this.submitTarget.disabled = false
    }
  }
}
```

## Character Counter Controller

Count characters in input:

```javascript
// app/javascript/controllers/character_counter_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = { max: Number }
  static targets = [ "input", "count" ]

  connect() {
    this.update()
  }

  update() {
    const count = this.inputTarget.value.length
    this.countTarget.textContent = count

    if (this.hasMaxValue) {
      this.countTarget.classList.toggle("over-limit", count > this.maxValue)
    }
  }
}
```

Usage:
```html
<div data-controller="character-counter" data-character-counter-max-value="280">
  <textarea data-character-counter-target="input"
            data-action="input->character-counter#update"></textarea>
  <span data-character-counter-target="count"></span>/280
</div>
```

## Design Patterns

1. **Debouncing** - Use timeouts to batch rapid inputs
2. **IME Handling** - Check `compositionstart`/`compositionend` for CJK input
3. **localStorage Persistence** - Save drafts, clear on successful submit
4. **Turbo Integration** - Listen to `turbo:submit-end` for success/failure
5. **Target Separation** - Separate targets for input and display elements
