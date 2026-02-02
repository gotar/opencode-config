# Frontend Design Skill

**Purpose**: Craft production-grade frontend interfaces with modern web technologies, focusing on the actual stack used in TRUG and similar Rails projects.

**Scope**: HTML/CSS/JavaScript web interfaces, not native apps or print design.

**Related Skills**:
- `web-design-guidelines` (external) - UI/UX best practices compliance review
- `web-artifacts-builder` - Complex React-based web applications
- `agent-browser` - Browser automation for testing
- `theme-factory` - Visual theme application
- `algorithmic-art` - Generative art (different domain)

---

## Quick Reference

### Tech Stack (Production-Ready)

| Layer | Technology | Why |
|-------|-----------|-----|
| **Framework** | Rails 8 | Full-stack, Hotwire native |
| **CSS** | Pure CSS + Variables | No preprocessor overhead, modern features sufficient |
| **JS** | Vanilla + Stimulus | Lightweight, Turbo integration |
| **Bundler** | Importmaps | No build step, fast dev |
| **Testing** | Minitest + Capybara | Rails default, fast |
| **Deployment** | Kamal | Simple, Docker-based |

### Common Patterns

| Pattern | Implementation |
|---------|---------------|
| CSS Variables | `:root { --color-brand: #e25454; }` |
| BEM Naming | `.navbar { } .navbar-brand { } .btn--primary { }` |
| Flexbox Grid | `display: flex; flex-wrap: wrap;` |
| Responsive | `@media (max-width: 768px) { }` |
| Stimulus | `data-controller="modal"` |
| Turbo | `<turbo-frame id="modal">` |

---

## Decision Trees

### "Which CSS Approach Should I Use?"

```
Need custom design system?
├─ Yes, unique branding required
│  └─ Pure CSS with custom properties (variables.css)
│     • Define: colors, spacing, typography, shadows
│     • Use BEM naming
│     • One file per component
│
└─ No, standard UI acceptable
   └─ Consider existing library
      ├─ Need components fast? → Bootstrap/DaisyUI
      ├─ Utility-first preference? → Tailwind (with constraints)
      └─ Rails default? → Pure CSS (recommended)
```

### "Which JavaScript Approach Should I Use?"

```
Interactivity level?
├─ Minimal (toggle, modal, dropdown)
│  └─ Vanilla JS + Stimulus
│     • Stimulus for organized behavior
│     • Vanilla for one-off interactions
│     • No build tools needed
│
├─ Moderate (forms, dynamic content)
│  └─ Hotwire (Turbo + Stimulus)
│     • Turbo Frames for partial updates
│     • Turbo Streams for real-time
│     • Stimulus for complex interactions
│
└─ High (SPA-like, complex state)
   └─ React/Vue/Svelte
      ├─ Use web-artifacts-builder skill
      └─ Consider if complexity justified
```

### "How Should I Structure CSS?"

```
Project size?
├─ Small (< 10 components)
│  └─ Single application.css
│     • Reset/Normalize
│     • Variables
│     • Utilities
│     • Components
│
├─ Medium (10-30 components)
│  └─ Modular CSS files
│     • variables.css (design tokens)
│     • reset.css (normalize)
│     • utilities.css (helpers)
│     • components/*.css (one per major component)
│     • application.css (imports all)
│
└─ Large (> 30 components)
   └─ Component-based organization
      • Each component: HTML + CSS + JS + Stimulus controller
      • CSS Modules or scoped styles
      • Consider CSS-in-JS if complex theming
```

### "Which Testing Approach?"

```
What to test?
├─ Visual regression
│  └─ agent-browser (screenshot comparison)
│     • Take baseline screenshots
│     • Compare on each change
│     • Visual diff detection
│
├─ User flows
│  └─ Minitest + Capybara
│     • System tests for critical paths
│     • Feature tests for user workflows
│     • Headless Chrome for CI
│
└─ Component isolation
   └─ Storybook or similar
      • Document components
      • Test edge cases
      • Visual documentation
```

---

## Implementation Guide

### 1. Project Setup

```css
/* app/assets/stylesheets/variables.css */
:root {
  /* Colors */
  --color-brand: #e25454;
  --color-brand-dark: #c23e3e;
  --color-dark: #505050;
  --color-light: #ffffff;
  --color-gray-light: #e0e0e0;
  --color-gray-dark: #333;
  
  /* Typography */
  --font-family: Lato, -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.25rem;
  --font-size-xl: 1.5rem;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 2rem;
  --spacing-xl: 4rem;
  
  /* Layout */
  --max-width: 1200px;
  --border-radius: 50px;
  --border-radius-sm: 8px;
  
  /* Transitions */
  --transition-fast: 0.2s;
  --transition-base: 0.3s;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.1);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
}
```

### 2. Component Structure

```css
/* BEM Naming: Block__Element--Modifier */

/* Block */
.card { }

/* Element */
.card__header { }
.card__body { }
.card__footer { }

/* Modifier */
.card--highlighted { }
.card--compact { }
```

### 3. Stimulus Controller

```javascript
// app/javascript/controllers/modal_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["content"]
  static values = { open: Boolean }

  connect() {
    this.openValue = false
  }

  toggle() {
    this.openValue = !this.openValue
    this.contentTarget.classList.toggle("hidden", !this.openValue)
  }

  close() {
    this.openValue = false
    this.contentTarget.classList.add("hidden")
  }
}
```

```html
<!-- Usage in ERB -->
<div data-controller="modal">
  <button data-action="click->modal#toggle">Open Modal</button>
  
  <div data-modal-target="content" class="hidden modal-overlay">
    <div class="modal-content">
      <button data-action="click->modal#close">×</button>
      <!-- Modal content -->
    </div>
  </div>
</div>
```

