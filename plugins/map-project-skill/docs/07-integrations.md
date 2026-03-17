# Step 6 — External Integrations (Document F)

## 6a. Scan Dependencies

1. Read dependency manifests (`.csproj`, `package.json`, `go.mod`, `requirements.txt`, etc.).
2. Filter for significant integrations — external service SDKs, database drivers, observability tools. Skip utility packages.
3. Note versions for forked or pre-release packages.

## 6b. Identify External API Clients

1. Check service registration / DI setup for HTTP clients, SDK clients, API wrappers.
2. For each external service: what SDK is used, what's it for?

## 6c. Map the Observability Stack

1. Identify required vs optional observability tools.
2. Note custom instrumentation — meters, trace sources, health checks.

## 6d. Document Credentials

1. Cross-reference with Document E — which secrets map to which integration?
2. List all credentials with config keys and the service they authenticate to.

## Output Format

Tables grouped by:
- **Core Services** — main external APIs
- **Data Stores** — database providers
- **Observability Stack** — monitoring/logging/tracing (required vs optional)
- **Supporting Libraries** — smaller notable dependencies
- **Credential Management** — all credentials with config keys

## Judgement Calls

- Focus on integrations that affect how you work with the code
- Distinguish required from optional for observability
- Version numbers matter for forks and pre-release packages
