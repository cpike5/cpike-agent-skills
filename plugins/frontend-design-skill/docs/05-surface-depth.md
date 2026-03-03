# Surface & Depth

Flat colored rectangles read as wireframes. Real interfaces have texture, shadow depth, and material quality.

---

## Layered Shadows

### The Problem

Generic AI shadow: `box-shadow: 0 4px 6px rgba(0,0,0,0.1)` — flat, unrealistic, and identical everywhere.

### Realistic Layered Shadows

Multiple shadows at different scales simulate real light behavior:

```css
/* Elevation Level 1 — Subtle lift */
.shadow-sm {
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.06),
    0 1px 3px rgba(0, 0, 0, 0.10);
}

/* Elevation Level 2 — Card */
.shadow-md {
  box-shadow:
    0 1px 1px rgba(0, 0, 0, 0.08),
    0 2px 2px rgba(0, 0, 0, 0.08),
    0 4px 4px rgba(0, 0, 0, 0.08),
    0 8px 8px rgba(0, 0, 0, 0.08);
}

/* Elevation Level 3 — Floating */
.shadow-lg {
  box-shadow:
    0 1px 1px rgba(0, 0, 0, 0.06),
    0 2px 2px rgba(0, 0, 0, 0.06),
    0 4px 4px rgba(0, 0, 0, 0.06),
    0 8px 8px rgba(0, 0, 0, 0.06),
    0 16px 16px rgba(0, 0, 0, 0.06);
}

/* Elevation Level 4 — Modal/Overlay */
.shadow-xl {
  box-shadow:
    0 1px 1px rgba(0, 0, 0, 0.05),
    0 2px 2px rgba(0, 0, 0, 0.05),
    0 4px 4px rgba(0, 0, 0, 0.05),
    0 8px 8px rgba(0, 0, 0, 0.05),
    0 16px 16px rgba(0, 0, 0, 0.05),
    0 32px 32px rgba(0, 0, 0, 0.05);
}
```

### Colored Shadows

Match shadow hue to the element's background for realism:

```css
.cta-button {
  background: #e63946;
  box-shadow:
    0 2px 4px rgba(230, 57, 70, 0.3),
    0 8px 16px rgba(230, 57, 70, 0.2);
}
```

### Hard Shadows (Neo-Brutalist)

Zero blur, solid offset:

```css
.brutalist-card {
  border: 3px solid #000;
  box-shadow: 6px 6px 0 #000;
}

.brutalist-card:hover {
  transform: translate(3px, 3px);
  box-shadow: 3px 3px 0 #000;
}

.brutalist-card:active {
  transform: translate(6px, 6px);
  box-shadow: 0 0 0 #000;
}
```

---

## Noise & Grain Textures

### Inline SVG Noise (No External Files)

```css
.grain-overlay::after {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  border-radius: inherit;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E");
  mix-blend-mode: overlay;
}
```

**Tuning:**
- `baseFrequency` controls grain size: 0.5 = coarse, 0.9 = fine
- `opacity` controls intensity: 0.03 = subtle, 0.10 = pronounced
- `mix-blend-mode`: `overlay` for light surfaces, `multiply` for dark

### Full-Page Grain

```css
body::after {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
  background: url("data:image/svg+xml,..."); /* same SVG as above */
  opacity: 0.06;
  mix-blend-mode: multiply;
}
```

---

## Gradient Techniques

### Lighting Gradients (Not Fills)

Gradients should simulate light direction, not fill backgrounds:

```css
/* Subtle top-light effect */
.card {
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.08) 0%,
    transparent 40%
  ), var(--color-surface);
}

/* Radial "spotlight" */
.hero {
  background: radial-gradient(
    ellipse at 30% 20%,
    rgba(255, 255, 255, 0.1) 0%,
    transparent 60%
  ), var(--color-bg);
}
```

### Ambient Background Blobs (Glassmorphism)

```css
.ambient-bg {
  position: fixed;
  inset: 0;
  z-index: -1;
  background: var(--color-bg);
  overflow: hidden;
}

.ambient-bg::before {
  content: '';
  position: absolute;
  width: 60vmax;
  height: 60vmax;
  top: -20%;
  left: -10%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(110, 231, 183, 0.15), transparent 70%);
  filter: blur(80px);
}

.ambient-bg::after {
  content: '';
  position: absolute;
  width: 50vmax;
  height: 50vmax;
  bottom: -30%;
  right: -10%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.12), transparent 70%);
  filter: blur(80px);
}
```

---

## Border Treatments

### Beyond `border: 1px solid #ddd`

```css
/* Gradient border */
.gradient-border {
  border: 1px solid transparent;
  background:
    linear-gradient(var(--color-surface), var(--color-surface)) padding-box,
    linear-gradient(135deg, var(--color-accent), transparent) border-box;
}

/* Top accent border */
.accent-top {
  border-top: 3px solid var(--color-accent);
}

/* Inset border (no layout shift) */
.inset-border {
  box-shadow: inset 0 0 0 1px var(--color-border);
}
```

---

## Glassmorphism Checklist

When building glass-style interfaces:

1. Dark background (`#0f0f1a` or similar) — glass needs contrast to read
2. `backdrop-filter: blur(20px) saturate(180%)`
3. Background: `rgba(255, 255, 255, 0.05)` — very low opacity
4. Border: `1px solid rgba(255, 255, 255, 0.1)`
5. Noise texture overlay at 3% opacity
6. Ambient gradient blobs behind the glass panels
7. Light text (`#e8e8f0`), never pure white
8. Glow on interactive elements: `box-shadow: 0 0 20px rgba(accent, 0.15)`
