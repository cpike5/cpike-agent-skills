# Update Instructions Command

Maintain the project's CLAUDE.md and optional CLAUDE-REFERENCE.md files. Prioritizes minimal context while providing accurate lookup tables when needed.

## User Arguments

```
Optional: What to update
- (no args): Update CLAUDE.md only
- "tables" or "reference": Generate/update CLAUDE-REFERENCE.md with lookup tables
- "all": Update both files
- "slim": Aggressively trim CLAUDE.md to absolute minimum
---
$ARGUMENTS
```

## Design Philosophy

**Context has a cost.** Every line loaded into conversation consumes tokens.

CLAUDE.md should be **small and focused** (~80-100 lines). It contains:
- Critical gotchas that cause real bugs
- Quick reference commands
- Key file locations
- Pointers to docs (not duplicates)

CLAUDE-REFERENCE.md is **optional and comprehensive**. It contains:
- Full configuration options table
- Complete UI page routes
- Command module inventory
- Generated from code, not hand-maintained

## Two-File Strategy

### CLAUDE.md (Always Loaded)

Target: **Under 100 lines**

**Include:**
- Quick reference commands (build, run, test)
- Architecture one-liner with key locations
- Critical gotchas (JS number overflow, terminology)
- Key patterns (2-3 sentences each with doc links)
- Top 5-8 most important doc links
- Pointer to CLAUDE-REFERENCE.md if it exists

**Exclude:**
- Comprehensive tables (use CLAUDE-REFERENCE.md)
- Content already in README.md
- Setup/installation instructions
- Full explanations (link to docs instead)

### CLAUDE-REFERENCE.md (Loaded On-Demand)

Generated file containing lookup tables. Agents read this when:
- Task involves configuration options
- Task involves page routes
- Task involves command modules

**Include:**
- Configuration Options table (all Options classes)
- UI Page Routes table (all pages with URL patterns)
- Command Modules table (if Discord bot)
- Key Documentation table (all docs with purposes)

## Process

### Default: Update CLAUDE.md

1. Read existing CLAUDE.md
2. Verify it follows slim structure
3. Update key doc links (verify they exist)
4. Check for new critical gotchas
5. Ensure under 100 lines

### With "tables" or "reference": Generate CLAUDE-REFERENCE.md

1. Scan for Options/Settings classes:
   ```
   src/*/Configuration/*.cs
   src/*/Options/*.cs
   ```

2. Scan for page routes:
   ```
   src/*/Pages/**/*.cshtml
   src/*/Pages/**/*.razor
   ```

3. Scan for command modules (if Discord bot):
   ```
   src/*/Commands/*.cs
   src/*/Modules/*.cs
   ```

4. Scan docs folder:
   ```
   docs/articles/*.md
   ```

5. Generate CLAUDE-REFERENCE.md with tables

6. Add pointer to CLAUDE.md if not present

### With "slim": Aggressive Trimming

1. Remove any content duplicated in README.md
2. Remove tables (move to CLAUDE-REFERENCE.md)
3. Condense patterns to single lines with doc links
4. Target under 80 lines

## CLAUDE.md Template

```markdown
# CLAUDE.md

Guidance for Claude Code. See README.md for full documentation.

## Quick Reference

\`\`\`bash
dotnet build
dotnet run --project src/[MainProject]
dotnet test
\`\`\`

## Architecture

[One-line description]: Core (domain) → Infrastructure (data) → [App] (UI/API)

| Location | Purpose |
|----------|---------|
| \`src/*.Core/\` | Entities, interfaces, DTOs |
| \`src/*.Infrastructure/\` | Repositories, data access |
| \`src/*.[App]/\` | Entry point, UI, API |

## Critical Gotchas

[Only items that have caused real bugs - with code examples]

## Key Patterns

[2-3 sentence summaries with doc links]

## Key Documentation

[5-8 most frequently needed docs as table]

## Lookup Reference

For comprehensive tables, see [CLAUDE-REFERENCE.md](CLAUDE-REFERENCE.md).
Generate with \`/update-instructions tables\`.
```

## CLAUDE-REFERENCE.md Template

```markdown
# CLAUDE-REFERENCE.md

Auto-generated lookup tables. Regenerate with \`/update-instructions tables\`.

Last updated: [timestamp]

## Configuration Options

| Options Class | appsettings Section | Purpose |
|--------------|---------------------|---------|
| [ClassName] | [Section] | [Description] |

## UI Page Routes

| Page | URL Pattern | Description |
|------|-------------|-------------|
| [PageName] | [/path] | [Description] |

## Command Modules

| Module | Commands |
|--------|----------|
| [ModuleName] | [/cmd1, /cmd2] |

## Documentation Index

| Doc | Purpose |
|-----|---------|
| [filename.md] | [Description] |
```

## Validation

After updating, verify:

**CLAUDE.md:**
- [ ] Under 100 lines (warn if over)
- [ ] No duplication with README.md
- [ ] All doc links valid
- [ ] Gotchas are genuinely non-obvious
- [ ] Has pointer to CLAUDE-REFERENCE.md

**CLAUDE-REFERENCE.md:**
- [ ] All Options classes listed
- [ ] All page routes captured
- [ ] All doc files indexed
- [ ] Timestamp is current

## Output

Report:
- CLAUDE.md line count (target: <100)
- CLAUDE-REFERENCE.md item counts (if generated)
- Items added/removed
- Warnings for any issues

## When to Run

| Situation | Command |
|-----------|---------|
| Setting up new project | `/update-instructions all` |
| After adding pages/config | `/update-instructions tables` |
| Context feels bloated | `/update-instructions slim` |
| Periodic maintenance | `/update-instructions` |
