# Writing Good Failing Tests

A TDD test does double duty: in the moment it's an executable specification that drives your design, and forever after it's a regression guard and a piece of documentation. Both jobs reward the same qualities — clarity, focus, and honesty about what's being checked. This doc is about writing tests worth keeping.

## Arrange-Act-Assert

Structure each test in three visually distinct movements:

```csharp
[Fact]
public void Withdraw_AmountExceedingBalance_ThrowsInsufficientFunds()
{
    // Arrange — set up the world
    var account = new Account(balance: 100m);

    // Act — perform the one action under test
    Action act = () => account.Withdraw(150m);

    // Assert — state the expectation
    act.Should().Throw<InsufficientFundsException>();
}
```

Keep **one action** in the Act. If you find yourself acting twice, that's usually two tests. The Arrange can be several lines; the Act should be one conceptual operation. This shape makes a test scannable — a reader sees the scenario, the trigger, and the expected outcome at a glance.

## Name the test as a specification

A good test name reads as a sentence about behavior, so that a list of test names reads as the spec for the unit. A widely-used pattern is `Method_Scenario_ExpectedOutcome`:

```
Withdraw_AmountExceedingBalance_ThrowsInsufficientFunds
ParsePrice_EmptyString_ReturnsNull
ApplyDiscount_TenPercentOnHundred_Returns90
IsEligible_UserUnder18_ReturnsFalse
```

The exact convention matters less than the property: someone reading only the name should know what behavior breaks if the test goes red. Avoid names like `Test1`, `WithdrawWorks`, or `HappyPath` — they tell a future debugger nothing.

## Assert on behavior, not implementation

Test *what* the code does, not *how* it does it. A test coupled to internal details — private fields, the exact sequence of internal calls, a specific collaborator being invoked when the behavior doesn't require it — breaks every time you refactor, which destroys the very safety net TDD is supposed to give you.

- Prefer asserting on **return values and observable state** over verifying mock interactions. `result.Should().Be(90)` survives refactoring; `calculator.Verify(c => c.Multiply(...))` does not, and it's testing the implementation you might want to change.
- Verify an interaction only when the interaction *is* the behavior — e.g. "an email is sent", "the order is persisted". There, the side effect is the contract.

## Test doubles: prefer the real thing

Reach for a mock/stub/fake only when a real collaborator can't be used in a test: it's slow (network, DB), non-deterministic (clock, random, external service), or has side effects you can't have (sends email, charges a card). For plain value objects and pure logic, use the real instances — they're faster to write, exercise more of the real system, and don't lie.

| Situation | Approach |
|-----------|----------|
| Pure function / value object collaborator | Use the real object |
| Repository hitting a database | Substitute an interface, or use an in-memory implementation |
| `DateTime.Now` / `Guid.NewGuid` / randomness | Inject an abstraction (`IClock`, `TimeProvider`) and control it |
| External HTTP / email / payment | Substitute the interface; assert the interaction if it's the behavior |
| Complex object graph you don't control | Consider a fake or builder rather than a deeply-stubbed mock |

When you do substitute, stub only what the test needs. A mock configured with five return values where the test only depends on one is noise — and a hint the unit under test has too many collaborators.

## Cover the edges, not the same case twice

Your test list should walk the interesting inputs, not pile up redundant happy-path variations. For most logic the high-value cases are:

- **The representative happy path** — one clear example that it works.
- **Boundaries** — zero, empty, the min and max, the off-by-one neighbors (`17` and `18` for an 18+ rule). Bugs cluster at boundaries.
- **Emptiness and absence** — empty string, empty collection, `null` where it's allowed, missing optional values.
- **Invalid input / error paths** — what *should* throw, and which exception, and what shouldn't throw.
- **Special values** — negative numbers, very large values, whitespace-only strings, duplicates, unicode if relevant.

Use `[Theory]`/`[TestCase]`/`[DataRow]` to express several inputs of the *same rule* compactly rather than copy-pasting near-identical test methods:

```csharp
[Theory]
[InlineData(17, false)]
[InlineData(18, true)]
[InlineData(65, true)]
public void IsEligible_ByAge(int age, bool expected)
    => new EligibilityRule().IsEligible(age).Should().Be(expected);
```

But keep distinct *behaviors* in distinct, well-named tests — a single parameterized method that mixes the success path and the throws-on-invalid path obscures both.

## Keep tests independent and deterministic

Each test must pass on its own and in any order, run a thousand times with the same result. That means: no shared mutable static state bleeding between tests, no dependence on test execution order, no real `DateTime.Now` in an assertion, no reliance on an external service being up. A flaky test is worse than no test — it trains everyone to ignore red.

## A test is code: hold it to the same bar

Test code is read far more than it's written, and it rots like any other code. Apply the refactor phase to it too (see `03-refactor-catalog.md`): extract a `CreateAccount(...)` helper or a builder when arrange blocks repeat, name your test data meaningfully (`var expiredCard` not `var c2`), and delete tests that no longer earn their keep. Resist the urge to add logic — `if`/`for`/`switch` — inside a test; a test with branches is a test that itself needs testing.
