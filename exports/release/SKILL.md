---
name: release
description: >-
  Version bump, tag, push, and GitHub release with changelog. Use whenever the
  user wants to release, publish, ship, or cut a new version of a project —
  e.g. "release 0.3.0", "cut a release", "tag and publish this", "bump the
  version and create a GitHub release", or "prepare release notes and ship
  it". Covers SemVer validation, version-file updates, annotated git tags,
  changelog drafting from commits and merged PRs, GitHub release creation via
  the gh CLI, and the post-release development version bump.
---

# Release

Create and publish a new release version for the project: bump the version,
tag, push, and publish a GitHub release with a changelog.

Version-file references below assume .NET (`Directory.Build.props`); on other
stacks use the project's equivalent (`pyproject.toml`, `package.json`, etc.).

The user may provide a target version (e.g., `0.3.0`, `1.0.0`). If they
don't, determine the current version and suggest options (step 2).

## Workflow

1. **Validate Prerequisites**
   - Ensure working directory is clean (no uncommitted changes)
   - Ensure on `main` branch
   - Ensure branch is up to date with remote

2. **Determine Version**
   - If a version was provided, validate it follows SemVer format
   - If not provided, read the current version from `Directory.Build.props`
     (or the stack's equivalent) and suggest next patch/minor/major versions
     for the user to choose from

3. **Update Version Files**
   - Update `Directory.Build.props` with the new version
   - Update `CLAUDE.md` current version reference if present
   - Review main documentation for version mentions needing updates:
     README.md, CONTRIBUTING.md, etc.
   - Commit version bump: `chore: Bump version to vX.Y.Z`

4. **Create Git Tag**
   - Create annotated tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`

5. **Push to Remote**
   - Push commits: `git push origin main`
   - Push tag: `git push origin vX.Y.Z`

6. **Prepare Release Notes**
   - For major/minor releases, draft a changelog (see "Drafting the
     changelog" below), review `temp/changelog-draft.md` with the user, and
     optionally update the main `CHANGELOG.md` with the new entry
   - For patch releases (hotfixes), skip the draft and use auto-generated
     notes in step 7 (`--generate-notes`)

7. **Create GitHub Release**
   - With changelog: `gh release create vX.Y.Z --notes-file temp/changelog-draft.md --title "vX.Y.Z"`
   - Without changelog (patches): `gh release create vX.Y.Z --generate-notes --title "vX.Y.Z"`

8. **Update Development Version**
   - Ask the user for the next development version: next patch, minor, or
     major (e.g., `X.Y.Z+1-dev`, `X.Y+1.0-dev`, `X+1.0.0-dev`)
   - Update `Directory.Build.props` with the new development version
   - Commit development version bump: `chore: Bump version to vX.Y.Z-dev`
   - Push commit: `git push origin main`

## Drafting the changelog

Used in step 6 for major/minor releases.

1. **Find the last release:** `git describe --tags --abbrev=0`. If no tags
   exist, ask the user how to proceed (use initial commit or abort).
2. **Gather changes since the tag:** merged PRs
   (`gh pr list --state merged --base main --search "merged:>YYYY-MM-DD" --json number,title,labels,author,mergedAt`
   using the tag date) and commits (`git log TAG..HEAD --oneline --no-merges`).
   Cross-reference to avoid duplicate entries.
3. **Categorize:** Breaking Changes, New Features, Enhancements, Bug Fixes,
   Documentation, Internal. Focus on user-facing changes; summarize internal
   ones briefly. Note breaking changes and security/critical fixes
   prominently, and capture the overall theme of the release if there is one.
   PRs with conventional commit prefixes (feat:, fix:, docs:, …) categorize
   more reliably; entries from PRs with unclear descriptions may need manual
   improvement.
4. **Write the draft** to `temp/changelog-draft.md` in this format, omitting
   empty sections:

```markdown
# Changelog Draft - vX.Y.Z

**Release Date**: [To be determined]
**Previous Version**: [last tag]

## Summary

[Brief 1-2 sentence summary of this release]

## Breaking Changes

- [Description of breaking change and migration path if applicable]

## New Features

- **[Feature Name]**: [Brief description] (PR #XX)

## Enhancements

- [Enhancement description] (PR #XX)

## Bug Fixes

- [Fix description] (PR #XX)

## Documentation

- [Doc change description]

## Internal Changes

- [Internal change summary]
```

## Example

> "Release version 0.3.0"

Creates tag `v0.3.0`, pushes to remote, and creates a GitHub release with
auto-generated notes.
