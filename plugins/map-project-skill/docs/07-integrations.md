# integrations.md — External Integrations

Show what the system talks to, what it needs to run, and what's optional.

## Dependencies

Read the dependency manifests. Keep external service SDKs, database drivers, messaging clients, observability packages, and anything forked or pre-release (note the version for those). Skip utility packages.

## External API clients

From DI registration, find HTTP clients, SDK clients, and wrappers. For each: the service, the SDK, what it's used for, and the domain that owns it.

## Data stores

Databases, caches, blob storage, search indexes — the provider, the client library, and whether it's required for local development.

## Observability

Logging sink, tracing, metrics, health checks. Mark each required or optional, and note custom instrumentation (meters, activity sources, health check names) an agent might need to extend.

## Credentials

Cross-reference the secrets table in `configuration.md`: each credential's config key and the service it authenticates to. Keys and locations only, never values.

## Format

Tables grouped as: Core services, Data stores, Observability (required/optional column), Supporting libraries, Credentials.

## Judgement calls

- Focus on integrations that change how you work with the code — a required Postgres matters more than a JSON library.
- If a service can be stubbed or disabled for local dev, say how; that's the first thing an agent setting up locally needs.
