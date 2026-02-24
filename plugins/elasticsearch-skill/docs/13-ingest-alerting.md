# Ingest Pipelines & Alerting

## Ingest Pipeline Processors

| Processor | Purpose | Performance |
|-----------|---------|-------------|
| `grok` | Pattern matching for unstructured text | Slower — uses regex |
| `dissect` | Token-based parsing for consistent formats | **Faster** — no regex |
| `date` | Parse date strings into `@timestamp` | Fast |
| `set` | Set field to static value or Mustache template | Fast |
| `rename` | Rename fields for ECS normalization | Fast |
| `remove` | Remove temporary or sensitive fields | Fast |
| `lowercase` | Lowercase field values | Fast |
| `script` | Painless code for complex transforms | Variable |
| `drop` | Conditionally drop entire documents | Fast |
| `pipeline` | Route to sub-pipeline | N/A |

### grok

- Parses unstructured text into structured fields using named regex patterns
- Uses `%{PATTERN:field_name}` syntax
- Built-in patterns: `IP`, `WORD`, `NUMBER`, `GREEDYDATA`, `TIMESTAMP_ISO8601`, `COMBINEDAPACHELOG`

```json
{
  "grok": {
    "field": "message",
    "patterns": [
      "%{COMBINEDAPACHELOG}"
    ]
  }
}
```

**Apache log result fields**: `clientip`, `ident`, `auth`, `timestamp`, `verb`, `request`, `httpversion`, `response`, `bytes`, `referrer`, `agent`

### date

```json
{
  "date": {
    "field": "timestamp",
    "formats": ["dd/MMM/yyyy:HH:mm:ss Z", "ISO8601"],
    "target_field": "@timestamp"
  }
}
```

### set

```json
{
  "set": {
    "field": "event.ingested",
    "value": "{{{_ingest.timestamp}}}"
  }
}
```

- **Mustache templates** use triple braces: `{{{field_name}}}`
- Access ingest metadata: `{{{_ingest.timestamp}}}`, `{{{_ingest.pipeline}}}`

### rename

```json
{
  "rename": {
    "field": "hostname",
    "target_field": "host.name",
    "ignore_missing": true
  }
}
```

### remove

```json
{
  "remove": {
    "field": ["_tmp_timestamp", "_tmp_raw"],
    "ignore_missing": true
  }
}
```

### script

```json
{
  "script": {
    "lang": "painless",
    "source": """
      if (ctx.http?.response?.status_code != null) {
        int code = ctx.http.response.status_code;
        if (code >= 500) {
          ctx.event.outcome = 'failure';
        } else {
          ctx.event.outcome = 'success';
        }
      }
    """
  }
}
```

### dissect

```json
{
  "dissect": {
    "field": "message",
    "pattern": "%{ts} %{log.level} [%{log.logger}] %{msg}"
  }
}
```

### drop

```json
{
  "drop": {
    "if": "ctx.log?.level == 'DEBUG'"
  }
}
```

### pipeline

```json
{
  "pipeline": {
    "name": "ecs-normalize",
    "if": "ctx.event?.category == 'web'"
  }
}
```

## Conditional Processing

- Every processor supports an `if` clause with a **Painless** expression
- **Always use the null-safe operator `?.`** to avoid NullPointerException

```json
{
  "set": {
    "field": "event.kind",
    "value": "alert",
    "if": "ctx.log?.level == 'ERROR' || ctx.log?.level == 'FATAL'"
  }
}
```

```json
{
  "grok": {
    "field": "message",
    "patterns": ["%{IP:source.ip} %{GREEDYDATA:message}"],
    "if": "ctx.message?.startsWith('{')==false",
    "ignore_failure": true
  }
}
```

## Pipeline API

```bash
# Create or update pipeline
PUT _ingest/pipeline/my-pipeline
{
  "description": "Parse application logs",
  "processors": [...]
}

# Get pipeline
GET _ingest/pipeline/my-pipeline

# Delete pipeline
DELETE _ingest/pipeline/my-pipeline

# Simulate pipeline with sample docs
POST _ingest/pipeline/my-pipeline/_simulate
{
  "docs": [
    {
      "_source": {
        "message": "192.168.1.1 - frank [10/Oct/2024:13:55:36 -0700] \"GET /index.html HTTP/1.1\" 200 2326"
      }
    }
  ]
}

# Inline simulate (no saved pipeline required)
POST _ingest/pipeline/_simulate
{
  "pipeline": {
    "processors": [
      { "grok": { "field": "message", "patterns": ["%{COMBINEDAPACHELOG}"] } }
    ]
  },
  "docs": [
    { "_source": { "message": "192.168.1.1 - - [10/Oct/2024:13:55:36 -0700] \"GET / HTTP/1.1\" 200 1234 \"-\" \"curl/7.68\"" } }
  ]
}
```

## Complete Log Parsing Pipeline Example

```json
PUT _ingest/pipeline/logs-myapp-pipeline
{
  "description": "Parse myapp application logs into ECS fields",
  "processors": [
    {
      "grok": {
        "field": "message",
        "patterns": [
          "%{TIMESTAMP_ISO8601:_tmp.timestamp} %{LOGLEVEL:log.level} \\[%{DATA:log.logger}\\] %{GREEDYDATA:message}"
        ],
        "ignore_failure": true
      }
    },
    {
      "date": {
        "field": "_tmp.timestamp",
        "formats": ["ISO8601"],
        "target_field": "@timestamp",
        "ignore_failure": true
      }
    },
    {
      "lowercase": {
        "field": "log.level",
        "ignore_failure": true
      }
    },
    {
      "set": {
        "field": "event.ingested",
        "value": "{{{_ingest.timestamp}}}"
      }
    },
    {
      "rename": {
        "field": "hostname",
        "target_field": "host.name",
        "ignore_missing": true
      }
    },
    {
      "remove": {
        "field": ["_tmp"],
        "ignore_missing": true
      }
    }
  ]
}
```

