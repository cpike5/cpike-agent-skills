# Aggregations Reference

## Bucket Aggregations

### terms

```json
{
  "size": 0,
  "aggs": {
    "by_status": {
      "terms": {
        "field": "status",
        "size": 20,
        "min_doc_count": 1,
        "order": { "_count": "desc" }
      }
    }
  }
}
```

| Parameter       | Default        | Description                                      |
|-----------------|----------------|--------------------------------------------------|
| `size`          | `10`           | Number of buckets to return                      |
| `min_doc_count` | `1`            | Minimum docs for a bucket to appear              |
| `order`         | `{ "_count": "desc" }` | Sort by `_count`, `_key`, or sub-agg     |
| `missing`       | (excluded)     | Value for docs missing the field                 |
| `include`       | all            | Regex or array to include terms                  |
| `exclude`       | none           | Regex or array to exclude terms                  |

### date_histogram

```json
{
  "size": 0,
  "aggs": {
    "over_time": {
      "date_histogram": {
        "field": "created_at",
        "calendar_interval": "month",
        "format": "yyyy-MM",
        "min_doc_count": 0,
        "extended_bounds": {
          "min": "2024-01-01",
          "max": "2024-12-31"
        }
      }
    }
  }
}
```

| Interval Type       | Values                                       |
|---------------------|----------------------------------------------|
| `calendar_interval` | `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year` |
| `fixed_interval`    | `30s`, `1m`, `1h`, `7d` -- any fixed duration |

- `extended_bounds` -- include empty buckets within the specified range
- `min_doc_count: 0` -- required to show empty buckets

### range

```json
{
  "aggs": {
    "price_ranges": {
      "range": {
        "field": "price",
        "ranges": [
          { "key": "cheap", "to": 50 },
          { "key": "mid", "from": 50, "to": 200 },
          { "key": "expensive", "from": 200 }
        ]
      }
    }
  }
}
```

- `from` is inclusive, `to` is exclusive

### histogram

```json
{
  "aggs": {
    "price_dist": {
      "histogram": {
        "field": "price",
        "interval": 25,
        "min_doc_count": 1
      }
    }
  }
}
```

### filter

- Single filter bucket

```json
{
  "aggs": {
    "active_only": {
      "filter": { "term": { "status": "active" } },
      "aggs": {
        "avg_price": { "avg": { "field": "price" } }
      }
    }
  }
}
```

### filters

- Named multi-bucket filter

```json
{
  "aggs": {
    "by_level": {
      "filters": {
        "filters": {
          "errors": { "term": { "level": "error" } },
          "warnings": { "term": { "level": "warn" } }
        },
        "other_bucket_key": "other"
      }
    }
  }
}
```

### significant_terms

```json
{
  "query": { "term": { "category": "elasticsearch" } },
  "aggs": {
    "significant_tags": {
      "significant_terms": { "field": "tags", "size": 10 }
    }
  }
}
```

- Returns terms that are statistically unusual in the result set compared to the full index

### missing

```json
{
  "aggs": {
    "no_price": {
      "missing": { "field": "price" }
    }
  }
}
```

## Metric Aggregations

### Single-value metrics

```json
{
  "size": 0,
  "aggs": {
    "avg_price": { "avg": { "field": "price" } },
    "max_price": { "max": { "field": "price" } },
    "min_price": { "min": { "field": "price" } },
    "total_revenue": { "sum": { "field": "price" } },
    "doc_count": { "value_count": { "field": "price" } },
    "unique_users": {
      "cardinality": {
        "field": "user_id",
        "precision_threshold": 3000
      }
    }
  }
}
```

- **`cardinality`**: approximate count of distinct values
  - `precision_threshold` (default `3000`, max `40000`) -- below this threshold, counts are nearly exact
  - Memory usage: `precision_threshold * 8` bytes

### Multi-value metrics

