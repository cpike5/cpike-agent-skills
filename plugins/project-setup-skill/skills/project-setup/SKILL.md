---
name: project-setup
description: "Set a repository up so agent sessions are productive in it — CLAUDE.md, a SessionStart hook, the docs tree, a CI build gate, versioning and image publishing, VPS deployment behind nginx, a PR template, and a real test database. Use this skill when the user asks to set up, onboard, bootstrap, or scaffold a project or repository for Claude Code; when they ask for a CLAUDE.md, a SessionStart hook, a build/CI workflow, a Dockerfile or image-publishing workflow, a pull request template, documentation standards, a deploy script, an nginx site config, a docker-compose production stack, or a throwaway test database; and when they ask how this project should handle CI/CD, versioning, releases, rollback, integration testing, Playwright screenshots, or deployment to a VPS. Also invoke when reviewing whether an existing repository has the setup an agent needs."
---

# Project Setup

Take a repository — new or existing — from "an agent flails in it" to "an agent
is productive in it". Seven artifacts, each independently useful: a `CLAUDE.md`,
a `SessionStart` hook, a docs tree, a CI build gate, versioning and image
publishing, a VPS deployment, and a test database that is a real database.

Extracted from a .NET 9 / Blazor / Postgres app shipped as a GHCR image to a
Docker Compose host behind nginx. The prose applies to any stack; the copy-ready
assets are .NET-flavoured and marked where they need translating.

## Always read first

`${CLAUDE_PLUGIN_ROOT}/docs/01-onboarding-workflow.md` — assess the repository
before copying anything, the order the steps go in, the asset-to-destination
table, the placeholders, and how to adapt to another stack.

Then read only the section the task actually touches.

## Sections

| Doc | Covers |
| --- | --- |
| `${CLAUDE_PLUGIN_ROOT}/docs/02-claude-code-setup.md` | `CLAUDE.md`, the `SessionStart` hook, `docs/local-dev-environment.md` |
| `${CLAUDE_PLUGIN_ROOT}/docs/03-ci-cd.md` | The PR build gate, versioning, image publishing, the release flow, rollback |
| `${CLAUDE_PLUGIN_ROOT}/docs/04-deployment.md` | VPS layout, deploy script, prod compose, nginx + TLS, operations |
| `${CLAUDE_PLUGIN_ROOT}/docs/05-pull-requests.md` | The PR template and why each section exists |
| `${CLAUDE_PLUGIN_ROOT}/docs/06-documentation-standards.md` | The `docs/` tree, what gets written when, specs before code |
| `${CLAUDE_PLUGIN_ROOT}/docs/07-testing.md` | The three test layers, a real test database, Playwright and screenshots |

Copy-ready assets live under `${CLAUDE_PLUGIN_ROOT}/assets/`; doc 01 has the
table mapping each one to its destination in the target repository.

## Principles

1. **Assess before you copy.** Read the repository first — stack, what already
   exists, how it deploys, whether the tests touch a database. Existing
   artifacts get improved, not overwritten.
2. **Propose an ordered plan and agree the scope.** The honest recommendation is
   usually the first few steps, not all nine. Each one pays off alone.
3. **Adapt, don't dump.** An asset copied with the wrong project names or a
   surviving `<appname>` placeholder is worse than no asset — it looks
   authoritative and is wrong.
4. **Every claim in a `CLAUDE.md` must be true today.** A stale one is worse than
   none, because the agent trusts it over the code.
5. **Say why, not just what.** A rule with its reason attached survives a
   situation the rule didn't anticipate. This is why the assets are commented —
   keep the comments when you copy them.
6. **Verify in the way the thing actually fails.** A hook is verified by a fresh
   session that builds, CI by a red run going green, a deploy from outside the
   box. Reading a file back proves nothing about any of them.
