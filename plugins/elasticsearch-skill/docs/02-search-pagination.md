# Search API & Pagination

## Basic _search

```bash
GET /my-index/_search
POST /my-index/_search
POST /my-index-*/_search
POST /_search
```

```json
{
  "query": { "match": { "title": "elasticsearch" } },
  "from": 0,
  "size": 20,
  "sort": [
    { "created_at": "desc" },
    { "_score": "desc" }
  ],
  "_source": {
    "includes": ["title", "created_at", "status"],
    "excludes": ["body"]
  },
  "track_total_hits": true
}
```

| Parameter         | Default | Description                                              |
|-------------------|---------|----------------------------------------------------------|
| `from`            | `0`     | Starting offset                                          |
| `size`            | `10`    | Number of hits to return                                 |
| `track_total_hits`| `10000` | Set `true` for exact count; `false` to skip; or integer  |

## Response Structure

```json
{
  "took": 5,
  "timed_out": false,
  "_shards": { "total": 5, "successful": 5, "skipped": 0, "failed": 0 },
  "hits": {
    "total": { "value": 10000, "relation": "gte" },
    "max_score": 1.5,
    "hits": [
      {
        "_index": "my-index",
        "_id": "abc123",
        "_score": 1.5,
        "_source": { "title": "Elasticsearch Guide", "created_at": "2024-01-15" },
        "sort": [1705276800000, 1.5]
      }
    ]
  }
}
```

- `hits.total.relation`: `"eq"` = exact count; `"gte"` = lower bound (when `track_total_hits` < actual)
- `sort` array present only when `sort` is specified in request

## search_after Pagination

**Recommended for deep pagination.** Stateless, cursor-based.

### First request

```json
{
  "size": 20,
  "query": { "match_all": {} },
  "sort": [
    { "created_at": "desc" },
    { "_id": "asc" }
  ]
}
```

- **Always include a tiebreaker field** (`_id` or `_shard_doc`) as last sort criterion

### Subsequent requests

- Take the `sort` array from the **last hit** of the previous response

```json
{
  "size": 20,
  "query": { "match_all": {} },
  "sort": [
    { "created_at": "desc" },
    { "_id": "asc" }
  ],
  "search_after": [1705276800000, "abc123"]
}
```

- **Do not use `from` with `search_after`**

## Point-in-Time (PIT) API

**Provides a consistent snapshot for paginating through results that may change.**

### Open PIT

```bash
POST /my-index/_pit?keep_alive=5m
```

Response:

```json
{ "id": "46ToAwMDaWR..." }
```

### Search with PIT

```json
{
  "size": 100,
  "query": { "match_all": {} },
  "pit": {
    "id": "46ToAwMDaWR...",
    "keep_alive": "5m"
  },
  "sort": [
    { "created_at": "desc" },
    { "_shard_doc": "asc" }
  ]
}
```

- **Do not specify an index** in the URL when using PIT
- `_shard_doc` is the most efficient tiebreaker with PIT

### search_after + PIT

```json
{
  "size": 100,
  "query": { "match_all": {} },
  "pit": {
    "id": "46ToAwMDaWR...",
    "keep_alive": "5m"
  },
  "sort": [
    { "created_at": "desc" },
    { "_shard_doc": "asc" }
  ],
  "search_after": [1705276800000, 42]
}
```

### Close PIT

```bash
DELETE /_pit
```

```json
{ "id": "46ToAwMDaWR..." }
```

- **Always close PITs when done** -- they hold resources on every shard

## Scroll API (Legacy)

**Deprecated for search use cases. Use search_after + PIT instead.** Scroll is appropriate only for reindexing or bulk data export.

### Initial request

```bash
POST /my-index/_search?scroll=1m
```

```json
{ "size": 1000, "query": { "match_all": {} } }
```

Response includes `_scroll_id`.

### Scroll continuation

```bash
POST /_search/scroll
```

```json
{ "scroll": "1m", "scroll_id": "DXF1ZXJ5..." }
```

### Cleanup

```bash
DELETE /_search/scroll
```

```json
{ "scroll_id": "DXF1ZXJ5..." }
```

## Multi-Search API (_msearch)

- **NDJSON format** -- header line then body line, alternating
- Each search is independent

```bash
POST /my-index/_msearch
```

```
{"index": "my-index"}
{"query": {"match": {"title": "elasticsearch"}}, "size": 5}
{"index": "other-index"}
{"query": {"term": {"status": "active"}}, "size": 10}

```

- **Trailing newline required**

Response:

```json
{
  "responses": [
    { "took": 3, "hits": { "..." : "..." } },
    { "took": 2, "hits": { "..." : "..." } }
  ]
}
```

