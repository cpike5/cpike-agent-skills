# Step 4 — Feature Map and Domain Diagrams (Document D)

## 4a. Top-Level Feature Map

1. Using context from Documents A–C, identify the major feature domains.
2. Create a Mermaid flowchart (`flowchart TB`) with subgraphs per domain, key features as nodes.
3. Draw cross-domain connections showing dependencies.

## 4b. Domain Priority Ranking

1. Rank domains by architectural importance — how much depends on them, not internal complexity.
2. Consult the user on priority — they know which domains are most active.
3. Drop small, self-contained domains that agents can pick up on-demand.

## 4c. Domain Deep-Dive Diagrams

For each priority domain, create a Mermaid class diagram showing:

1. **Entities** — IDs, FKs, and 3–5 domain-significant properties.
2. **Service interfaces** — key methods that define what the service does (not CRUD boilerplate).
3. **Relationships** — entity-to-entity with cardinality, service-to-entity dependencies.
4. Use `<<interface>>`, `<<DbContext>>`, etc. annotations where they add clarity.

To gather information:
- Scan entity files for properties, navigation properties, foreign keys
- Scan service interfaces for method signatures
- Group by the domain categories from Documents B and C

## Output Format

- Top-level map: `flowchart TB` with subgraphs
- Domain diagrams: `classDiagram` with `direction TB`
- For page/endpoint-oriented domains (e.g., Web Portal), use a flowchart instead
- Keep labels short — diagrams are for structure, not full API docs

## Judgement Calls

- Not every property or method needs to appear — include what defines the entity/service
- If a domain has sub-subsystems, reflect that grouping
- Cross-domain relationships belong in the top-level flowchart, not every domain diagram
