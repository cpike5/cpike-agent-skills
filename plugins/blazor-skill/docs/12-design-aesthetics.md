# Design Aesthetics

How to produce Blazor pages that are both functionally correct AND visually striking. This document adapts general frontend design principles to Blazor's component model, CSS isolation, and rendering pipeline.

## Design Thinking

Before writing any `.razor` file, commit to a clear aesthetic direction:

- **Purpose** — What problem does this interface solve? Who uses it? A dashboard for analysts and a landing page for a coffee roaster demand entirely different aesthetics.
- **Tone** — Pick a bold direction: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian. Use these as inspiration, then design something true to the context.
- **Constraints** — Render mode affects what's possible (animations that rely on JS interop need InteractiveServer or InteractiveWebAssembly). Consider accessibility and performance.
- **Differentiation** — What makes this unforgettable? What's the one thing someone will remember?

**Critical**: Choose a conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work — the key is intentionality, not intensity.

## Typography in Blazor

### Google Fonts Integration

Add font links in `App.razor` inside `<head>`:

```html
<head>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Source+Sans+3:wght@300;400;600&display=swap" rel="stylesheet" />
</head>
```

### Font Pairing with CSS Variables

Define font stacks as design tokens in `wwwroot/css/app.css`:

```css
:root {
    --font-display: 'Playfair Display', Georgia, serif;
    --font-body: 'Source Sans 3', system-ui, sans-serif;
    --font-mono: 'JetBrains Mono', 'Cascadia Code', monospace;
}
```

Consume in `.razor.css`:

```css
h1, h2, h3 {
    font-family: var(--font-display);
    letter-spacing: -0.02em;
}

p, li, label {
    font-family: var(--font-body);
    line-height: 1.6;
}
```

### Font Guidance

- **Pair a distinctive display font with a refined body font.** Contrast (serif + sans-serif) creates hierarchy.
- **Avoid generic defaults when you have creative freedom** — Inter, Roboto, Arial, and system fonts produce forgettable pages. (If the project specifies a brand font, use it.)
- **Vary choices per project.** Never converge on the same font (e.g., Space Grotesk) across every component.

## Color Systems

### CSS Custom Properties as Design Tokens

Define a cohesive palette in `wwwroot/css/app.css`:

```css
:root {
    /* Core palette */
    --color-primary: #1a1a2e;
    --color-accent: #e94560;
    --color-surface: #f8f7f4;
    --color-text: #16213e;
    --color-text-muted: #6b7280;

    /* Semantic tokens */
    --color-success: #10b981;
    --color-warning: #f59e0b;
    --color-error: #ef4444;

    /* Spacing scale */
    --space-xs: 0.25rem;
    --space-sm: 0.5rem;
    --space-md: 1rem;
    --space-lg: 2rem;
    --space-xl: 4rem;
}
```

### Dark/Light Theming

```css
:root {
    --bg: #f8f7f4;
    --fg: #1a1a2e;
    --surface: #ffffff;
    --border: #e5e7eb;
}

[data-theme="dark"] {
    --bg: #0f0f1a;
    --fg: #e4e4e7;
    --surface: #1a1a2e;
    --border: #2d2d44;
}
```

Toggle with a cascading value or JS interop to set the `data-theme` attribute on `<html>`.

### Palette Guidance

- **Dominant color + sharp accent** outperforms timid, evenly-distributed palettes.
- Override tokens in `.razor.css` for component-specific tweaks — the cascade handles the rest.
- Commit to a cohesive scheme. Random colors produce visual noise.

## Motion & Animation

### CSS Keyframes in Isolated CSS

```css
/* Card.razor.css */
@keyframes fade-in-up {
    from {
        opacity: 0;
        transform: translateY(1rem);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.card {
    animation: fade-in-up 0.5s ease-out both;
}
```

### Staggered Reveals with `animation-delay`

```razor
@* CardGrid.razor *@
@for (int i = 0; i < Items.Count; i++)
{
    <div class="card" style="animation-delay: @(i * 80)ms">
        @Items[i].Title
    </div>
}
```

```css
/* CardGrid.razor.css */
.card {
    animation: fade-in-up 0.4s ease-out both;
}
```

### Transition Patterns

```css
/* NavItem.razor.css */
.nav-link {
    transition: color 0.2s ease, transform 0.2s ease;
}

.nav-link:hover {
    color: var(--color-accent);
    transform: translateX(4px);
}
```

### Animation End Events

```razor
<div class="toast @(IsVisible ? "show" : "hide")" @onanimationend="OnDismissed">
    @Message
</div>
```

### Scroll-Triggered Effects via JS Interop

For effects triggered by scroll position, use JS interop with `IntersectionObserver`:

