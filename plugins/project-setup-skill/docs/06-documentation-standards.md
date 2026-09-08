# Documentation Standards

An agent works well in a repository in proportion to how much it can learn
without reading source. The docs tree is that budget.

## Layout

```
docs/
  project-overview.md      # the map: every feature, one paragraph, with file pointers
  local-dev-environment.md # how to actually run it here, incl. the test database
                           # and the screenshot recipe (see 02, 07)
  <topic>.md               # cross-cutting concerns: auth, database, observability
  features/<feature>.md    # one page per user-facing feature
  tools/<tool_name>.md     # one spec per agent tool, written before the code
  planning/<name>.md       # designs for work not yet done
  reviews/<name>-<date>.md # audits and findings, dated
project-map/               # code-first orientation: structure, architecture, config
```

The split between `docs/` and `project-map/` is behaviour versus shape. `docs/`
answers "how does this feature work"; `project-map/` answers "where does anything
live". Different questions, and mixing them makes both harder to search.

`planning/` and `reviews/` are **dated snapshots, not living documents**. Leave
them stale on purpose — a plan is evidence of what was intended at the time, and
rewriting it destroys that. Living truth belongs in `features/` and the top-level
topic pages.

## Rules

**Documentation is part of the change, not a follow-up.** For anything beyond a
small fix, the PR that changes behaviour updates the doc that describes it. A
feature with no doc gets one.

**Write for someone with no context, arriving today.** No "as discussed", no
references to a conversation. Name the files.

**Say why, not just what.** A rule with its reason attached survives a situation
the rule didn't anticipate; one without it gets cargo-culted or dropped.

**Record the traps.** A doc's highest-value paragraph is usually the one naming
the mistake everyone makes — the framework quirk, the silent degradation, the
config that fails at runtime rather than at build. Include the symptom, not just
the fix, so it is recognisable when encountered rather than only when looked up.

**Prune.** A doc describing code that no longer exists is worse than no doc,
because it is trusted. When you delete a feature, delete its page.

## Specs before code

Anything with a contract — an agent tool, an API endpoint, a shared component —
gets its spec written first: name, purpose, inputs, and every result shape,
success *and* failure. For agent tools this is not a formality: the description
and results are prompt surface the model reads at runtime, so they are the
feature, and deciding them after the C# means deciding them by accident.

## `README.md` vs `CLAUDE.md`

The README is for a human deciding whether to use or run the project: what it is,
screenshots, quickstart, licence. `CLAUDE.md` is for anyone about to change it.
They overlap on the stack and diverge everywhere else. Don't merge them, and
don't let the README rot into the only accurate one.
