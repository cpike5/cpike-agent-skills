# API Scripts

Wrapper scripts that handle auth headers, content-type, and base URLs. Requires a `.env` file at the plugin root.

## First-Time Setup

Before using the API scripts, walk the user through this setup:

1. **Copy the template:** `cp ${CLAUDE_PLUGIN_ROOT}/.env.example ${CLAUDE_PLUGIN_ROOT}/.env`
2. **Set `ES_URL`:** The Elasticsearch endpoint (e.g. `https://my-cluster.es.us-east-1.aws.found.io:9243` for Elastic Cloud, or `https://localhost:9200` for local). Ask the user for this value.
3. **Set `ES_API_KEY`:** A Base64-encoded API key. The user can generate one in Kibana at **Stack Management > API Keys > Create API key**, or via the ES API: `POST /_security/api_key { "name": "claude-code" }`. The response `encoded` field is the value to use.
4. **Set `KIBANA_URL`:** The Kibana endpoint (e.g. `https://my-cluster.kb.us-east-1.aws.found.io:9243` or `https://localhost:5601`). Only needed for Kibana API calls.
5. **Set `KIBANA_SPACE` (optional):** The Kibana space ID if not using the default space. Leave blank for the default space.
6. **Verify:** Run `${CLAUDE_PLUGIN_ROOT}/scripts/es-check-env` to confirm all required variables are set.
7. **Test connectivity:** Run `${CLAUDE_PLUGIN_ROOT}/scripts/es-api GET /_cat/health` to verify the connection works.

> **Important:** The `.env` file contains credentials and is git-ignored. Never commit it.

> **Tip:** Define a short alias at the start of your session to avoid repeating the full path:
> ```bash
> ES="${CLAUDE_PLUGIN_ROOT}/scripts"
> ```
> Then use `$ES/es-api`, `$ES/kibana-api`, etc.

## Script Reference

| Script | Usage | Notes |
|--------|-------|-------|
| `es-api` | `$ES/es-api [METHOD] /path [body]` | Adds `Authorization: ApiKey` + `Content-Type: application/json`. METHOD is optional — infers GET (no body) or POST (with body) |
| `kibana-api` | `$ES/kibana-api [METHOD] /api/path [body]` | Same as es-api + `kbn-xsrf: true` for POST/PUT/DELETE. Space-aware when `KIBANA_SPACE` is set |
| `es-indices` | `$ES/es-indices [filter]` | Lists indices (`_cat/indices`). Optional filter greps by name |
| `es-datastreams` | `$ES/es-datastreams [filter]` | Lists data streams. Optional filter greps by name |
| `es-check-env` | `$ES/es-check-env` | Validates `.env` exists and required vars are set |

## Configuration

Scripts support timeout overrides via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `ES_CONNECT_TIMEOUT` | `10` | Connection timeout in seconds |
| `ES_MAX_TIME` | `120` | Maximum total request time in seconds |

## Examples

```bash
ES="${CLAUDE_PLUGIN_ROOT}/scripts"

# Check cluster health (method inferred as GET)
$ES/es-api /_cat/health

# Search an index (method inferred as POST because body is provided)
$ES/es-api /my-index/_search '{"query":{"match_all":{}}}'

# Explicit method still works
$ES/es-api GET /_cat/health

# Kibana saved objects
$ES/kibana-api GET /api/saved_objects/_find?type=dashboard

# List all indices, or filter by name
$ES/es-indices
$ES/es-indices logs

# List data streams
$ES/es-datastreams

# Pipe body from stdin
echo '{"query":{"match":{"message":"error"}}}' | $ES/es-api POST /logs/_search -
```
