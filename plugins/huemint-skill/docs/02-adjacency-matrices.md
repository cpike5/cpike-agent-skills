# Adjacency Matrices

## What Is an Adjacency Matrix?

The adjacency matrix tells Huemint how **different** each pair of colors should be from each other. Values are based on the CIE Delta-E perceptual color difference scale.

## CIE Delta-E Scale

| Value | Perceptual Difference | Use Case |
|-------|----------------------|----------|
| 0 | Identical | Diagonal (color vs itself) |
| 10–25 | Subtle | Tints/shades of the same hue |
| 25–40 | Noticeable | Related accent colors |
| 40–60 | Clear | Distinct but harmonious colors |
| 60–80 | Strong | High-contrast pairs (text vs background) |
| 80–100 | Maximum | Extreme contrast (black vs white) |

## Matrix Rules

1. **Symmetric**: Value at `[i][j]` must equal `[j][i]`
2. **Diagonal = 0**: A color has zero difference from itself
3. **Flat row-major format**: The 2D matrix is flattened into a 1D array, row by row
4. **All values are strings**: `"65"` not `65`
5. **Length = num_colors²**: A 3-color palette needs 9 values, 4-color needs 16, etc.

## 3-Color Example

Scenario: Background, primary text, accent button.

Conceptual 2D matrix:

```
         BG    Text   Accent
BG     [  0     65     45  ]
Text   [ 65      0     35  ]
Accent [ 45     35      0  ]
```

- BG ↔ Text = 65 (high contrast for readability)
- BG ↔ Accent = 45 (visible but not jarring)
- Text ↔ Accent = 35 (distinct but related)

Flattened (row-major):
```json
["0", "65", "45", "65", "0", "35", "45", "35", "0"]
```

Reading order: Row 0 (BG→BG, BG→Text, BG→Accent), Row 1 (Text→BG, Text→Text, Text→Accent), Row 2 (Accent→BG, Accent→Text, Accent→Accent).

## 4-Color Example

Scenario: Background, surface, primary text, accent.

```
            BG    Surface  Text   Accent
BG       [  0      20      65      50  ]
Surface  [ 20       0      55      40  ]
Text     [ 65      55       0      35  ]
Accent   [ 50      40      35       0  ]
```

- BG ↔ Surface = 20 (subtle variation — same family)
- BG ↔ Text = 65 (high readability contrast)
- Surface ↔ Text = 55 (still readable on surface)
- Text ↔ Accent = 35 (distinct roles, moderate contrast)

Flattened:
```json
["0","20","65","50","20","0","55","40","65","55","0","35","50","40","35","0"]
```

## Building Your Own Matrix

Step-by-step:

1. **List your color roles** (e.g., background, surface, text, primary, secondary)
2. **For each pair**, decide how different they need to be (use the Delta-E table above)
3. **Fill the upper triangle** of the matrix
4. **Mirror to the lower triangle** (symmetry)
5. **Set diagonal to 0**
6. **Flatten row by row** into a 1D array
7. **Convert all values to strings**

## Common Pitfalls

| Mistake | Result |
|---------|--------|
| Non-symmetric matrix | Unpredictable outputs |
| Diagonal ≠ 0 | API error or nonsense results |
| Numeric values instead of strings | Undefined behavior |
| Wrong array length | HTTP 400 |
| All values too similar (e.g., all "30") | Muddy, indistinct palette |
| All values too high (e.g., all "90") | Garish, clashing palette |
