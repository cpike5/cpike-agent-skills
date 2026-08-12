---
name: frontend-design
description: "Create distinctive, production-grade frontend interfaces that avoid generic AI aesthetics. Use this skill when the user asks to build web components, pages, or applications. Covers bold aesthetic direction selection, architectural typography (curated Google Fonts, fluid clamp-based sizing), advanced CSS layout (grid-template-areas, subgrid, intentional overlapping, negative margins), surface and depth (layered shadows, SVG noise textures, grain effects), motion and micro-interactions (staggered animations, custom cubic-bezier easing, scroll-triggered reveals), CSS custom property systems (color palettes, spacing scales, type scales), and anti-convergence enforcement (banned defaults, forced variation triggers). Invoke when: building HTML/CSS pages or components, creating landing pages, designing web layouts, implementing animations or transitions, choosing typography or color palettes for web projects, the user asks for visually distinctive or creative UI, the user wants to avoid generic or cookie-cutter design, or when generating any frontend HTML/CSS that should look professionally designed rather than AI-generated."
---

# Frontend Design Skill

Create distinctive, production-grade frontend interfaces with a clear aesthetic point of view. Implement real working code with exceptional attention to aesthetic detail.

## Design Thinking

Before coding, commit to a clear aesthetic direction:

- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick a direction and execute it with precision — brutally minimal, maximalist, retro-futuristic, editorial, luxury, brutalist, art deco, industrial, and many more. Bold maximalism and refined minimalism both work; the key is intentionality, not intensity.
- **Constraints**: Framework, performance, accessibility.
- **Differentiation**: What's the one thing someone will remember?

When the brief is open-ended, consider proposing 3–4 distinct visual directions (background/accent colors, typeface, one-line rationale) and letting the user pick before building.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is production-grade, visually striking, and cohesive.

## Aesthetics Guidelines

- **Typography**: Distinctive, characterful font choices — avoid generic fonts like Arial and Inter. Pair a display font with a refined body font.
- **Color**: Commit to a cohesive palette in CSS variables. Dominant colors with sharp accents beat timid, evenly-distributed palettes.
- **Motion**: High-impact moments over scattered effects — one well-orchestrated page load with staggered reveals beats many micro-interactions. CSS-only for plain HTML; Motion library for React.
- **Composition**: Unexpected layouts — asymmetry, overlap, grid-breaking elements, generous negative space OR controlled density.
- **Depth**: Atmosphere through noise textures, layered shadows, decorative borders, and grain — not flat solid fills or default gradients.

Avoid the generic-AI defaults — gradient-everything, centered hero + CTA, card-grid layouts, glassmorphism, purple/indigo primaries, rounded-everything. The full banned-defaults list and forced-variation triggers are in doc 08; when a design drifts generic, pick one variation trigger and commit hard.

## Reference Documentation

- ${CLAUDE_PLUGIN_ROOT}/docs/01-design-philosophy.md — Anti-convergence philosophy, intentional design principles, the decision framework.
- ${CLAUDE_PLUGIN_ROOT}/docs/02-design-languages.md — Five worked aesthetic systems (Swiss International, editorial, brutalist, etc.) with complete CSS variable foundations.
- ${CLAUDE_PLUGIN_ROOT}/docs/03-typography.md — Font selection, fluid sizing with clamp(), type scales, pairing strategies, Google Fonts imports.
- ${CLAUDE_PLUGIN_ROOT}/docs/04-layout-spacing.md — Grid mastery, subgrid, breaking the box with overlaps, spacing scales, aspect-ratio, container queries.
- ${CLAUDE_PLUGIN_ROOT}/docs/05-surface-depth.md — Layered shadows, SVG noise/grain textures, lighting effects, border treatments.
- ${CLAUDE_PLUGIN_ROOT}/docs/06-motion-interactions.md — Staggered entrance animations, custom cubic-bezier easing, scroll-triggered animations, cursor interactions, hover transforms.
- ${CLAUDE_PLUGIN_ROOT}/docs/07-color-systems.md — CSS custom property palettes, contrast ratios, dark mode strategies, color as information, avoiding generic palettes.
- ${CLAUDE_PLUGIN_ROOT}/docs/08-anti-patterns-workflow.md — Banned defaults, forced variation triggers, finalization checks, implementation workflow.
