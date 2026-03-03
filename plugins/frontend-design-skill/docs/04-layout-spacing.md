# Layout & Spacing

Layout is the skeleton. Get it right and the design holds together; get it wrong and no amount of styling saves it.

---

## Grid Mastery

### Named Grid Areas

Use `grid-template-areas` for complex, readable layouts:

```css
.page-layout {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  grid-template-rows: auto 1fr auto;
  grid-template-areas:
    "header  header  header"
    "sidebar content aside"
    "footer  footer  footer";
  gap: var(--space-md);
  min-height: 100dvh;
}

.page-header  { grid-area: header; }
.page-sidebar { grid-area: sidebar; }
.page-content { grid-area: content; }
.page-aside   { grid-area: aside; }
.page-footer  { grid-area: footer; }
```

### Responsive Grid Without Media Queries

Use `auto-fill` / `auto-fit` with `minmax()`:

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(300px, 100%), 1fr));
  gap: var(--space-md);
}
```

The `min(300px, 100%)` prevents overflow on small screens.

### Asymmetric Grids

Symmetry is the default. Break it intentionally:

```css
/* Editorial two-column: text narrow, image wide */
.editorial-split {
  display: grid;
  grid-template-columns: 1fr 1.618fr; /* Golden ratio */
  gap: var(--space-lg);
  align-items: center;
}

/* Alternate direction on even sections */
.editorial-split:nth-child(even) {
  direction: rtl;
}
.editorial-split:nth-child(even) > * {
  direction: ltr;
}
```

---

## Subgrid

Use `display: subgrid` to align children across nested components:

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-md);
}

.card {
  display: grid;
  grid-template-rows: subgrid;
  grid-row: span 3; /* header, body, footer */
}
```

This ensures card headers, bodies, and footers align horizontally across the row.

---

## Breaking the Box

AI defaults to everything neatly contained. Professional design uses intentional overflow and overlap.

### Negative Margins (Full-Bleed from Container)

```css
.container {
  max-width: 65ch;
  margin-inline: auto;
  padding-inline: var(--space-md);
}

.full-bleed {
  width: 100vw;
  margin-inline: calc(50% - 50vw);
}

.breakout {
  width: calc(100% + var(--space-lg) * 2);
  margin-inline: calc(var(--space-lg) * -1);
}
```

### Overlapping Elements

```css
.overlap-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.overlap-image {
  grid-column: 1 / 2;
  grid-row: 1;
}

.overlap-text {
  grid-column: 1 / -1;
  grid-row: 1;
  align-self: end;
  padding: var(--space-lg);
  margin-left: 30%;
  background: var(--color-surface);
  z-index: 1;
  transform: translateY(20%);
}
```

### Pull Quotes / Offset Elements

```css
.pull-quote {
  font-size: var(--text-2xl);
  font-family: var(--font-display);
  font-style: italic;
  margin-left: -15%;
  padding-left: var(--space-md);
  border-left: 4px solid var(--color-accent);
}
```

---

## Spacing Scale

Use a geometric scale based on a space unit. Never use arbitrary values:

```css
:root {
  --space-unit: 0.5rem; /* 8px base */
  --space-2xs: calc(var(--space-unit) * 0.5);  /* 4px */
  --space-xs:  calc(var(--space-unit) * 1);     /* 8px */
  --space-sm:  calc(var(--space-unit) * 2);     /* 16px */
  --space-md:  calc(var(--space-unit) * 4);     /* 32px */
  --space-lg:  calc(var(--space-unit) * 8);     /* 64px */
  --space-xl:  calc(var(--space-unit) * 12);    /* 96px */
  --space-2xl: calc(var(--space-unit) * 16);    /* 128px */
  --space-3xl: calc(var(--space-unit) * 24);    /* 192px */
}
```

**Rules:**
- Component internal padding: `--space-sm` to `--space-md`
- Between components: `--space-md` to `--space-lg`
- Between sections: `--space-xl` to `--space-3xl`
- Never use the same spacing everywhere — variation creates rhythm

---

## Aspect Ratio

Use `aspect-ratio` for intentional media sizing:

```css
.hero-image    { aspect-ratio: 21/9; }
.card-image    { aspect-ratio: 16/9; }
.portrait      { aspect-ratio: 3/4; }
.square        { aspect-ratio: 1; }
.cinema        { aspect-ratio: 2.35/1; }

img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```

---

## Container Queries

Size components based on their container, not the viewport:

```css
.card-container {
  container-type: inline-size;
  container-name: card;
}

@container card (min-width: 400px) {
  .card {
    grid-template-columns: 200px 1fr;
  }
}

@container card (min-width: 600px) {
  .card {
    grid-template-columns: 250px 1fr;
    padding: var(--space-lg);
  }
}
```
