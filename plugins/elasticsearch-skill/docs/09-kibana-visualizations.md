# Kibana Dashboards & Visualizations

## Dashboard JSON Structure

A dashboard saved object has these key `attributes`:

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Dashboard name |
| `panelsJSON` | string (JSON array) | Panel definitions, positions, configurations |
| `optionsJSON` | string (JSON object) | Dashboard display options |
| `kibanaSavedObjectMeta.searchSourceJSON` | string (JSON object) | Dashboard-level query, filter, index |
| `timeRestore` | boolean | Restore saved time range on load |
| `timeTo` / `timeFrom` | string | Saved time range (e.g., `now-15m`, `now`) |
| `refreshInterval` | object | `{ pause: bool, value: ms }` |

Top-level `references` array links panels to their saved objects.

### panelsJSON Panel Entry

```json
{
  "type": "lens",
  "gridData": { "x": 0, "y": 0, "w": 24, "h": 15, "i": "panel_1" },
  "panelIndex": "panel_1",
  "embeddableConfig": {
    "title": "Request Rate",
    "hidePanelTitles": false,
    "enhancements": {},
    "attributes": {}
  },
  "panelRefName": "panel_panel_1"
}
```

- **Grid**: 48 units wide, unlimited height
- **`gridData.i`** must match **`panelIndex`**
- **`panelRefName`** links to the `references` array entry by `name` field
- **Inline panels** embed full config in `embeddableConfig.attributes` (no `panelRefName`)

### optionsJSON

```json
{
  "useMargins": true,
  "syncColors": true,
  "syncCursor": true,
  "syncTooltips": true,
  "hidePanelTitles": false
}
```

### references Array

```json
[
  {
    "name": "panel_panel_1",
    "type": "lens",
    "id": "abc-123-lens-id"
  },
  {
    "name": "panel_panel_2:indexpattern-datasource-layer-layer1",
    "type": "index-pattern",
    "id": "data-view-id"
  }
]
```

## Panel Types

| Type | Description |
|------|-------------|
| `lens` | Primary visualization type (charts, metrics, tables) |
| `visualization` | Legacy visualizations (TSVB, Vega, Markdown, etc.) |
| `search` | Embedded saved search from Discover |
| `map` | Elastic Maps |
| `links` | Dashboard links panel |
| `ml_anomaly_swimlane` | ML anomaly swimlane |
| `ml_anomaly_chart` | ML anomaly chart |

## Lens Visualization Architecture

### visualizationType Values

| Value | Chart |
|-------|-------|
| `lnsXY` | XY chart (bar, line, area) |
| `lnsPie` | Pie, donut, treemap, mosaic, waffle |
| `lnsMetric` | Single metric / trend metric |
| `lnsDatatable` | Data table |
| `lnsGauge` | Gauge (arc, circle, semi-circle) |
| `lnsHeatmap` | Heatmap |
| `lnsTagcloud` | Tag cloud |

### XY Series Types

| Series Type | Description |
|-------------|-------------|
| `bar` | Vertical bar |
| `bar_stacked` | Stacked vertical bar |
| `bar_horizontal` | Horizontal bar |
| `bar_horizontal_stacked` | Stacked horizontal bar |
| `line` | Line |
| `area` | Area |
| `area_stacked` | Stacked area |
| `bar_percentage_stacked` | 100% stacked bar |
| `area_percentage_stacked` | 100% stacked area |

### Datasource State Structure

- Located at `state.datasourceStates`
- **All three datasource siblings must be present**: `formBased`, `indexpattern`, `textBased`
- Layers are keyed by `layerId` (UUID), each containing `columns` keyed by `columnId` (UUID)
- **Each layer MUST include** `indexPatternId` and `ignoreGlobalFilters` — omitting either causes silent render failure

```json
{
  "state": {
    "datasourceStates": {
      "formBased": {
        "layers": {
          "layer1-uuid": {
            "columns": {
              "col1-uuid": {
                "label": "@timestamp per 30 seconds",
                "dataType": "date",
                "operationType": "date_histogram",
                "sourceField": "@timestamp",
                "isBucketed": true,
                "scale": "interval",
                "params": { "interval": "30s" }
              },
              "col2-uuid": {
                "label": "Count of records",
                "dataType": "number",
                "operationType": "count",
                "isBucketed": false,
                "scale": "ratio",
                "sourceField": "___records___"
              }
            },
            "columnOrder": ["col1-uuid", "col2-uuid"],
            "incompleteColumns": {},
            "indexPatternId": "data-view-id",
            "ignoreGlobalFilters": false,
            "sampling": 1
          }
        }
      },
      "indexpattern": { "layers": {} },
      "textBased": { "layers": {} }
    }
  }
}
```

