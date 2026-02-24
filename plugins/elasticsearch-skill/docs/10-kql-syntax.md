# KQL & Query Syntax

## KQL (Kibana Query Language)

### Field Matching

```
field: value
field: "exact phrase"
field: (value1 or value2)
```

### Boolean Operators

```
status: 200 AND method: GET
status: 404 OR status: 500
NOT status: 200
(status: 404 OR status: 500) AND method: POST
```

- **Operator precedence**: `NOT` > `AND` > `OR`
- **Always use parentheses** to make OR grouping explicit

### Wildcards

```
message: err*
host.name: *prod*
field: web-server-??
```

- `*` matches zero or more characters
- **No regex support in KQL**

### Range

```
response_time >= 200
response_time < 500
bytes > 1000 AND bytes <= 5000
```

### Nested Field Queries

```
items: { name: "widget" and price > 10 }
```

- For `nested` field type mappings only
- Uses lowercase `and` / `or` inside nested scope

### Exists Check

```
field: *
```

- Returns documents where `field` has any value
- Equivalent to an exists query

### Special Character Escaping

| Character | Escaped |
|-----------|---------|
| `\` | `\\` |
| `(` | `\(` |
| `)` | `\)` |
| `:` | `\:` |
| `<` | `\<` |
| `>` | `\>` |
| `"` | `\"` |
| `*` | `\*` |
| `{` | `\{` |
| `}` | `\}` |

## KQL vs Lucene Comparison

| Feature | KQL | Lucene |
|---------|-----|--------|
| **Default operator** | OR | OR |
| **Field matching** | `field: value` | `field:value` |
| **Phrase** | `field: "foo bar"` | `field:"foo bar"` |
| **Wildcards** | `field: err*` | `field:err*` |
| **Regex** | Not supported | `field:/[a-z]+/` |
| **Fuzzy** | Not supported | `field:term~2` |
| **Proximity** | Not supported | `field:"foo bar"~3` |
| **Boosting** | Not supported | `field:term^2` |
| **Range** | `field >= 10` | `field:[10 TO *]` |
| **Exists** | `field: *` | `_exists_:field` |
| **Nested** | `items: { name: "x" }` | Not natively supported |
| **Boolean** | `AND`, `OR`, `NOT` | `AND`, `OR`, `NOT`, `+`, `-` |
| **Grouping** | `(a OR b)` | `(a OR b)` |
| **Scripted fields** | Supported | Supported |

## Lucene Syntax Quick Reference

```
# Regex
message:/err[ou]r/

# Fuzzy (edit distance)
message:quikc~2

# Proximity (words within N positions)
message:"quick fox"~3

# Boosting
title:important^2

# Range (inclusive)
status:[200 TO 299]

# Range (exclusive)
bytes:{1000 TO 5000}

# Range (mixed)
age:[18 TO *}

# Required / excluded
+status:200 -method:DELETE

# Wildcard (single char)
host:web-0?
```

## Filters vs KQL in Kibana

| Aspect | Filters (structured) | KQL (text) |
|--------|---------------------|------------|
| **Format** | JSON query DSL | Text string |
| **Caching** | **Cached by Elasticsearch** (bitset) | Analyzed per query |
| **Toggle** | Individual enable/disable/pin/negate | Entire query bar |
| **UI** | Filter pills below query bar | Query bar text |
| **Combine with** | Combined via bool/filter clause | Combined via bool/must |
| **Performance** | Better for repeated, static conditions | Better for ad-hoc text search |
| **Pinning** | Can pin across dashboards in session | Not pinnable |

- **Best practice**: use filters for reusable conditions (environment, team, status), KQL for ad-hoc investigation

## Using KQL in API Calls

### In searchSourceJSON (Saved Objects)

```json
{
  "query": {
    "query": "log.level: error AND service.name: api-gateway",
    "language": "kuery"
  },
  "filter": [
    {
      "meta": {
        "index": "data-view-id",
        "negate": false,
        "disabled": false,
        "alias": null,
        "type": "phrase",
        "key": "environment",
        "params": { "query": "production" }
      },
      "query": {
        "match_phrase": { "environment": "production" }
      }
    }
  ]
}
```

### In Elasticsearch _search API

- KQL is **not natively supported** by Elasticsearch `_search`
- Kibana translates KQL to query DSL before sending to Elasticsearch
- For direct ES API calls, use query DSL:

```json
{
  "query": {
    "bool": {
      "must": [
        { "match_phrase": { "log.level": "error" } },
        { "match_phrase": { "service.name": "api-gateway" } }
      ]
    }
  }
}
```

### Filter Structure in searchSourceJSON

```json
{
  "filter": [
    {
      "meta": {
        "index": "<data-view-id>",
        "negate": false,
        "disabled": false,
        "alias": "Custom Label",
        "type": "phrase",
        "key": "<field>",
        "params": { "query": "<value>" }
      },
      "query": {
        "match_phrase": { "<field>": "<value>" }
      }
    }
  ]
}
```

**Filter `meta.type` values**: `phrase`, `phrases`, `range`, `exists`, `geo_bounding_box`, `geo_polygon`

### language Values

| Value | Description |
|-------|-------------|
| `kuery` | KQL (default in 8.x) |
| `lucene` | Lucene query syntax |

## Common Mistakes

- **Using Lucene syntax in KQL mode** -- regex (`/pattern/`), fuzzy (`~`), proximity, boosting are **Lucene-only**; KQL silently treats them as literal text
- **Forgetting to escape special characters** -- unescaped `:`, `(`, `)` in field values cause parse errors; use `\:`, `\(`, `\)`
- **OR precedence without parentheses** -- `status: 200 OR status: 404 AND method: GET` evaluates as `status: 200 OR (status: 404 AND method: GET)`, not `(status: 200 OR status: 404) AND method: GET`
- **Assuming KQL supports regex** -- use Lucene mode or Elasticsearch query DSL for regex matching
- **Using `language: "kql"`** instead of **`language: "kuery"`** -- the API value is `kuery`, not `kql`
- **Quoting numeric values** -- `status: "200"` performs text match; `status: 200` performs numeric match; behavior depends on field mapping
- **Nested query syntax outside nested fields** -- `items: { field: value }` only works on fields mapped as `nested` type; for object fields, use dot notation: `items.field: value`