```javascript
// wwwroot/js/scroll-reveal.js
export function observe(dotNetRef, element) {
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                dotNetRef.invokeMethodAsync('OnElementVisible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    observer.observe(element);
    return observer;
}
```

This requires an interactive render mode (InteractiveServer or InteractiveWebAssembly).

### Motion Guidance

- **One well-orchestrated page load with staggered reveals** creates more delight than scattered micro-interactions.
- Prefer CSS-only solutions. Reserve JS interop for scroll-triggered and complex orchestration.
- Use `animation-delay` for stagger — no JS needed for sequential card reveals.

## Spatial Composition

### CSS Grid Layouts in `.razor.css`

```css
/* Dashboard.razor.css */
.dashboard-grid {
    display: grid;
    grid-template-columns: 1fr 2fr 1fr;
    grid-template-rows: auto 1fr auto;
    gap: var(--space-lg);
    min-height: 100vh;
}

.feature-card {
    grid-column: span 2; /* Asymmetric — breaks the uniform grid */
}
```

### Asymmetry and Overlap

```css
.hero-section {
    display: grid;
    grid-template-columns: 1.2fr 0.8fr;
    align-items: center;
    gap: var(--space-xl);
}

.hero-image {
    margin-right: -4rem; /* Overlap into adjacent space */
    z-index: 1;
}
```

### Responsive Breakpoints

```css
/* Page.razor.css */
.content-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: var(--space-md);
}

@media (min-width: 768px) {
    .content-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: var(--space-lg);
    }
}

@media (min-width: 1200px) {
    .content-grid {
        grid-template-columns: repeat(3, 1fr);
    }
}
```

### Layout Guidance

- **Unexpected layouts** — asymmetry, overlap, diagonal flow, grid-breaking elements.
- **Generous negative space OR controlled density** — both work when intentional.
- Use CSS Grid for two-dimensional layouts, Flexbox for one-dimensional alignment.

## Backgrounds & Visual Details

### Gradient Meshes

```css
.hero-bg {
    background:
        radial-gradient(ellipse at 20% 50%, rgba(233, 69, 96, 0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(26, 26, 46, 0.1) 0%, transparent 50%),
        var(--bg);
}
```

### Noise / Grain Overlay

```css
.textured {
    position: relative;
}

.textured::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 1;
}
```

### Glassmorphism

```css
.glass-card {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 1rem;
}
```

### Decorative Borders

```css
.accent-card {
    border-left: 4px solid var(--color-accent);
    padding-left: var(--space-md);
}

.gradient-border {
    border: 2px solid transparent;
    background-clip: padding-box;
    background-image: linear-gradient(var(--surface), var(--surface)),
                      linear-gradient(135deg, var(--color-accent), var(--color-primary));
    background-origin: border-box;
}
```

## Anti-Patterns (Avoid Unless Brand Guidelines Dictate Otherwise)

> **Note**: If the project has established brand guidelines or a corporate design system, those take precedence over the preferences below. These anti-patterns target greenfield projects and prototypes where you have creative freedom.

- **Avoid Inter/Roboto/Arial defaults** — these produce generic, forgettable pages when no brand font is specified.
- **No generic purple gradients on white** — this is the hallmark of AI-generated design.
- **No cookie-cutter layouts** — identical card grids with uniform spacing and no visual hierarchy.
- **No overused component patterns** — every project deserves a fresh aesthetic, not recycled templates.
- **No cliched color schemes** — commit to a palette that matches the project's context and tone.
- **No timid design** — half-measures (slight border-radius, faint shadows) produce mediocrity. Commit to bold or minimal, never in-between.

## Blazor-Specific Tips

### `::deep` for Consistent Design Tokens

Style child components from a layout or parent to enforce design consistency:

```css
/* MainLayout.razor.css */
.page-content ::deep h1 {
    font-family: var(--font-display);
    color: var(--fg);
}

.page-content ::deep .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 0.75rem;
}
```

### CSS Isolation + Design Tokens

Each component's `.razor.css` consumes global tokens but adds component-specific styling:

```css
/* Sidebar.razor.css */
.sidebar {
    background: var(--surface);
    border-right: 1px solid var(--border);
    padding: var(--space-lg);
    font-family: var(--font-body);
}

.sidebar-title {
    font-family: var(--font-display);
    font-size: 1.25rem;
    color: var(--color-accent);
}
```

### Dynamic Theming via Cascading Values

```csharp
// In a layout or root component
[CascadingParameter] public string Theme { get; set; } = "light";
```

Apply the theme attribute to the root element:

```razor
<div data-theme="@Theme" class="app-root">
    @Body
</div>
```

Components read from CSS variables — no per-component theme logic needed. Changing the `data-theme` attribute repaints everything through the cascade.
