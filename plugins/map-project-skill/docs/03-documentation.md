# documentation.md — Documentation Index

Tell an agent where existing written knowledge lives so it reads that before exploring code.

## Sources

Documentation is wherever it is: a `docs/` tree, ADRs, a wiki folder, `README.md` files inside `src/` subfolders, inline design notes in CLAUDE.md, OpenAPI specs, changelogs. Find all of it. If the project has only a root README, say so in two lines and stop — don't pad.

## Grouping

Group by topic using filename and folder patterns. Take topic names from the project itself (folder names, section headings, the domain names you'll fix in `architecture.md`), not from a preset list. Don't open every file; titles and first headings are enough.

## Format

An H2 per documentation location, an H3 per topic group within large ones. Files as comma-separated names without extensions, or as a short table when the location holds few enough files that each deserves a description.

Call out the two or three documents an agent should read first (architecture overview, domain glossary, decision log) in a "Start here" line at the top.

## Judgement calls

- Skip non-documentation that lives under `docs/`: prototypes, templates, deployment manifests, images.
- Flag stale docs when it's obvious (references to removed projects, dates years old) — a wrong doc costs more than a missing one.
