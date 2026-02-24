# Kibana Saved Objects & Data Views API

## Authentication Headers

| Header | Required | Description |
|--------|----------|-------------|
| `kbn-xsrf` | **POST, PUT, DELETE** | Any non-empty value (e.g., `true`). **Requests fail without this.** |
| `Content-Type` | All with body | `application/json` for JSON, `multipart/form-data` for import |
| `Authorization` | All | `ApiKey <base64>` or `Basic <base64(user:pass)>` |

## Base URL Patterns

- **Default space**: `https://<host>:5601/api/...`
- **Named space**: `https://<host>:5601/s/<space-id>/api/...`
- **All API calls are space-scoped** -- omitting `/s/<space-id>` targets the default space

## Saved Objects API

| Method | Endpoint | Parameters / Body |
|--------|----------|-------------------|
| GET | `/api/saved_objects/_find` | `type` (required), `search`, `search_fields`, `fields`, `page`, `per_page`, `sort_field`, `sort_order`, `has_reference`, `filter` |
| GET | `/api/saved_objects/<type>/<id>` | — |
| POST | `/api/saved_objects/<type>/<id>` | Body: `attributes`, `references`, `overwrite` |
| PUT | `/api/saved_objects/<type>/<id>` | Body: `attributes`, `references` |
| DELETE | `/api/saved_objects/<type>/<id>` | `force` (boolean) |
| POST | `/api/saved_objects/_bulk_create` | Body: array of `{ type, id, attributes, references }`, query: `overwrite` |
| POST | `/api/saved_objects/_bulk_get` | Body: array of `{ type, id }` |
| POST | `/api/saved_objects/_bulk_delete` | Body: array of `{ type, id }`, query: `force` |
| POST | `/api/saved_objects/_export` | Body: `type` (array), `objects` (array of `{type, id}`), `includeReferencesDeep` |
| POST | `/api/saved_objects/_import` | Multipart file upload, query: `overwrite`, `createNewCopies` |
| POST | `/api/saved_objects/_resolve_import_errors` | Body: `retries` array with `id`, `type`, `overwrite`, `replaceReferences` |

## Saved Object Types

| Type | Description |
|------|-------------|
| `dashboard` | Dashboard definition (panels, layout, filters) |
| `visualization` | Legacy visualizations (TSVB, Vega, Markdown) |
| `lens` | Lens visualization |
| `search` | Saved search (Discover) |
| `index-pattern` | Data view (legacy type name) |
| `map` | Elastic Maps |
| `tag` | Saved object tag |
| `query` | Saved query |
| `canvas-workpad` | Canvas workpad |
| `url` | Short URL |
| `config` | Kibana advanced settings |

## Data Views API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/data_views` | List all data views |
| GET | `/api/data_views/data_view/<id>` | Get single data view |
| POST | `/api/data_views/data_view` | Create data view |
| POST | `/api/data_views/data_view/<id>` | Update data view |
| DELETE | `/api/data_views/data_view/<id>` | Delete data view |
| POST | `/api/data_views/swap_references` | Remap data views across saved objects |
| GET | `/api/data_views/default` | Get default data view |
| POST | `/api/data_views/default` | Set default data view |

### Create Data View Body

```json
{
  "data_view": {
    "title": "logs-*",
    "name": "Logs",
    "timeFieldName": "@timestamp",
    "sourceFilters": [
      { "value": "meta.*" }
    ],
    "fieldFormats": {
      "bytes": { "id": "bytes", "params": { "pattern": "0.0b" } }
    },
    "runtimeFieldMap": {
      "duration_seconds": {
        "type": "double",
        "script": { "source": "emit(doc['duration_ms'].value / 1000.0)" }
      }
    }
  }
}
```

## Spaces API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/spaces/space` | List all spaces |
| POST | `/api/spaces/space` | Create space |
| GET | `/api/spaces/space/<id>` | Get space |
| PUT | `/api/spaces/space/<id>` | Update space |
| DELETE | `/api/spaces/space/<id>` | Delete space |
| POST | `/api/spaces/_copy_saved_objects` | Copy objects between spaces |
| POST | `/api/spaces/_resolve_copy_saved_objects_errors` | Resolve copy conflicts |

