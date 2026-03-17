# Step 5 — Configuration (Document E)

## 5a. Identify Configuration Sources

1. Check the entry point (Program.cs, main.go, etc.) — what config sources are loaded and in what order?
2. Check the main config file (appsettings.json, .env, config.yaml) — capture section names and purpose, not every key.
3. Check for env var templates (.env.example) — which are required vs optional?
4. Check for secrets management — User Secrets, vault references, etc.

## 5b. Map Configuration Classes

1. List configuration/options classes (e.g., `IOptions<T>` in .NET, config structs in Go).
2. Note the binding pattern — how do classes map to config sections?
3. Don't enumerate every property — class names and sections are enough.

## 5c. Map Database-Stored Settings (if applicable)

1. Find the settings definition registry — what settings exist?
2. List all defined settings grouped by category: key, type, default, description.
3. Understand merge behavior — how do DB values combine with file-based config?

## 5d. Document Design Rationale

Summarize the dividing line:
- **File/environment**: deployment-time, infrastructure-level, technical
- **Database**: runtime-tunable, admin-facing, changeable without restart

## Output Format

- Design rationale paragraph up front
- Text-based config flow diagram showing load order
- Tables for: config sections, secrets, DB-stored settings
- Code example showing the binding pattern

## Judgement Calls

- "What goes where and why" is more valuable than exhaustive key listings
- For file config, section names and purpose > individual keys
- For DB settings, enumerate them all — there are typically few enough
- The "What Goes Where" summary table is the most valuable output
