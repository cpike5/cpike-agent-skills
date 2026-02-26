# State Diagram

## Declaration

Always use `stateDiagram-v2`. The original `stateDiagram` is deprecated and lacks composite state, concurrency, and choice support.

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Running : start
    Running --> Idle : stop
    Running --> [*] : terminate
```

## States

### Simple state

```
s1
```

### State with description

```
s1 : Waiting for Payment
```

- The description replaces the state ID as the display label

### Long name alias

```
state "Waiting for Payment Authorization" as WaitingAuth
```

- Use `state "..." as id` when the display name would otherwise be invalid as an identifier

## Transitions

| Syntax                    | Meaning                          |
|---------------------------|----------------------------------|
| `s1 --> s2`               | Transition (no label)            |
| `s1 --> s2 : event`       | Transition with event/label      |
| `[*] --> s1`              | Entry point (start)              |
| `s1 --> [*]`              | Exit point (end / terminal)      |

- Multiple transitions from the same state are valid -- each is a separate line
- Multiple `[*] --> sN` entries create multiple start states (use sparingly)

## Composite States

Nest states inside a parent state block to model sub-state machines:

```mermaid
stateDiagram-v2
    [*] --> Processing

    state Processing {
        [*] --> Validating
        Validating --> Charging : valid
        Charging --> Fulfilled : charged
        Validating --> [*] : invalid
    }

    Processing --> Failed : error
    Processing --> [*] : done
```

- Entry/exit points inside the composite (`[*]`) are local to that block
- Transitions from the parent label (`Processing --> Failed`) fire from any sub-state

## Choice Pseudostate

Model conditional branching with `<<choice>>`:

```mermaid
stateDiagram-v2
    [*] --> CheckStock

    state CheckStock <<choice>>

    [*] --> CheckStock
    CheckStock --> Reserved : [in stock]
    CheckStock --> BackOrdered : [out of stock]
    CheckStock --> Discontinued : [discontinued]
```

- **`state id <<choice>>`** -- declares a diamond decision node
- Transition labels on branches act as guards

## Fork and Join

Model parallel execution with `<<fork>>` and `<<join>>`:

```mermaid
stateDiagram-v2
    [*] --> Fork1

    state Fork1 <<fork>>
    Fork1 --> SendEmail
    Fork1 --> CreateInvoice
    Fork1 --> UpdateInventory

    SendEmail --> Join1
    CreateInvoice --> Join1
    UpdateInventory --> Join1

    state Join1 <<join>>
    Join1 --> [*]
```

- **`<<fork>>`** -- splits into parallel flows
- **`<<join>>`** -- waits for all incoming flows before continuing

## Concurrency

Use `--` inside a composite state to define parallel regions:

```mermaid
stateDiagram-v2
    state OrderProcessing {
        [*] --> Active

        state Active {
            [*] --> PaymentPending
            PaymentPending --> PaymentComplete : paid

            --

            [*] --> InventoryReserved
            InventoryReserved --> InventoryAllocated : allocated
        }

        Active --> Complete : all done
    }
```

- `--` separator creates horizontal concurrent regions inside the composite
- Each region has its own `[*]` start and runs independently

## Notes

```mermaid
stateDiagram-v2
    [*] --> Pending
    Pending --> Confirmed : payment received

    note right of Pending
        Awaiting payment gateway
        callback. TTL = 30 min.
    end note

    note left of Confirmed
        Triggers fulfillment
        pipeline.
    end note
```

| Syntax               | Placement            |
|----------------------|----------------------|
| `note right of sN`   | Right side of state  |
| `note left of sN`    | Left side of state   |

- Close with `end note`
- Multi-line content is supported between declaration and `end note`

## Direction

```mermaid
stateDiagram-v2
    direction LR
    [*] --> A
    A --> B
    B --> [*]
```

| Value | Meaning                   |
|-------|---------------------------|
| `TB`  | Top to bottom (default)   |
| `LR`  | Left to right             |

- `direction` can be placed at the top level or inside a composite state block to control only that region
- `BT` and `RL` are supported but rarely useful for state diagrams

## v2 Syntax Notes

| Feature               | v1 (`stateDiagram`) | v2 (`stateDiagram-v2`) |
|-----------------------|---------------------|------------------------|
| Composite states      | Limited             | Full support           |
| Concurrency (`--`)    | No                  | Yes                    |
| Choice (`<<choice>>`) | No                  | Yes                    |
| Fork/Join             | No                  | Yes                    |
| Notes                 | No                  | Yes                    |
| Direction             | No                  | Yes                    |

**Always use `stateDiagram-v2`.**

## Full Example: Order Lifecycle State Machine

```mermaid
stateDiagram-v2
    direction LR

    [*] --> Created : order submitted

    state ValidatePayment <<choice>>

    Created --> ValidatePayment : customer checks out

    ValidatePayment --> PaymentFailed : [payment declined]
    ValidatePayment --> Confirmed : [payment approved]

    PaymentFailed --> [*] : abandoned
    PaymentFailed --> ValidatePayment : retry

    state Confirmed {
        direction TB
        [*] --> Picking
        Picking --> Packed : items packed
        Packed --> ReadyToShip
    }

    note right of Confirmed
        Fulfillment sub-process.
        SLA: complete within 24h.
    end note

    Confirmed --> Shipped : carrier collected
    Confirmed --> Cancelled : merchant cancels

    Shipped --> OutForDelivery : in transit
    OutForDelivery --> Delivered : delivery confirmed
    OutForDelivery --> DeliveryFailed : undeliverable

    DeliveryFailed --> OutForDelivery : re-attempt
    DeliveryFailed --> ReturnedToSender : max attempts reached

    Delivered --> Refunded : return approved
    Cancelled --> Refunded : refund issued

    Delivered --> [*]
    Refunded --> [*]
    ReturnedToSender --> [*]
    Cancelled --> [*]
```

## Common Mistakes

- **Using `stateDiagram` instead of `stateDiagram-v2`** -- the v1 syntax silently omits composite states, concurrency, and choice nodes
- **Missing `[*]` inside composite states** -- composite states need their own `[*] --> firstChild` entry; without it the sub-state machine has no entry point
- **Forgetting `end note`** -- notes must be closed explicitly; an unclosed note breaks the entire diagram
- **Overloading transition labels** -- a label is an event or guard, not a multi-sentence description; keep labels short and use notes for elaboration
- **Using `<<fork>>` without a matching `<<join>>`** -- parallel regions that never converge produce diagrams that imply the process never completes
