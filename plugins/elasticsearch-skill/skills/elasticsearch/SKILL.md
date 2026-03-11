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

Wrapper scripts that handle auth headers, content-type, and base URLs. Requires a `.env` file at the plugin root (copy `.env.example`).

| Script | Usage | Notes |
|--------|-------|-------|
| `es-api` | `${CLAUDE_PLUGIN_ROOT}/scripts/es-api METHOD /path [body]` | Adds `Authorization: ApiKey` + `Content-Type: application/json` |
| `kibana-api` | `${CLAUDE_PLUGIN_ROOT}/scripts/kibana-api METHOD /api/path [body]` | Same as es-api + `kbn-xsrf: true` for POST/PUT/DELETE. Space-aware when `KIBANA_SPACE` is set |
| `es-check-env` | `${CLAUDE_PLUGIN_ROOT}/scripts/es-check-env` | Validates `.env` exists and required vars are set |

**Examples:**
```bash
# Check cluster health
${CLAUDE_PLUGIN_ROOT}/scripts/es-api GET /_cat/health

# Search an index
${CLAUDE_PLUGIN_ROOT}/scripts/es-api POST /my-index/_search '{"query":{"match_all":{}}}'

# Kibana saved objects (kbn-xsrf added automatically)
${CLAUDE_PLUGIN_ROOT}/scripts/kibana-api POST /api/saved_objects/_find '{"type":"dashboard"}'

# Pipe body from stdin
echo '{"query":{"match":{"message":"error"}}}' | ${CLAUDE_PLUGIN_ROOT}/scripts/es-api POST /logs/_search -
```

## Reference Documentation

### Always Read First
- `${CLAUDE_PLUGIN_ROOT}/docs/01-query-dsl.md` -- Bool queries, match, term, range, nested, function_score, multi_match

### Core Elasticsearch (read as needed)
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

## Critical Rules (Common Mistakes)

1. **Filter vs query context** -- Use `bool.filter` for exact matches (status, dates, IDs). Only use `must`/`should` when relevance scoring matters. Filters are cached and faster.
2. **No deep pagination with from/size** -- `from + size` cannot exceed 10,000. Use `search_after` with a PIT for anything deeper. Never use scroll for search UIs.
3. **Document types are gone** -- ES 8.x has no document types. The `_doc` in `PUT /index/_doc/id` is a fixed endpoint marker, not a type.
4. **Always set size: 0 for agg-only queries** -- If you only want aggregation results, set `"size": 0` to skip returning hits.
5. **keyword vs text** -- Use `keyword` for exact-match fields (status, IDs, names). Use `text` or `match_only_text` for full-text search. Never use `match` query on `keyword` fields or `term` query on `text` fields.
6. **Bulk API for batch operations** -- Never index documents one at a time. Always use `_bulk` with 5-15 MB batches. For data streams, use `create` action not `index`.
7. **NEST is legacy** -- The new .NET client is `Elastic.Clients.Elasticsearch`. NEST is for ES 7.x only. The new client uses `System.Text.Json`, not `Newtonsoft.Json`.
8. **kbn-xsrf header required** -- All Kibana API mutations (POST/PUT/DELETE) require the `kbn-xsrf: true` header. GET requests do not.
9. **ECS field names for logs** -- Use `@timestamp`, `message`, `log.level`, `service.name`, `trace.id` etc. ECS compliance enables cross-service correlation and Kibana dashboards.
10. **Data streams for time-series data** -- Always use data streams (not plain indices) for logs, metrics, and traces. They require `@timestamp` and are append-only.