## Source Filtering

### _source includes/excludes

```json
{ "_source": { "includes": ["title", "metadata.*"], "excludes": ["body"] } }
```

### fields parameter (preferred for formatted retrieval)

```json
{
  "fields": [
    "title",
    { "field": "created_at", "format": "yyyy-MM-dd" },
    "metadata.*"
  ],
  "_source": false
}
```

- `fields` returns values from doc values and stored fields
- Supports wildcard patterns and format overrides
- Returned in a `fields` object per hit (values always arrays)

## Script Fields and Runtime Fields

### Script fields

```json
{
  "script_fields": {
    "price_with_tax": {
      "script": {
        "source": "doc['price'].value * params.tax_rate",
        "params": { "tax_rate": 1.2 }
      }
    }
  }
}
```

### Runtime fields (query-time)

```json
{
  "runtime_mappings": {
    "day_of_week": {
      "type": "keyword",
      "script": {
        "source": "emit(doc['@timestamp'].value.dayOfWeekEnum.getDisplayName(TextStyle.FULL, Locale.ROOT))"
      }
    }
  },
  "query": { "term": { "day_of_week": "Monday" } },
  "fields": ["day_of_week"]
}
```

## _count and _explain APIs

### _count

```bash
GET /my-index/_count
```

```json
{ "query": { "range": { "created_at": { "gte": "now-7d/d" } } } }
```

Response: `{ "count": 42, "_shards": { ... } }`

### _explain

```bash
GET /my-index/_explain/abc123
```

```json
{ "query": { "match": { "title": "elasticsearch" } } }
```

- Returns scoring breakdown for a specific document against a query

## Highlighting

```json
{
  "query": { "match": { "body": "elasticsearch tutorial" } },
  "highlight": {
    "pre_tags": ["<mark>"],
    "post_tags": ["</mark>"],
    "fields": {
      "body": {
        "fragment_size": 150,
        "number_of_fragments": 3
      },
      "title": {}
    }
  }
}
```

| Highlighter | Description                                        |
|-------------|----------------------------------------------------|
| `unified`   | **Default.** Best general-purpose highlighter      |
| `plain`     | Standard Lucene highlighter; works on any field    |
| `fvh`       | Fast Vector Highlighter; requires `term_vector: with_positions_offsets` in mapping |

## Suggesters

### Term suggester

```json
{
  "suggest": {
    "my-suggestion": {
      "text": "elasticsaerch",
      "term": { "field": "title" }
    }
  }
}
```

### Phrase suggester

```json
{
  "suggest": {
    "my-suggestion": {
      "text": "elasticsaerch tutoral",
      "phrase": {
        "field": "title.trigram",
        "confidence": 1.0,
        "max_errors": 2
      }
    }
  }
}
```

### Completion suggester

- Requires `completion` field type in mapping
- Supports context filtering (category, geo)

```json
{
  "suggest": {
    "my-suggestion": {
      "prefix": "elast",
      "completion": {
        "field": "title_suggest",
        "size": 5,
        "contexts": {
          "category": [{ "context": "tutorial" }]
        },
        "fuzzy": { "fuzziness": "AUTO" }
      }
    }
  }
}
```

## Field Collapsing

- Collapses results by a field value (like SQL `GROUP BY` for search results)

```json
{
  "query": { "match": { "body": "elasticsearch" } },
  "collapse": {
    "field": "category",
    "inner_hits": {
      "name": "top_per_category",
      "size": 3,
      "sort": [{ "_score": "desc" }]
    }
  },
  "sort": [{ "_score": "desc" }]
}
```

- `inner_hits` returns the top N docs per collapsed group
- Collapse field **must be a `keyword` or `numeric` type** with doc values

## Common Mistakes

- **`from` + `size` exceeding 10,000** -- default `index.max_result_window` is 10,000. Use `search_after` for deep pagination.
- **Not closing PIT handles** -- open PITs consume resources on every shard. Always close them in a `finally` block.
- **Using scroll API for user-facing search** -- scroll holds a snapshot context and does not support sorting by relevance. Use `search_after` + PIT instead.
- **Missing tiebreaker in sort** -- without a unique tiebreaker field (`_id` or `_shard_doc`), `search_after` may skip or duplicate documents.
- **`track_total_hits` default is 10,000** -- `hits.total.value` will cap at 10,000 with `relation: "gte"`. Set `track_total_hits: true` for exact counts (costs performance).
- **Using `_source` when `fields` is more appropriate** -- `fields` respects mapping formats and handles multi-fields cleanly.
