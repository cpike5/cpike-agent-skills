# Flowchart

## Direction Keywords

| Keyword | Direction |
|---------|-----------|
| `TB` | Top to bottom (default) |
| `TD` | Top-down (alias for TB) |
| `BT` | Bottom to top |
| `LR` | Left to right |
| `RL` | Right to left |

```mermaid
flowchart LR
    A --> B --> C
```

## Node Shapes

| Syntax | Shape | Use for |
|--------|-------|---------|
| `A[text]` | Rectangle | Default process step |
| `A(text)` | Rounded rectangle | Start / end (rounded corners) |
| `A([text])` | Stadium / pill | Terminal node |
| `A[[text]]` | Subroutine | Predefined process / function call |
| `A[(text)]` | Cylinder | Database / data store |
| `A((text))` | Circle | Junction / connector |
| `A{text}` | Diamond | Decision / condition |
| `A{{text}}` | Hexagon | Preparation / config step |
| `A[/text/]` | Parallelogram | Input / output |
| `A[\text\]` | Parallelogram (alt) | Alternate I/O direction |
| `A[/text\]` | Trapezoid | Manual operation |
| `A[\text/]` | Trapezoid (alt) | Manual input |
| `A>text]` | Asymmetric / flag | Tagged / annotated step |

```mermaid
flowchart TD
    start([Start])
    input[/User Input/]
    decide{Valid?}
    proc[Process]
    db[(Database)]
    done([End])

    start --> input --> decide
    decide -->|Yes| proc --> db --> done
    decide -->|No| input
```

## Link Types

See [01-syntax-foundations.md](./01-syntax-foundations.md) for the full arrow type table. Flowchart-specific usage patterns:

```mermaid
flowchart LR
    A -->|happy path| B
    A -.->|async call| C
    B ==>|critical path| D
    C --> D
    D ~~~E         %% invisible link for vertical alignment
    E --o F        %% aggregation
    F --x G        %% blocked path
```

- **Label placement**: `-->|label|` and `--label-->` are equivalent; prefer `-->|label|` for readability
- **Multi-target shorthand**: `A --> B & C & D` links A to B, C, and D simultaneously

## Subgraphs

```mermaid
flowchart LR
    subgraph client["Client Tier"]
        browser[Browser]
        mobile[Mobile App]
    end

    subgraph api["API Tier"]
        direction TB
        gw[API Gateway]
        svc[Service Layer]
    end

    subgraph data["Data Tier"]
        db[(SQL DB)]
        cache[(Redis)]
    end

    browser --> gw
    mobile --> gw
    gw --> svc
    svc --> db
    svc --> cache
```

Key rules:
- **`subgraph id["Label"]`** -- ID is the linkable identifier; label is the display name
- **`direction TB|LR|...`** inside a subgraph overrides layout direction for that group only
- **Linking between subgraphs** -- use the subgraph ID as a node target: `A --> subgraphId`
- **Nesting** -- subgraphs can contain other subgraphs; keep to 2 levels to avoid layout issues
- **No reserved word IDs** -- avoid `end` as a subgraph ID

## Click Events

```mermaid
flowchart LR
    A[Home] --> B[Dashboard]
    click A href "https://example.com" "Go to home"
    click B callback "handleDashboard"
```

| Syntax | Behavior |
|--------|----------|
| `click nodeId href "url"` | Navigate to URL on click |
| `click nodeId href "url" "tooltip"` | URL click with hover tooltip |
| `click nodeId callback "fnName"` | Call JavaScript function |
| `click nodeId call fnName()` | Alternative callback syntax |

- `_blank` target: `click A href "url" _blank`
- Click events require the renderer to have `securityLevel` set to `loose`

## Layout Tips

- **Invisible links for alignment** -- `A ~~~ B` forces spacing without a visible edge; useful for vertically aligning parallel branches
- **Keep subgraphs small** -- large subgraphs confuse the auto-layout engine; split into sibling subgraphs and link them
- **Consistent direction** -- mixing `LR` and `TB` within nested subgraphs produces unpredictable results; override direction only when necessary
- **Long labels push edges** -- use short node labels and put detail in tooltips or notes
- **Multi-edge shorthand** -- `A --> B & C` is cleaner than two separate edge declarations
- **Avoid cycles in subgraph boundaries** -- edges that cross subgraph boundaries in both directions confuse layout; use a single crossing direction

## Full Example: .NET Request Pipeline

```mermaid
%%{init: {"theme": "default", "flowchart": {"curve": "basis"}}}%%
flowchart TD
    req([HTTP Request])
    cors["CORS Middleware"]
    auth["Auth Middleware\n(JWT Validation)"]
    ratelimit["Rate Limit Middleware"]
    routing["Endpoint Routing"]

    subgraph controllers["Controller Layer"]
        direction TB
        ctrl["ApiController"]
        validation["Model Validation\n(FluentValidation)"]
    end

    subgraph services["Service Layer"]
        direction TB
        svc["Business Service"]
        cache[(Redis Cache)]
    end

    subgraph data["Data Layer"]
        direction TB
        repo["Repository"]
        db[(SQL Server)]
    end

    resp([HTTP Response])

    req --> cors --> auth
    auth -->|401 Unauthorized| resp
    auth -->|Valid token| ratelimit
    ratelimit -->|429 Too Many Requests| resp
    ratelimit --> routing --> ctrl --> validation
    validation -->|400 Bad Request| resp
    validation -->|Valid| svc
    svc --> cache
    cache -->|Hit| resp
    cache -->|Miss| repo --> db
    db --> svc --> resp
```
