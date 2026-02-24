# Query DSL Reference

## Bool Query

- Combines multiple clauses with boolean logic
- **`filter` context does not score** -- use for exact matches, ranges, existence checks

| Occurrence   | Behavior                              | Scoring |
|--------------|---------------------------------------|---------|
| `must`       | Clause must match                     | Yes     |
| `filter`     | Clause must match                     | No      |
| `should`     | At least one should match (see below) | Yes     |
| `must_not`   | Clause must not match                 | No      |

- `should` with no `must`/`filter`: at least 1 clause must match (default `minimum_should_match: 1`)
- `should` with `must`/`filter` present: 0 required unless `minimum_should_match` set

```json
{
  "query": {
    "bool": {
      "must": [
        { "match": { "title": "elasticsearch" } }
      ],
      "filter": [
        { "term": { "status": "published" } },
        { "range": { "created_at": { "gte": "now-30d/d" } } }
      ],
      "should": [
        { "term": { "featured": true } },
        { "match": { "tags": "tutorial" } }
      ],
      "must_not": [
        { "term": { "archived": true } }
      ],
      "minimum_should_match": 1
    }
  }
}
```

## Full-Text Queries

### match

```json
{
  "query": {
    "match": {
      "title": {
        "query": "quick brown fox",
        "operator": "and",
        "fuzziness": "AUTO",
        "minimum_should_match": "75%"
      }
    }
  }
}
```

| Parameter              | Default   | Description                                      |
|------------------------|-----------|--------------------------------------------------|
| `operator`             | `or`      | `or` = any term matches; `and` = all must match  |
| `fuzziness`            | none      | `AUTO`, `0`, `1`, `2` -- edit distance           |
| `minimum_should_match` | `1`       | Number or percentage of terms that must match     |
| `analyzer`             | field default | Override analyzer at query time               |
| `lenient`              | `false`   | Ignore type mismatches                           |

### match_phrase

- All terms must appear **in order** with no gaps (unless `slop` set)

```json
{ "query": { "match_phrase": { "title": { "query": "quick brown fox", "slop": 1 } } } }
```

### match_phrase_prefix

- Like `match_phrase` but last term is treated as a prefix
- **`max_expansions`** controls how many prefix expansions (default 50)

```json
{ "query": { "match_phrase_prefix": { "title": { "query": "quick bro", "max_expansions": 10 } } } }
```

## multi_match

```json
{
  "query": {
    "multi_match": {
      "query": "elasticsearch guide",
      "fields": ["title^3", "description^2", "body"],
      "type": "best_fields",
      "tie_breaker": 0.3,
      "fuzziness": "AUTO"
    }
  }
}
```

| Type           | Behavior                                                        |
|----------------|-----------------------------------------------------------------|
| `best_fields`  | Score from best matching field; `tie_breaker` blends others     |
| `most_fields`  | Scores from all fields combined                                 |
| `cross_fields` | Term-centric; analyzes as if one big field; **requires same analyzer** |
| `phrase`        | Runs `match_phrase` on each field, takes best                  |
| `phrase_prefix` | Runs `match_phrase_prefix` on each field, takes best          |

- **Field boosting**: `"title^3"` multiplies that field's score by 3

## Term-Level Queries

**Term-level queries operate on exact values. Do not use on `text` fields.**

### term / terms

```json
{ "query": { "term": { "status": { "value": "published" } } } }
```

```json
{ "query": { "terms": { "status": ["published", "draft"] } } }
```

### terms lookup

- Fetch term values from another document

```json
{
  "query": {
    "terms": {
      "user_id": {
        "index": "permissions",
        "id": "admin_group",
        "path": "members"
      }
    }
  }
}
```

### range

```json
{
  "query": {
    "range": {
      "created_at": {
        "gte": "now-1d/d",
        "lte": "now/d",
        "format": "yyyy-MM-dd||epoch_millis"
      }
    }
  }
}
```

| Operator | Meaning                |
|----------|------------------------|
| `gt`     | Greater than           |
| `gte`    | Greater than or equal  |
| `lt`     | Less than              |
| `lte`    | Less than or equal     |

- **Date math**: `now-1d/d` = yesterday rounded to start of day; `now-1M` = one month ago; `now/M` = start of current month

### exists

```json
{ "query": { "exists": { "field": "email" } } }
```

### prefix

```json
{ "query": { "prefix": { "username": { "value": "adm" } } } }
```

### wildcard

```json
{ "query": { "wildcard": { "hostname": { "value": "server-*-prod" } } } }
```

- `*` matches any characters; `?` matches one character
- **Avoid leading wildcards** -- extremely slow

### regexp

```json
{ "query": { "regexp": { "code": { "value": "ERR-[0-9]{3,5}", "flags": "ALL" } } } }
```

