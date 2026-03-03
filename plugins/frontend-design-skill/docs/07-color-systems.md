# Color Systems

Color isn't decoration — it encodes hierarchy, state, and meaning. Every color in the palette should have a job.

---

## CSS Custom Property Structure

### Full Palette Template

```css
:root {
  /* Surfaces */
  --color-bg:          #faf8f5;  /* Page background */
  --color-surface:     #ffffff;  /* Card/panel background */
  --color-surface-alt: #f0ece6;  /* Alternate surface (zebra, sidebar) */

  /* Text */
  --color-ink:         #1a1a1a;  /* Primary text */
  --color-ink-light:   #555555;  /* Secondary text */
  --color-muted:       #8c8580;  /* Tertiary/disabled text */

  /* Brand / Accent */
  --color-accent:      #c45d3e;  /* Primary action, links */
  --color-accent-hover:#a84d33;  /* Hover state */
  --color-accent-soft: rgba(196, 93, 62, 0.12); /* Backgrounds, tags */

  /* Semantic */
  --color-success:     #2d8659;
  --color-warning:     #c4860e;
  --color-error:       #c43e3e;
  --color-info:        #3e7cc4;

  /* Structural */
  --color-border:      #d4cdc5;  /* Default borders */
  --color-rule:        #e0dbd5;  /* Horizontal rules, dividers */
  --color-focus:       var(--color-accent);
}
```

### Naming Convention

| Prefix | Purpose | Examples |
|--------|---------|---------|
| `--color-bg` | Page-level backgrounds | `--color-bg`, `--color-bg-alt` |
| `--color-surface` | Component backgrounds | `--color-surface`, `--color-surface-hover` |
| `--color-ink` | Text colors | `--color-ink`, `--color-ink-light`, `--color-muted` |
| `--color-accent` | Brand/interactive | `--color-accent`, `--color-accent-hover` |
| `--color-{state}` | Semantic states | `--color-success`, `--color-error` |
| `--color-border` | Lines and borders | `--color-border`, `--color-rule` |

---

## Contrast Requirements

### WCAG 2.1 Minimums

| Usage | Minimum Ratio | Level |
|-------|---------------|-------|
| Body text | 4.5:1 | AA |
| Large text (≥24px or ≥18.66px bold) | 3:1 | AA |
| UI components (borders, icons) | 3:1 | AA |
| Decorative elements | No requirement | — |

### Quick Contrast Pairs

| Background | Minimum text color | Ratio |
|------------|-------------------|-------|
| `#ffffff` | `#595959` | 7:1 |
| `#faf8f5` | `#5c5550` | 7:1 |
| `#1a1a1a` | `#a0a0a0` | 7:1 |
| `#0f0f1a` | `#9999a8` | 7:1 |

Test with browser DevTools: Inspect element → color picker → contrast ratio indicator.

---

## Dark Mode Strategy

### CSS Custom Properties with `prefers-color-scheme`

```css
:root {
  --color-bg: #faf8f5;
  --color-surface: #ffffff;
  --color-ink: #1a1a1a;
  --color-muted: #8c8580;
  --color-border: #d4cdc5;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #121212;
    --color-surface: #1e1e1e;
    --color-ink: #e8e8e8;
    --color-muted: #888888;
    --color-border: #333333;
  }
}
```

### Manual Toggle

```css
[data-theme="dark"] {
  --color-bg: #121212;
  --color-surface: #1e1e1e;
  --color-ink: #e8e8e8;
  /* ... */
}
```

### Dark Mode Pitfalls

- Don't invert colors mechanically — dark mode needs independent tuning
- Reduce shadow intensity (shadows on dark backgrounds look wrong at full strength)
- Desaturate accent colors slightly — vivid colors on dark backgrounds cause eye strain
- Use `#121212` or `#1a1a1a`, never `#000000` — pure black is too harsh

---

## Color as Information

### Hierarchy Through Saturation

Use saturation levels to encode importance:
- **Primary actions**: Full saturation accent color
- **Secondary actions**: Muted/desaturated version
- **Disabled**: Even more desaturated, reduced opacity
- **Backgrounds**: Accent at 5-12% opacity

### Status Colors Pattern

```css
.badge {
  padding: 0.25em 0.75em;
  border-radius: 2px;
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge--success {
  color: var(--color-success);
  background: rgba(45, 134, 89, 0.1);
}

.badge--error {
  color: var(--color-error);
  background: rgba(196, 62, 62, 0.1);
}

.badge--warning {
  color: var(--color-warning);
  background: rgba(196, 134, 14, 0.1);
}
```

---

## Palettes to Avoid

These colors scream "AI-generated":

| Signal | Why It's Generic | Alternative |
|--------|-----------------|-------------|
| `#007bff` (Bootstrap blue) | Default framework color | Choose a blue with character: `#2563eb`, `#1e40af`, `#0284c7` |
| `#6366f1` → `#3b82f6` gradient | Every AI chat app | Use a single solid accent or a gradient from the chosen palette |
| `#f3f4f6` (gray-100) | Tailwind default | Warm it: `#f5f0eb` or cool it: `#edf2f7` — pick a temperature |
| `#10b981` (emerald) | AI-favored green | Richer: `#059669` or warmer: `#2d8659` |
| Pure `#000000` on `#ffffff` | Maximum but harsh contrast | `#1a1a1a` on `#faf8f5` for warmth, or `#0a0a0a` on `#f8f8f8` for cool |

---

## Integration with Huemint

For algorithmically generated palettes that respect color relationships, use the huemint-skill to generate palettes via the Huemint API, then map the results into the CSS variable structure above.