### operationType Values

| Category | Operations |
|----------|-----------|
| **Bucket** | `date_histogram`, `terms`, `filters`, `range`, `intervals` |
| **Metric** | `count`, `sum`, `avg`, `min`, `max`, `unique_count`, `median`, `percentile`, `last_value` |
| **Pipeline** | `cumulative_sum`, `counter_rate`, `moving_average`, `differences` |
| **Calculated** | `formula`, `static_value`, `math` |

- **`terms`** columns use `params.size`, `params.orderBy`, `params.orderDirection`
- **`percentile`** columns use `params.percentile` (e.g., `95`)
- **`formula`** columns use `params.formula` (e.g., `count() / overall_sum(count())`) — **AVOID in API-created dashboards**. Formulas require hidden sub-columns (suffixed `X0`, `X1`) with `references` arrays and `tinymathAst` objects that are internal structures generated by the Kibana UI. Use native operations (`average`, `percentile`, `count`, `terms`) instead.

### Column Builder Quick Reference

| Operation | `scale` | Key `params` |
|-----------|---------|-------------|
| `date_histogram` | `interval` | `interval`, `includeEmptyRows`, `dropPartials` |
| `count` | `ratio` | `emptyAsNull` |
| `average` | `ratio` | `emptyAsNull` |
| `percentile` | `ratio` | `percentile`, `emptyAsNull` |
| `terms` | `ordinal` | `size`, `orderBy.type: "column"` + `columnId`, `orderDirection`, `otherBucket`, `missingBucket` |
| `last_value` | `ordinal` | `sortField: "@timestamp"` — only works on aggregatable field types |

### `last_value` Field Type Compatibility

`last_value` uses the `top_metrics` aggregation under the hood, which requires fields that support sorting/aggregation. Incompatible fields cause **silent panel hangs** with no error message.

| Field Type | `last_value` | `terms` | Notes |
|------------|-------------|---------|-------|
| `keyword` | OK | OK | |
| `long`/`double`/`float` | OK | OK | |
| `date` | OK | OK | |
| `match_only_text` | **FAILS** (silent hang) | N/A | No sorting/aggregation support |
| `wildcard` | **FAILS** (`top_metrics` error) | OK | No segment ordinals |
| `text` (with keyword sub) | Use `.keyword` | Use `.keyword` | |

**Always check field mappings before using `last_value`.** Use `terms` as an alternative for `match_only_text` and `wildcard` fields.

### Visualization State

- Located at `state.visualization`
- Maps `columnId` values to chart dimensions
- Structure varies by `visualizationType`

**lnsXY example:**

```json
{
  "state": {
    "visualization": {
      "legend": { "isVisible": true, "position": "right" },
      "preferredSeriesType": "bar_stacked",
      "layers": [
        {
          "layerId": "layer1-uuid",
          "layerType": "data",
          "seriesType": "bar_stacked",
          "xAccessor": "col1-uuid",
          "accessors": ["col2-uuid"],
          "splitAccessor": "col3-uuid"
        }
      ],
      "axisTitlesVisibilitySettings": { "x": true, "yLeft": true, "yRight": true },
      "yLeftExtent": { "mode": "full" }
    }
  }
}
```

**lnsMetric example:**

```json
{
  "state": {
    "visualization": {
      "layerId": "layer1-uuid",
      "layerType": "data",
      "metricAccessor": "col1-uuid",
      "secondaryMetricAccessor": "col2-uuid",
      "maxAccessor": "col3-uuid",
      "breakdownByAccessor": "col4-uuid",
      "color": "#6092C0"
    }
  }
}
```

### References Naming Convention

- **Data view reference name format**: `indexpattern-datasource-layer-<layerId>`
- Each layer needs a reference entry mapping to the data view ID

```json
{
  "name": "indexpattern-datasource-layer-layer1-uuid",
  "type": "index-pattern",
  "id": "data-view-id"
}
```

### Top-Level References: Critical Duplication Rule

When the dashboard's top-level `references` array is **non-empty** (e.g., because it includes tag references), Kibana expects **all** panel data view references to also appear at the top level, prefixed with the panel index. If only tags are present without panel references, the entire dashboard fails to load silently.

