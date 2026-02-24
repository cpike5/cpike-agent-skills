# Data Streams & Index Lifecycle Management

## Data Streams

- **What**: A named resource backed by auto-generated, hidden backing indices
- **When**: Time-series data with `@timestamp`, append-only workloads (logs, metrics, traces)
- **Naming convention**: `<type>-<dataset>-<namespace>` — e.g., `logs-myapp-production`
- **Backing index pattern**: `.ds-<name>-<generation>-<date>` — e.g., `.ds-logs-myapp-production-2024.01.15-000001`
- **Write index**: Always the most recent backing index; receives all new documents
- Documents **cannot be updated or deleted** in place — use `_delete_by_query` or `_update_by_query` with `op_type=index`

### Creating a Data Stream (Step-by-Step)

**Step 1: Create the ILM policy**

```json
PUT _ilm/policy/logs-myapp-policy
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_age": "1d",
            "max_primary_shard_size": "50gb"
          },
          "set_priority": { "priority": 100 }
        }
      },
      "warm": {
        "min_age": "2d",
        "actions": {
          "shrink": { "number_of_shards": 1 },
          "forcemerge": { "max_num_segments": 1 },
          "set_priority": { "priority": 50 }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "set_priority": { "priority": 0 },
          "allocate": {
            "number_of_replicas": 0
          }
        }
      },
      "frozen": {
        "min_age": "90d",
        "actions": {
          "searchable_snapshot": {
            "snapshot_repository": "my-s3-repo"
          }
        }
      },
      "delete": {
        "min_age": "365d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

**Step 2: Create component templates**

```json
PUT _component_template/logs-myapp-mappings
{
  "template": {
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" },
        "message": { "type": "match_only_text" },
        "log.level": { "type": "keyword" },
        "service.name": { "type": "keyword" },
        "trace.id": { "type": "keyword" },
        "error.stack_trace": { "type": "wildcard" }
      }
    }
  }
}
```

```json
PUT _component_template/logs-myapp-settings
{
  "template": {
    "settings": {
      "index.lifecycle.name": "logs-myapp-policy",
      "index.number_of_shards": 1,
      "index.number_of_replicas": 1,
      "index.codec": "best_compression"
    }
  }
}
```

**Step 3: Create the index template**

```json
PUT _index_template/logs-myapp
{
  "index_patterns": ["logs-myapp-*"],
  "data_stream": {},
  "composed_of": [
    "ecs@mappings",
    "logs-myapp-mappings",
    "logs-myapp-settings"
  ],
  "priority": 200
}
```

**Step 4: Index a document (creates the data stream)**

```json
POST logs-myapp-production/_doc
{
  "@timestamp": "2024-01-15T10:30:00.000Z",
  "message": "Order processed successfully",
  "log.level": "INFO",
  "service.name": "order-api"
}
```

## ILM Architecture

### Phase Overview

| Phase | Purpose | Typical Hardware | Key Actions |
|-------|---------|-----------------|-------------|
| **Hot** | Active indexing and search | NVMe SSD, high CPU/RAM | `rollover`, `set_priority` |
| **Warm** | Read-only, frequent search | SSD or HDD, moderate RAM | `shrink`, `forcemerge`, `readonly`, `set_priority` |
| **Cold** | Infrequent search | HDD, low RAM | `allocate` (reduce replicas), `set_priority` |
| **Frozen** | Rare search, lowest cost | Object storage (S3, GCS, Azure Blob) | `searchable_snapshot` |
| **Delete** | Data removal | N/A | `delete` |

### Transition Timing

- `min_age` is calculated from **index creation time** or **last rollover time**
- Each phase waits until `min_age` is satisfied **after the previous phase completes**
- **Hot phase**: `min_age` is typically `0ms`; rollover triggers phase transition
- Transitions are checked by ILM every **10 minutes** by default (`indices.lifecycle.poll_interval`)

## ILM Policy

### Rollover Conditions

| Condition | Type | Description |
|-----------|------|-------------|
| `max_age` | Trigger | Roll when index age exceeds value (`7d`, `30d`) |
| `max_primary_shard_size` | Trigger | Roll when largest primary shard exceeds size (`50gb`) |
| `max_size` | Trigger | Roll when total index size exceeds value |
| `max_docs` | Trigger | Roll when document count exceeds value |
| `min_primary_shard_size` | **Floor** | Do **not** roll until largest primary shard reaches this size |
| `min_age` | **Floor** | Do **not** roll until index is at least this old |
| `min_docs` | **Floor** | Do **not** roll until document count reaches this value |

- **Trigger conditions are OR'd** — any one being met triggers rollover
- **Floor conditions are AND'd with triggers** — all floors must be met before any trigger can fire
- **Recommended**: Use `max_primary_shard_size: "50gb"` as primary rollover condition

## ILM API Operations

```bash
# Create or update policy
PUT _ilm/policy/my-policy

