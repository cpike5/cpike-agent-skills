---
name: frontend-design
description: "Create distinctive, production-grade frontend interfaces that avoid generic AI aesthetics. Use this skill when the user asks to build web components, pages, or applications. Covers bold aesthetic direction selection, architectural typography (curated Google Fonts, fluid clamp-based sizing), advanced CSS layout (grid-template-areas, subgrid, intentional overlapping, negative margins), surface and depth (layered shadows, SVG noise textures, grain effects), motion and micro-interactions (staggered animations, custom cubic-bezier easing, scroll-triggered reveals), CSS custom property systems (color palettes, spacing scales, type scales), anti-convergence enforcement (banned defaults, forced variation triggers), and a pre-finalization litmus test. Invoke when: building HTML/CSS pages or components, creating landing pages, designing web layouts, implementing animations or transitions, choosing typography or color palettes for web projects, the user asks for visually distinctive or creative UI, the user wants to avoid generic or cookie-cutter design, or when generating any frontend HTML/CSS that should look professionally designed rather than AI-generated."
---

# Frontend Design Skill

Create distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

---

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work — the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

---

## Frontend Aesthetics Guidelines

- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics — unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors or gradients. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, and grain overlays.

---

## Anti-Convergence Enforcement

Before designing, roll a mental die. Force yourself away from your defaults by explicitly ruling out:
- The first color palette you thought of
- The first font pairing you thought of
- The first layout structure you thought of

If your design could plausibly appear on any other AI-generated UI, start over.

**Banned by default unless explicitly requested:**
- Gradient backgrounds, gradient text, gradient buttons, gradient anything
- Hero sections with centered heading + subheading + CTA button
- Card grids as the primary layout pattern
- Glassmorphism / frosted blur panels
- Purple, indigo, or teal as primary brand colors
- Rounded-everything (border-radius on every element)
- The "dark dashboard with glowing accent" pattern

**Forced variation triggers — pick one that fits and commit hard:**
- *Typographic-led*: The layout IS the typography. No decorative UI chrome. Text size contrast does all the visual work.
- *Editorial/print*: Newspaper columns, ruled lines, masthead-style headers, ink-black on newsprint or vice versa.
- *Utilitarian/brutalist*: No border-radius, visible structure, functional colors only, borders instead of shadows.
- *Monochrome + one*: Strictly black/white/grey plus exactly one non-neutral color used sparingly.
- *Dense/data-rich*: Small type, tight spacing, information density as an aesthetic choice.
- *Handcrafted*: Organic shapes, rough edges, imperfect geometry, texture-forward.
- *Period-specific*: Commit to a real design era (90s web, 70s print, Bauhaus, Swiss International) with accuracy.

**On gradients specifically:** Default to flat color, solid fills, and sharp contrast. If depth is needed, use shadows, borders, layering, or texture — not gradients. Gradients must be explicitly justified by the aesthetic direction, not used as a default polish move.

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

---

## Reference Documentation

Read the relevant docs based on your task for detailed CSS implementations:

### Technical Execution (read as needed)
- ${CLAUDE_PLUGIN_ROOT}/docs/03-typography.md — Font selection, fluid sizing with clamp(), type scales, pairing strategies, Google Fonts imports.
- ${CLAUDE_PLUGIN_ROOT}/docs/04-layout-spacing.md — Grid mastery, subgrid, breaking the box with overlaps, spacing scales, aspect-ratio, container queries.
- ${CLAUDE_PLUGIN_ROOT}/docs/05-surface-depth.md — Layered shadows, SVG noise/grain textures, lighting effects, border treatments.
- ${CLAUDE_PLUGIN_ROOT}/docs/06-motion-interactions.md — Staggered entrance animations, custom cubic-bezier easing, scroll-triggered animations, cursor interactions, hover transforms.
- ${CLAUDE_PLUGIN_ROOT}/docs/07-color-systems.md — CSS custom property palettes, contrast ratios, dark mode strategies, color as information, avoiding generic palettes.