## Attaching Pipeline to Index Template

```json
PUT _component_template/logs-myapp-settings
{
  "template": {
    "settings": {
      "index.default_pipeline": "logs-myapp-pipeline",
      "index.lifecycle.name": "logs-myapp-policy"
    }
  }
}
```

- `index.default_pipeline` — applied when no pipeline is specified at index time
- `index.final_pipeline` — **always** applied, even if a request specifies a different pipeline

## Kibana Alerting Rules

### Rule Types

| Rule Type | Trigger | Best For |
|-----------|---------|----------|
| **Elasticsearch query** | KQL or ES|QL query returns results | Custom log-based alerts |
| **Log threshold** | Log count crosses threshold in time window | Log volume anomalies |
| **Anomaly detection** | ML job detects anomaly | Baseline deviation detection |
| **Index threshold** | Aggregation value crosses threshold | Metric-based alerts |

### Creating via Kibana UI

1. **Stack Management → Rules → Create rule**
2. Select rule type
3. Define query/conditions and threshold
4. Set check interval
5. Attach one or more **connectors** (actions)
6. Save

### Creating via API

```json
POST kbn:/api/alerting/rule
{
  "name": "High Error Rate",
  "rule_type_id": ".es-query",
  "consumer": "alerts",
  "schedule": { "interval": "5m" },
  "params": {
    "esQuery": "{\"query\":{\"bool\":{\"filter\":[{\"term\":{\"log.level\":\"ERROR\"}},{\"range\":{\"@timestamp\":{\"gte\":\"now-5m\"}}}]}}}",
    "index": ["logs-myapp-*"],
    "timeField": "@timestamp",
    "threshold": [10],
    "thresholdComparator": ">",
    "size": 100
  },
  "actions": [
    {
      "id": "slack-connector-id",
      "group": "query matched",
      "params": {
        "message": "Error rate exceeded threshold: {{context.value}} errors in 5 minutes"
      }
    }
  ],
  "tags": ["production", "error-rate"]
}
```

### Connectors

| Connector | Use Case | Setup |
|-----------|----------|-------|
| **Slack** | Team notifications | Webhook URL or Slack API token |
| **Email** | On-call alerts, reports | SMTP configuration in `kibana.yml` |
| **PagerDuty** | Incident escalation | Integration key |
| **Webhook** | Custom integrations | URL + headers + body template |

## Watcher (Legacy)

> **Use Kibana Alerting Rules for new implementations.** Watcher is maintained but not actively developed.

### Components

| Component | Purpose | Required |
|-----------|---------|----------|
| `trigger` | When to execute (schedule) | **Yes** |
| `input` | Data to load (search, HTTP, chain) | **Yes** |
| `condition` | Whether to act on the data | No (defaults to always) |
| `transform` | Reshape data before actions | No |
| `actions` | What to do (email, webhook, index, log) | **Yes** |

### Error Spike Watch Example

```json
PUT _watcher/watch/error-spike
{
  "trigger": {
    "schedule": { "interval": "5m" }
  },
  "input": {
    "search": {
      "request": {
        "indices": ["logs-myapp-*"],
        "body": {
          "size": 0,
          "query": {
            "bool": {
              "filter": [
                { "term": { "log.level": "ERROR" } },
                { "range": { "@timestamp": { "gte": "now-5m" } } }
              ]
            }
          }
        }
      }
    }
  },
  "condition": {
    "compare": {
      "ctx.payload.hits.total.value": { "gt": 50 }
    }
  },
  "actions": {
    "notify_webhook": {
      "webhook": {
        "method": "POST",
        "url": "https://hooks.example.com/alert",
        "headers": { "Content-Type": "application/json" },
        "body": "{\"text\": \"Error spike detected: {{ctx.payload.hits.total.value}} errors in 5 minutes\"}"
      }
    },
    "index_alert": {
      "index": {
        "index": "alerts-watcher",
        "doc_id": "error-spike-{{ctx.trigger.scheduled_time}}"
      }
    }
  }
}
```

## Common Alert Patterns

| Pattern | Rule Type | Condition | Interval |
|---------|-----------|-----------|----------|
| **Error rate threshold** | ES query | `log.level:ERROR` count > N in window | 5m |
| **Error spike** | Index threshold | Error count > 2x rolling average | 5m |
| **Missing logs** | ES query | 0 documents from `service.name` in window | 10m |
| **Slow responses** | Index threshold | `event.duration` p95 > threshold | 5m |
| **Security events** | ES query | `event.category:authentication AND event.outcome:failure` count > N | 1m |

## Common Mistakes

- **Not using null-safe operator `?.` in pipeline conditions** — `ctx.log.level` throws NullPointerException if `log` is missing. Always use `ctx.log?.level`.
- **Forgetting `ignore_failure` on optional processors** — If a grok pattern or rename doesn't match, the entire pipeline fails. Add `"ignore_failure": true` to processors that may not apply to every document.
- **Not simulating pipeline before deploying** — Always `POST _ingest/pipeline/<name>/_simulate` with representative sample documents before attaching to an index template.
- **Using Watcher for new implementations** — Watcher is legacy. **Use Kibana Alerting Rules** for new alert definitions — better UI, connector ecosystem, and active development.
- **Forgetting `ignore_missing` on rename/remove** — If the source field doesn't exist, the processor fails. Always set `"ignore_missing": true`.
- **Not attaching pipeline to index template** — Creating a pipeline does not activate it. Set `index.default_pipeline` in the index template settings.
