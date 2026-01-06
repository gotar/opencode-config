# DaisyUI + TailwindCSS

Alternative frontend approach using Tailwind CSS with DaisyUI component library.

> **Note:** For up-to-date DaisyUI component examples and API details, use Context7 to look up live documentation (resolve "daisyui" library ID, then fetch docs for specific components or topics).

## When to Use

Choose DaisyUI/Tailwind when:
- Rapid prototyping is prioritized
- Team is familiar with utility-first CSS
- Project needs extensive pre-built components
- Custom design system is not required

## Setup

```bash
# Rails 7+
./bin/rails css:install:tailwind
yarn add daisyui
```

```javascript
// tailwind.config.js
module.exports = {
  content: [
    './app/views/**/*.{erb,html}',
    './app/helpers/**/*.rb',
    './app/javascript/**/*.js'
  ],
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["light", "dark"]
  }
}
```

## Integration with Stimulus

DaisyUI components work seamlessly with Stimulus controllers:

```html
<div data-controller="dialog">
  <button class="btn btn-primary" data-action="dialog#open">
    Open Modal
  </button>

  <dialog data-dialog-target="dialog" class="modal">
    <div class="modal-box">
      <h3 class="font-bold text-lg">Hello!</h3>
      <p class="py-4">Modal content</p>
      <div class="modal-action">
        <button class="btn" data-action="dialog#close">Close</button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop">
      <button>close</button>
    </form>
  </dialog>
</div>
```

## Key Differences from Vanilla CSS Approach

| Aspect | Vanilla CSS | DaisyUI/Tailwind |
|--------|-------------|------------------|
| File size | ~8KB custom | ~20KB+ framework |
| Learning curve | CSS knowledge | Tailwind classes |
| Customization | Full control | Theme constraints |
| Dark mode | OKLCH variables | Theme switching |
| Components | Build from scratch | Pre-built |

## Resources

- [DaisyUI Documentation](https://daisyui.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Rails + Tailwind Guide](https://tailwindcss.com/docs/guides/ruby-on-rails)
