# structure.md — Top-Level Structure

Show what's at the root and why each entry matters, so an agent knows where to look and what to ignore.

## Include

Source and test directories, domain-relevant asset folders, documentation, CI/CD workflows, container and compose files, the solution or workspace file, README and CLAUDE.md. Anything an agent would otherwise have to open to understand.

## Exclude

Tool configuration dotfiles, lock files, editor settings, build output, temp folders, and env files (mention that `.env.example` exists in `configuration.md` instead).

## Format

A single tree with one-line descriptions. Directories first, then files, separated by a bare `│` line:

```
project-name/
├── src/                       # Application projects (see architecture.md)
├── tests/                     # xUnit projects mirroring src/
├── docs/                      # Architecture notes and ADRs (see documentation.md)
├── .github/workflows/         # CI: build, test, publish image
│
├── Project.sln
├── docker-compose.yml         # Local Postgres + Seq
└── README.md
```

Follow the tree with a short "How to build, run, and test" block if README doesn't already state it plainly. Link rather than restate when it does.

## Judgement calls

- One level deep at the root is usually enough. Go a second level only for `src/` and `tests/` when the project layout isn't obvious from names.
- A description that just restates the name ("`tests/` — tests") adds nothing. Say what kind, or drop the comment.
