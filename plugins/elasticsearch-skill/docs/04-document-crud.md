# Document CRUD & Bulk Operations

## Index (Create / Replace)

### Auto-generated ID

```bash
POST /my-index/_doc
```

```json
{ "title": "Elasticsearch Guide", "status": "published" }
```

### Specific ID (creates or replaces)

```bash
PUT /my-index/_doc/abc123
```

```json
{ "title": "Elasticsearch Guide", "status": "published" }
```

### Create only (409 on conflict)

```bash
PUT /my-index/_create/abc123
```

```json
{ "title": "Elasticsearch Guide", "status": "published" }
```

- Returns `409 Conflict` if document already exists
- Equivalent to `PUT /my-index/_doc/abc123?op_type=create`

### Response

```json
{
  "_index": "my-index",
  "_id": "abc123",
  "_version": 1,
  "result": "created",
  "_seq_no": 0,
  "_primary_term": 1
}
```

## Get Document

### Full document

```bash
GET /my-index/_doc/abc123
```

### With source filtering

```bash
GET /my-index/_doc/abc123?_source_includes=title,status
```

### Source only

```bash
GET /my-index/_source/abc123
```

### Existence check

```bash
HEAD /my-index/_doc/abc123
```

- Returns `200` if exists, `404` if not

### Multi-get

```bash
GET /my-index/_mget
```

```json
{
  "ids": ["abc123", "def456", "ghi789"]
}
```

Or with mixed indices:

```bash
GET /_mget
```

```json
{
  "docs": [
    { "_index": "my-index", "_id": "abc123" },
    { "_index": "other-index", "_id": "def456", "_source": ["title"] }
  ]
}
```

## Update

### Partial update (doc merge)

```bash
POST /my-index/_update/abc123
```

```json
{
  "doc": {
    "status": "archived",
    "archived_at": "2024-06-15T10:00:00Z"
  }
}
```

- Merges provided fields into existing `_source`
- **Does not remove fields** -- only adds or overwrites

### Scripted update (Painless)

```json
{
  "script": {
    "source": "ctx._source.views += params.count",
    "lang": "painless",
    "params": { "count": 1 }
  }
}
```

### Conditional logic in scripts

```json
{
  "script": {
    "source": """
      if (ctx._source.stock > 0) {
        ctx._source.stock -= 1;
      } else {
        ctx.op = 'noop';
      }
    """
  }
}
```

- `ctx.op = 'noop'` -- skip update, return `result: "noop"`
- `ctx.op = 'delete'` -- delete the document instead

### Upsert

```json
{
  "doc": { "views": 1 },
  "doc_as_upsert": true
}
```

- If document exists: merge `doc` fields
- If document does not exist: insert `doc` as new document

### Scripted upsert

```json
{
  "scripted_upsert": true,
  "script": {
    "source": """
      if (ctx.op == 'create') {
        ctx._source.views = 1;
      } else {
        ctx._source.views += 1;
      }
    """
  },
  "upsert": {}
}
```

## Optimistic Concurrency Control (OCC)

- Use `if_seq_no` and `if_primary_term` to prevent lost updates

### Read, then conditional write

```bash
GET /my-index/_doc/abc123
```

Response includes `_seq_no: 5` and `_primary_term: 1`.

```bash
PUT /my-index/_doc/abc123?if_seq_no=5&if_primary_term=1
```

```json
{ "title": "Updated Title", "status": "published" }
```

- Returns `409 Conflict` if another write occurred between read and write

### OCC on update

```bash
POST /my-index/_update/abc123?if_seq_no=5&if_primary_term=1
```

```json
{ "doc": { "status": "archived" } }
```

## Delete Document

```bash
DELETE /my-index/_doc/abc123
```

### With OCC

```bash
DELETE /my-index/_doc/abc123?if_seq_no=5&if_primary_term=1
```

## Bulk API

**NDJSON format** -- each action is 1-2 lines. No array wrapper, no trailing comma.

```bash
POST /_bulk
POST /my-index/_bulk
```

```json
{"index": {"_index": "my-index", "_id": "1"}}
{"title": "Doc 1", "status": "active"}
{"index": {"_index": "my-index", "_id": "2"}}
{"title": "Doc 2", "status": "active"}
{"create": {"_index": "my-index", "_id": "3"}}
{"title": "Doc 3", "status": "draft"}
{"update": {"_index": "my-index", "_id": "1"}}
{"doc": {"status": "archived"}}
{"delete": {"_index": "my-index", "_id": "2"}}

```

**Trailing newline required.**

### Actions

| Action   | Description                          | Body Required |
|----------|--------------------------------------|---------------|
| `index`  | Create or replace document           | Yes           |
| `create` | Create only (409 on conflict)        | Yes           |
| `update` | Partial update (doc or script)       | Yes           |
| `delete` | Delete document                      | No            |

