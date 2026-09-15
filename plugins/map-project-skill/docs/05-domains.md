# domains.md — Feature Map and Domain Diagrams

Show how the domains relate, then go deeper on the ones that matter.

## Feature map

One Mermaid `flowchart TB` with a subgraph per domain from the taxonomy in `architecture.md`, key features as nodes, and edges for cross-domain dependencies. Keep labels to a few words. Cross-domain relationships live here and only here — don't repeat them in every domain diagram.

## Priority ranking

Rank domains by how much depends on them, not by internal complexity. In an interactive session, ask the user which domains are most active before ranking. Headless, rank from evidence — fan-in in the feature map, file counts, `git log` churn over the last few months — and write the ranking and its basis into the document so a reader can disagree with it.

Small, self-contained domains get no diagram; an agent can pick them up from `architecture.md` when needed.

## Domain diagrams

For each priority domain (typically three to five), one Mermaid `classDiagram` with `direction TB` showing:

- **Entities** with IDs, foreign keys, and the three to five properties that define the entity.
- **Service interfaces** with the methods that say what the service does — not CRUD.
- **Relationships** with cardinality, and service-to-entity dependencies.

Use `<<interface>>`, `<<DbContext>>`, and similar annotations where they clarify. For page- or endpoint-oriented domains, a flowchart of routes beats a class diagram.

Gather from entity files (properties, navigation properties, FKs) and interface files (signatures). The mermaid skill in this marketplace, if installed, covers syntax and rendering checks.

## Judgement calls

- Diagrams rot fastest. Fewer, smaller diagrams that stay true beat a complete set that's wrong in six months.
- Cap each class diagram around 12 classes. Past that, split by sub-subsystem or cut.
- Check the Mermaid renders — a syntax error makes the whole document look untrustworthy.
