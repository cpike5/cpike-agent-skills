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

Wrapper scripts that handle auth headers, content-type, and base URLs. Requires a `.env` file at the plugin root.

### First-Time Setup

Before using the API scripts, walk the user through this setup:

1. **Copy the template:** `cp ${CLAUDE_PLUGIN_ROOT}/.env.example ${CLAUDE_PLUGIN_ROOT}/.env`
2. **Set `ES_URL`:** The Elasticsearch endpoint (e.g. `https://my-cluster.es.us-east-1.aws.found.io:9243` for Elastic Cloud, or `https://localhost:9200` for local). Ask the user for this value.
3. **Set `ES_API_KEY`:** A Base64-encoded API key. The user can generate one in Kibana at **Stack Management > API Keys > Create API key**, or via the ES API: `POST /_security/api_key { "name": "claude-code" }`. The response `encoded` field is the value to use.
4. **Set `KIBANA_URL`:** The Kibana endpoint (e.g. `https://my-cluster.kb.us-east-1.aws.found.io:9243` or `https://localhost:5601`). Only needed for Kibana API calls.
5. **Set `KIBANA_SPACE` (optional):** The Kibana space ID if not using the default space. Leave blank for the default space.
6. **Verify:** Run `${CLAUDE_PLUGIN_ROOT}/scripts/es-check-env` to confirm all required variables are set.
7. **Test connectivity:** Run `${CLAUDE_PLUGIN_ROOT}/scripts/es-api GET /_cat/health` to verify the connection works.

> **Important:** The `.env` file contains credentials and is git-ignored. Never commit it.

> **Tip:** Define a short alias at the start of your session to avoid repeating the full path:
> ```bash
> ES="${CLAUDE_PLUGIN_ROOT}/scripts"
> ```
> Then use `$ES/es-api`, `$ES/kibana-api`, etc.

| Script | Usage | Notes |
|--------|-------|-------|
| `es-api` | `$ES/es-api [METHOD] /path [body]` | Adds `Authorization: ApiKey` + `Content-Type: application/json`. METHOD is optional — infers GET (no body) or POST (with body) |
| `kibana-api` | `$ES/kibana-api [METHOD] /api/path [body]` | Same as es-api + `kbn-xsrf: true` for POST/PUT/DELETE. Space-aware when `KIBANA_SPACE` is set |
| `es-indices` | `$ES/es-indices [filter]` | Lists indices (`_cat/indices`). Optional filter greps by name |
| `es-datastreams` | `$ES/es-datastreams [filter]` | Lists data streams. Optional filter greps by name |
| `es-check-env` | `$ES/es-check-env` | Validates `.env` exists and required vars are set |

**Examples:**
```bash
ES="${CLAUDE_PLUGIN_ROOT}/scripts"

# Check cluster health (method inferred as GET)
$ES/es-api /_cat/health

# Search an index (method inferred as POST because body is provided)
$ES/es-api /my-index/_search '{"query":{"match_all":{}}}'

# Explicit method still works
$ES/es-api GET /_cat/health

# Kibana saved objects (kbn-xsrf added automatically)
$ES/kibana-api /api/saved_objects/_find '{"type":"dashboard"}'

# List all indices, or filter by name
$ES/es-indices
$ES/es-indices logs

# List data streams
$ES/es-datastreams

# Pipe body from stdin
echo '{"query":{"match":{"message":"error"}}}' | $ES/es-api POST /logs/_search -
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