## RBAC

- Roles created via **Elasticsearch Security API** (`POST /_security/role/<name>`)
- Kibana privileges defined in the `kibana` section of the role body

```json
{
  "kibana": [
    {
      "spaces": ["default", "marketing"],
      "feature": {
        "discover": ["all"],
        "dashboard": ["read"],
        "visualize": ["all"]
      }
    },
    {
      "spaces": ["*"],
      "base": ["read"]
    }
  ]
}
```

- **`base`** privileges: `all`, `read` -- apply to all features in the space
- **`feature`** privileges: per-feature granularity (`all`, `read`, `minimal_all`, `minimal_read`)
- Feature names: `discover`, `dashboard`, `visualize`, `canvas`, `maps`, `ml`, `monitoring`, `siem`, `observability`, `fleet`, `stackAlerts`, `actions`, `advancedSettings`, `indexPatterns`, `savedObjectsManagement`, `dev_tools`

## Import / Export Patterns

- **Export format**: NDJSON (newline-delimited JSON), one saved object per line
- **Export by type**: set `type` array in body
- **Export specific objects**: set `objects` array with `{ type, id }` entries
- **`includeReferencesDeep: true`**: pulls all referenced objects (data views, tags, etc.)

### Version Control Workflow

1. Export dashboards with deep references
2. Commit NDJSON files to git
3. On target environment, import with `createNewCopies=false` and `overwrite=true`
4. Use `swap_references` API if data view IDs differ between environments

## Examples

### Find All Dashboards

```bash
curl -s -X GET "https://localhost:5601/api/saved_objects/_find?type=dashboard&per_page=100" \
  -H "Authorization: ApiKey $KIBANA_API_KEY" | jq '.saved_objects[] | {id, title: .attributes.title}'
```

### Create a Data View

```bash
curl -s -X POST "https://localhost:5601/api/data_views/data_view" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -H "Authorization: ApiKey $KIBANA_API_KEY" \
  -d '{
    "data_view": {
      "title": "metrics-*",
      "name": "Metrics",
      "timeFieldName": "@timestamp"
    }
  }'
```

### Export Dashboards

```bash
curl -s -X POST "https://localhost:5601/api/saved_objects/_export" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -H "Authorization: ApiKey $KIBANA_API_KEY" \
  -d '{
    "type": ["dashboard"],
    "includeReferencesDeep": true
  }' > dashboards.ndjson
```

### Import Dashboards

```bash
curl -s -X POST "https://localhost:5601/api/saved_objects/_import?overwrite=true" \
  -H "kbn-xsrf: true" \
  -H "Authorization: ApiKey $KIBANA_API_KEY" \
  -F file=@dashboards.ndjson
```

### Copy Objects to Another Space

```bash
curl -s -X POST "https://localhost:5601/api/spaces/_copy_saved_objects" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -H "Authorization: ApiKey $KIBANA_API_KEY" \
  -d '{
    "spaces": ["marketing"],
    "objects": [{ "type": "dashboard", "id": "abc-123" }],
    "includeReferences": true,
    "overwrite": true
  }'
```

## Common Mistakes

- **Forgetting `kbn-xsrf` header** on POST/PUT/DELETE -- returns `400 Bad Request` with no useful message
- **Using `createNewCopies=false` for environment migration** -- causes ID collisions; use `createNewCopies=true` when moving between unrelated clusters, `false` only for same-cluster space copies or git-based promotion
- **Broken references after import** -- always export with `includeReferencesDeep: true`; if data views have different IDs in target, use `swap_references` API or `_resolve_import_errors`
- **Not scoping API calls to the correct space** -- all saved object operations target the default space unless `/s/<space-id>/` is in the URL path
- **Using `index-pattern` type in Data Views API** -- the Data Views API uses its own endpoints (`/api/data_views/...`), not the saved objects API; the `index-pattern` type is the legacy saved object type
- **Exceeding `_find` default page size** -- default `per_page` is 20; set explicitly for bulk retrieval (max 10,000)
