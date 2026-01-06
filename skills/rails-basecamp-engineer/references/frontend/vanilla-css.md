# Vanilla CSS Architecture

Modern CSS approach used by 37signals - no Sass, no PostCSS, no Tailwind.

## CSS Cascade Layers

Foundation for predictable specificity:

```css
/* _global.css */
@layer reset, base, components, modules, utilities;
```

Layer priority (lowest to highest):
- `reset` - Normalize browser defaults
- `base` - Global element styles (body, a, kbd)
- `components` - Reusable UI patterns (.btn, .card, .input)
- `modules` - Page-specific styles
- `utilities` - Single-purpose classes (highest priority)

## OKLCH Color System

Perceptually uniform color space for better theming:

```css
:root {
  /* Define colors as LCH components */
  --lch-blue-dark: 57.02% 0.1895 260.46;
  --lch-blue-medium: 66% 0.196 257.82;
  --lch-blue-light: 84.04% 0.0719 255.29;

  /* Use oklch() to create colors */
  --color-link: oklch(var(--lch-blue-dark));
  --color-selected: oklch(var(--lch-blue-lighter));
}
```

Benefits:
- **Perceptually uniform** - Equal steps in lightness look equal
- **P3 gamut support** - Wider color range on modern displays
- **Easy theming** - Flip lightness values for dark mode

## Dark Mode

Achieved by redefining OKLCH values:

```css
/* Light mode (default) */
:root {
  --lch-ink-darkest: 26% 0.05 264;  /* Dark text */
  --lch-canvas: 100% 0 0;           /* White background */
}

/* Dark mode */
html[data-theme="dark"] {
  --lch-ink-darkest: 96.02% 0.0034 260;  /* Light text */
  --lch-canvas: 20% 0.0195 232.58;       /* Dark background */
}

/* Also respects system preference */
@media (prefers-color-scheme: dark) {
  html:not([data-theme]) {
    /* Same dark values */
  }
}
```

## Native CSS Nesting

No preprocessor needed:

```css
.btn {
  background-color: var(--btn-background);

  @media (any-hover: hover) {
    &:hover {
      filter: brightness(var(--btn-hover-brightness));
    }
  }

  html[data-theme="dark"] & {
    --btn-hover-brightness: 1.25;
  }

  &[disabled] {
    cursor: not-allowed;
    opacity: 0.3;
  }
}
```

## Component Pattern

Simple naming convention (BEM-inspired but pragmatic):

```css
/* Base component */
.card { }

/* Sub-elements with __ */
.card__header { }
.card__body { }
.card__title { }

/* Variants with -- */
.card--notification { }
.card--closed { }
```

## CSS Variables for Component APIs

Components expose customization via variables:

```css
.btn {
  --btn-background: var(--color-canvas);
  --btn-border-color: var(--color-ink-light);
  --btn-color: var(--color-ink);
  --btn-padding: 0.5em 1.1em;
  --btn-border-radius: 99rem;

  background-color: var(--btn-background);
  border: 1px solid var(--btn-border-color);
  color: var(--btn-color);
  padding: var(--btn-padding);
  border-radius: var(--btn-border-radius);
}

/* Variants override variables */
.btn--link {
  --btn-background: var(--color-link);
  --btn-color: var(--color-ink-inverted);
}

.btn--negative {
  --btn-background: var(--color-negative);
  --btn-color: var(--color-ink-inverted);
}
```

## Modern CSS Features

### @starting-style for Entry Animations

```css
.dialog {
  opacity: 0;
  transform: scale(0.2);
  transition: 150ms allow-discrete;
  transition-property: display, opacity, overlay, transform;

  &[open] {
    opacity: 1;
    transform: scale(1);
  }

  @starting-style {
    &[open] {
      opacity: 0;
      transform: scale(0.2);
    }
  }
}
```

### color-mix() for Dynamic Colors

