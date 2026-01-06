# Stimulus Controller Catalog

Quick reference for finding the right Stimulus controller patterns.

## Decision Table

| Need | Controller | File |
|------|------------|------|
| Copy text to clipboard | `copy-to-clipboard` | `utility-controllers.md` |
| Keyboard shortcuts | `hotkey` | `utility-controllers.md` |
| Toggle CSS classes | `toggle-class` | `utility-controllers.md` |
| Remove element from DOM | `element-removal` | `utility-controllers.md` |
| Track page views | `beacon` | `utility-controllers.md` |
| Auto-click on connect | `auto-click` | `utility-controllers.md` |
| Auto-submit form on change | `auto-submit` | `form-controllers.md` |
| Auto-resize textarea | `autoresize` | `form-controllers.md` |
| Save draft to localStorage | `local-save` | `form-controllers.md` |
| Character counter | `character-counter` | `form-controllers.md` |
| Form utilities (debounce, IME) | `form` | `form-controllers.md` |
| Modal/non-modal dialogs | `dialog` | `ui-controllers.md` |
| Image lightbox | `lightbox` | `ui-controllers.md` |
| Keyboard list navigation | `navigable-list` | `ui-controllers.md` |
| Lazy load on scroll | `fetch-on-visible` | `ui-controllers.md` |
| Format time in user timezone | `local-time` | `ui-controllers.md` |
| Simple tooltips | `tooltip` | `ui-controllers.md` |
| Drag and drop between containers | `drag-and-drop` | `interaction-controllers.md` |
| Reorder items in list | `sortable` | `interaction-controllers.md` |
| Resize panels | `resize` | `interaction-controllers.md` |

## Reference Files

### `utility-controllers.md`
Small, focused, reusable controllers:
- **copy-to-clipboard** - Async clipboard API with visual feedback
- **auto-click** - Click element on connect
- **element-removal** - Remove any element on action
- **toggle-class** - Toggle/add/remove CSS classes
- **hotkey** - Bind keyboard shortcuts
- **beacon** - Track views via navigator.sendBeacon

### `form-controllers.md`
Form interactions and persistence:
- **auto-submit** - Submit form on input change with debounce
- **autoresize** - Auto-expand textareas
- **local-save** - Save drafts to localStorage
- **form** - Debounced submission, IME handling
- **character-counter** - Count input characters

### `ui-controllers.md`
Dialogs, lists, and visual components:
- **dialog** - Native `<dialog>` management
- **lightbox** - Image lightbox with `<dialog>`
- **local-time** - Format UTC in user timezone
- **fetch-on-visible** - Lazy load with IntersectionObserver
- **navigable-list** - Arrow key navigation
- **tooltip** - CSS-based tooltips

### `interaction-controllers.md`
Complex interactions:
- **drag-and-drop** - Full drag-and-drop with Turbo integration
- **sortable** - Simple reordering within a list
- **resize** - Resizable panels

## Design Patterns

All controllers follow these patterns:

1. **Stimulus Values for Configuration**
   ```javascript
   static values = { delay: { type: Number, default: 300 } }
   ```

2. **Stimulus Classes for Styling**
   ```javascript
   static classes = [ "active", "loading" ]
   ```

3. **Private Methods with #**
   ```javascript
   #privateMethod() { ... }
   ```

4. **No Dependencies** - Vanilla JS only, no jQuery