```json
{
  "size": 0,
  "aggs": {
    "price_stats": { "stats": { "field": "price" } },
    "price_extended": { "extended_stats": { "field": "price" } },
    "price_percentiles": {
      "percentiles": {
        "field": "price",
        "percents": [50, 75, 90, 95, 99]
      }
    }
  }
}
```

- `stats` returns: `count`, `min`, `max`, `avg`, `sum`
- `extended_stats` adds: `sum_of_squares`, `variance`, `std_deviation`, `std_deviation_bounds`

### top_hits

```json
{
  "size": 0,
  "aggs": {
    "by_category": {
      "terms": { "field": "category", "size": 5 },
      "aggs": {
        "top_docs": {
          "top_hits": {
            "size": 3,
            "sort": [{ "created_at": "desc" }],
            "_source": ["title", "created_at"]
          }
        }
      }
    }
  }
}
```

## Nested Sub-Aggregations

- Bucket aggregations can contain sub-aggregations (both bucket and metric)

```json
{
  "size": 0,
  "aggs": {
    "by_category": {
      "terms": { "field": "category", "size": 10 },
      "aggs": {
        "monthly": {
          "date_histogram": {
            "field": "created_at",
            "calendar_interval": "month"
          },
          "aggs": {
            "total_revenue": { "sum": { "field": "price" } },
            "avg_price": { "avg": { "field": "price" } }
          }
        }
      }
    }
  }
}
```

## Pipeline Aggregations

- Operate on the output of other aggregations
- Specified as sibling or child of the source aggregation
- Reference other aggs via `buckets_path`

### derivative

```json
{
  "size": 0,
  "aggs": {
    "monthly_sales": {
      "date_histogram": {
        "field": "date",
        "calendar_interval": "month"
      },
      "aggs": {
        "total": { "sum": { "field": "amount" } },
        "total_deriv": {
          "derivative": { "buckets_path": "total" }
        }
      }
    }
  }
}
```

### cumulative_sum

```json
{
  "aggs": {
    "running_total": {
      "cumulative_sum": { "buckets_path": "total" }
    }
  }
}
```

### moving_fn

```json
{
  "aggs": {
    "moving_avg_sales": {
      "moving_fn": {
        "buckets_path": "total",
        "window": 5,
        "script": "MovingFunctions.unweightedAvg(values)"
      }
    }
  }
}
```

### bucket_script

```json
{
  "aggs": {
    "conversion_rate": {
      "bucket_script": {
        "buckets_path": {
          "purchases": "purchase_count",
          "visits": "visit_count"
        },
        "script": "params.purchases / params.visits"
      }
    }
  }
}
```

### bucket_selector

- Filters buckets based on a condition

```json
{
  "aggs": {
    "high_value_only": {
      "bucket_selector": {
        "buckets_path": { "total": "total_revenue" },
        "script": "params.total > 1000"
      }
    }
  }
}
```

### bucket_sort

```json
{
  "aggs": {
    "sort_by_revenue": {
      "bucket_sort": {
        "sort": [{ "total_revenue": { "order": "desc" } }],
        "size": 5
      }
    }
  }
}
```

### avg_bucket / max_bucket

- Sibling pipeline aggs -- operate across all buckets of a parent

```json
{
  "size": 0,
  "aggs": {
    "monthly_sales": {
      "date_histogram": {
        "field": "date",
        "calendar_interval": "month"
      },
      "aggs": {
        "total": { "sum": { "field": "amount" } }
      }
    },
    "avg_monthly_sales": {
      "avg_bucket": { "buckets_path": "monthly_sales>total" }
    },
    "best_month": {
      "max_bucket": { "buckets_path": "monthly_sales>total" }
    }
  }
}
```

- `>` separator navigates into nested aggs in `buckets_path`

## Composite Aggregation

**Paginates through all buckets.** Use when you need every bucket, not just top N.

### First request

