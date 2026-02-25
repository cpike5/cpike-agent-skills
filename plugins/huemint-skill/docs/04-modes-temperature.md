# Modes & Temperature

## Mode Comparison

| Feature | `transformer` | `diffusion` | `random` |
|---------|--------------|-------------|----------|
| Quality | Highest | High | Low |
| Speed | Fast | Slower | Instant |
| Max colors | 12 | **5** | 12 |
| Best for | Production palettes | Small artistic palettes | Quick exploration |
| Respects adjacency | Strong | Strong | Weak |
| Temperature range | 0.0–2.4 | 0.0–2.4 | N/A |

**Critical**: Diffusion mode supports a maximum of 5 colors. Use transformer for 6+ color palettes.

## Mode Selection Flowchart

```
Need > 5 colors? ──YES──→ transformer
       │
       NO
       │
Need production quality? ──YES──→ transformer
       │
       NO
       │
Want artistic/unique palettes? ──YES──→ diffusion
       │
       NO
       │
Just exploring? ──→ random
```

## Temperature

Temperature controls how creative/random the output is. It's a **string** value.

| Range | Label | Behavior |
|-------|-------|----------|
| `"0.0"` – `"0.5"` | Conservative | Safe, predictable, conventional palettes |
| `"0.6"` – `"1.0"` | Balanced | Good variety while staying harmonious |
| `"1.0"` – `"1.4"` | Creative | More unexpected combinations, still usable |
| `"1.5"` – `"2.0"` | Bold | Wild, experimental — may need curation |
| `"2.0"` – `"2.4"` | Extreme | Maximum chaos — mostly for exploration |

## Mode + Temperature Recipes

| Scenario | Mode | Temperature | Why |
|----------|------|-------------|-----|
| Corporate website | transformer | `"0.8"` | Professional, predictable |
| SaaS dashboard | transformer | `"0.6"` | Clean, functional |
| Creative portfolio | transformer | `"1.4"` | Distinctive but usable |
| Artistic brand | diffusion | `"1.2"` | Unique, expressive |
| Dark mode UI | transformer | `"0.8"` | Controlled contrast |
| Exploration / brainstorm | random | `"1.0"` | Fast variety |
| Startup landing page | transformer | `"1.0"` | Balanced energy |
| Healthcare / fintech | transformer | `"0.6"` | Conservative trust |
| E-commerce | transformer | `"0.8"` | Inviting but professional |
| Dev tools / technical | transformer | `"0.7"` | Clean, no-nonsense |

## Combining Mode and Temperature

Low temperature + transformer = most predictable, safest results.
High temperature + diffusion = most experimental, unpredictable results.

**Strategy**: Start with `transformer` at `"1.0"` and adjust:
- Results too boring? Increase temperature by 0.2–0.4
- Results too wild? Decrease temperature by 0.2–0.4
- Want completely different aesthetic? Switch to diffusion
- Just need quick options? Use random to scan the space, then refine with transformer
