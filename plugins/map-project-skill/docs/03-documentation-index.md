# Step 2 — Documentation Index (Document B)

## Procedure

1. List all files in `docs/` recursively.
2. Identify major subdirectories and their purpose (architecture, articles, specs, requirements, lessons-learned, changelogs, etc.).
3. Skip non-documentation directories — prototypes, templates, deployment configs, build assets.
4. For the largest section (typically `articles/`), group files by domain using naming patterns. Common groupings: Audio/Voice, AI, Moderation, Community, Scheduling, UI/Portal, Infrastructure, Observability, Identity, Deployment, General Reference.
5. For other directories, list files with brief groupings where natural clusters exist.

## Output Format

H2 headers per `docs/` subdirectory. H3 subheaders per domain group within large sections. Filenames without extensions, comma-separated.

## Judgement Calls

- Group by filename patterns — don't open every file.
- Optimize for "where do I look for X" — discoverability over completeness.
