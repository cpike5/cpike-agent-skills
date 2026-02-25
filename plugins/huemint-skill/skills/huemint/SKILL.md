---
name: huemint
description: >
  Use this skill when working with the Huemint API, generating color palettes,
  building adjacency matrices, using color locking, creating HTML/CSS prototypes
  that showcase color palettes, or translating natural language color requests
  into Huemint API parameters. Invoke when: calling the Huemint color API,
  designing adjacency matrices for color relationships, locking brand colors
  in palette generation, choosing between transformer/diffusion/random modes,
  iterating on palette refinement, converting mood/style keywords to API parameters,
  or building HTML/CSS color showcases.
---

# Huemint Skill

## Quick Reference — Mode Selection

| Scenario | Mode | Max Colors |
|----------|------|------------|
| Production palettes | `transformer` | 12 |
| Small artistic palettes (≤5 colors) | `diffusion` | 5 |
| Quick exploration | `random` | 12 |

## Documentation

### Always Read First
- `${CLAUDE_PLUGIN_ROOT}/docs/01-api-basics.md` — Endpoint, parameters, request/response format, examples, error handling

### Core Concepts
- `${CLAUDE_PLUGIN_ROOT}/docs/02-adjacency-matrices.md` — CIE Delta-E scale, matrix rules, worked examples
- `${CLAUDE_PLUGIN_ROOT}/docs/03-color-locking.md` — Lock/unlock syntax, brand workflows, dark mode locking
- `${CLAUDE_PLUGIN_ROOT}/docs/04-modes-temperature.md` — Mode comparison, temperature ranges, recipes

### Workflow & Templates
- `${CLAUDE_PLUGIN_ROOT}/docs/05-palette-refinement.md` — 3-round explore→refine→polish workflow, score interpretation
- `${CLAUDE_PLUGIN_ROOT}/docs/06-adjacency-templates.md` — Copy-paste matrices for common scenarios (3–6 colors)
- `${CLAUDE_PLUGIN_ROOT}/docs/07-intent-translation.md` — Natural language → API parameters, industry presets, worked examples

### Prototyping
- `${CLAUDE_PLUGIN_ROOT}/docs/08-html-css-prototypes.md` — CSS custom properties, component showcase, full page template

## Critical Rules

1. **No text prompts** — Huemint has no prompt/description parameter. Translate intent into adjacency + temperature + mode + locking.
2. **Flat array format** — Adjacency is a 1D row-major array, not a 2D matrix. Length = `num_colors²`.
3. **All values are strings** — `temperature`, `adjacency` values, and `palette` values must be strings (`"65"` not `65`, `"1.2"` not `1.2`).
4. **Diffusion max 5** — Diffusion mode only supports up to 5 colors. Use transformer for 6+.
5. **Diagonal = 0** — Every `adjacency[i*num_colors + i]` must be `"0"`.
6. **Dimension consistency** — `len(adjacency) == num_colors²` and `len(palette) == num_colors`. Always verify.
7. **Non-commercial use** — The API is free for non-commercial use. Be respectful with request volume.
8. **Temperature semantics** — Low (0.0–0.8) = safe/predictable, Medium (0.8–1.4) = balanced/creative, High (1.4–2.4) = wild/experimental.
9. **Request multiple results** — Always set `num_results` ≥ 3 to give users options. Use 5–10 for exploration rounds.
10. **Prototype after selection** — Generate palettes first, let the user choose, then build the HTML/CSS prototype with the selected palette.
