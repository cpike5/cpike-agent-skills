# conventions.md — Conventions and Extension Points

Answer "where do I add Y?" — the question agents ask most and the one no other document covers.

## Scope

Recipes for the changes the project sees most often, each as a short numbered list of the files to touch and the pattern to copy:

- Add an entity (model, `DbContext` registration, configuration class, migration, repository).
- Add a service (interface location, implementation location, DI registration, options binding if any).
- Add an endpoint, page, or command handler (routing, auth attributes, validation, where the UI lives).
- Add a configuration setting (file section, options class, or runtime setting — pick by the "What goes where" table in `configuration.md`).
- Add a test (which test project, fixture or factory to reuse, naming pattern).
- Add a background job, event handler, or integration client, when the project has that shape.

Include only the recipes the codebase actually supports. Name a concrete existing example for each ("follow `OrderService` / `IOrderService`") so an agent copies a real pattern rather than inventing one.

## Boundary with CLAUDE.md

CLAUDE.md states rules (naming, style, what not to do). This document states locations and patterns. When CLAUDE.md already covers a recipe, link to it in one line instead of repeating it. If you notice a rule that belongs in CLAUDE.md and isn't there, tell the user rather than adding it here.

## Format

H2 per recipe. Numbered steps with file paths. One "Example:" line per recipe pointing at an existing implementation.

## Judgement calls

- Five accurate recipes beat twelve speculative ones.
- If the codebase does the same thing two different ways, say which is current and which is legacy — that's the single most useful sentence an agent can read before making a change.
