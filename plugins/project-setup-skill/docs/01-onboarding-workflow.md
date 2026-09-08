# Onboarding Workflow

How to take a repository — new or existing — from "an agent flails in it" to
"an agent is productive in it": what to install, in what order, and when to stop.

The rest of this skill is the reasoning behind each artifact. This doc is the
procedure.

## Assess before you copy

Never open with a bulk file copy. Read the repository first and establish, in
one pass:

- **Stack and layout** — language, framework, build tool, test runner, database.
  This decides which assets apply verbatim and which need translating.
- **What already exists** — `CLAUDE.md`, `docs/`, `.github/workflows/`,
  `.claude/`, a Dockerfile, a test project. Existing artifacts get *improved*,
  not overwritten. A repository's own CI workflow encodes decisions you cannot
  see from the file.
- **How it deploys today**, if it does. Section 04 describes one shape — a VPS
  running Compose behind nginx, fed by GHCR. A project deploying to a PaaS keeps
  its own deployment and takes the rest.
- **Whether the tests touch a database.** This is the question that most often
  changes the plan, because it decides whether "the tests pass" currently means
  anything (`${CLAUDE_PLUGIN_ROOT}/docs/07-testing.md`).

Then propose an ordered plan and get agreement on scope before writing files.
Each step below is independently useful, so the honest recommendation is often
"do the first three now" rather than all nine.

## The order

Roughly dependency order. Stop wherever the value runs out.

1. **`CLAUDE.md`** — highest leverage by a wide margin, and the only step that
   pays off before any of the others. Per
   `${CLAUDE_PLUGIN_ROOT}/docs/02-claude-code-setup.md`.
2. **`docs/project-overview.md`** — one paragraph per feature with file pointers,
   so an agent reads instead of grepping.
3. **`.github/workflows/build.yml`** — plus branch protection on `main` making it
   a required check. An unenforced gate is a suggestion.
   (`${CLAUDE_PLUGIN_ROOT}/docs/03-ci-cd.md`)
4. **`.github/pull_request_template.md`** —
   `${CLAUDE_PLUGIN_ROOT}/docs/05-pull-requests.md`.
5. **`.claude/hooks/session-start.sh`** — needed as soon as work happens from the
   web or from fresh containers. Verify it by starting a fresh session and
   building, not by reading it.
6. **`Directory.Build.props` + `Dockerfile` + `docker-release.yml`** — versioning
   and image publishing, together, since the Dockerfile's restore layer depends
   on the props file.
7. **A real test database** — `test-db.sh` or a Testcontainers fixture, per
   `${CLAUDE_PLUGIN_ROOT}/docs/07-testing.md`. Do this as soon as an agent is
   expected to verify its own work: without it, "all tests pass" means "no test
   touched a database".
8. **VPS setup** — `${CLAUDE_PLUGIN_ROOT}/docs/04-deployment.md`. The only step
   with work outside the repository.
9. **Docs conventions** — `${CLAUDE_PLUGIN_ROOT}/docs/06-documentation-standards.md`,
   adopted as you touch each area rather than as a big-bang backfill.

For a greenfield project the same order holds; steps 1 and 2 are just shorter,
and step 9 is cheapest to adopt at the start rather than retrofitted.

## Copy-ready assets

All paths are relative to `${CLAUDE_PLUGIN_ROOT}`.

| Asset | Destination in the target repo |
| --- | --- |
| `assets/claude/settings.json` | `.claude/settings.json` |
| `assets/claude/hooks/session-start.dotnet.sh` | `.claude/hooks/session-start.sh` |
| `assets/claude/hooks/session-start.node.sh` | `.claude/hooks/session-start.sh` (Node/TS alternative) |
| `assets/github/workflows/build.yml` | `.github/workflows/build.yml` |
| `assets/github/workflows/docker-release.yml` | `.github/workflows/docker-release.yml` |
| `assets/github/dependabot.yml` | `.github/dependabot.yml` |
| `assets/github/pull_request_template.md` | `.github/pull_request_template.md` |
| `assets/Dockerfile` | `src/<AppName>.Server/Dockerfile` |
| `assets/Directory.Build.props` | `Directory.Build.props` (repo root) |
| `assets/deploy/docker-compose.prod.yml` | `/opt/<appname>/docker-compose.yml` (on the VPS) |
| `assets/deploy/env.example` | `/opt/<appname>/.env` (on the VPS) |
| `assets/deploy/deploy-appname.sh` | `/usr/local/bin/deploy-<appname>.sh` (on the VPS) |
| `assets/deploy/nginx-site.conf` | `/etc/nginx/sites-available/<domain>` (on the VPS) |
| `assets/scripts/test-db.sh` | `scripts/test-db.sh` |
| `assets/scripts/screenshot.mjs` | `scripts/screenshot.mjs` |

The asset directories are named `claude/` and `github/` rather than `.claude/`
and `.github/` so they are visible and cannot be picked up as configuration for
this repository. They land dotted.

Every asset is commented with the reasoning behind its non-obvious lines. **Read
them, and keep the comments when you copy** — they are documentation for whoever
next edits the file, not packaging.

Placeholders are `<appname>` (lowercase; paths, image names, hostnames) and
`<AppName>` (Pascal case; .NET project and solution names). Replace every
occurrence before committing, and grep for the angle brackets afterwards — a
surviving `<appname>` in a shell script is a redirect, not a string.

## Adapting to another stack

The kit was extracted from a .NET 9 / Blazor / Postgres app shipped as a GHCR
image to a Docker Compose host behind nginx. The prose applies to any stack;
these are the only stack-specific pieces:

- `build.yml` — the restore/build/test commands.
- `Dockerfile` — the build and runtime images and the publish step.
- `Directory.Build.props` — versioning. Another ecosystem has its own single
  place for this; the requirement is that there *is* one.
- The `SessionStart` hook — a Node variant ships alongside the .NET one.
- The C# fixture examples in `${CLAUDE_PLUGIN_ROOT}/docs/07-testing.md`.

Everything else — the deploy script, the compose file, nginx, the PR template,
the documentation conventions, `test-db.sh`, `screenshot.mjs`, and every
Playwright and test-isolation practice — is stack-agnostic as written.

The nginx config's WebSocket and buffering settings are tuned for Blazor Server /
SignalR; they are equally correct for any app doing WebSockets or server-sent
events, and harmless for one that does neither.

## Rules for the agent doing this

**Adapt, don't dump.** An asset copied with the wrong project names, an
irrelevant service, or a placeholder left in is worse than no asset — it looks
authoritative and is wrong.

**Verify each step in the way that step actually fails.** The hook is verified by
a fresh session that builds. CI is verified by a red run turning green, not by
the YAML parsing. The deploy is verified from outside the box. Reading a file
back proves nothing about any of these.

**One concern per PR.** Onboarding produces several independent changes; they
review far better separately, and a rollback of one shouldn't take the others
with it (`${CLAUDE_PLUGIN_ROOT}/docs/05-pull-requests.md`).

**Say what you did not do.** If step 7 was skipped because the project has no
database, or step 8 because it deploys to a PaaS, name that. Silence is
indistinguishable from an oversight.
