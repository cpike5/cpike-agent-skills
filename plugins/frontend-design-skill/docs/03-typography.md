# Typography as Architecture

Typography creates the visual structure of a page. It is not decoration — it is the primary design tool.

---

## Font Selection Rules

### Never Use
- Arial, Helvetica (generic, invisible)
- Inter, Roboto, Open Sans (overused, reads as "AI default")
- System-UI (surrenders all typographic control)

### Curated Google Fonts by Role

| Role | Fonts | Character |
|------|-------|-----------|
| Display (impact) | Syne, Bricolage Grotesque, Outfit, Bebas Neue | Bold, architectural |
| Display (editorial) | Playfair Display, Fraunces, DM Serif Display | Elegant, literary |
| Body (sans) | Space Grotesk, DM Sans, Libre Franklin, Work Sans | Clean, readable |
| Body (serif) | Source Serif 4, Lora, Crimson Pro, Newsreader | Warm, long-form |
| Mono/Data | Space Mono, JetBrains Mono, Fira Code, IBM Plex Mono | Technical, precise |
| Caption/UI | Libre Franklin, Work Sans, Outfit | Small, legible |

### Import Pattern

Always use `@import` at the top of the CSS file. Request only needed weights:

```css
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Grotesk:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap');
```

### Pairing Strategy

Pair fonts by **contrast, not similarity**:
- Geometric sans display + humanist serif body (e.g., Syne + Source Serif 4)
- High-contrast serif display + clean sans body (e.g., Playfair Display + DM Sans)
- Decorative display + monospace body (e.g., Fraunces + Space Mono) — for creative/indie sites

Never pair two sans-serifs or two serifs that are too similar. The pairing should create clear visual hierarchy.

---

## Fluid Type Scale with clamp()

### The Formula

```
font-size: clamp(minimum, preferred, maximum);
```

- **minimum**: Smallest readable size (mobile)
- **preferred**: Viewport-relative value (`vw` unit) that creates smooth scaling
- **maximum**: Largest size (desktop cap)

### Recommended Scale

```css
:root {
  --text-xs:   clamp(0.75rem,  0.7rem  + 0.25vw, 0.875rem);
  --text-sm:   clamp(0.875rem, 0.8rem  + 0.35vw, 1rem);
  --text-base: clamp(1rem,     0.9rem  + 0.45vw, 1.125rem);
  --text-lg:   clamp(1.125rem, 1rem    + 0.55vw, 1.375rem);
  --text-xl:   clamp(1.375rem, 1.1rem  + 1.2vw,  2rem);
  --text-2xl:  clamp(1.75rem,  1.2rem  + 2.4vw,  3rem);
  --text-3xl:  clamp(2.25rem,  1.5rem  + 3.5vw,  4.5rem);
  --text-4xl:  clamp(3rem,     2rem    + 5vw,    6rem);
  --text-hero: clamp(3.5rem,   2rem    + 8vw,    8rem);
}
```

### Usage

```css
h1 { font-size: var(--text-hero); }
h2 { font-size: var(--text-3xl); }
h3 { font-size: var(--text-2xl); }
h4 { font-size: var(--text-xl); }
p  { font-size: var(--text-base); }
small, .caption { font-size: var(--text-sm); }
```

---

## Line Height and Measure

### Line Height by Role

| Element | line-height | Reason |
|---------|-------------|--------|
| Display/hero text | 0.9 – 1.0 | Tight for impact |
| Headings (h2-h4) | 1.1 – 1.2 | Compact but readable |
| Body text | 1.5 – 1.7 | Comfortable reading |
| UI/labels | 1.2 – 1.3 | Compact for interfaces |

### Measure (Line Length)

Optimal reading measure is **45-75 characters**:

```css
.prose {
  max-width: 65ch;
}
```

Never let body text run full-width on desktop. `ch` units scale naturally with font size.

---

## Letter Spacing

| Context | letter-spacing | Example |
|---------|---------------|---------|
| Uppercase headings | 0.05em – 0.1em | Section labels, nav items |
| Small caps / captions | 0.08em – 0.15em | Bylines, metadata |
| Large display text | -0.02em – -0.04em | Hero headlines (optical tightening) |
| Body text | 0 (default) | Never adjust body letter-spacing |

```css
.section-label {
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-muted);
}

.hero-title {
  font-size: var(--text-hero);
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 0.95;
}
```

---

## Vertical Rhythm

Use a spacing scale tied to line-height for consistent vertical rhythm:

```css
/* Heading spacing: more above, less below */
h1, h2, h3, h4 {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}

/* Paragraphs: consistent gap */
p + p {
  margin-top: 1em;
}

/* Section breaks: generous */
section + section {
  margin-top: var(--space-xl);
}
```

Headings should feel "attached" to the content they introduce (closer below, further above).
