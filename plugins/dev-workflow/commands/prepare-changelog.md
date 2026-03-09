# Prepare Changelog Instructions

Prepare a changelog document summarizing notable changes since the last release.

## Usage

/prepare-changelog [output-path]

- `output-path` (optional): Path for the changelog document. Defaults to `temp/changelog-draft.md`.

## Workflow

1. **Find Last Release**
   - Run `git describe --tags --abbrev=0` to get the most recent tag
   - If no tags exist, inform the user and ask how to proceed (use initial commit or abort)
   - Note the tag name and date for reference

2. **Gather Changes Since Last Release**
   - Get all merged PRs since the tag: `gh pr list --state merged --base main --search "merged:>YYYY-MM-DD" --json number,title,labels,author,mergedAt`
   - Get all commits since the tag: `git log TAG..HEAD --oneline --no-merges`
   - Cross-reference to avoid duplicate entries

3. **Categorize Changes**
   - Review each PR/commit and categorize into:
     - **Breaking Changes**: API changes, removed features, behavior changes
     - **New Features**: New functionality, capabilities
     - **Enhancements**: Improvements to existing features
     - **Bug Fixes**: Resolved issues, corrections
     - **Documentation**: Doc updates, README changes
     - **Internal**: Refactoring, dependency updates, CI/CD changes
   - Focus on user-facing changes; internal changes can be summarized briefly

4. **Identify Notable Changes**
   - Highlight major features or significant improvements
   - Note any breaking changes prominently
   - Include any security fixes or critical bug fixes
   - Summarize the overall theme of the release if applicable

5. **Create Changelog Document**
   - Delegate to the **docs-writer** agent to create the changelog
   - Provide the agent with:
     - Previous version (last tag) and tag date
     - Categorized list of changes (Breaking, Features, Enhancements, Bug Fixes, Documentation, Internal)
     - PR numbers and titles for each change
     - Output path for the document
   - The docs-writer should use this format:

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

6. **Report Results**
   - Display the path to the created changelog document
   - Summarize the number of changes in each category
   - Highlight any items that may need manual review or clarification

## Example

/prepare-changelog

Finds the last tag (e.g., `v0.2.0`), gathers all PRs and commits since then, categorizes the changes, and creates `temp/changelog-draft.md` with the formatted changelog.

## Notes

- The generated changelog is a draft; review before including in a release
- PRs with conventional commit prefixes (feat:, fix:, docs:, etc.) are easier to categorize
- If PRs lack clear descriptions, the changelog entry may need manual improvement
