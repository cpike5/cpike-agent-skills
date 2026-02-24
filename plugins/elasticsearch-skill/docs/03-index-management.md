# Index Management

## Create Index

```bash
PUT /my-index
```

```json
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "refresh_interval": "30s",
    "analysis": {
      "analyzer": {
        "my_custom_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "asciifolding", "my_stemmer"]
        }
      },
      "filter": {
        "my_stemmer": {
          "type": "stemmer",
          "language": "english"
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "my_custom_analyzer",
        "fields": {
          "keyword": { "type": "keyword", "ignore_above": 256 }
        }
      },
      "status": { "type": "keyword" },
      "price": { "type": "float" },
      "created_at": { "type": "date", "format": "yyyy-MM-dd'T'HH:mm:ss.SSSZ||epoch_millis" },
      "tags": { "type": "keyword" },
      "location": { "type": "geo_point" },
      "metadata": { "type": "object" },
      "comments": {
        "type": "nested",
        "properties": {
          "author": { "type": "keyword" },
          "body": { "type": "text" }
        }
      }
    }
  }
}
```

## Common Field Types

| Type          | Use Case                          | Doc Values | Searchable | Aggregatable |
|---------------|-----------------------------------|------------|------------|--------------|
| `text`        | Full-text search (analyzed)       | No         | Yes        | No*          |
| `keyword`     | Exact values, sorting, aggs       | Yes        | Yes        | Yes          |
| `long`        | 64-bit integer                    | Yes        | Yes        | Yes          |
| `integer`     | 32-bit integer                    | Yes        | Yes        | Yes          |
| `float`       | 32-bit IEEE 754                   | Yes        | Yes        | Yes          |
| `double`      | 64-bit IEEE 754                   | Yes        | Yes        | Yes          |
| `date`        | Dates (ISO 8601 or epoch)         | Yes        | Yes        | Yes          |
| `boolean`     | `true` / `false`                  | Yes        | Yes        | Yes          |
| `geo_point`   | Lat/lon coordinates               | Yes        | Yes        | Yes          |
| `geo_shape`   | Arbitrary GeoJSON shapes          | No         | Yes        | Limited      |
| `ip`          | IPv4 and IPv6 addresses           | Yes        | Yes        | Yes          |
| `nested`      | Array of objects (independent)    | N/A        | Via nested query | Via nested agg |
| `object`      | JSON object (flattened)           | N/A        | Yes        | Depends on sub-fields |
| `flattened`   | Entire JSON object as keywords    | Yes        | Yes        | Yes          |
| `dense_vector`| Dense float vectors (kNN search)  | Yes        | Yes        | No           |

*`text` fields can use `fielddata: true` for aggs but this is **strongly discouraged** -- high memory usage.

## Multi-Fields

- Index the same data in multiple ways

```json
{
  "properties": {
    "title": {
      "type": "text",
      "analyzer": "standard",
      "fields": {
        "keyword": { "type": "keyword", "ignore_above": 256 },
        "english": { "type": "text", "analyzer": "english" }
      }
    }
  }
}
```

- Search: `match` on `title`, `term` on `title.keyword`, `match` on `title.english`
- Sort/agg: use `title.keyword`

## Get / Update Mappings

### Get

```bash
GET /my-index/_mapping
GET /my-index/_mapping/field/title
```

### Add new fields

```bash
PUT /my-index/_mapping
```

```json
{
  "properties": {
    "new_field": { "type": "keyword" }
  }
}
```

- **Cannot change the type of an existing field** -- must reindex to a new index
- Can add new fields, add multi-fields, update `ignore_above`

## Dynamic vs Static Settings

| Setting              | Dynamic | Description                                    |
|----------------------|---------|------------------------------------------------|
| `number_of_replicas` | Yes     | Change anytime                                 |
| `refresh_interval`   | Yes     | `-1` to disable; `1s` default                 |
| `max_result_window`  | Yes     | Default 10,000; controls from+size limit       |
| `number_of_shards`   | **No**  | Set at creation only; requires reindex to change |
| `analysis`           | **No**  | Analyzers set at creation only; close/open to add |
| `codec`              | **No**  | Compression codec set at creation only         |

```bash
PUT /my-index/_settings
```

```json
{ "index": { "refresh_interval": "30s", "number_of_replicas": 2 } }
```

## Aliases

### Create alias

```bash
POST /_aliases
```

```json
{
  "actions": [
    { "add": { "index": "my-index-v1", "alias": "my-index" } }
  ]
}
```

### Atomic swap (zero-downtime reindex)

```json
{
  "actions": [
    { "remove": { "index": "my-index-v1", "alias": "my-index" } },
    { "add": { "index": "my-index-v2", "alias": "my-index" } }
  ]
}
```

- **Atomic** -- both actions happen in a single cluster state update

### Filtered alias