Each inline panel's data view reference must be duplicated at the top level with format `"name": "<panelIndex>:<original-ref-name>"`:

```json
{
  "references": [
    { "type": "tag", "id": "my-tag", "name": "tag-ref-my-tag" },
    { "type": "index-pattern", "id": "my-data-view", "name": "p1:indexpattern-datasource-layer-l1" },
    { "type": "index-pattern", "id": "my-data-view", "name": "p2:indexpattern-datasource-layer-l1" }
  ]
}
```

- An **empty** `"references": []` works fine — Kibana falls back to inline panel references
- A **non-empty** array triggers Kibana to resolve ALL references from the top level
- Tag reference names use convention `"tag-ref-<tag-id>"`

### Ad-Hoc Data Views

> **WARNING**: Ad-hoc data views with `internalReferences` **do not work reliably** when created via the Saved Objects API. Panels fail with "Could not find the data view". **Always use saved data views** created via the Data Views API, referenced by ID in both the layer's `indexPatternId` and the panel's `references` array.

- Defined inline in `state.adHocDataViews` (keyed by ad-hoc ID)
- Mapped in `state.internalReferences` instead of top-level `references`
- No saved data view object required
- **Only works when created through the Kibana UI**, not via API

```json
{
  "state": {
    "adHocDataViews": {
      "adhoc-uuid": {
        "title": "logs-*",
        "timeFieldName": "@timestamp",
        "sourceFilters": [],
        "fieldFormats": {},
        "runtimeFieldMap": {},
        "allowNoIndex": false,
        "name": "Logs (ad-hoc)"
      }
    },
    "internalReferences": [
      {
        "type": "index-pattern",
        "id": "adhoc-uuid",
        "name": "indexpattern-datasource-layer-layer1-uuid"
      }
    ]
  }
}
```

## Creating a Dashboard with Inline Lens Panel via API

The inline panel JSON below includes the three fields that are **required but undocumented** by Kibana:
1. `indexPatternId` in each layer (matching the data view in `references`)
2. `ignoreGlobalFilters: false` in each layer
3. `indexpattern` and `textBased` siblings alongside `formBased` in `datasourceStates`

```bash
curl -s -X POST "https://localhost:5601/api/saved_objects/dashboard/my-dashboard-id" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -H "Authorization: ApiKey $KIBANA_API_KEY" \
  -d '{
    "attributes": {
      "title": "Request Metrics",
      "panelsJSON": "[{\"type\":\"lens\",\"gridData\":{\"x\":0,\"y\":0,\"w\":24,\"h\":15,\"i\":\"p1\"},\"panelIndex\":\"p1\",\"embeddableConfig\":{\"attributes\":{\"title\":\"Requests Over Time\",\"visualizationType\":\"lnsXY\",\"state\":{\"datasourceStates\":{\"formBased\":{\"layers\":{\"l1\":{\"columns\":{\"c1\":{\"operationType\":\"date_histogram\",\"sourceField\":\"@timestamp\",\"isBucketed\":true,\"scale\":\"interval\",\"params\":{\"interval\":\"auto\",\"includeEmptyRows\":true}},\"c2\":{\"operationType\":\"count\",\"isBucketed\":false,\"scale\":\"ratio\",\"sourceField\":\"___records___\"}},\"columnOrder\":[\"c1\",\"c2\"],\"incompleteColumns\":{},\"indexPatternId\":\"logs-data-view-id\",\"ignoreGlobalFilters\":false,\"sampling\":1}}},\"indexpattern\":{\"layers\":{}},\"textBased\":{\"layers\":{}}},\"visualization\":{\"preferredSeriesType\":\"line\",\"layers\":[{\"layerId\":\"l1\",\"layerType\":\"data\",\"seriesType\":\"line\",\"xAccessor\":\"c1\",\"accessors\":[\"c2\"]}]}},\"references\":[{\"type\":\"index-pattern\",\"id\":\"logs-data-view-id\",\"name\":\"indexpattern-datasource-layer-l1\"}]}}}]",
      "optionsJSON": "{\"useMargins\":true,\"syncColors\":true,\"syncCursor\":true,\"syncTooltips\":true}",
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"query\":{\"query\":\"\",\"language\":\"kuery\"},\"filter\":[]}"
      },
      "timeRestore": true,
      "timeFrom": "now-1h",
      "timeTo": "now"
    },
    "references": []
  }'
```

