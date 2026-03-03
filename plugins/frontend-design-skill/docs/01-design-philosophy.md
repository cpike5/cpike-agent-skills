# Design Philosophy: The Anti-Slop Manifesto

## The Problem with AI-Generated UI

Standard AI output converges on identical visual patterns:
- Centered content in a `max-width: 1200px` container
- Inter or system-ui font stack
- `border-radius: 0.5rem` on every surface
- Purple-to-blue gradients (#6366f1 → #3b82f6)
- Hero → Features (3 cards) → Pricing → Footer
- `box-shadow: 0 4px 6px rgba(0,0,0,0.1)` on everything
- "Lorem ipsum" placeholder text
- Identical spacing on all elements (1rem, 2rem)

This creates a **homogeneous aesthetic** instantly recognizable as machine-generated. Users deserve better.

## High-Agency Design

**High-Agency Design** means every visual choice is deliberate:

1. **Intentional constraints** — Choose a design language *before* writing markup. The constraint creates coherence.
2. **Typographic hierarchy as architecture** — Type size, weight, and spacing create the visual structure, not borders and boxes.
3. **Texture over flatness** — Real surfaces have grain, shadow depth, and imperfection. Flat colored rectangles read as placeholder.
4. **Rhythm over uniformity** — Spacing should create visual rhythm. Uniform padding makes everything feel like a wireframe.
5. **Motion with purpose** — Animation communicates state changes and spatial relationships. Gratuitous transitions feel cheap.

## The Decision Framework

Before writing code, answer these questions:

### 1. What is the emotional register?
- **Authoritative**: Swiss International, hard grids, monochrome
- **Energetic**: Neo-Brutalist, high saturation, thick borders
- **Sophisticated**: Glassmorphism, frosted layers, subtle motion
- **Refined**: Editorial/Luxury, serif typography, generous whitespace
- **Warm/Human**: Tactile/Analog, textures, muted palettes

### 2. What is the content density?
- **Data-heavy** → Grid-based layouts, compact type, clear hierarchy
- **Narrative** → Generous line-height, `ch`-based widths, editorial flow
- **Interactive** → Clear affordances, state feedback, spatial grouping

### 3. What distinguishes this from a template?
Every project needs at least one "unexpected" element:
- An asymmetric layout where symmetry is expected
- An oversized typographic element that commands attention
- A texture or pattern that adds tactile quality
- A motion detail that rewards attention
- A color accent used sparingly but memorably

## Core Principles

### Typography First
The typeface sets the tone before anything else renders. Choose it with the same care as a brand name. See `03-typography.md`.

### Color as Communication
Color isn't decoration — it encodes hierarchy, state, and meaning. Every color in the palette should have a job. See `07-color-systems.md`.

### Whitespace is Structure
Generous, intentional whitespace is the hallmark of professional design. Cramped layouts signal amateur work. Use spacing scales, not arbitrary values.

### Depth Through Layers
Real interfaces have depth. Use layered shadows, overlapping elements, and z-index stacking to create spatial hierarchy. See `05-surface-depth.md`.

### Motion as Feedback
Animation should answer "what just happened?" and "where should I look?" — not "look how fancy this is." See `06-motion-interactions.md`.
