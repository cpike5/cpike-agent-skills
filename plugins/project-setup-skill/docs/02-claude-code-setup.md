# Claude Code Project Setup

What a repository needs before an agent session is productive in it. Three
artifacts: a `CLAUDE.md`, a `SessionStart` hook, and a documentation tree the
agent is told to read before searching.

## `CLAUDE.md`

The file every session loads before doing anything. It is not a README — the
README explains the project to a human evaluating it; `CLAUDE.md` explains it to
someone about to change it, today, with no prior context.

Write these sections:

- **Background** — what the app is, the solution/package layout with one line per
  project saying what it owns, and the stack (framework, database, auth,
  observability, deployment). Enough that the agent picks the right project to
  put a new file in without grepping.
- **Exploring the codebase** — the instruction to read `docs/` before doing a
  broad code search, and where the map lives. This is the highest-leverage
  paragraph in the file: an agent that greps for a feature spends five tool calls
  finding what one doc page would have handed it.
- **Running it locally** — a pointer to the local dev doc, with the specific
  traps named inline. See below.
- **Building & testing** — the exact commands, copy-pasteable, with expected
  runtimes. State which of them CI runs and that both must be green before a push.
  Include **how to get a test database**, in one command, and say which layers
  need one — an agent that can't stand up a database will silently confine itself
  to the tests that don't need one and call that verification
  (`${CLAUDE_PLUGIN_ROOT}/docs/07-testing.md`).
- **Conventions that are not discoverable from the code** — where migrations go,
  where specs go, what must ship alongside a schema change.
- **Development philosophy** — plan before editing, keep blast radius small, no
  unrelated changes, update the docs for anything medium or larger.
- **Gotchas** — the framework traps that cost a build cycle each. One bullet per
  trap, each naming the symptom *and* the fix, because a gotcha you only describe
  abstractly won't be recognised in the wild.

Two rules for the whole file. **Every claim must be true today** — a stale
`CLAUDE.md` is worse than none, because the agent trusts it over the code. And
**say why, not just what**: a rule with its reason attached survives contact with
a situation the rule didn't anticipate.

## The local dev environment doc

Write `docs/local-dev-environment.md` for a fresh agent session on a machine it
has never seen, and put in it every fact that would otherwise cost a wasted
cycle to discover:

- What is *not* available (no Docker? no network to a given host?) and what to do
  instead, so the agent doesn't burn a turn on the obvious-but-wrong path.
- Which services need starting by hand, and how.
- The actual bind address, if the framework ignores the usual environment
  variable for setting it.
- Proxy or TLS quirks that break a naive `curl`.
- **Anything that silently degrades rather than failing.** The expensive ones are
  never errors; they are a panel that renders empty because the dev sign-in path
  carries no user id, and an agent that concludes the feature is broken.
- A working browser-automation recipe for screenshotting the running app at both
  a desktop and a mobile breakpoint, if the project has a UI — including how to
  get a signed-in user, which is the part that actually costs the time. See
  `${CLAUDE_PLUGIN_ROOT}/docs/07-testing.md` § Playwright and screenshots.

## The `SessionStart` hook

Remote (web) sessions get a fresh container: no SDK guarantees, no restored
packages, no warm cache. The hook makes `build` and `test` work on the first try.

`${CLAUDE_PLUGIN_ROOT}/assets/claude/settings.json` wires it up;
`${CLAUDE_PLUGIN_ROOT}/assets/claude/hooks/` has a .NET and a Node version. Copy
one to `.claude/hooks/session-start.sh`, `chmod +x`, and edit the paths.

Four properties matter, and each is a bug if missed:

1. **Guard on `CLAUDE_CODE_REMOTE`.** Local machines manage their own toolchain;
   an unguarded hook runs `apt-get install` on the developer's laptop.
2. **Be idempotent.** Check for a usable toolchain before installing one. The
   container image often carries it from a previous session, and reinstalling
   costs a minute of every session start.
3. **Export through `CLAUDE_ENV_FILE`.** The hook is a separate process — a plain
   `export` dies with it and never reaches the session's tool calls.
4. **Don't fail on noise.** `set -euo pipefail` is right, but a sandbox with
   blocked package sources makes `apt-get update` return non-zero while still
   fetching the indexes that matter. `|| true` on exactly that line, not on the
   install.

Restore dependencies at the end. It is the single slowest thing the first build
would otherwise do, and doing it once at session start is free time.

**Verify the hook by starting a fresh session and running the build**, not by
reading it. Hook failures are quiet, and a hook that exits 0 without having
installed anything looks identical to one that worked.