**Note**: Inline panels embed the full Lens config in `embeddableConfig.attributes` with their own `references` array inside the attributes. Top-level `references` is empty when all panels are inline. If you add tags or other top-level references, you must also duplicate all panel data view references at the top level (see "Top-Level References: Critical Duplication Rule" above).

## Saved Searches Structure

```json
{
  "attributes": {
    "title": "Error Logs",
    "columns": ["message", "log.level", "service.name"],
    "sort": [["@timestamp", "desc"]],
    "kibanaSavedObjectMeta": {
      "searchSourceJSON": "{\"query\":{\"query\":\"log.level: error\",\"language\":\"kuery\"},\"filter\":[],\"indexRefName\":\"kibanaSavedObjectMeta.searchSourceJSON.index\"}"
    }
  },
  "references": [
    {
      "name": "kibanaSavedObjectMeta.searchSourceJSON.index",
      "type": "index-pattern",
      "id": "logs-data-view-id"
    }
  ]
}
```

- Embed in dashboard as panel type `search`
- Reference via `panelRefName` in `panelsJSON`

## Legacy Visualization Types

| Type | Notes |
|------|-------|
| **Markdown** | `visState.type: "markdown"`, raw markdown in `params.markdown` |
| **TSVB** | `visState.type: "metrics"`, complex multi-series time series; being replaced by Lens |
| **Vega / Vega-Lite** | `visState.type: "vega"`, full Vega spec in `params.spec`; use for unsupported chart types |
| **Aggregation-based** | `visState.type: "histogram"`, `"pie"`, `"metric"`, etc.; fully replaced by Lens in 8.x |

## Common Mistakes

- **Missing required layer fields** -- each layer MUST have `indexPatternId`, `ignoreGlobalFilters: false`, and `sampling: 1`. The `datasourceStates` MUST include `indexpattern: { layers: {} }` and `textBased: { layers: {} }` siblings alongside `formBased`. Omitting any of these causes panels to hang indefinitely with no error.
- **Using formula columns via API** -- `operationType: "formula"` requires hidden sub-columns with `tinymathAst` objects that the API doesn't generate. Use native operations (`average`, `percentile`, `count`, `terms`) instead.
- **Using `last_value` on incompatible field types** -- `match_only_text` fields (e.g., `message`, `error.message`) and `wildcard` fields (e.g., `url.path`) silently break `last_value`. Use `terms` instead, or use the `.keyword` sub-field for `text` fields.
- **Ad-hoc data views via API** -- `adHocDataViews` with `internalReferences` fail to resolve when created via the Saved Objects API. Always use saved data views created via the Data Views API.
- **Top-level references missing panel refs** -- if the dashboard's `references` array is non-empty (e.g., tags), ALL panel data view references must be duplicated there with `"<panelIndex>:<ref-name>"` format. Missing panel refs cause the entire dashboard to silently fail.
- **Mismatched `layerId`/`columnId`** between `datasourceStates` and `visualization` state -- every `xAccessor`, `accessors[]`, `splitAccessor`, `metricAccessor` must reference a valid `columnId` from the matching `layerId`
- **Wrong reference name format** -- must be exactly `indexpattern-datasource-layer-<layerId>` with the matching layer UUID
- **Grid overlap** -- panels with overlapping coordinates (`x + w > 48` or overlapping `y` ranges) cause rendering errors; grid is **48 units wide**
- **Missing referenced saved objects on import** -- importing a dashboard without its Lens objects, saved searches, or data views breaks the dashboard; always export with `includeReferencesDeep: true`
- **Stringified JSON fields** -- `panelsJSON`, `optionsJSON`, `searchSourceJSON` are **strings**, not objects; double-encoding or failing to stringify causes parse errors
- **Inline vs referenced panel confusion** -- inline panels have `embeddableConfig.attributes` with their own `references`; referenced panels use `panelRefName` pointing to top-level `references`
- **One broken panel kills the whole dashboard** -- a single misconfigured panel causes the entire dashboard to hang/fail, not just that panel

## Debugging API-Created Dashboards

1. Start with a **single known-working panel** and verify it renders
2. **Add one panel at a time**, verify after each addition
3. If the dashboard breaks, the last added panel is the culprit
4. **Export a working panel** from an existing dashboard (e.g., Elastic Agent built-in dashboards) to compare structures: `GET /api/saved_objects/dashboard/<id>`
5. Compare against working dashboards' `references` arrays to understand expected naming conventions