### Single-index bulk

When targeting a single index, specify in URL and omit `_index` from actions:

```bash
POST /my-index/_bulk
```

```json
{"index": {"_id": "1"}}
{"title": "Doc 1"}
{"index": {"_id": "2"}}
{"title": "Doc 2"}

```

## Bulk Best Practices

| Recommendation                   | Details                                                      |
|----------------------------------|--------------------------------------------------------------|
| **Batch size**                   | 5-15 MB per request; benchmark to find optimal size          |
| **Check `errors` field**         | Response `"errors": true` means at least one action failed   |
| **Use `create` for data streams**| Data streams require `create`; `index` is not supported      |
| **Parallel requests**            | Send multiple bulk requests concurrently (2-4 threads)       |
| **Disable replicas for bulk load** | Set `number_of_replicas: 0` during initial load, restore after |
| **Increase refresh interval**    | `"refresh_interval": "-1"` during bulk load, reset after     |
| **Retry on 429**                 | `429 Too Many Requests` = back off and retry                 |

### Checking bulk response for errors

```json
{
  "took": 30,
  "errors": true,
  "items": [
    { "index": { "_id": "1", "status": 201, "result": "created" } },
    { "index": { "_id": "2", "status": 429, "error": { "type": "es_rejected_execution_exception" } } }
  ]
}
```

- **Always check `errors` field** -- a 200 HTTP response does not mean all actions succeeded
- Iterate `items` to find and retry individual failures

## Update by Query

```bash
POST /my-index/_update_by_query
```

```json
{
  "query": {
    "term": { "status": "draft" }
  },
  "script": {
    "source": "ctx._source.status = 'archived'",
    "lang": "painless"
  }
}
```

### With conflict handling

```bash
POST /my-index/_update_by_query?conflicts=proceed
```

- `conflicts=proceed` -- skip version conflicts instead of aborting

### Async execution

```bash
POST /my-index/_update_by_query?wait_for_completion=false
```

- Returns a `task` ID immediately
- Check progress: `GET /_tasks/<task_id>`
- Cancel: `POST /_tasks/<task_id>/_cancel`

## Delete by Query

```bash
POST /my-index/_delete_by_query
```

```json
{
  "query": {
    "range": { "created_at": { "lt": "now-90d/d" } }
  }
}
```

### With rate limiting

```bash
POST /my-index/_delete_by_query?scroll_size=500&requests_per_second=1000
```

| Parameter              | Default    | Description                          |
|------------------------|------------|--------------------------------------|
| `scroll_size`          | `1000`     | Docs per scroll batch                |
| `requests_per_second`  | `-1` (unlimited) | Throttle to N docs/sec         |
| `conflicts`            | `abort`    | `proceed` to skip conflicts          |
| `wait_for_completion`  | `true`     | Set `false` for async               |

## HTTP Methods Quick Reference

| Operation                  | Method | Endpoint                                 |
|----------------------------|--------|------------------------------------------|
| Index (auto ID)            | POST   | `/index/_doc`                            |
| Index (specific ID)        | PUT    | `/index/_doc/{id}`                       |
| Create only                | PUT    | `/index/_create/{id}`                    |
| Get document               | GET    | `/index/_doc/{id}`                       |
| Get source only            | GET    | `/index/_source/{id}`                    |
| Check existence            | HEAD   | `/index/_doc/{id}`                       |
| Partial update             | POST   | `/index/_update/{id}`                    |
| Delete                     | DELETE | `/index/_doc/{id}`                       |
| Bulk                       | POST   | `/_bulk` or `/index/_bulk`               |
| Multi-get                  | GET    | `/_mget` or `/index/_mget`              |
| Update by query            | POST   | `/index/_update_by_query`                |
| Delete by query            | POST   | `/index/_delete_by_query`                |

## Common Mistakes

- **Single-document indexing in loops** -- always use the Bulk API for multiple documents. Single-doc indexing has significant per-request overhead.
- **Not checking bulk response `errors` field** -- HTTP 200 does not mean all actions succeeded. Individual items can fail with 409, 429, or 500.
- **Using `index` instead of `create` for data streams** -- data streams require `op_type=create`. The `index` action will be rejected.
- **Not using OCC for concurrent updates** -- without `if_seq_no` / `if_primary_term`, concurrent updates cause last-write-wins. Use OCC or scripted updates for safe concurrency.
- **Forgetting `doc_as_upsert`** -- a partial update on a non-existent document returns 404 unless `doc_as_upsert: true` or `upsert` is provided.
- **Bulk request too large** -- requests over 100 MB risk HTTP timeouts and memory pressure. Stay in the 5-15 MB range.
