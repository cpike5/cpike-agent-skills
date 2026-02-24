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

- Located at `state.datasourceStates.formBased.layers`
- **Keyed by `layerId`** (UUID)
- Each layer contains `columns` keyed by **`columnId`** (UUID)

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
            "indexPatternId": "data-view-id"
          }
        }
      }
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

- **`formula`** columns use `params.formula` (e.g., `count() / overall_sum(count())`)
- **`terms`** columns use `params.size`, `params.orderBy`, `params.orderDirection`
- **`percentile`** columns use `params.percentile` (e.g., `95`)

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

### Ad-Hoc Data Views

- Defined inline in `state.adHocDataViews` (keyed by ad-hoc ID)
- Mapped in `state.internalReferences` instead of top-level `references`
- No saved data view object required

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

```bash
curl -s -X POST "https://localhost:5601/api/saved_objects/dashboard/my-dashboard-id" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -H "Authorization: ApiKey $KIBANA_API_KEY" \
  -d '{
    "attributes": {
      "title": "Request Metrics",
      "panelsJSON": "[{\"type\":\"lens\",\"gridData\":{\"x\":0,\"y\":0,\"w\":24,\"h\":15,\"i\":\"p1\"},\"panelIndex\":\"p1\",\"embeddableConfig\":{\"attributes\":{\"title\":\"Requests Over Time\",\"visualizationType\":\"lnsXY\",\"state\":{\"datasourceStates\":{\"formBased\":{\"layers\":{\"l1\":{\"columns\":{\"c1\":{\"operationType\":\"date_histogram\",\"sourceField\":\"@timestamp\",\"isBucketed\":true,\"params\":{\"interval\":\"auto\"}},\"c2\":{\"operationType\":\"count\",\"isBucketed\":false,\"sourceField\":\"___records___\"}},\"columnOrder\":[\"c1\",\"c2\"],\"incompleteColumns\":{}}}}},\"visualization\":{\"preferredSeriesType\":\"line\",\"layers\":[{\"layerId\":\"l1\",\"layerType\":\"data\",\"seriesType\":\"line\",\"xAccessor\":\"c1\",\"accessors\":[\"c2\"]}]}},\"references\":[{\"type\":\"index-pattern\",\"id\":\"logs-data-view-id\",\"name\":\"indexpattern-datasource-layer-l1\"}]}}}]",
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

**Note**: Inline panels embed the full Lens config in `embeddableConfig.attributes` with their own `references` array inside the attributes. Top-level `references` is empty when all panels are inline.

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

- **Mismatched `layerId`/`columnId`** between `datasourceStates` and `visualization` state -- every `xAccessor`, `accessors[]`, `splitAccessor`, `metricAccessor` must reference a valid `columnId` from the matching `layerId`
- **Wrong reference name format** -- must be exactly `indexpattern-datasource-layer-<layerId>` with the matching layer UUID
- **Grid overlap** -- panels with overlapping coordinates (`x + w > 48` or overlapping `y` ranges) cause rendering errors; grid is **48 units wide**
- **Missing referenced saved objects on import** -- importing a dashboard without its Lens objects, saved searches, or data views breaks the dashboard; always export with `includeReferencesDeep: true`
- **Stringified JSON fields** -- `panelsJSON`, `optionsJSON`, `searchSourceJSON` are **strings**, not objects; double-encoding or failing to stringify causes parse errors
- **Inline vs referenced panel confusion** -- inline panels have `embeddableConfig.attributes` with their own `references`; referenced panels use `panelRefName` pointing to top-level `references`
