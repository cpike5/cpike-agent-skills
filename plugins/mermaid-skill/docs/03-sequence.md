# Sequence Diagram

## Participant Declaration

```mermaid
sequenceDiagram
    participant API as API Gateway
    participant SVC as OrderService
    actor U as User
    actor Admin
```

| Syntax | Renders As |
|--------|-----------|
| `participant A` | Box labeled "A" |
| `participant A as Alias` | Box with display name "Alias", ID remains "A" |
| `actor U` | Stick figure labeled "U" |
| `actor U as User` | Stick figure with display name "User" |

- Participants are displayed left-to-right in declaration order
- Declare all participants at the top to control ordering; undeclared participants appear on first use

## Message Types

| Syntax | Arrow Style | Notes |
|--------|------------|-------|
| `A->B: msg` | Solid line, no arrowhead | Rarely used; open line |
| `A-->B: msg` | Dotted line, no arrowhead | Response / optional |
| `A->>B: msg` | Solid line with filled arrowhead | Standard synchronous call |
| `A-->>B: msg` | Dotted line with filled arrowhead | Standard response / return |
| `A-xB: msg` | Solid line with X at end | Lost message / error |
| `A--xB: msg` | Dotted line with X at end | Lost async message |
| `A-)B: msg` | Solid line with open arrowhead | Fire-and-forget async |
| `A--)B: msg` | Dotted line with open arrowhead | Async response |

Conventions:
- **Request** -- use `->>` (solid, arrowhead)
- **Response / return value** -- use `-->>` (dotted, arrowhead)
- **Async / event** -- use `-)` or `--)` (open arrowhead)
- **Error / dead message** -- use `-x` or `--x`

## Activations

Activation bars show when a participant is actively processing.

**Explicit syntax:**

```mermaid
sequenceDiagram
    Client->>Server: Request
    activate Server
    Server-->>Client: Response
    deactivate Server
```

**Shorthand (`+` / `-` on the arrow):**

```mermaid
sequenceDiagram
    Client->>+Server: Request
    Server-->>-Client: Response
```

- `+` on the target activates it
- `-` on the sender deactivates it (must match a prior `+`)
- Activations can nest -- each `+` stacks a new bar; each `-` pops one

## Control Flow Blocks

| Block | Syntax | Purpose |
|-------|--------|---------|
| Loop | `loop [label] ... end` | Repetition |
| Alt / Else | `alt [cond] ... else [cond] ... end` | Conditional branches |
| Optional | `opt [cond] ... end` | Zero-or-one execution |
| Parallel | `par [label] ... and [label] ... end` | Concurrent execution |
| Critical | `critical [label] ... option [label] ... end` | Required with fallback |
| Break | `break [label] ... end` | Early exit / exception path |

```mermaid
sequenceDiagram
    Client->>+API: GET /orders

    loop Retry on 503
        API->>+DB: Query orders
        DB-->>-API: Result set
    end

    alt Token valid
        API-->>Client: 200 OK + orders
    else Token expired
        API-->>Client: 401 Unauthorized
    end

    opt Admin request
        API->>Audit: Log access
    end

    par Async notifications
        API-)Email: Send summary
    and
        API-)Push: Notify device
    end

    break DB connection lost
        API-->>Client: 503 Service Unavailable
    end

    deactivate API
```

## Notes

| Syntax | Placement |
|--------|-----------|
| `Note right of A: text` | Right side of participant A |
| `Note left of A: text` | Left side of participant A |
| `Note over A: text` | Centered above participant A |
| `Note over A,B: text` | Spanning from A to B |

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server

    Note over C,S: TLS Handshake complete
    C->>S: GET /data
    Note right of S: Validates JWT
    S-->>C: 200 OK
    Note left of C: Renders result
```

## Participant Boxes

Groups related participants under a labeled background box:

```mermaid
sequenceDiagram
    box "Frontend"
        actor U as User
        participant Browser
    end
    box "Backend" #lightblue
        participant API
        participant Auth
    end
    box "Data"
        participant DB
        participant Cache
    end

    U->>Browser: Click Login
    Browser->>+API: POST /auth
    API->>Auth: Validate credentials
    Auth-->>API: JWT token
    API-->>-Browser: 200 + token
```

- Color hint is optional: `box "Label" #hexOrColorName`
- All participants inside the box must be declared between `box` and `end`

## Autonumber

```mermaid
sequenceDiagram
    autonumber
    Client->>API: Request
    API->>DB: Query
    DB-->>API: Data
    API-->>Client: Response
```

- `autonumber` prefixes each message arrow with an incrementing integer
- Place `autonumber` before any messages

## Full Example: .NET API Request with Auth

```mermaid
sequenceDiagram
    autonumber

    actor U as User
    participant B as Browser
    box "API Host" #f0f4ff
        participant MW as Auth Middleware
        participant CTRL as OrderController
        participant SVC as OrderService
    end
    box "Infrastructure" #f4f0ff
        participant CACHE as Redis
        participant DB as SQL Server
    end

    U->>B: Click "My Orders"
    B->>+MW: GET /api/orders\nAuthorization: Bearer <token>

    alt Token missing or malformed
        MW-->>B: 401 Unauthorized
        B-->>U: Show login prompt
    else Token valid
        Note right of MW: Claims extracted,\nscopes validated
        MW->>+CTRL: Forward request + ClaimsPrincipal

        CTRL->>+SVC: GetOrdersAsync(userId)

        SVC->>CACHE: GET orders:userId:42
        alt Cache hit
            CACHE-->>SVC: Cached order list
        else Cache miss
            CACHE-->>SVC: nil
            SVC->>+DB: SELECT * FROM Orders\nWHERE UserId = 42
            DB-->>-SVC: Row set
            SVC-)CACHE: SET orders:userId:42 (TTL 5m)
        end

        SVC-->>-CTRL: List#lt;OrderDto#gt;
        CTRL-->>-MW: 200 OK + JSON body
        MW-->>-B: 200 OK + JSON body
        B-->>U: Render order list
    end
```