```json
{
  "size": 0,
  "aggs": {
    "all_combos": {
      "composite": {
        "size": 1000,
        "sources": [
          { "category": { "terms": { "field": "category" } } },
          { "month": { "date_histogram": { "field": "created_at", "calendar_interval": "month" } } }
        ]
      },
      "aggs": {
        "total_revenue": { "sum": { "field": "price" } }
      }
    }
  }
}
```

### Subsequent requests

- Use `after_key` from previous response

```json
{
  "size": 0,
  "aggs": {
    "all_combos": {
      "composite": {
        "size": 1000,
        "sources": [
          { "category": { "terms": { "field": "category" } } },
          { "month": { "date_histogram": { "field": "created_at", "calendar_interval": "month" } } }
        ],
        "after": { "category": "electronics", "month": 1706745600000 }
      }
    }
  }
}
```

- **Stop paginating when `after_key` is absent** from response (no more buckets)

## Aggregations on Nested Fields

- **Must wrap in a `nested` aggregation** to reach nested object fields

```json
{
  "size": 0,
  "aggs": {
    "nested_comments": {
      "nested": { "path": "comments" },
      "aggs": {
        "top_authors": {
          "terms": { "field": "comments.author", "size": 10 }
        },
        "avg_rating": {
          "avg": { "field": "comments.rating" }
        }
      }
    }
  }
}
```

### reverse_nested (escape back to parent)

```json
{
  "aggs": {
    "nested_comments": {
      "nested": { "path": "comments" },
      "aggs": {
        "by_author": {
          "terms": { "field": "comments.author" },
          "aggs": {
            "back_to_root": {
              "reverse_nested": {},
              "aggs": {
                "avg_doc_price": { "avg": { "field": "price" } }
              }
            }
          }
        }
      }
    }
  }
}
```

## Response Structure

### terms aggregation response

```json
{
  "aggregations": {
    "by_status": {
      "doc_count_error_upper_bound": 0,
      "sum_other_doc_count": 150,
      "buckets": [
        { "key": "published", "doc_count": 500 },
        { "key": "draft", "doc_count": 120 },
        { "key": "archived", "doc_count": 80 }
      ]
    }
  }
}
```

- `sum_other_doc_count` -- docs in buckets not returned (due to `size` limit)
- `doc_count_error_upper_bound` -- max possible error in bucket counts

### stats aggregation response

```json
{
  "aggregations": {
    "price_stats": {
      "count": 700,
      "min": 1.99,
      "max": 999.99,
      "avg": 149.50,
      "sum": 104650.00
    }
  }
}
```

## Always Set size: 0 for Aggregation-Only Queries

```json
{
  "size": 0,
  "query": { "match_all": {} },
  "aggs": { "..." : "..." }
}
```

- **`size: 0`** skips fetching hits entirely -- significantly faster
- Without this, Elasticsearch fetches 10 hits by default (wasted work for agg-only requests)

## Common Mistakes

- **Forgetting `size: 0`** -- returns unnecessary hits alongside aggregation results. Wastes bandwidth and processing.
- **Using `terms` aggregation on high-cardinality fields** -- `terms` returns approximate results. With millions of unique values, counts become inaccurate and memory usage is high. Use `composite` aggregation for full enumeration.
- **Not using `composite` for full bucket enumeration** -- `terms` with large `size` is memory-intensive and still approximate. `composite` paginates through all buckets efficiently.
- **Missing `nested` agg wrapper for nested fields** -- aggregating directly on `comments.author` without the `nested` aggregation wrapper returns zero results. Always wrap with `nested: { "path": "comments" }`.
- **Pipeline agg `buckets_path` syntax** -- use `>` to navigate nested aggs (e.g., `monthly>total`), not `.` or `/`.
- **`terms` size vs query size** -- the `size` inside a `terms` agg controls the number of buckets, not the number of documents. Do not confuse with the top-level `size` parameter.
