# configuration.md — Configuration

Answer "what goes where and why" — the design rationale is worth more than any key listing.

## Sources and load order

From the entry point (`Program.cs` or equivalent), capture which config sources load and in what order: base file, environment-specific file, user secrets, environment variables, vault, database. Draw it as a short text flow. Note which env var template exists (`.env.example`) and which entries are required versus optional.

## Sections and binding

List config sections by name and purpose — not every key. List the options classes that bind to them and the binding pattern (`services.Configure<T>(config.GetSection("X"))`, `[ConfigurationKeyName]`, validation on start). One code example of the pattern is enough.

## Secrets

Where secrets live per environment (user secrets locally, env vars or vault in deployment) and the config keys they populate. Names and locations only, never values. `integrations.md` cross-references this table.

## Runtime-tunable settings

If the project stores settings in a database or a feature-flag service, this is the one place to enumerate them in full: key, type, default, description, grouped by domain. Explain how they merge with file config and whether changes take effect without restart. If the project has no such mechanism, omit this section entirely.

## Format

- Design rationale paragraph first: the dividing line between deployment-time config (files, env) and runtime-tunable config (database, flags).
- Text flow of load order.
- Tables for sections, secrets, and runtime settings.
- A closing "What goes where" table mapping kinds of setting to their home. This table is the most-used part of the document.

## Judgement calls

- Section names and purpose beat individual keys for file config.
- If load order has a surprise (env vars overriding a file most people expect to win), say so prominently.
