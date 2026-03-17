# General Workflow

## Pre-Exploration

Before scanning the filesystem, read these files if they exist:

1. **README.md** — project purpose, tech stack, setup
2. **CLAUDE.md** — project conventions, gotchas, domain context

These provide framing for all subsequent steps.

## Output Convention

All output goes into a `project-map/` folder in the project root. Each step produces one document (A through F). Create the folder if it doesn't exist.

## Sequential Dependency

Steps must be executed in order. Each step builds on context from previous documents:

- **Step 1 (A)** → standalone, but informed by README/CLAUDE.md
- **Step 2 (B)** → uses A for directory context
- **Step 3 (C)** → uses A and B for grouping context
- **Step 4 (D)** → synthesizes A, B, and C into domain diagrams
- **Step 5 (E)** → references C for config class mapping
- **Step 6 (F)** → cross-references E for credential mapping

## Domain Grouping Consistency

Once you establish domain groupings in Document B or C, reuse them consistently across all subsequent documents. Common groupings include: Audio/Voice, AI, Moderation, Community, Scheduling, UI/Portal, Infrastructure, Observability, Identity, Deployment, General Reference — but adapt to the actual project.
