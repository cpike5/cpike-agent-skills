# The Refactor Phase: A Working Catalog

Green is permission to improve the design. The suite you just made pass is the safety net that lets you change structure with confidence — if a refactoring breaks behavior, a test goes red and tells you immediately. That's the whole bargain: small, behavior-preserving changes, re-run the suite, keep it green.

This doc is a catalog of what to look for in the refactor phase and how to act on it safely. You won't apply all of it every cycle — often there's nothing worth changing, and forcing a refactor is its own kind of waste. Scan for the smells; act on the ones that are actually present.

## The golden rule: structure, not behavior

A refactoring changes how the code is organized without changing what it does. The tests are the definition of "what it does" — so they should stay green throughout, and you should **not** be editing tests and implementation in the same breath to make a failing test pass. If you find yourself changing a test's expectations during refactor, you've crossed from refactoring into changing behavior; back out and do that as its own Red-Green cycle.

Work in small steps and re-run the suite after each meaningful one. A green-to-green sequence of tiny moves is safer and easier to debug than one big restructuring you can't bisect when it breaks.

## Smells and their refactorings

### Duplication
The most common and most valuable thing to remove. Two cases that passed via copy-pasted logic, the same calculation in two methods, repeated literal values.
- **Extract Method** for duplicated logic; give it a name that says *why*, not *how*.
- **Introduce Constant** for magic numbers/strings that recur or carry meaning (`const decimal VipDiscount = 0.10m;`).
- Watch for duplication *across the test/implementation boundary* too — sometimes a value belongs in one place both reference.

### A method doing two things
If you can describe a method only with "and" — "validates the order *and* saves it" — it likely wants splitting.
- **Extract Method** to separate the concerns, then have the original call both. Each becomes independently testable and nameable.

### Poor names
Names written under the pressure of getting to green are often provisional. Now's the time to fix them.
- **Rename** variables, methods, and types to match the vocabulary the tests revealed. `tmp`, `data`, `Process()` are invitations to rename. The IDE/`dotnet` rename is mechanical and safe under green tests.

### Primitive obsession
A `string` that's really an email, a `decimal` that's really money, three parameters that always travel together.
- **Introduce Parameter Object / value type** to give the concept a name and a home for its rules. Do this when the duplication or the invariants justify it — not speculatively.

### Long parameter lists / data clumps
The same cluster of arguments passed through several methods.
- **Introduce Parameter Object** or pass an existing domain object instead of its disassembled fields.

### Conditional complexity
Nested `if`s, a `switch` that keeps growing, boolean flags steering behavior.
- **Guard clauses / early returns** to flatten nesting and handle edge cases up front.
- **Decompose Conditional** — extract the condition and each branch into well-named methods so the intent reads in plain language.
- A `switch` on a type code that keeps growing is a hint toward polymorphism — but only refactor toward that when a second or third reason to branch appears, not on the first.

### Feature envy / misplaced responsibility
A method that reaches deep into another object's data to make a decision.
- **Move Method** to where the data lives, so the object that owns the state owns the behavior over it.

## Refactor the tests too

Test code earns the same care. With the suite green, look at the tests you just wrote:
- **Extract test helpers / builders** when arrange blocks repeat. A `CreateAccount(balance: 100m)` factory or a fluent builder removes noise and makes each test's *relevant* setup stand out.
- **Use fixtures/shared setup** (xUnit constructor or `IClassFixture`, NUnit `[SetUp]`) for genuinely common arrangement — but keep anything that varies per test *in* the test, where the reader can see it.
- **Rename test data** to carry meaning: `expiredCard`, `vipCustomer`, not `c1`, `obj2`.
- **Delete redundant tests** that assert the same behavior as another. Coverage isn't test count; an overlapping test is maintenance cost with no added safety.

## When *not* to refactor

- When there's nothing there — don't manufacture abstraction to feel productive. Premature generalization (building for cases you have no test for) is the opposite failure from the one TDD guards against, and just as costly.
- When the suite is red — fix or revert to green first. Refactoring on a red bar means you can't tell your refactoring from a regression.
- When the change you want is actually a behavior change — that's a new Red-Green cycle, not a refactor.

## Closing each cycle

After refactoring, run the **full** test suite (not just the filtered subset) to confirm the whole system is still green, then move to the next behavior on your list. Leaving each cycle on a green full-suite run is what makes the next cycle's failure unambiguous — if something's red at the start of the next Red phase, it's the test you just wrote, not a mess you left behind.
