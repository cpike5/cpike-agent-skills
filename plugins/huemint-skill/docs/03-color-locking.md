# Color Locking

## Overview

Color locking lets you **fix specific colors** in the palette while Huemint generates the rest. This is essential for brand compliance, dark mode design, and iterative refinement.

## Syntax

| Palette Value | Meaning |
|---------------|---------|
| `"-"` | Generate this color (unlocked) |
| `"#RRGGBB"` | Lock this exact color |

The `palette` array length must equal `num_colors`.

## Basic Example — Lock Brand Color

Lock a brand blue as the primary, generate background and accent:

```json
{
  "mode": "transformer",
  "num_colors": 3,
  "temperature": "1.0",
  "num_results": 5,
  "adjacency": ["0", "65", "45", "65", "0", "35", "45", "35", "0"],
  "palette": ["-", "#2563EB", "-"]
}
```

Color roles: `[background, primary (locked), accent]`

## Multi-Lock — Brand Color + Background

Lock both the background and primary brand color:

```json
{
  "palette": ["#FFFFFF", "#2563EB", "-", "-"],
  "num_colors": 4,
  "adjacency": ["0","65","50","40","65","0","35","45","50","35","0","30","40","45","30","0"]
}
```

Huemint generates colors 3 and 4 that harmonize with the locked white background and blue primary.

## Dark Mode Locking

Lock a dark background and let Huemint find complementary colors:

```json
{
  "palette": ["#1A1A2E", "-", "-", "-"],
  "num_colors": 4,
  "adjacency": ["0","15","60","50","15","0","50","40","60","50","0","35","50","40","35","0"]
}
```

Note the lower BG ↔ Surface adjacency (15) to keep dark tones cohesive.

## Locking + Adjacency Interaction

Locked colors still obey adjacency constraints. The adjacency values for locked color positions guide how the **generated** colors relate to them.

Example: If you lock `"#FFFFFF"` at position 0 and set adjacency `[0][1] = "80"`, Huemint will generate a very dark color at position 1 (high Delta-E from white).

**Key insight**: Increase adjacency values for locked ↔ unlocked pairs when you need strong contrast against a locked color.

## Brand Palette Expansion

Start with 1–2 brand colors and expand to a full palette:

**Round 1** — Lock primary, generate 3 supporting colors:
```json
{
  "palette": ["#2563EB", "-", "-", "-"],
  "num_colors": 4,
  "adjacency": ["0","60","40","70","60","0","35","50","40","35","0","45","70","50","45","0"]
}
```

**Round 2** — Lock primary + favorite result from Round 1, generate remaining:
```json
{
  "palette": ["#2563EB", "#F0F4FF", "-", "-"],
  "num_colors": 4,
  "adjacency": ["0","60","40","70","60","0","35","50","40","35","0","45","70","50","45","0"]
}
```

## Patterns

| Scenario | What to Lock | What to Generate |
|----------|-------------|-----------------|
| Brand compliance | Brand primary + secondary | Background, surface, accents |
| Dark mode variant | Dark background (#1A–#2A range) | Text, accent, surface |
| Light mode variant | White/light background | Text, primary, accent |
| Accessible text | Background + text color pair | Accents and supporting colors |
| Iterative refinement | Colors you like from previous round | Colors you want to improve |

## Rules

- You can lock any number of colors from 0 to `num_colors - 1` (locking all is pointless)
- Locked colors must be valid `#RRGGBB` hex strings
- Unlocked slots must be exactly `"-"`
- Position in the palette array determines the color's role (matches adjacency matrix rows/columns)
