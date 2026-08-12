---
description: Draft a categorized changelog from PRs and commits since the last release tag
argument-hint: "[output-path]"
---

# Prepare Changelog

Prepare a changelog document summarizing notable changes since the last release.

## Usage

/prepare-changelog [output-path]

- `output-path` (optional): defaults to `temp/changelog-draft.md`.

## Workflow

1. **Find the last release:** `git describe --tags --abbrev=0`. If no tags exist, ask the user how to proceed (use initial commit or abort).
2. **Gather changes since the tag:** merged PRs (`gh pr list --state merged --base main --search "merged:>YYYY-MM-DD" --json number,title,labels,author,mergedAt` using the tag date) and commits (`git log TAG..HEAD --oneline --no-merges`). Cross-reference to avoid duplicate entries.
3. **Categorize:** Breaking Changes, New Features, Enhancements, Bug Fixes, Documentation, Internal. Focus on user-facing changes; summarize internal ones briefly. Note breaking changes and security/critical fixes prominently, and capture the overall theme of the release if there is one.
4. **Write the changelog** to the output path in this format:

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

---

*This changelog was auto-generated. Review and edit before publishing.*
```

Omit empty sections.

5. **Report:** the changelog path, counts per category, and any items needing manual review or clarification.

## Notes

- PRs with conventional commit prefixes (feat:, fix:, docs:, …) categorize more reliably; entries from PRs with unclear descriptions may need manual improvement.
