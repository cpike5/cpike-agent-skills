# Anti-Patterns & Implementation Workflow

---

## The "Never" List (Slop Signals)

These patterns immediately identify output as generic AI-generated:

### Typography Slop
- **NO** Arial, Inter, Roboto, Open Sans, or system-ui as the only font
- **NO** uniform `font-size` across headings (all the same size or insufficient contrast)
- **NO** `line-height: 1.5` everywhere without variation by element role
- **NO** media queries for font-size changes — use `clamp()` instead

### Layout Slop
- **NO** "Hero → 3 Feature Cards → Pricing Table → Footer" without a unique structural twist
- **NO** `max-width: 1200px; margin: 0 auto` as the only layout container
- **NO** uniform grid of identical cards as the primary content pattern
- **NO** everything perfectly centered when asymmetry would be more interesting
- **NO** content that never breaks out of its container

### Surface Slop
- **NO** `border-radius: 8px` (or any single radius) on every element
- **NO** `box-shadow: 0 4px 6px rgba(0,0,0,0.1)` as the only shadow
- **NO** purple-to-blue gradients (`#6366f1` → `#3b82f6`)
- **NO** "Brand Blue" `#007bff` as the accent color
- **NO** pure `#000` on pure `#fff` without color temperature consideration

### Interaction Slop
- **NO** `transition: all 0.3s ease` — specify properties, tune duration, use custom easing
- **NO** hover effects that only change `opacity` or `background-color`
- **NO** animations without `prefers-reduced-motion` support

### Content Slop
- **NO** "Lorem ipsum" placeholder text — write context-appropriate copy
- **NO** "Click here" or "Learn more" as the only button labels
- **NO** stock photo placeholder URLs — use real or descriptive alt text

---

## Implementation Workflow

Follow this order. Do not skip steps.

### Step 1: Define CSS Variables

Before any component styles, establish the design system:

```css
@import url('https://fonts.googleapis.com/css2?family=...');

:root {
  /* Typography */
  --font-display: '...', sans-serif;
  --font-body: '...', serif;
  --font-mono: '...', monospace;

  /* Type Scale */
  --text-xs: clamp(...);
  --text-sm: clamp(...);
  --text-base: clamp(...);
  /* ... through --text-hero */

  /* Colors */
  --color-bg: ...;
  --color-surface: ...;
  --color-ink: ...;
  --color-accent: ...;
  /* ... full palette from 07-color-systems.md */

  /* Spacing Scale */
  --space-unit: 0.5rem;
  --space-xs: calc(var(--space-unit) * 1);
  /* ... through --space-3xl */

  /* Easing */
  --ease-out-expo: cubic-bezier(0.23, 1, 0.32, 1);
  --ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);

  /* Borders */
  --radius: ...;
  --border-width: ...;
}
```

### Step 2: Reset & Base Styles

```css
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
}

html {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

body {
  font-family: var(--font-body);
  font-size: var(--text-base);
  line-height: 1.6;
  color: var(--color-ink);
  background: var(--color-bg);
}

img, picture, video, canvas, svg {
  display: block;
  max-width: 100%;
}
```

### Step 3: Structural HTML

Write semantic markup before any styling:

```html
<body>
  <header>
    <nav>...</nav>
  </header>
  <main>
    <section aria-labelledby="hero-heading">...</section>
    <section aria-labelledby="features-heading">...</section>
    <aside>...</aside>
  </main>
  <footer>...</footer>
</body>
```

Use `<main>`, `<section>`, `<article>`, `<aside>`, `<header>`, `<nav>`, `<footer>`. Reach for `<div>` only when no semantic element fits.

### Step 4: The "Vibe" Layer

Apply the core aesthetic from the chosen design language:
- Font assignments (display, body, mono)
- Color application (backgrounds, text colors, borders)
- Spacing (section padding, component gaps)

### Step 5: Refinement (The "Unexpected" Layer)

Add the details that separate professional from generic:
- Noise/grain textures (if appropriate to the design language)
- Staggered entrance animations
- One intentional overlap or asymmetric element
- Custom hover/focus states
- Scroll-triggered reveals

---

## Self-Review Checklist

Before delivering, verify:

| Check | Question |
|-------|----------|
| Design language | Can you name the specific aesthetic system in use? |
| Typography | Are there at least 2 imported fonts (display + body)? |
| Type scale | Are headings using `clamp()` for fluid sizing? |
| Color | Does the palette avoid the "generic" colors listed above? |
| Layout | Is there at least one asymmetric or overlapping element? |
| Shadows | Are shadows layered (multiple values) or intentionally hard? |
| Motion | Is there custom easing (not `ease-in-out`)? |
| Motion a11y | Is `prefers-reduced-motion` handled? |
| Spacing | Are values from a consistent scale (not arbitrary numbers)? |
| Content | Is all copy context-appropriate (no Lorem ipsum)? |
| Semantic HTML | Are `<main>`, `<section>`, `<nav>`, etc. used correctly? |
| CSS variables | Is the `:root` block established before component styles? |
| Radius | Is `border-radius` intentional per design language, not uniform? |
