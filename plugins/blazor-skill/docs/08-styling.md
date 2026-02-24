# Styling

## CSS Isolation

Place a `.razor.css` file next to the component. Blazor appends a `b-{10chars}` scope attribute at build time.

```
Components/Pages/
    Counter.razor
    Counter.razor.css    <-- scoped to Counter
```

All scoped styles are bundled into `{AssemblyName}.styles.css` (already referenced in App.razor template).

```css
/* Counter.razor.css */
h1 {
    color: blue;     /* Only affects h1 in Counter.razor */
}

.btn {
    padding: 10px;   /* Only affects .btn in Counter.razor */
}
```

## ::deep Combinator

Style elements inside child components from the parent's scoped CSS.

```css
/* Parent.razor.css */
.container ::deep h1 {
    color: red;    /* Targets h1 inside child components within .container */
}
```

**Requires a wrapper element** — the scope attribute is applied to the wrapper:

```razor
@* Parent.razor *@
<div class="container">   @* <-- Required wrapper for ::deep *@
    <ChildComponent />
</div>
```

Transforms to: `div.container[b-abc123] h1 { color: red; }`

## CSS Isolation Limitations

- Only applies to HTML elements, not Razor component tags or Tag Helpers
- `::deep` requires a block-level wrapper element
- Build-time only — no runtime CSS generation
- Importing CSS inside `@code` blocks breaks bundling
- Cannot target pseudo-elements of child components without `::deep`

## Conditional CSS Classes

### Ternary Expressions
```razor
<div class="@(isActive ? "active" : "")">
<div class="card @(isSelected ? "selected" : "") @(isHighlighted ? "highlighted" : "")">
```

### Helper Method
```csharp
private string GetButtonClass()
{
    var classes = new List<string> { "btn" };
    if (isPrimary) classes.Add("btn-primary");
    if (isLarge) classes.Add("btn-lg");
    if (isDisabled) classes.Add("disabled");
    return string.Join(" ", classes);
}
```

```razor
<button class="@GetButtonClass()">Click</button>
```

## Inline Styles

For runtime-computed values (positions, heights, progress bars).

```razor
<div style="width: @(progress)%; background-color: @color">
<div style="@($"transform: translateX({offsetX}px)")">
```

Prefer CSS classes and isolated CSS when possible — inline styles can't use pseudo-classes or media queries.

## Third-Party CSS (Bootstrap)

Bootstrap is included in Blazor project templates. Use classes directly:

```razor
<div class="container">
    <div class="row">
        <div class="col-md-6">
            <button class="btn btn-primary">Click</button>
        </div>
    </div>
</div>
```

CSS isolation and Bootstrap coexist. Use `::deep` to override Bootstrap inside components.

Global styles go in `wwwroot/css/app.css`. Additional libraries linked in `App.razor`:

```html
<link rel="stylesheet" href="css/app.css" />
<link rel="stylesheet" href="MyApp.styles.css" />  @* Scoped CSS bundle *@
```

## CSS Custom Properties (Design Tokens)

Define tokens in `wwwroot/css/app.css` and consume them in any `.razor.css`:

```css
/* wwwroot/css/app.css */
:root {
    --color-primary: #1a1a2e;
    --color-accent: #e94560;
    --color-surface: #ffffff;
    --font-display: 'Playfair Display', Georgia, serif;
    --font-body: 'Source Sans 3', system-ui, sans-serif;
    --space-md: 1rem;
    --space-lg: 2rem;
}
```

```css
/* Card.razor.css */
.card {
    background: var(--color-surface);
    padding: var(--space-md);
    font-family: var(--font-body);
}

.card-title {
    font-family: var(--font-display);
    color: var(--color-primary);
}
```

Design tokens provide a single source of truth for colors, fonts, and spacing. Override them with `[data-theme="dark"]` or `@media (prefers-color-scheme: dark)` for theming. See `12-design-aesthetics.md` for full guidance.

## Google Fonts Integration

Add font links in `App.razor` inside `<head>`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Source+Sans+3:wght@300;400;600&display=swap" rel="stylesheet" />
```

Reference the fonts via CSS variables (defined in `app.css`) and consume in `.razor.css` files. Use `font-display=swap` in the Google Fonts URL to avoid layout shift.

## Advanced Selectors in Scoped CSS

Modern CSS selectors work in `.razor.css` files:

```css
/* Form.razor.css */
.field:has(input:invalid) {
    border-color: var(--color-error);
}

:is(h1, h2, h3) {
    font-family: var(--font-display);
}

:where(.card, .panel) {
    border-radius: 0.75rem;
}
```

Note: Blazor's CSS isolation adds a scope attribute (`b-{hash}`) to the first selector segment. Complex selectors work as long as the scoped element is in the selector chain.

## Responsive Patterns

Use `@media` queries directly in `.razor.css` files:

```css
/* ProductGrid.razor.css */
.grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
}

@media (min-width: 768px) {
    .grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (min-width: 1200px) {
    .grid {
        grid-template-columns: repeat(3, 1fr);
    }
}
```

Media queries in isolated CSS are scoped the same way as regular rules — Blazor appends the scope attribute correctly inside `@media` blocks.

## Layout Patterns

### Fixed Sidebar + Scrollable Content

A common dashboard pattern. **Do not combine CSS Grid columns with `position: fixed`** — this creates a double-offset where the grid reserves space for the sidebar AND the margin pushes content again.

**Wrong** — double-offset:
```css
/* Layout.razor.css */
.shell {
    display: grid;
    grid-template-columns: 260px 1fr;  /* Grid reserves sidebar space */
}

.sidebar {
    position: fixed;  /* Sidebar is taken out of flow */
    width: 260px;
}

.main {
    margin-left: 260px;  /* Double offset! Content squeezed to ~half width */
}
```

**Correct** — fixed sidebar with margin only:
```css
/* Layout.razor.css */
.sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 260px;
    overflow-y: auto;
    z-index: 100;
}

.main {
    margin-left: 260px;  /* Only offset needed */
    min-height: 100vh;
}
```

**Also correct** — CSS Grid with no fixed positioning:
```css
/* Layout.razor.css */
.shell {
    display: grid;
    grid-template-columns: 260px 1fr;
    min-height: 100vh;
}

.sidebar {
    /* No position: fixed — sidebar scrolls with page or use overflow-y: auto + height: 100vh + position: sticky */
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
}
```

Choose one strategy, not both. Use CSS variables for the sidebar width so it's consistent:

```css
:root {
    --sidebar-width: 260px;
}
```
