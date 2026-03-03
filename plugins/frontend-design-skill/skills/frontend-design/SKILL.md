---
name: frontend-design
description: "Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, or applications. Covers design language selection (Swiss International, Neo-Brutalist, Glassmorphism, Editorial/Luxury, Tactile/Analog), architectural typography (fluid type scales, curated Google Fonts, clamp-based sizing), advanced CSS layout (grid-template-areas, subgrid, intentional overlapping, negative margins), surface and depth (layered shadows, SVG noise textures, grain effects, lighting gradients), motion and micro-interactions (staggered animations, custom cubic-bezier easing, cursor interactions, hover transforms), CSS custom property systems (color palettes, spacing scales, type scales), and anti-pattern avoidance (generic AI aesthetics, default border-radius, placeholder copy, centered-stack layouts). Generates creative, polished code that avoids generic AI aesthetics. Invoke when: building HTML/CSS pages or components, creating landing pages, designing web layouts, implementing animations or transitions, choosing typography or color palettes for web projects, the user asks for visually distinctive or creative UI, the user wants to avoid generic or cookie-cutter design, or when generating any frontend HTML/CSS that should look professionally designed rather than AI-generated."
---

# Frontend Design Knowledge Base

You are building distinctive frontend interfaces. Read the relevant reference docs below based on what you're designing. **Always choose a design language first** — without an aesthetic anchor, output defaults to generic AI slop.

## Design Thinking

Before writing a single `<div>`, commit to a specific **Design Language**. Generic AI output defaults to centered divs, Inter font, `border-radius: 8px`, and purple-to-blue gradients. Reject these. Every pixel must feel intentional, not predicted. See `01-design-philosophy.md` for the full manifesto and `02-design-languages.md` for the five aesthetic systems.

## Quick Decision: Which Design Language?

| Audience / Tone | Design Language | Key Traits |
|-----------------|----------------|------------|
| Corporate, data-heavy, authoritative | Swiss International | Hard grids, massive type contrast, zero radii, red/black/white |
| Bold, playful, startup energy | Neo-Brutalist | Thick borders, 100% saturation, clunky shadows, oversized buttons |
| Premium SaaS, modern dashboard | Glassmorphism 2.0 | Frosted overlays, blur(20px), noise textures, thin white borders |
| Editorial, long-form, luxury brand | Editorial/Luxury | Serif headers, generous `ch` widths, asymmetric images, high-contrast whitespace |
| Indie, creative, artisanal | Tactile/Analog | Grainy gradients, paper textures, monospaced data, muted ink colors |

## Reference Documentation

Read the relevant docs based on your task:

### Always Read First
- ${CLAUDE_PLUGIN_ROOT}/docs/01-design-philosophy.md — The anti-slop manifesto. High-agency design principles and what makes AI output look generic.

### Design Languages (pick one, then read it)
- ${CLAUDE_PLUGIN_ROOT}/docs/02-design-languages.md — Complete CSS implementations for all five aesthetic systems with variables, typography, and layout patterns.

### Technical Execution (read as needed)
- ${CLAUDE_PLUGIN_ROOT}/docs/03-typography.md — Font selection, fluid sizing with clamp(), type scales, pairing strategies, Google Fonts imports.
- ${CLAUDE_PLUGIN_ROOT}/docs/04-layout-spacing.md — Grid mastery, subgrid, breaking the box with overlaps, spacing scales, aspect-ratio, container queries.
- ${CLAUDE_PLUGIN_ROOT}/docs/05-surface-depth.md — Layered shadows, SVG noise/grain textures, lighting gradients, glassmorphism overlays, border treatments.
- ${CLAUDE_PLUGIN_ROOT}/docs/06-motion-interactions.md — Staggered entrance animations, custom cubic-bezier easing, scroll-triggered animations, cursor interactions, hover transforms.
- ${CLAUDE_PLUGIN_ROOT}/docs/07-color-systems.md — CSS custom property palettes, contrast ratios, dark mode strategies, color as information, avoiding generic palettes.

### Quality Assurance
- ${CLAUDE_PLUGIN_ROOT}/docs/08-anti-patterns-workflow.md — The "never" list (slop signals), implementation workflow, self-review checklist.

## Critical Rules

1. **Choose a design language FIRST** — Before any markup. If the user hasn't specified one, infer from context (audience, tone, content type) and state your choice explicitly.
2. **Never use default system fonts** — No Arial, Inter, Roboto, or system-ui. Always import a curated font via `@import` from Google Fonts.
3. **No generic shadows** — Never use `box-shadow: 0 4px 6px rgba(0,0,0,0.1)`. Use layered shadows from `05-surface-depth.md`.
4. **No uniform border-radius** — `border-radius: 8px` on everything is a slop signal. Radius should be intentional: 0 for brutalist, large for pills, mixed for editorial.
5. **No placeholder copy** — Never use "Lorem ipsum." Write context-aware copy that fits the design's purpose and tone.
6. **Use clamp() for fluid typography** — No media query breakpoints for font sizes. Use `clamp(min, preferred, max)` for smooth scaling.
7. **Establish CSS variables first** — Define `:root` palette, spacing scale, and type scale before writing component styles.
8. **Semantic HTML first** — Use `<main>`, `<section>`, `<article>`, `<aside>`, `<header>`, `<nav>`, `<footer>` before reaching for `<div>`.
9. **Custom easing always** — Never use `ease-in-out`. Use `cubic-bezier(0.23, 1, 0.32, 1)` or similar for premium motion feel.
10. **Overlap intentionally** — AI usually fears overlapping elements. Use negative margins, `translate`, or absolute positioning to create depth and visual interest.
