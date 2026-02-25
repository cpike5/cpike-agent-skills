# Intent Translation

Huemint has **no text prompt parameter**. This guide maps natural language requests to numeric API parameters.

## Mood → Temperature

| User Says | Temperature | Rationale |
|-----------|-------------|-----------|
| "professional", "corporate", "clean" | `"0.6"` – `"0.8"` | Conservative, predictable |
| "modern", "balanced", "versatile" | `"0.8"` – `"1.0"` | Moderate variety |
| "creative", "unique", "distinctive" | `"1.0"` – `"1.4"` | More adventurous |
| "bold", "vibrant", "energetic" | `"1.2"` – `"1.6"` | High variety |
| "experimental", "avant-garde", "wild" | `"1.6"` – `"2.4"` | Maximum creativity |
| "calm", "minimal", "muted" | `"0.4"` – `"0.7"` | Low variance + low adjacency values |
| "warm", "cozy", "earthy" | `"0.8"` – `"1.0"` | Moderate temp, often lock warm anchors |
| "cool", "tech", "futuristic" | `"0.8"` – `"1.0"` | Moderate temp, often lock cool anchors |
| "dark", "moody", "dramatic" | `"1.0"` – `"1.4"` | Lock dark background, higher temp for exploration |
| "playful", "fun", "youthful" | `"1.2"` – `"1.6"` | Higher temp for variety |

## Style Keyword → Adjacency Approach

| Keyword | Adjacency Strategy |
|---------|--------------------|
| "monochromatic" | Low values across the board (10–30) |
| "complementary" | High contrast pairs (60–80) with low internal pairs (15–25) |
| "analogous" | All moderate values (25–45) |
| "high contrast" | BG↔Text at 70–85, accent pairs at 50–65 |
| "pastel" | Moderate values (30–50), lock a light background |
| "neon" / "vivid" | Higher values (50–70), high temperature |
| "muted" / "desaturated" | Lower values (15–35), low temperature |
| "gradient-friendly" | Sequential adjacency (position N↔N+1 low, N↔N+2 medium, etc.) |

## Industry Presets

### Fintech / Banking
- Mode: `transformer`
- Temperature: `"0.6"`
- Lock: Consider locking a navy/dark blue (`#1B2A4A`) or white background
- Adjacency: Use 4-Color Website template with higher BG↔Text (70+)
- Traits: Conservative, high contrast, trustworthy

### Healthcare
- Mode: `transformer`
- Temperature: `"0.6"`
- Lock: Consider locking soft blue/teal (`#0D9488`) or white background
- Adjacency: Use 4-Color Website template, moderate values
- Traits: Calming, accessible, professional

### E-Commerce
- Mode: `transformer`
- Temperature: `"0.8"` – `"1.0"`
- Lock: Brand color if available
- Adjacency: Use 5-Color SaaS Dashboard template, higher CTA adjacency (55+)
- Traits: Inviting, action-oriented, strong CTA contrast

### Dev Tools / Technical
- Mode: `transformer`
- Temperature: `"0.7"`
- Lock: Consider dark background for dark mode (`#0D1117`)
- Adjacency: Use 4-Color Dark Mode template
- Traits: Clean, dark-friendly, subtle accents

## Worked Examples

### Example 1: "I need a professional blue website palette"

**Translation**:
- "professional" → temperature `"0.7"`
- "blue" → lock a blue as primary
- "website" → use 4-Color Website template

```json
{
  "mode": "transformer",
  "num_colors": 4,
  "temperature": "0.7",
  "num_results": 5,
  "adjacency": ["0","20","65","50","20","0","55","40","65","55","0","35","50","40","35","0"],
  "palette": ["-", "-", "-", "#2563EB"]
}
```

Roles: Background, Surface, Text, Primary (locked blue).

### Example 2: "Bold, creative startup landing page"

**Translation**:
- "bold, creative" → temperature `"1.4"`
- "startup" → energetic, distinctive
- "landing page" → use 6-Color Landing Page template

```json
{
  "mode": "transformer",
  "num_colors": 6,
  "temperature": "1.4",
  "num_results": 8,
  "adjacency": ["0","18","65","55","55","40","18","0","55","45","45","30","65","55","0","15","40","35","55","45","15","0","35","30","55","45","40","35","0","25","40","30","35","30","25","0"],
  "palette": ["-","-","-","-","-","-"]
}
```

### Example 3: "Dark mode dashboard with our brand green #10B981"

**Translation**:
- "dark mode" → lock dark background, use dark mode adjacency
- "dashboard" → use 5-Color SaaS Dashboard template adapted for dark
- "brand green #10B981" → lock at accent position

```json
{
  "mode": "transformer",
  "num_colors": 5,
  "temperature": "0.8",
  "num_results": 5,
  "adjacency": ["0","12","55","50","50","12","0","45","40","40","55","45","0","35","30","50","40","35","0","25","50","40","30","25","0"],
  "palette": ["#1A1A2E", "-", "-", "#10B981", "-"]
}
```

Roles: Dark Background (locked), Surface, Text, Accent (locked green), Secondary.
