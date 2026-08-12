---
description: Version bump, tag, push, and GitHub release with changelog
argument-hint: "[version]"
---

# Release Instructions

Create and publish a new release version for the project.

Version-file references below assume .NET (`Directory.Build.props`); on other stacks use the project's equivalent (`pyproject.toml`, `package.json`, etc.).

## Usage

```
/release [version]
```

- `version` (optional): The version to release (e.g., `0.3.0`, `1.0.0`). If not provided, will prompt for version.

## Workflow

1. **Validate Prerequisites**
   - Ensure working directory is clean (no uncommitted changes)
   - Ensure on `main` branch
   - Ensure branch is up to date with remote

2. **Determine Version**
   - If version provided, validate it follows SemVer format
   - If not provided, read current version from `Directory.Build.props` and suggest next versions

3. **Update Version Files**
   - Update `Directory.Build.props` with new version
   - Update `CLAUDE.md` current version reference if present
   - Review main documentation for version mentions needing updates: README.md, CONTRIBUTING.md, etc.
   - Commit version bump: `chore: Bump version to vX.Y.Z`

4. **Create Git Tag**
   - Create annotated tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`

5. **Push to Remote**
   - Push commits: `git push origin main`
   - Push tag: `git push origin vX.Y.Z`

6. **Prepare Release Notes**
   - For major/minor releases:
     - Run `/prepare-changelog` to generate changelog draft
     - Review and edit `temp/changelog-draft.md`
     - Optionally update main `CHANGELOG.md` with the new entry
   - For patch releases (hotfixes):
     - Use auto-generated notes (skip to step 7 with `--generate-notes`)

7. **Create GitHub Release**
   - With changelog: `gh release create vX.Y.Z --notes-file temp/changelog-draft.md --title "vX.Y.Z"`
   - Without changelog (patches): `gh release create vX.Y.Z --generate-notes --title "vX.Y.Z"`

8. **Update Development Version**
   - Ask user for next development version: Next patch, minor, or major (e.g., `X.Y.Z+1-dev`, `X.Y+1.0-dev`, `X+1.0.0-dev`)
   - Update `Directory.Build.props` with new development version
   - Commit development version bump: `chore: Bump version to vX.Y.Z-dev`
   - Push commit: `git push origin main`

## Example

```
/release 0.3.0
```

Creates tag `v0.3.0`, pushes to remote, and creates GitHub release with auto-generated notes.
