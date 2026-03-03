# Design Languages

Select **one** design language before writing any markup. Each system below includes a complete CSS variable foundation and key structural patterns.

---

## Swiss International

Hard grids, massive typographic contrast, zero decoration. Influenced by the International Typographic Style (Müller-Brockmann, Vignelli).

```css
:root {
  /* Palette */
  --color-primary: #e60012;
  --color-surface: #ffffff;
  --color-ink: #0a0a0a;
  --color-muted: #6b6b6b;
  --color-rule: #0a0a0a;

  /* Typography */
  --font-display: 'Syne', sans-serif;
  --font-body: 'Space Grotesk', sans-serif;
  --font-mono: 'Space Mono', monospace;
  --type-scale-ratio: 1.414; /* Augmented Fourth */

  /* Spacing (8px base) */
  --space-unit: 0.5rem;
  --space-xs: calc(var(--space-unit) * 1);   /* 8px */
  --space-sm: calc(var(--space-unit) * 2);   /* 16px */
  --space-md: calc(var(--space-unit) * 4);   /* 32px */
  --space-lg: calc(var(--space-unit) * 8);   /* 64px */
  --space-xl: calc(var(--space-unit) * 16);  /* 128px */

  /* Borders */
  --radius: 0;
  --border-width: 2px;
}
```

**Key patterns:**
- Grid: 12-column with `grid-template-columns: repeat(12, 1fr)` and explicit `grid-template-areas`
- Headlines: `font-size: clamp(3rem, 10vw, 8rem)` with `font-weight: 900` and `text-transform: uppercase`
- Rules: Thick horizontal `<hr>` elements as structural dividers (`border-top: 3px solid var(--color-ink)`)
- Color: Monochrome with a single red accent — never more than 10% of the page

---

## Neo-Brutalist

High contrast, maximum energy. Borders as architecture. Influenced by web brutalism and 90s rave poster design.

```css
:root {
  /* Palette */
  --color-primary: #ff5722;
  --color-secondary: #ffeb3b;
  --color-accent: #00e676;
  --color-surface: #fafafa;
  --color-ink: #000000;

  /* Typography */
  --font-display: 'Bricolage Grotesque', sans-serif;
  --font-body: 'DM Sans', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Spacing */
  --space-unit: 0.5rem;
  --space-xs: calc(var(--space-unit) * 1);
  --space-sm: calc(var(--space-unit) * 2);
  --space-md: calc(var(--space-unit) * 4);
  --space-lg: calc(var(--space-unit) * 8);
  --space-xl: calc(var(--space-unit) * 12);

  /* Borders */
  --radius: 0;
  --border-width: 3px;
  --border-color: #000000;
  --shadow-offset: 6px;
}
```

**Key patterns:**
- Borders: `border: 3px solid #000` on everything — cards, buttons, inputs
- Shadows: Hard offset, no blur — `box-shadow: var(--shadow-offset) var(--shadow-offset) 0 #000`
- Colors: 100% saturation, no transparency — backgrounds are solid blocks of color
- Buttons: Oversized (`padding: 1rem 2rem`), `text-transform: uppercase`, thick borders
- Hover: Translate + shadow removal — `transform: translate(3px, 3px); box-shadow: 0 0 0 #000`
- Layout: Asymmetric, elements can break grid alignment intentionally

---

## Glassmorphism 2.0

Frosted layers, depth through translucency. Modern and premium without being fragile.

```css
:root {
  /* Palette */
  --color-bg: #0f0f1a;
  --color-surface: rgba(255, 255, 255, 0.05);
  --color-surface-hover: rgba(255, 255, 255, 0.08);
  --color-border: rgba(255, 255, 255, 0.12);
  --color-ink: #e8e8f0;
  --color-muted: rgba(255, 255, 255, 0.5);
  --color-accent: #6ee7b7;

  /* Typography */
  --font-display: 'Outfit', sans-serif;
  --font-body: 'Outfit', sans-serif;
  --font-mono: 'Fira Code', monospace;

  /* Glass properties */
  --glass-blur: 20px;
  --glass-saturation: 180%;
  --glass-border: 1px solid var(--color-border);
  --glass-noise-opacity: 0.03;

  /* Spacing */
  --space-unit: 0.5rem;
  --space-sm: calc(var(--space-unit) * 2);
  --space-md: calc(var(--space-unit) * 4);
  --space-lg: calc(var(--space-unit) * 8);

  /* Borders */
  --radius-sm: 12px;
  --radius-md: 20px;
  --radius-lg: 28px;
}

.glass-panel {
  background: var(--color-surface);
  backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-saturation));
  -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-saturation));
  border: var(--glass-border);
  border-radius: var(--radius-md);
  position: relative;
}

/* Noise texture overlay */
.glass-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
  pointer-events: none;
}
```

