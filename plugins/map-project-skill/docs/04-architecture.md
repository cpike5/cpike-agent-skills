# architecture.md — Source Architecture

Answer "what does this system model and what can it do?" and fix the domain taxonomy every later document reuses.

## Projects and layering

Find every project file under `src/` (and `tests/`). For each, give its responsibility in one line and its top-level folders when they aren't self-explanatory. Then state the layering: which project references which, and the rule that enforces it (e.g. "Domain has no references; Infrastructure implements Domain interfaces; Web references both").

Skip `bin/`, `obj/`, `node_modules/`, generated code.

## Domain taxonomy

Derive domain groupings from the code: namespace segments, folder names under the domain and application layers, feature folders in the web project. Write them down as a short list with a one-line scope each. This list is the taxonomy — `domains.md`, `configuration.md`, and `conventions.md` reuse these names verbatim.

## Data model

Entities grouped by domain, as comma-separated names. Note the persistence pattern once (EF Core `DbContext` name, migrations location, any multi-tenancy or soft-delete conventions). Don't list properties here — that belongs in `domains.md` diagrams, and only for priority domains.

## Service contracts

Interfaces grouped by domain, comma-separated. Repositories that follow a predictable naming pattern get one line ("one `I{Entity}Repository` per aggregate") rather than a list. Preserve subfolder groupings when they mark a distinct subsystem (e.g. `Interfaces/LLM/`).

## Format

H2 per section, H3 per domain group. Names, not descriptions — entity and interface names are self-describing.

## Judgement calls

- If a "domain" is one entity and one service, fold it into a neighbor rather than giving it a heading.
- Note the exceptions to the layering rule — those are what trip agents up.
