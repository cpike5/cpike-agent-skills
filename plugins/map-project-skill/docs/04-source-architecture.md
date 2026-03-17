# Step 3 — Source Architecture (Document C)

## 3a. Solution & Project Structure

1. Find all project files (`.csproj`, `package.json`, `go.mod`, etc.) under `src/`.
2. List top-level folders in each project to understand its responsibility.
3. Identify the layering pattern — which project depends on which.
4. Write a tree per project with one-line descriptions. Skip `bin/`, `obj/`, `node_modules/`, etc.

## 3b. Data Model

1. List all entity/model files in the domain layer.
2. Group by domain using naming patterns and context from Documents A and B.
3. List entity names as comma-separated items under each group.

## 3c. Service Contracts

1. List all interface/contract files in the domain layer.
2. Separate repositories from services — repositories follow predictable naming (`I{Entity}Repository`). Note their existence in one line, don't enumerate.
3. Group service interfaces by domain, same groupings as the data model.
4. Preserve subfolder-based groupings (e.g., `Interfaces/LLM/`) as they signal distinct subsystems.

## Output Format

H2 per section, H3 per domain group. Comma-separated names.

## Judgement Calls

- Entity and interface names are self-describing — grouping by name is sufficient.
- The goal is "what does this system model and what can it do" — not implementation detail.