**Key patterns:**
- Background: Dark base (`#0f0f1a`) with ambient gradient blobs (radial gradients at 30% opacity positioned off-center)
- Cards: `.glass-panel` class with noise overlay
- Borders: Thin (`1px`), white at 10-15% opacity
- Glow effects: `box-shadow: 0 0 30px rgba(accent, 0.15)` on interactive elements
- Typography: Light weight (`300-400`) on dark backgrounds, high contrast for headings

---

## Editorial / Luxury

Serif-driven, generous whitespace, asymmetric composition. Influenced by magazine layouts and luxury brand websites.

```css
:root {
  /* Palette */
  --color-surface: #faf8f5;
  --color-ink: #1a1a1a;
  --color-muted: #8c8580;
  --color-accent: #c5a572;
  --color-rule: #d4cdc5;

  /* Typography */
  --font-display: 'Playfair Display', serif;
  --font-body: 'Source Serif 4', serif;
  --font-caption: 'Libre Franklin', sans-serif;
  --font-mono: 'IBM Plex Mono', monospace;

  /* Spacing */
  --space-unit: 0.5rem;
  --space-sm: calc(var(--space-unit) * 3);   /* 24px */
  --space-md: calc(var(--space-unit) * 6);   /* 48px */
  --space-lg: calc(var(--space-unit) * 12);  /* 96px */
  --space-xl: calc(var(--space-unit) * 20);  /* 160px */

  /* Borders */
  --radius: 0;
  --border-width: 1px;
}
```

**Key patterns:**
- Body text: `max-width: 65ch` for optimal readability, `line-height: 1.7`
- Headlines: `font-size: clamp(2.5rem, 6vw, 5rem)` in display serif, `font-weight: 700`, sometimes italic
- Layout: Asymmetric 2-column — text on one side, full-bleed image on the other, using `grid-template-columns: 1fr 1.2fr`
- Images: `aspect-ratio: 3/4` or `16/9`, full-bleed (negative margins to escape container)
- Captions: Sans-serif, small caps (`font-variant: small-caps`), tracked out (`letter-spacing: 0.1em`)
- Dividers: Thin rules (`border-top: 1px solid var(--color-rule)`) with generous vertical padding

---

## Tactile / Analog

Grainy, warm, handmade feel. Influenced by letterpress, risograph, and analog photography.

```css
:root {
  /* Palette — muted, "ink-on-paper" */
  --color-surface: #f2ede8;
  --color-ink: #2c2825;
  --color-muted: #8a7e75;
  --color-accent: #c45d3e;
  --color-accent-alt: #3d6b5e;
  --color-paper: #e8e0d8;

  /* Typography */
  --font-display: 'Fraunces', serif;
  --font-body: 'Lora', serif;
  --font-data: 'Space Mono', monospace;
  --font-ui: 'Work Sans', sans-serif;

  /* Spacing */
  --space-unit: 0.5rem;
  --space-sm: calc(var(--space-unit) * 2);
  --space-md: calc(var(--space-unit) * 4);
  --space-lg: calc(var(--space-unit) * 8);
  --space-xl: calc(var(--space-unit) * 14);

  /* Borders */
  --radius-sm: 2px;
  --radius-md: 4px;
}

/* Grain overlay */
body::after {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='grain'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23grain)' opacity='0.08'/%3E%3C/svg%3E");
  mix-blend-mode: multiply;
}
```

**Key patterns:**
- Textures: SVG noise grain overlay on `body::after`, paper-colored backgrounds
- Data: Monospaced font for numbers, statistics, dates — `font-family: var(--font-data)`
- Colors: Desaturated, warm-shifted. No pure black or white — use `#2c2825` and `#f2ede8`
- Borders: Minimal or absent. Separate content with whitespace and subtle background color shifts
- Images: Slightly desaturated (`filter: saturate(0.85) contrast(1.05)`), optional duotone effect
- Shadows: Warm-tinted — `box-shadow: 0 2px 8px rgba(44, 40, 37, 0.12)`