```css
.card {
  --card-bg-color: color-mix(in srgb, var(--card-color) 4%, var(--color-canvas));
  --card-text-color: color-mix(in srgb, var(--card-color) 75%, var(--color-ink));
}
```

### :has() for Parent-Aware Styling

```css
.btn:has(input:checked) {
  --btn-background: var(--color-ink);
  --btn-color: var(--color-ink-inverted);
}

.card:has(.card__closed) {
  --card-color: var(--color-card-complete) !important;
}
```

### Logical Properties

```css
.pad-block { padding-block: var(--block-space); }
.pad-inline { padding-inline: var(--inline-space); }
.margin-inline-start { margin-inline-start: var(--inline-space); }
```

### Container Queries

```css
.card__content {
  contain: inline-size;  /* Enable container queries */
}
```

### Field Sizing

```css
.input--textarea {
  @supports (field-sizing: content) {
    field-sizing: content;
    max-block-size: calc(3lh + (2 * var(--input-padding)));
  }
}
```

## Design Tokens

All values come from CSS custom properties:

```css
:root {
  /* Spacing */
  --inline-space: 1ch;
  --block-space: 1rem;

  /* Typography */
  --text-small: 0.85rem;
  --text-normal: 1rem;
  --text-large: 1.5rem;

  /* Responsive typography */
  @media (max-width: 639px) {
    --text-small: 0.95rem;
    --text-normal: 1.1rem;
  }

  /* Z-index scale */
  --z-popup: 10;
  --z-nav: 30;
  --z-tooltip: 50;

  /* Animation */
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --dialog-duration: 150ms;
}
```

## Utility Classes (Minimal)

~60 focused utilities, not hundreds:

```css
@layer utilities {
  /* Text */
  .txt-small { font-size: var(--text-small); }
  .txt-subtle { color: var(--color-ink-dark); }

  /* Layout */
  .flex { display: flex; }
  .gap { column-gap: var(--column-gap, var(--inline-space)); }

  /* Spacing (using design tokens) */
  .pad { padding: var(--block-space) var(--inline-space); }
  .margin-block { margin-block: var(--block-space); }

  /* Visibility */
  .visually-hidden {
    clip-path: inset(50%);
    position: absolute;
  }
}
```

## File Organization

One file per concern, ~100-300 lines each:

```
app/assets/stylesheets/
├── _global.css          # CSS variables, layers, dark mode
├── reset.css            # Modern CSS reset
├── base.css             # Element defaults
├── layout.css           # Grid layout
├── utilities.css        # Utility classes
├── buttons.css          # .btn component
├── cards.css            # .card component
├── inputs.css           # Form controls
├── dialog.css           # Dialog animations
├── popup.css            # Dropdown menus
└── ... (component files)
```

## Responsive Strategy

Minimal breakpoints, mostly fluid:

```css
/* Fluid main padding */
--main-padding: clamp(var(--inline-space), 3vw, calc(var(--inline-space) * 3));

/* Responsive via container */
--tray-size: clamp(12rem, 25dvw, 24rem);

/* Only 2-3 breakpoints used */
@media (max-width: 639px) { /* Mobile */ }
@media (min-width: 640px) { /* Desktop */ }
@media (max-width: 799px) { /* Tablet and below */ }
```

## What's NOT Used

1. **No Sass/SCSS** - Native CSS is powerful enough
2. **No PostCSS** - Browser support is good
3. **No Tailwind** - Utilities exist but are minimal
4. **No CSS-in-JS** - Keep styles in stylesheets
5. **No CSS Modules** - Global styles with naming conventions
6. **No !important abuse** - Layers handle specificity

## CSS Philosophy

1. **Use the platform** - Native CSS is capable
2. **Design tokens everywhere** - Variables for consistency
3. **Layers for specificity** - No specificity wars
4. **Components own their styles** - Self-contained
5. **Utilities are escape hatches** - Not the primary approach
6. **Progressive enhancement** - `@supports` for new features
7. **Minimal responsive** - Fluid over breakpoint-heavy
