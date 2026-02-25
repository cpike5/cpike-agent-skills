# Palette Refinement

## 3-Round Workflow

### Round 1 — Explore

**Goal**: Generate a wide variety of palettes to establish direction.

- Mode: `transformer` (or `random` for very broad exploration)
- Temperature: `"1.2"` – `"1.6"` (higher for variety)
- Results: `num_results: 8–10`
- Palette: All unlocked `["-", "-", "-", ...]`
- Adjacency: Use a template from `06-adjacency-templates.md`

Present all results to the user with swatches. Ask which palette or individual colors they like.

### Round 2 — Refine

**Goal**: Generate palettes that build on the user's preferences.

- Mode: `transformer`
- Temperature: `"0.8"` – `"1.0"` (tighter)
- Results: `num_results: 5–8`
- Palette: Lock 1–2 colors the user liked from Round 1
- Adjacency: Same as Round 1, or adjust based on feedback

Present results. Ask the user to pick their top 1–2 palettes.

### Round 3 — Polish

**Goal**: Fine-tune the final palette.

- Mode: `transformer`
- Temperature: `"0.4"` – `"0.8"` (conservative)
- Results: `num_results: 3–5`
- Palette: Lock 2–3 colors the user confirmed
- Adjacency: Fine-tune if specific relationships need adjustment

Present final options for selection.

## Score Interpretation

| Score Range | Quality | Action |
|-------------|---------|--------|
| 0.85–1.00 | Excellent | Use confidently |
| 0.70–0.84 | Good | Usable, minor tweaks possible |
| 0.50–0.69 | Fair | Consider adjusting adjacency or temperature |
| Below 0.50 | Poor | Rethink adjacency matrix or mode |

Higher scores indicate better adherence to the adjacency constraints with perceptual harmony. Scores are relative within a batch — compare results against each other, not against an absolute standard.

## Presenting Results to the User

For each palette result, show:

1. **Color swatches** — visual representation (use HTML/CSS if in a prototype context)
2. **Hex values** — list all colors with their role labels
3. **Score** — the harmony score
4. **Role mapping** — which color maps to which UI role (background, text, accent, etc.)

Example presentation format:
```
Palette 1 (score: 0.87)
  Background: #F8F9FA
  Primary:    #2B4C7E
  Accent:     #FF6B35
  Text:       #1A1A2E

Palette 2 (score: 0.82)
  Background: #FFFBF0
  Primary:    #3D5A80
  Accent:     #E07A5F
  Text:       #2D3436
```

## When to Restart

Restart from Round 1 if:
- User doesn't like any results after Round 2
- The adjacency matrix isn't producing the right relationships
- The mood/style direction has fundamentally changed
- Scores are consistently below 0.50

## Adjustment Strategies

| Problem | Adjustment |
|---------|------------|
| Colors too similar | Increase adjacency values between those positions |
| Colors clash | Decrease adjacency values for that pair |
| Background too dark/light | Lock a specific background color |
| Not enough variety between rounds | Increase temperature by 0.3 |
| Too much variety | Decrease temperature by 0.3, lock more colors |
| Accent doesn't pop | Increase adjacency between accent and its neighbors |
