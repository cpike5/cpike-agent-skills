# CI/CD

Two workflows, one job each. `build.yml` gates every PR; `docker-release.yml`
publishes an image when a release is tagged. Templates are in
`${CLAUDE_PLUGIN_ROOT}/assets/github/workflows/`.

The pipeline deliberately does *nothing* on a push to `main` beyond building and
testing it. Continuous deployment from `main` to a VPS trades a real safety
property — that what is running was deliberately chosen — for a convenience you
rarely want at this scale. A tagged release is the deliberate act.

## `build.yml` — the PR gate

Restore, build, test. Nothing else. What "test" should cover — and why a suite
that never touches a database is not a gate — is
`${CLAUDE_PLUGIN_ROOT}/docs/07-testing.md`.

The constraint worth defending: **CI must not check anything a contributor
cannot run locally with one command.** A check that only exists in CI produces
failures nobody can reproduce, and the fix becomes push-and-pray. If a linter or
analyzer belongs in CI, wire it into the local build first.

Two details in the template earn their keep:

- **`concurrency` with `cancel-in-progress`** — a second push to a branch makes
  the first run's result meaningless. Without this you pay for both and, worse,
  a stale green can land before the fresh red.
- **`dotnet test --no-build`** — reuses the Release output the previous step
  produced, so the tests exercise exactly the binaries that were verified,
  and the job doesn't compile the solution twice.

Set this workflow as a required status check on `main` in branch protection. An
unenforced gate is a suggestion.

## Versioning

One `Directory.Build.props` at the repository root holds `VersionPrefix` and
`VersionSuffix`; MSBuild imports it into every project automatically, and nothing
else declares a version. Template in
`${CLAUDE_PLUGIN_ROOT}/assets/Directory.Build.props`.

`VersionSuffix` is `dev` between releases and empty on the release commit, so a
build off `main` is visibly ahead of the last tag rather than impersonating it.

The one non-obvious coupling: **the Dockerfile must `COPY` this file into the
restore layer.** Restore and publish each compute a version, and if restore does
not see the file it computes a different one — a mismatch that surfaces as a
confusing publish-time error, not as a missing-file error.

## `docker-release.yml` — publishing the image

Fires on `release: published`. Logs in to `ghcr.io` with the built-in
`GITHUB_TOKEN` (no PAT, no registry secret — just `permissions: packages: write`,
since the default token is read-only), builds from the repository root, and
pushes.

`docker/metadata-action` derives the tag set from the release tag: `v1.4.2`
publishes `1.4.2`, `1.4`, `1`, and `latest`. That is what lets a VPS choose its
own update policy in `.env` — `APP_TAG=latest` to track everything, `APP_TAG=1.4`
to take patches only, `APP_TAG=1.4.2` to pin hard while investigating.

`cache-from`/`cache-to: type=gha` makes a rebuild that changed only app code
reuse the dependency-restore layer.

## The release flow

1. `main` is green.
2. Bump `VersionPrefix`, clear `VersionSuffix`, commit.
3. Tag `vX.Y.Z` and push the tag.
4. Publish a GitHub release for that tag, with notes drawn from the merged PRs.
   Publishing is what triggers the image build — a tag alone does nothing.
5. Set `VersionSuffix` back to `dev`, commit.
6. On the VPS: `sudo deploy-<appname>.sh`.

Steps 2–5 are what the `/release` skill automates if you use it.

Semantic versioning, honestly applied: patch for fixes, minor for features, major
for a break. On a personal project the majors rarely come, but the discipline is
what makes `APP_TAG=1.4` a safe thing to pin.

## Rolling back

Set `APP_TAG` in `/opt/<appname>/.env` to the last good version and re-run the
deploy script. This is the reason images are tagged by version and not only by
`latest`, and it is worth testing once before you need it.

The rollback that does **not** work is a database migration that has already run.
Applying migrations at startup (`Database.Migrate()`) means the old image can
meet a newer schema. Keep migrations additive — add a column, backfill, and drop
the old one in a *later* release rather than the same one — and one-version
rollback stays safe.
