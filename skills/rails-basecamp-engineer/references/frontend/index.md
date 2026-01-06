# Frontend Styling Approaches

## Detecting Existing CSS Approach

Before choosing an approach, check what the project already uses:

**Indicators of DaisyUI/Tailwind:**
- `tailwind.config.js` exists in project root
- `@tailwind` directives in CSS files
- DaisyUI component classes in views (`btn`, `card`, `modal`, `drawer`)
- `daisyui` or `tailwindcss` in `package.json`

**Indicators of Vanilla CSS (37signals style):**
- `app/assets/stylesheets/_global.css` with `@layer` declarations
- OKLCH color values (`oklch(...)`) in stylesheets
- CSS custom properties for design tokens (`--color-*`, `--spacing-*`)
- No Tailwind config file

**If unknown:** Use Explore agent to search for `tailwind.config.js` or `@layer` in stylesheets.

---

Choose based on your project requirements:

| Approach | When to Use |
|----------|-------------|
| **Vanilla CSS** | Full control, 37signals patterns, no framework overhead |
| **DaisyUI/Tailwind** | Rapid prototyping, pre-built components, utility-first |

## Decision Guide

**Choose `vanilla-css.md` when:**
- Building a custom design system
- Want to follow 37signals CSS architecture (layers, OKLCH, tokens)
- Need maximum performance (smaller bundle)
- Team has strong CSS knowledge

**Choose `daisyui.md` when:**
- Rapid prototyping is priority
- Need pre-built accessible components
- Team prefers utility-first CSS
- Don't need highly custom designs

## Reference Files

- `vanilla-css.md` - 37signals CSS patterns: CSS layers, OKLCH colors, design tokens, dark mode, native nesting
- `daisyui.md` - DaisyUI/TailwindCSS integration with Stimulus (use Context7 for live docs)

## Quick Comparison

| Aspect | Vanilla CSS | DaisyUI |
|--------|-------------|---------|
| Bundle size | ~8KB custom | ~20KB+ |
| Learning curve | CSS knowledge | Tailwind classes |
| Customization | Full control | Theme-based |
| Dark mode | OKLCH variable flip | Theme switching |
| Components | Build from scratch | Pre-built |
| Modern CSS | Native (layers, :has(), nesting) | PostCSS processed |
