---
name: elasticsearch
description: "Use this skill when working with Elasticsearch, Kibana, or the Elastic stack. Covers ES 8.x REST API (Query DSL, search, aggregations, index management, CRUD), .NET client (Elastic.Clients.Elasticsearch, DI registration, repository pattern), Kibana APIs (dashboards, Lens visualizations, saved objects, data views, saved searches, import/export), KQL syntax, ECS logging, data streams, ILM, ingest pipelines, Serilog sinks, and alerting. Invoke when: writing ES queries or aggregations, configuring index mappings or templates, using the .NET Elasticsearch client, creating or managing Kibana dashboards/visualizations programmatically, setting up log pipelines or ingest processing, configuring ILM or data streams, writing KQL queries, or integrating Serilog with Elasticsearch."
---

# Elasticsearch & Kibana Knowledge Base

You are working with Elasticsearch 8.x and Kibana 8.x. Read the relevant reference docs below before writing queries, client code, or Kibana API calls.

## Quick Decision: Which API Pattern?

| Task | Approach |
|------|----------|
| Full-text search with relevance | `bool.must` with `match` / `multi_match` |
| Exact filtering (no scoring needed) | `bool.filter` with `term` / `range` |
| Deep pagination (>10k results) | `search_after` + Point-in-Time (PIT) |
| Bulk data export | `search_after` + PIT (not scroll) |
| Analytics / metrics | Aggregations with `"size": 0` |
| Paginate all agg buckets | Composite aggregation |
| .NET querying | `Elastic.Clients.Elasticsearch` fluent API |
| Ship logs from .NET | `Elastic.Serilog.Sinks` to data stream |
| Create Kibana dashboard via API | Saved Objects API with NDJSON import |
| Manage log retention | ILM policy on data streams |

## API Scripts

Wrapper scripts for ES/Kibana REST API calls with auth. See `${CLAUDE_PLUGIN_ROOT}/docs/00-api-scripts.md` for first-time setup.

| Script | Usage |
|--------|-------|
| `es-api` | `${CLAUDE_PLUGIN_ROOT}/scripts/es-api [METHOD] /path [body]` |
| `kibana-api` | `${CLAUDE_PLUGIN_ROOT}/scripts/kibana-api [METHOD] /api/path [body]` |
| `es-indices` | `${CLAUDE_PLUGIN_ROOT}/scripts/es-indices [filter]` |
| `es-datastreams` | `${CLAUDE_PLUGIN_ROOT}/scripts/es-datastreams [filter]` |
| `es-check-env` | `${CLAUDE_PLUGIN_ROOT}/scripts/es-check-env` |

## Reference Documentation

### Setup
- `${CLAUDE_PLUGIN_ROOT}/docs/00-api-scripts.md` -- API script setup guide, configuration, and examples

### Core Elasticsearch (read as needed)
- `${CLAUDE_PLUGIN_ROOT}/docs/01-query-dsl.md` -- Bool queries, match, term, range, nested, function_score, multi_match
- `${CLAUDE_PLUGIN_ROOT}/docs/02-search-pagination.md` -- Search API, search_after, PIT, scroll, msearch, source filtering
- `${CLAUDE_PLUGIN_ROOT}/docs/03-index-management.md` -- Index creation, mappings, settings, aliases, composable templates, reindex
- `${CLAUDE_PLUGIN_ROOT}/docs/04-document-crud.md` -- Index, get, update, delete, bulk API, update_by_query, delete_by_query
- `${CLAUDE_PLUGIN_ROOT}/docs/05-aggregations.md` -- Bucket, metric, pipeline, composite aggregations, nested aggs

### .NET Integration (read as needed)
- `${CLAUDE_PLUGIN_ROOT}/docs/06-dotnet-client.md` -- Elastic.Clients.Elasticsearch setup, fluent queries, mapping, bulk ops, NEST migration
- `${CLAUDE_PLUGIN_ROOT}/docs/07-dotnet-patterns.md` -- DI registration, IOptions, repository pattern, health checks, Polly retry, Serilog sinks

### Kibana & Visualization (read as needed)
- `${CLAUDE_PLUGIN_ROOT}/docs/08-kibana-api.md` -- Saved Objects API, Data Views API, Spaces, RBAC, import/export NDJSON
- `${CLAUDE_PLUGIN_ROOT}/docs/09-kibana-visualizations.md` -- Lens architecture, dashboard JSON structure, saved searches, panel types
- `${CLAUDE_PLUGIN_ROOT}/docs/10-kql-syntax.md` -- KQL reference, Lucene comparison, filters vs queries

### Logging & Observability (read as needed)
- `${CLAUDE_PLUGIN_ROOT}/docs/11-ecs-logging.md` -- Elastic Common Schema field reference, ECS mappings template
- `${CLAUDE_PLUGIN_ROOT}/docs/12-data-streams-ilm.md` -- Data streams, ILM policies, hot-warm-cold-frozen, rollover, retention
- `${CLAUDE_PLUGIN_ROOT}/docs/13-ingest-alerting.md` -- Ingest pipeline processors, Kibana alerting rules, Watcher

## Critical Rules

1. **Filter vs query context** -- Use `bool.filter` for exact matches (status, dates, IDs). Only use `must`/`should` when relevance scoring matters. Filters are cached and faster.
2. **No deep pagination with from/size** -- `from + size` cannot exceed 10,000. Use `search_after` with a PIT for anything deeper.
3. **Always set size: 0 for agg-only queries** -- If you only want aggregation results, set `"size": 0` to skip returning hits.
4. **keyword vs text** -- Use `keyword` for exact-match fields (status, IDs). Use `text` for full-text search. Never use `match` on `keyword` or `term` on `text`.
5. **kbn-xsrf header required** -- All Kibana API mutations (POST/PUT/DELETE) require `kbn-xsrf: true`.

> See the **Common Mistakes** section in each doc for domain-specific pitfalls.