### 4. Responsive Patterns

```css
/* Mobile-first approach */

.container {
  width: 100%;
  padding: 0 var(--spacing-md);
}

/* Tablet */
@media (min-width: 768px) {
  .container {
    max-width: 750px;
    margin: 0 auto;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .container {
    max-width: var(--max-width);
  }
}
```

---

## Real-World Examples

### TRUG Project Patterns

**Navbar Component:**
```css
/* navbar.css */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-brand);
}

.navbar__brand {
  color: var(--color-light);
  font-weight: 700;
  text-decoration: none;
}

.navbar__actions {
  display: flex;
  gap: var(--spacing-md);
}

.navbar__link {
  color: var(--color-light);
  text-decoration: none;
  transition: opacity var(--transition-fast);
}

.navbar__link:hover {
  opacity: 0.8;
}
```

**Video Player (Lazy Loading):**
```javascript
// archive.js
const createIframe = (videoId, provider) => {
  const iframe = document.createElement('iframe');
  iframe.src = provider === 'youtube' 
    ? `https://www.youtube.com/embed/${videoId}?autoplay=1`
    : `https://player.vimeo.com/video/${videoId}?autoplay=true`;
  iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
  iframe.allowFullscreen = true;
  iframe.className = 'video-iframe';
  iframe.loading = 'lazy';
  return iframe;
};
```

**Form Styling:**
```css
/* forms.css */
.form-group {
  margin-bottom: var(--spacing-md);
}

.form-label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-weight: 600;
  color: var(--color-dark);
}

.form-input {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-gray-light);
  border-radius: var(--border-radius-sm);
  font-family: var(--font-family);
  font-size: var(--font-size-base);
  transition: border-color var(--transition-fast);
}

.form-input:focus {
  outline: none;
  border-color: var(--color-brand);
  box-shadow: 0 0 0 3px rgba(226, 84, 84, 0.1);
}

.form-error {
  color: var(--color-brand);
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-xs);
}
```

---

## Browser Automation (Preferred over MCP)

When testing or automating browser interactions, prefer agent-browser over MCP servers:

### Screenshot Testing
```javascript
// Using agent-browser for visual regression
delegate_task(
  category="visual-engineering",
  load_skills=["agent-browser"],
  prompt=""
1. Navigate to localhost:3000
2. Take screenshot of homepage
3. Compare with baseline
4. Report visual differences
  """)
```

### Form Automation
```javascript
// Fill and submit forms for testing
delegate_task(
  category="unspecified-high",
  load_skills=["agent-browser"],
  prompt=""
1. Navigate to /contact
2. Fill name: "Test User"
3. Fill email: "test@example.com"
4. Fill message: "Test message"
5. Submit form
6. Verify success message appears
  """)
```

---

## Self-Learning & Improvement

### Trace Capture Template

After completing a frontend task, document:

```markdown
# Trace: frontend-design_[timestamp]
Skill: frontend-design
Task: [brief description]
Status: [success/partial/failure]

## Approach
- CSS architecture used: [variables/BEM/utility]
- JS approach: [vanilla/stimulus/hotwire]
- Browser testing: [manual/automated]

## Decisions Made
- [Decision 1 and rationale]
- [Decision 2 and rationale]

## Challenges
- [What was difficult]

## Solutions
- [How it was resolved]

## Performance Metrics
- Lighthouse score: [X/100]
- Bundle size: [X KB]
- Render time: [X ms]

## Key Learnings
- [What worked well]
- [What to improve next time]
- [New pattern discovered]
```

Save to: `.tmp/learning/traces/frontend-design_[timestamp].md`

### Pattern Recognition

After 5+ traces, analyze for:
- **CSS patterns**: Which variable naming works best?
- **JS patterns**: When to use Stimulus vs vanilla?
- **Testing patterns**: Which visual regression approach catches most bugs?
- **Performance patterns**: Common bottlenecks and optimizations

Extract insights to: `.tmp/learning/insights/frontend-design.md`

### Skill Evolution

If patterns emerge:
1. Update this SKILL.md with new learnings
2. Add new decision trees based on experience
3. Expand real-world examples section
4. Document browser-specific gotchas

---

## Common Pitfalls

**Don't:**
- Use `!important` (indicates specificity issues)
- Mix BEM with utility classes without clear boundaries
- Skip mobile testing (test at 320px, 768px, 1024px, 1440px)
- Ignore accessibility (always include focus states, ARIA labels)
- Use external tools (MCP) when agent-browser suffices

**Do:**
- Define CSS variables at `:root` for theming
- Test with real data (lorem ipsum hides layout issues)
- Use Stimulus for JavaScript organization
- Prefer external tools (agent-browser) for testing over MCP
- Document browser support requirements

---

## Tool Selection Guide

| Task | Primary Tool | Alternative | Avoid |
|------|-------------|-------------|-------|
| Visual testing | agent-browser | Manual screenshots | MCP servers |
| Form automation | agent-browser | Capybara system tests | Complex MCP |
| Component dev | Hotwire + Stimulus | React (if SPA) | jQuery |
| CSS architecture | Pure CSS + Variables | SCSS (if needed) | CSS-in-JS |
| Responsive testing | agent-browser viewports | Browser DevTools | Manual only |

---

## Further Reading

- [Hotwire Documentation](https://hotwired.dev/)
- [Stimulus Handbook](https://stimulus.hotwired.dev/)
- [Every Layout](https://every-layout.dev/) - CSS layout patterns
- [Web Design Guidelines](https://developer.mozilla.org/en-US/docs/Web) - MDN reference
