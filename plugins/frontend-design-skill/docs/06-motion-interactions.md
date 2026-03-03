# Motion & Micro-interactions

Animation should answer "what just happened?" and "where should I look?" — never "look how fancy this is."

---

## Custom Easing

### The Problem

`ease-in-out` is the AI default. It feels sluggish and predictable.

### Premium Easing Curves

```css
:root {
  /* Snappy — elements feel responsive */
  --ease-out-expo: cubic-bezier(0.23, 1, 0.32, 1);

  /* Smooth — fluid state changes */
  --ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);

  /* Bouncy — playful, attention-grabbing */
  --ease-out-back: cubic-bezier(0.34, 1.56, 0.64, 1);

  /* Dramatic — large movements */
  --ease-in-out-circ: cubic-bezier(0.85, 0, 0.15, 1);

  /* Spring-like — organic feel */
  --ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
```

### Duration Guidelines

| Action | Duration | Easing |
|--------|----------|--------|
| Button hover/press | 100-150ms | `--ease-out-expo` |
| Tooltip appear | 150-200ms | `--ease-out-quart` |
| Card expand | 250-350ms | `--ease-out-expo` |
| Page section reveal | 400-600ms | `--ease-out-quart` |
| Modal open | 300-400ms | `--ease-out-back` |
| Modal close | 200-250ms | `--ease-out-expo` |
| Page transition | 400-600ms | `--ease-in-out-circ` |

**Rule of thumb**: Exits should be faster than entrances.

---

## Staggered Entrance Animations

Animate a list of items with progressive delay using CSS custom properties:

```css
@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stagger-item {
  opacity: 0;
  animation: slide-up 0.5s var(--ease-out-expo) forwards;
  animation-delay: calc(var(--i, 0) * 80ms);
}
```

```html
<div class="stagger-item" style="--i: 0">First</div>
<div class="stagger-item" style="--i: 1">Second</div>
<div class="stagger-item" style="--i: 2">Third</div>
<div class="stagger-item" style="--i: 3">Fourth</div>
```

### Variant: Stagger with Scale

```css
@keyframes pop-in {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
```

---

## Hover & Focus States

### Card Lift

```css
.card {
  transition: transform 200ms var(--ease-out-expo),
              box-shadow 200ms var(--ease-out-expo);
}

.card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 4px 4px rgba(0, 0, 0, 0.06),
    0 8px 8px rgba(0, 0, 0, 0.06),
    0 16px 16px rgba(0, 0, 0, 0.06);
}
```

### Button Press (Brutalist)

```css
.btn {
  border: 3px solid #000;
  box-shadow: 4px 4px 0 #000;
  transition: transform 100ms, box-shadow 100ms;
}

.btn:hover {
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0 #000;
}

.btn:active {
  transform: translate(4px, 4px);
  box-shadow: 0 0 0 #000;
}
```

### Link Underline Reveal

```css
.link {
  text-decoration: none;
  background-image: linear-gradient(currentColor, currentColor);
  background-size: 0% 2px;
  background-position: 0 100%;
  background-repeat: no-repeat;
  transition: background-size 300ms var(--ease-out-expo);
}

.link:hover {
  background-size: 100% 2px;
}
```

### Focus Ring (Accessible)

```css
:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 3px;
  border-radius: 2px;
}
```

---

## Scroll-Triggered Animations

### Using `@keyframes` + Intersection Observer (Vanilla)

```css
.reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s var(--ease-out-quart),
              transform 0.6s var(--ease-out-quart);
}

.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}
```

```javascript
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.15 }
);

document.querySelectorAll('.reveal').forEach((el) => observer.observe(el));
```

### CSS-Only with `animation-timeline` (Progressive Enhancement)

```css
@keyframes fade-slide-up {
  from { opacity: 0; transform: translateY(30px); }
  to   { opacity: 1; transform: translateY(0); }
}

.scroll-reveal {
  animation: fade-slide-up linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 40%;
}
```

---

## Motion Preferences

Always respect `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

Place this at the end of your stylesheet. Non-negotiable for accessibility.

---

## Cursor Interactions (Creative Sites Only)

For portfolio/creative sites, custom cursor effects add personality:

```css
/* Enlarge cursor on interactive elements */
.interactive-zone {
  cursor: none;
}

.custom-cursor {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid var(--color-ink);
  position: fixed;
  pointer-events: none;
  z-index: 9999;
  transition: width 200ms var(--ease-out-expo),
              height 200ms var(--ease-out-expo),
              border-color 200ms;
  transform: translate(-50%, -50%);
}

.interactive-zone:hover ~ .custom-cursor {
  width: 50px;
  height: 50px;
  border-color: var(--color-accent);
}
```

Only use custom cursors when the site's creative context justifies it (portfolios, studios, art). Never on SaaS, dashboards, or utility interfaces.
