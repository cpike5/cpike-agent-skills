# Step 1 — Top-Level Structure (Document A)

## Procedure

1. List the root directory.
2. Filter for architectural significance — source directories, domain-relevant assets, documentation, CI/CD, key root files (solution/workspace, Dockerfile, compose, README).
3. Exclude noise — build helpers, tool configs, temp folders, env files, lock files.
4. Write a clean tree to `project-map/A-top-level-structure.md` with one-line descriptions per entry.

## Output Format

```
project-name/
├── src/                       # Short description
├── tests/                     # Short description
│
├── SolutionFile.sln           # Short description
└── README.md                  # Short description
```

Group directories above files, separated by a blank `│` line.