```json
{
  "actions": [
    {
      "add": {
        "index": "logs",
        "alias": "logs-error",
        "filter": { "term": { "level": "error" } }
      }
    }
  ]
}
```

### Write alias

```json
{
  "actions": [
    { "add": { "index": "my-index-v2", "alias": "my-index", "is_write_index": true } }
  ]
}
```

## Composable Index Templates

**Applied automatically when an index name matches the `index_patterns`.**

```bash
PUT /_index_template/my-template
```

```json
{
  "index_patterns": ["logs-*"],
  "priority": 200,
  "composed_of": ["my-settings-component", "my-mappings-component"],
  "template": {
    "settings": {
      "number_of_shards": 3
    },
    "mappings": {
      "properties": {
        "message": { "type": "text" }
      }
    },
    "aliases": {
      "logs-current": {}
    }
  },
  "data_stream": {}
}
```

- `priority`: higher wins when multiple templates match
- `composed_of`: list of component templates applied in order
- `data_stream`: presence of this object makes matching indices data streams

## Component Templates

- Reusable building blocks for composable index templates

```bash
PUT /_component_template/my-settings-component
```

```json
{
  "template": {
    "settings": {
      "number_of_replicas": 1,
      "refresh_interval": "10s"
    }
  }
}
```

```bash
PUT /_component_template/my-mappings-component
```

```json
{
  "template": {
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" },
        "host": { "type": "keyword" }
      }
    }
  }
}
```

## Reindex API

### Basic reindex

```bash
POST /_reindex
```

```json
{
  "source": { "index": "my-index-v1" },
  "dest": { "index": "my-index-v2" }
}
```

### With query filter

```json
{
  "source": {
    "index": "my-index-v1",
    "query": { "term": { "status": "active" } }
  },
  "dest": { "index": "my-index-v2" }
}
```

### With script transform

```json
{
  "source": { "index": "my-index-v1" },
  "dest": { "index": "my-index-v2" },
  "script": {
    "source": "ctx._source.fullname = ctx._source.remove('first') + ' ' + ctx._source.remove('last')"
  }
}
```

### Async reindex

```bash
POST /_reindex?wait_for_completion=false
```

Returns a `task` ID. Check progress:

```bash
GET /_tasks/<task_id>
```

## Other Operations

### Delete index

```bash
DELETE /my-index
```

### Force merge (reduce segments)

```bash
POST /my-index/_forcemerge?max_num_segments=1
```

- **Only run on read-only indices** -- expensive operation

### Refresh

```bash
POST /my-index/_refresh
```

- Makes recent changes searchable immediately

### Flush

```bash
POST /my-index/_flush
```

## Cat APIs

| API               | Command                         | Description                      |
|--------------------|---------------------------------|----------------------------------|
| Indices            | `GET /_cat/indices?v&s=index`   | List all indices with stats      |
| Shards             | `GET /_cat/shards?v&s=index`    | Shard allocation per index       |
| Nodes              | `GET /_cat/nodes?v`             | Node stats (heap, CPU, disk)     |
| Health             | `GET /_cat/health?v`            | Cluster health summary           |
| Aliases            | `GET /_cat/aliases?v`           | All alias-to-index mappings      |
| Templates          | `GET /_cat/templates?v`         | Legacy templates (not composable)|
| Allocation         | `GET /_cat/allocation?v`        | Disk allocation per node         |
| Recovery           | `GET /_cat/recovery?v&active_only=true` | Active shard recoveries |

- `?v` = verbose (column headers)
- `?s=column` = sort by column
- `?format=json` = JSON output instead of tabular

## Cluster Health API

```bash
GET /_cluster/health
GET /_cluster/health/my-index
```

| Status   | Meaning                                                    |
|----------|------------------------------------------------------------|
| `green`  | All primary and replica shards assigned                    |
| `yellow` | All primaries assigned; some replicas unassigned           |
| `red`    | Some primary shards unassigned -- **data loss risk**       |

```json
{
  "cluster_name": "my-cluster",
  "status": "green",
  "number_of_nodes": 3,
  "number_of_data_nodes": 3,
  "active_primary_shards": 15,
  "active_shards": 30,
  "unassigned_shards": 0
}
```

## Common Mistakes

- **Changing an existing field's type** -- not possible. Must create a new index with the correct mapping and reindex data. Use aliases to make this transparent.
- **Not using aliases for zero-downtime migration** -- without aliases, clients must update their index name during reindex. Aliases make the swap atomic.
- **Dynamic mapping in production** -- any new field is automatically mapped. Leads to mapping explosions (thousands of fields). Set `"dynamic": "strict"` or `"dynamic": "false"` in production.
- **Too many shards for small indices** -- each shard has overhead. Aim for 10-50 GB per shard. A single-shard index is fine for small data.
- **Running force merge on active write indices** -- force merge competes with indexing. Only use on read-only / rolled-over indices.
- **Forgetting `close`/`open` to add analyzers** -- analysis settings are static. Must close index, update settings, reopen.