# Get policy
GET _ilm/policy/my-policy

# Delete policy
DELETE _ilm/policy/my-policy

# Explain lifecycle state of an index
GET logs-myapp-production/_ilm/explain

# Retry failed step
POST logs-myapp-production/_ilm/retry

# Move to specific step (manual intervention)
POST _ilm/move/logs-myapp-production
{
  "current_step": {
    "phase": "hot",
    "action": "rollover",
    "name": "check-rollover-ready"
  },
  "next_step": {
    "phase": "warm",
    "action": "shrink",
    "name": "shrink"
  }
}
```

## Retention Strategies

| Strategy | Mechanism | Best For |
|----------|-----------|----------|
| **Time-based deletion** | ILM `delete` phase with `min_age` | Compliance-driven retention windows |
| **Size-based rollover** | `max_primary_shard_size` trigger | Controlling shard sizes for performance |
| **Tiered storage** | Hot → Warm → Cold allocation rules | Balancing cost and query performance |
| **Searchable snapshots** | Frozen phase with snapshot repository | Very old data that still needs rare access |
| **Snapshot and restore** | Snapshot to repository, delete indices | Archive data, restore on demand |
| **Per-source retention** | Separate data streams per source with different ILM policies | Different retention per team/app |

## Retention Tiers

| Tier | Age Range | Storage | Replicas | Notes |
|------|-----------|---------|----------|-------|
| **Hot** | 0–2 days | NVMe SSD | 1 | Active writes + fast queries |
| **Warm** | 2–30 days | SSD / HDD | 1 | Read-only, force-merged |
| **Cold** | 30–90 days | HDD | 0 | Reduced replicas, slower queries |
| **Frozen** | 90–365 days | Object storage | N/A | Searchable snapshots, on-demand hydration |
| **Delete** | >365 days | N/A | N/A | Permanent removal |

## Common Mistakes

- **Using plain indices instead of data streams for logs** — Plain indices require manual rollover management. Data streams handle this automatically.
- **Forgetting `@timestamp` field** — Data streams **require** `@timestamp`. Documents without it are rejected.
- **Not attaching ILM policy to index template** — The policy must be set in `index.lifecycle.name` in the template settings. Creating the policy alone does nothing.
- **Expecting update/delete to work on data streams** — Data streams are **append-only**. Use `_delete_by_query` or `_update_by_query` with `op_type=index` for corrections.
- **Assuming rollover conditions are AND'd** — Trigger conditions (`max_age`, `max_primary_shard_size`, `max_docs`) are **OR'd**. Any single trigger fires rollover. Only `min_*` conditions act as floors.
- **Setting `min_age` relative to "now"** — `min_age` in each phase is relative to **rollover time** (or index creation if no rollover), not the current time.
- **Forgetting `"data_stream": {}`** — The index template must include this empty object to enable data stream behavior. Without it, a regular index is created.
