# Huemint API Basics

## Endpoint

```
POST https://api.huemint.com/color
```

Content-Type: `application/json`

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mode` | string | Yes | Generation algorithm: `"transformer"`, `"diffusion"`, or `"random"` |
| `num_colors` | integer | Yes | Number of colors to generate (2–12) |
| `temperature` | string | Yes | Creativity/randomness level `"0.0"` to `"2.4"` (string, not number) |
| `num_results` | integer | Yes | Number of palettes to return (1–50) |
| `adjacency` | string[] | Yes | Flat row-major adjacency matrix — length must equal `num_colors * num_colors`. All values are **strings**. |
| `palette` | string[] | Yes | Length must equal `num_colors`. Use `"-"` for colors to generate, `"#RRGGBB"` to lock a color. |

**Critical**: `temperature`, all `adjacency` values, and all `palette` values are **strings**, not numbers or raw hex.

## Request Format

```json
{
  "mode": "transformer",
  "num_colors": 3,
  "temperature": "1.2",
  "num_results": 5,
  "adjacency": ["0", "65", "45", "65", "0", "35", "45", "35", "0"],
  "palette": ["-", "-", "-"]
}
```

## Response Format

```json
{
  "results": [
    {
      "palette": ["#2B2D42", "#8D99AE", "#EDF2F4"],
      "score": 0.85
    },
    {
      "palette": ["#1A1A2E", "#16213E", "#0F3460"],
      "score": 0.78
    }
  ]
}
```

Each result contains:
- `palette`: Array of hex color strings
- `score`: Quality/harmony score (0–1, higher is better)

## curl Example — Transformer Mode (3 colors)

```bash
curl -X POST https://api.huemint.com/color \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "transformer",
    "num_colors": 3,
    "temperature": "1.2",
    "num_results": 5,
    "adjacency": ["0", "65", "45", "65", "0", "35", "45", "35", "0"],
    "palette": ["-", "-", "-"]
  }'
```

## curl Example — Diffusion Mode (4 colors)

```bash
curl -X POST https://api.huemint.com/color \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "diffusion",
    "num_colors": 4,
    "temperature": "1.0",
    "num_results": 3,
    "adjacency": ["0","65","45","80","65","0","35","60","45","35","0","50","80","60","50","0"],
    "palette": ["-", "-", "-", "-"]
  }'
```

## JavaScript fetch Example

```javascript
const response = await fetch("https://api.huemint.com/color", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    mode: "transformer",
    num_colors: 3,
    temperature: "1.2",
    num_results: 5,
    adjacency: ["0", "65", "45", "65", "0", "35", "45", "35", "0"],
    palette: ["-", "-", "-"]
  })
});
const data = await response.json();
// data.results[0].palette → ["#2B2D42", "#8D99AE", "#EDF2F4"]
```

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Invalid JSON body | HTTP 400 |
| `adjacency` length ≠ `num_colors²` | HTTP 400 |
| `palette` length ≠ `num_colors` | HTTP 400 |
| `num_results` > 50 | Clamped to 50 |
| Diffusion with `num_colors` > 5 | HTTP 400 — diffusion only supports up to 5 colors |
| Non-string adjacency values | Undefined behavior — always use strings |
| Server overload | HTTP 429 or 503 — retry with exponential backoff |

## Rate Limiting

The API is free for non-commercial use. Be respectful:
- Request ≤ 10 results at a time during exploration
- Pause between batch requests
- Cache results when iterating on adjacency matrices
