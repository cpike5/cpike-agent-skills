# Testing

Three layers, each answering a question the others cannot:

| Layer | Runs against | Answers | Budget |
| --- | --- | --- | --- |
| Unit / service | Fakes, in-memory store | Does this logic branch correctly? | Seconds, every save |
| Integration | **A real ephemeral database**, real HTTP pipeline | Does it work against the actual schema? | ~a minute, every PR |
| End-to-end | The running app in a real browser | Does the user-visible thing work and look right? | Minutes, on demand + PR |

The failure mode this document exists to prevent: a project with only the first
layer, where an agent "verifies" a change by running 1,100 fast tests that never
touched a database or a browser, and the bug ships anyway.

## The in-memory provider is not a database

EF Core's in-memory provider is a dictionary with a `DbContext` on it. It is
excellent for the first layer and it is fair to build most tests on it — this
repo does. But be explicit about what it cannot see:

- **No SQL translation.** A LINQ query the in-memory provider evaluates happily
  in C# may have no SQL equivalent, and throws only against a real provider.
- **No constraints.** Unique indexes, foreign keys, `NOT NULL`, check
  constraints — none are enforced. A test proving you can't create a duplicate
  proves nothing.
- **No provider-specific types.** JSONB columns, arrays, `citext`, generated
  columns, collation-sensitive ordering. Case-sensitive sort order is a classic:
  in-memory orders by .NET string comparison, Postgres by database collation.
- **No transactions or concurrency.** Rollback semantics and optimistic
  concurrency tokens are untested.
- **Migrations never run.** A model change with no migration builds, passes every
  in-memory test, and fails at startup in production.

So: keep the fast layer, and add a second layer that runs against real Postgres.
The rule is **anything that reaches SQL gets an integration test** — queries with
non-trivial `Where`/`OrderBy`/`GroupBy`, anything relying on a constraint,
anything touching a JSONB column, and the migration set itself.

## Spinning up a test database

The app must be able to stand up a throwaway database on demand, with no manual
setup, from a single command. This is what makes end-to-end work possible for an
agent, and it is the piece most projects are missing.

Two mechanisms; pick by what the environment has.

### Testcontainers — the default

`Testcontainers.PostgreSql` starts a real Postgres in Docker, hands you a
connection string, and tears it down. Works identically on a laptop and on a
GitHub Actions runner (both have a Docker daemon), which is the whole point.

```csharp
// One container per test assembly, shared via a collection fixture. Starting a
// container costs ~2s; starting one per test class costs minutes.
public sealed class PostgresFixture : IAsyncLifetime
{
    private readonly PostgreSqlContainer _db = new PostgreSqlBuilder()
        // Pin the tag. "latest" silently upgrades your test target underneath you,
        // and must match what production runs — see docker-compose.prod.yml.
        .WithImage("postgres:16-alpine")
        .Build();

    public string ConnectionString => _db.GetConnectionString();

    public async Task InitializeAsync()
    {
        await _db.StartAsync();

        // Migrate, never EnsureCreated. EnsureCreated builds the schema from the
        // model and skips migrations entirely — which means the one bug this
        // layer exists to catch (a model change with no migration) walks past it.
        await using var ctx = NewContext();
        await ctx.Database.MigrateAsync();
    }

    public AppDbContext NewContext() =>
        new(new DbContextOptionsBuilder<AppDbContext>()
            .UseNpgsql(ConnectionString).Options);

    public Task DisposeAsync() => _db.DisposeAsync().AsTask();
}

[CollectionDefinition("postgres")]
public sealed class PostgresCollection : ICollectionFixture<PostgresFixture> { }
```

### A throwaway database on a host Postgres — the fallback

Some environments have the `docker` CLI and no daemon (this repo's remote agent
sandbox is one), so Testcontainers cannot start. The fallback is a real Postgres
running on the host with **one fresh database per test run**:

```bash
scripts/test-db.sh up      # starts the cluster, creates a uniquely-named database
                           # and prints its connection string
scripts/test-db.sh down    # drops it
```

Template in `${CLAUDE_PLUGIN_ROOT}/assets/scripts/test-db.sh`. Have the fixture read
`TEST_DB_CONNECTION` and fall back to Testcontainers when it is unset — one
fixture, either mechanism, no test aware of which.

### Isolation between tests

A shared database and parallel tests will interfere. Three options, in order of
preference:

1. **A distinct database per test class**, created from a template database that
   already has the schema (`CREATE DATABASE x TEMPLATE test_template`) — fast,
   and gives real isolation.
2. **Truncate between tests** with [Respawn](https://github.com/jbogard/Respawn)
   (`DbAdapter.Postgres`, with your migrations-history table in `TablesToIgnore`).
   Fast and simple; requires tests within a class to run serially.
3. **A transaction per test, rolled back at the end.** Cheapest, but it cannot
   test anything that manages its own transaction, and it hides commit-time
   constraint violations from deferred constraints.

Do **not** rely on tests cleaning up after themselves. One forgotten delete and
failures start depending on execution order, which is the worst class of flake
to diagnose.

### Seeding

Seed through a **builder or factory in test code**, not through SQL scripts and
not through the UI. A `RecipeBuilder().WithTitle("x").Build()` keeps a test
readable at the point of the one field it actually cares about, and survives a
schema change in one place. Seed the minimum each test needs; a large shared
fixture makes every test depend on data it does not use.

## End-to-end API tests

`WebApplicationFactory<Program>` runs the real pipeline — routing, model binding,
filters, middleware, auth — against the test database, in-process, with no port
to bind. This is the layer that catches the things unit tests structurally cannot:
a missing `[Authorize]`, a 404 from a route typo, a DTO that doesn't round-trip.

Two adjustments in `ConfigureWebHost`:

- Replace the `DbContext` registration with one pointing at the fixture's
  connection string. Remove the existing service descriptor first — adding a
  second registration does not replace the first.
- Register a stub authentication handler so a test can act as a specific user.
  **Stub the handler, not the authorization** — a test that disables auth
  entirely will not notice when a real endpoint loses its `[Authorize]`.

## Playwright and screenshots

Playwright drives the running app in a real browser. It answers the questions
nothing below it can: does the page render, does the flow work, and does it look
right at both breakpoints.

Official test-runner integrations exist for NUnit and MSTest
(`Microsoft.Playwright.NUnit` / `.MSTest`); with xUnit, use the `Microsoft.Playwright`
library directly. For screenshots specifically — the common agent task — a small
Node script is usually less friction than a test project. Template in
`${CLAUDE_PLUGIN_ROOT}/assets/scripts/screenshot.mjs`.

### Environment

**Never run `playwright install` in a preconfigured sandbox.** Managed agent
environments ship Chromium at a fixed path with `PLAYWRIGHT_BROWSERS_PATH` set
and `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1`; re-downloading is a slow no-op at best
and a network-policy failure at worst. If a project pins a different Playwright
version than the preinstalled browser, pass `executablePath` rather than
downloading.

Where the package is a global CommonJS install, an ESM script must import the
default export rather than named ones:

```js
import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
```

### Waiting

- **Wait on a selector or a web-first assertion, never on a clock.** `expect(locator).toBeVisible()`
  and `waitForSelector` retry until they succeed or time out. A `sleep` is either
  too short (flake) or too long (slow suite), and usually both on different machines.
- **Use `waitUntil: 'domcontentloaded'`, not `'networkidle'`.** `networkidle`
  waits for *every* request to settle, so one blocked CDN font or one long-poll
  connection hangs it for the full timeout. It is also deprecated for exactly this
  reason. Wait for a selector that proves the thing you care about is on screen.
- **Give a client-side-rendered app a real first timeout** (60s). A WASM or
  heavy-SPA boot on a cold cache is genuinely slow, and a 5s default failure here
  looks like a broken app.

### Locators

Prefer, in order: `getByRole`, `getByLabel`, `getByText`, then `data-testid`.
Long CSS chains (`.panel > div:nth-child(3) .btn`) break on every markup tweak and
tell a reader nothing about intent. Add `data-testid` deliberately where the
accessible name is genuinely ambiguous — it is a contract, so don't scatter it.

### Authentication — the trap that costs the most time

The obstacle in E2E is almost never rendering; it is getting a signed-in user.
Two approaches:

- **`storageState`** — sign in once in a setup step, save the cookie/token state
  to a file, and load it in every context. This is the right answer when the
  project's real login can be driven locally.
- **Route interception** — when the real provider (Google OAuth, SSO) simply is
  not configurable in a local or sandboxed environment, intercept the calls that
  decide what the client believes:

  ```js
  await ctx.route('**/api/auth/me', r => r.fulfill({ json: {
    isAuthenticated: true, isAdmin: true, name: 'Test User',
  }}));
  ```

**The failure this prevents is silent, which is why it's worth a paragraph.** A
guest or anonymous principal often carries no user id, so every per-user API
answers 404 and the panel renders its empty or error state. Nothing throws. An
agent screenshots it, sees a plausible-looking empty page, and concludes the
feature is broken — or worse, "verifies" a change against a component that never
rendered. Document the app's specific version of this in
`docs/local-dev-environment.md`.

Seed the data the page needs through the API or the test database, **not by
clicking through the UI**. Driving setup through the UI makes every test depend
on every earlier screen.

### Screenshots

For screenshots to be worth anything as evidence, they must be deterministic:

- **Fixed viewports, both breakpoints.** 1440×1000 desktop and 390×844 mobile at
  minimum. A responsive shell often hides or moves whole regions on the phone, so
  the two are different layouts, not one layout at two widths. Screenshot both,
  every time — this is what PR "Verification" means for UI work.
- **One browser context per screenshot.** Contexts carry viewport, routes and
  storage state; reusing one across shots leaks configuration between them.
  Budget ~10s each and background any run of more than a few.
- **Kill animation and caret.** `page.emulateMedia({ reducedMotion: 'reduce' })`
  plus Playwright's `animations: 'disabled'` and `caret: 'hide'` screenshot
  options. An in-flight transition is the single most common source of a diff.
- **Freeze anything that varies.** Clocks, relative timestamps ("2 minutes ago"),
  random ids, rotating content. Seed fixed data; `page.clock` can pin time.
- **Wait for fonts** (`document.fonts.ready`) — a shot taken mid-swap catches the
  fallback face and diffs against every later run.
- **Mask what you cannot control.** `screenshot({ mask: [locator] })` paints a box
  over avatars, live data, or third-party embeds.
- **`fullPage: true` for layout review, element screenshots for a component.** A
  full-page shot of a virtualized or lazy-loaded list captures whatever happened
  to be mounted, so scroll and settle first, or shoot the element.

**On visual regression baselines:** `toHaveScreenshot` is genuinely useful, but
font rasterization differs between operating systems and even between container
images, so a baseline captured on a laptop will diff endlessly in CI. Only adopt
it if baselines are generated in the *same* image CI runs, and commit them as
such. Otherwise keep screenshots as PR evidence for a human, which is most of
their value anyway.

**On failure diagnostics:** turn on `trace: 'on-first-retry'` and
`video: 'retain-on-failure'` and upload them as CI artifacts. A Playwright trace
turns "flaked in CI, passes locally" from a research project into a two-minute
look at the DOM at the moment of failure.

### Flakes

A flaky E2E test is worse than no test, because it teaches everyone to ignore red.
When one flakes, fix the wait or the isolation — never add a retry and move on,
and never `sleep` it into submission. If a test cannot be made deterministic,
delete it and cover the behaviour a layer down.

## CI

The fast layer runs on every PR, always. The integration layer needs a database:

```yaml
# Not needed with Testcontainers — GitHub's ubuntu-latest runners have a Docker
# daemon, so the fixture starts its own. Use this only for the host-Postgres path.
services:
  postgres:
    image: postgres:16-alpine
    env:
      POSTGRES_PASSWORD: postgres
    options: >-
      --health-cmd pg_isready --health-interval 5s
      --health-timeout 5s --health-retries 10
    ports:
      - 5432:5432
```

E2E browser tests are slower and more fragile; run them as a separate job so a
browser flake doesn't mask a real unit failure, and so the fast gate stays fast.

Whatever you add, keep the rule from `${CLAUDE_PLUGIN_ROOT}/docs/03-ci-cd.md`:
**a contributor must be able to run it locally with one command.** If the
integration suite needs three environment variables and a manual database, it
will only ever run in CI, and its
failures will be unreproducible.

## Behavioural tests for LLM features

If the app has an agent loop, unit tests prove it plumbs correctly; they cannot
tell you whether it *answers* well. That needs a separate suite that talks to a
real model through the real loop — kept out of the PR gate (it costs money and is
non-deterministic) by skipping itself when the API key is absent.

Two rules make it useful rather than decorative:

- **Assert on machine-checkable facts, never on the model's word.** Assert that a
  row was written and a tool was called. A reply *saying* it saved the recipe is
  the failure mode, not the evidence.
- **Treat it as a regression gate, not a scoreboard.** A case that flips is
  signal. A moved percentage at this sample size is noise.