### ids

```json
{ "query": { "ids": { "values": ["1", "2", "100"] } } }
```

### fuzzy

```json
{ "query": { "fuzzy": { "username": { "value": "elastisearch", "fuzziness": "AUTO" } } } }
```

## Nested Query

**Required when the field mapping is `type: nested`.** Standard queries cannot reach inside nested objects.

### Mapping

```json
{
  "mappings": {
    "properties": {
      "comments": {
        "type": "nested",
        "properties": {
          "author": { "type": "keyword" },
          "body": { "type": "text" },
          "rating": { "type": "integer" }
        }
      }
    }
  }
}
```

### Query

```json
{
  "query": {
    "nested": {
      "path": "comments",
      "query": {
        "bool": {
          "must": [
            { "match": { "comments.body": "elasticsearch" } },
            { "range": { "comments.rating": { "gte": 4 } } }
          ]
        }
      },
      "score_mode": "max",
      "inner_hits": {
        "size": 3,
        "_source": ["comments.author", "comments.body"]
      }
    }
  }
}
```

| score_mode | Behavior                                  |
|------------|-------------------------------------------|
| `avg`      | Average of all matching nested docs       |
| `max`      | Highest score among matching nested docs  |
| `min`      | Lowest score among matching nested docs   |
| `sum`      | Sum of all matching nested doc scores     |
| `none`     | Do not use nested doc scores              |

## query_string and simple_query_string

### query_string

- Supports full Lucene syntax: `AND`, `OR`, `NOT`, `field:value`, wildcards, regex, grouping
- **Throws errors on invalid syntax**

```json
{
  "query": {
    "query_string": {
      "query": "(title:elasticsearch OR title:opensearch) AND status:published",
      "default_field": "body",
      "default_operator": "AND"
    }
  }
}
```

### simple_query_string

- Simplified syntax; **never throws parse errors** (discards invalid parts)
- Operators: `+` (AND), `|` (OR), `-` (NOT), `"` (phrase), `*` (prefix), `~N` (fuzziness/slop), `()` (precedence)

```json
{
  "query": {
    "simple_query_string": {
      "query": "elasticsearch +tutorial -beginner",
      "fields": ["title^3", "body"],
      "default_operator": "and"
    }
  }
}
```

## function_score

```json
{
  "query": {
    "function_score": {
      "query": { "match": { "title": "elasticsearch" } },
      "functions": [
        {
          "filter": { "term": { "featured": true } },
          "weight": 10
        },
        {
          "gauss": {
            "created_at": {
              "origin": "now",
              "scale": "10d",
              "offset": "2d",
              "decay": 0.5
            }
          }
        },
        {
          "field_value_factor": {
            "field": "likes",
            "factor": 1.2,
            "modifier": "log1p",
            "missing": 1
          }
        }
      ],
      "score_mode": "sum",
      "boost_mode": "multiply",
      "max_boost": 42
    }
  }
}
```

| Parameter    | Values                                        | Default    |
|--------------|-----------------------------------------------|------------|
| `score_mode` | `multiply`, `sum`, `avg`, `first`, `max`, `min` | `multiply` |
| `boost_mode` | `multiply`, `replace`, `sum`, `avg`, `max`, `min` | `multiply` |
| `modifier` (field_value_factor) | `none`, `log`, `log1p`, `log2p`, `ln`, `ln1p`, `ln2p`, `sqrt`, `square`, `reciprocal` | `none` |

## Boosting Query

- Demotes documents matching `negative` without excluding them

```json
{
  "query": {
    "boosting": {
      "positive": { "match": { "title": "elasticsearch" } },
      "negative": { "term": { "status": "deprecated" } },
      "negative_boost": 0.2
    }
  }
}
```

- `negative_boost` must be between `0` and `1.0`
- Final score = positive score * `negative_boost` for docs matching negative clause

## Common Mistakes

- **Using `match` on `keyword` fields** -- `match` runs an analyzer; keyword fields store exact values. Use `term` for keyword fields.
- **Using `term` on `text` fields** -- `text` fields are analyzed at index time (lowercased, stemmed). A `term` query for `"Elasticsearch"` will not match the indexed token `"elasticsearch"`. Use `match` instead.
- **Forgetting `nested` query for nested objects** -- queries against `nested` type fields silently return no results without the `nested` query wrapper.
- **Not using `filter` context for non-scoring conditions** -- putting range/term filters in `must` wastes CPU on scoring. Use `filter` for any clause where relevance score is irrelevant.
- **Leading wildcards in `wildcard` queries** -- `*suffix` scans every term in the index. Extremely slow on large indices.
- **Confusing `minimum_should_match` behavior** -- only applies when `should` clauses have no sibling `must`/`filter` clauses, unless explicitly set.
