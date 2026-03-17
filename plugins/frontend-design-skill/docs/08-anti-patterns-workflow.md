# Anti-Patterns & Implementation Workflow

---

## Banned by Default

These patterns are **banned unless the user explicitly requests them**:

- Gradient backgrounds, gradient text, gradient buttons, gradient anything
- Hero sections with centered heading + subheading + CTA button
- Card grids as the primary layout pattern
- Glassmorphism / frosted blur panels
- Purple, indigo, or teal as primary brand colors
- Rounded-everything (border-radius on every element)
- The "dark dashboard with glowing accent" pattern

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
- **NO** gradient backgrounds, gradient text, gradient buttons as a default polish move

### Interaction Slop
- **NO** `transition: all 0.3s ease` — specify properties, tune duration, use custom easing
- **NO** hover effects that only change `opacity` or `background-color`
- **NO** animations without `prefers-reduced-motion` support

### Content Slop
- **NO** "Lorem ipsum" placeholder text — write context-appropriate copy
- **NO** "Click here" or "Learn more" as the only button labels
- **NO** stock photo placeholder URLs — use real or descriptive alt text

---

## Forced Variation Triggers

When starting a design, pick one that fits and commit hard:

- *Typographic-led*: The layout IS the typography. No decorative UI chrome. Text size contrast does all the visual work.
- *Editorial/print*: Newspaper columns, ruled lines, masthead-style headers, ink-black on newsprint or vice versa.
- *Utilitarian/brutalist*: No border-radius, visible structure, functional colors only, borders instead of shadows.
- *Monochrome + one*: Strictly black/white/grey plus exactly one non-neutral color used sparingly.
- *Dense/data-rich*: Small type, tight spacing, information density as an aesthetic choice.
- *Handcrafted*: Organic shapes, rough edges, imperfect geometry, texture-forward.
- *Period-specific*: Commit to a real design era (90s web, 70s print, Bauhaus, Swiss International) with accuracy.

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

Apply the core aesthetic from the chosen direction:
- Font assignments (display, body, mono)
- Color application (backgrounds, text colors, borders)
- Spacing (section padding, component gaps)

### Step 5: Refinement (The "Unexpected" Layer)

Add the details that separate professional from generic:
- Noise/grain textures (if appropriate to the aesthetic)
- Staggered entrance animations
- One intentional overlap or asymmetric element
- Custom hover/focus states
- Scroll-triggered reveals

---

## Pre-Finalization Litmus Test

Answer each honestly before considering the design done:

1. **The swap test** — Could you swap the color scheme and fonts for a different project's and have it still look fine? If yes, the design isn't specific enough to this context.
2. **The screenshot test** — If someone posted a screenshot on Twitter/X, would anyone comment on the design itself — for any reason? If the answer is "probably not," it's too forgettable.
3. **The gradient audit** — Count the gradients. If the answer is more than zero and they weren't explicitly chosen for a reason you can articulate, remove them.
4. **The font gut-check** — Say the font name out loud. Is it one of the first five fonts you'd think of? If yes, go find something else.
5. **The layout test** — Cover all the content and look at just the layout skeleton. Does it have any structural personality, or is it just stacked rectangles?
6. **The "what era / what world" test** — Could you describe in one sentence what design world this belongs to? (e.g. "1970s technical manual", "brutalist Eastern European poster", "dense Bloomberg terminal"). If you can't, it doesn't have a clear enough point of view.
7. **The detail pass** — Zoom into one small area. Is there anything there that shows craft — a subtle rule, a considered spacing choice, an unexpected typographic detail? Or is it just filler?

**If you fail more than two:** Restart with a different aesthetic direction, not a revision of the current one. Iteration on a bad direction produces a polished bad direction.
