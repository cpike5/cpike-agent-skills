---
name: tdd
description: "Implement .NET features and fix bugs test-first using the Red-Green-Refactor cycle. Use this skill whenever the user asks to build, add, or implement a feature, fix a bug, or write code 'test-first', 'with TDD', 'test-driven', or 'red-green-refactor', or mentions writing tests before the implementation. Also consider it proactively when implementing non-trivial .NET logic — services, domain rules, validators, parsers, calculations, state machines, bug fixes with a clear reproduction — where a failing test would pin down the behavior and de-risk the change; in that case briefly propose the TDD approach before starting. Covers detecting the existing test stack (xUnit/NUnit/MSTest, FluentAssertions, Moq/NSubstitute), writing failing tests first, minimal implementations, and refactoring under a green test suite."
---

# Test-Driven Development (.NET)

Drive the implementation from tests. Write a test that describes a small slice of the desired behavior, watch it fail, make it pass with the least code that honestly does the job, then clean up — all while the suite stays green. The tests aren't paperwork you produce afterward; they're the specification you build against and the safety net that lets you refactor without fear.

This works because each cycle keeps the gap between "what I think the code does" and "what the code actually does" small enough to reason about. You're never more than one failing test away from understanding what broke.

## The loop

For each slice of behavior, run this cycle:

1. **RED** — Write a test for one new behavior. Run it. Confirm it fails, and that it fails *for the reason you expect* (the assertion, not a compile error or typo). A test that passes immediately, or fails for the wrong reason, is telling you something — stop and understand it.
2. **GREEN** — Write the simplest implementation that makes the test pass. Resist building for requirements you haven't written a test for yet. Run the test; confirm green. Run the rest of the suite to confirm you didn't break anything.
3. **REFACTOR** — With the bar green, improve the design: remove duplication, clarify names, extract methods, tighten types. Change structure, not behavior. Re-run the suite after each meaningful change. This phase is not optional, but it is proportionate — sometimes there's nothing to clean up, and that's fine.

Then pick the next behavior and repeat. Stop when every behavior on your list is covered and green.

## Before the first test: build a test list

Spend a moment decomposing the feature or bug into a short list of concrete, observable behaviors before writing any test. Think in terms of *examples*: specific inputs and the outputs or effects they should produce — the happy path, the boundaries, the error cases, the "what should happen when…" questions.

This list is your map. You don't have to get it perfect or complete; you'll discover new cases as you go and add them. But starting with 3–6 examples keeps you from either over-building or forgetting the unhappy paths. Share the list with the user when the behavior is ambiguous — it's a cheap way to surface a misunderstanding before you've written code.

For a **bug fix**, the first item on the list is always a test that reproduces the bug — one that fails *because* of the bug. That test failing is your proof you've actually found the defect; that test passing is your proof you've fixed it, and it stays in the suite forever as a guard against regression.

## Detect the stack first, don't assume

Before writing tests, find out what the project already uses — test runner, assertion style, mocking library — and match it. A test that imports the wrong framework or apes a foreign style is friction for everyone who reads it. If the project is greenfield with no test project yet, default to xUnit and set one up.

See `${CLAUDE_PLUGIN_ROOT}/docs/01-dotnet-testing.md` for how to detect the stack, lay out and reference the test project, run targeted tests with `dotnet test --filter`, and read the output to tell a real failure from a flaky or misconfigured one.

## Staying disciplined without being rigid

The discipline that matters is **writing the test before the implementation** — that ordering is what forces you to define the behavior from the outside and keeps the code testable. Hold that line.

Be pragmatic about the rest:

- **Batch when it's natural.** For a cluster of closely related cases (e.g. several input variations of one rule), it's fine to write a few tests together and implement against them as a group, rather than ceremonially looping one assertion at a time. Use judgment: the smaller the step, the faster the feedback, but tiny steps on obvious code is busywork.
- **Always confirm the failure is real for non-trivial logic.** Running the test and seeing red is what distinguishes TDD from "writing tests that happen to pass." For genuinely trivial cases you can use judgment, but when in doubt, watch it fail first — it's caught more bad tests than any review.
- **Don't test the framework or trivial getters.** Test behavior and logic you actually wrote, the decisions and the edge cases. Exhaustively testing plumbing the compiler already guarantees is noise that future readers have to wade through.
- **Keep implementations honest, not artificially dumb.** "Simplest thing that passes" is a discipline against speculative generality, not a license to hard-code a return value you know is wrong. If the obvious correct implementation is clear, write it; if you're unsure of the shape, let a second test drive it out.

See `${CLAUDE_PLUGIN_ROOT}/docs/02-test-design.md` for what makes a good failing test: Arrange-Act-Assert, descriptive naming that reads as a spec, choosing real collaborators vs. test doubles, and covering edge cases without redundancy.

## The refactor phase, concretely

Green is permission to improve the design, and the suite you just wrote is what makes that safe. Look at both the implementation *and the tests* — test code is real code and rots the same way. Common targets: duplication between cases, names that no longer fit, a method doing two things, primitive obsession, a test setup that's begging to be a helper or fixture.

See `${CLAUDE_PLUGIN_ROOT}/docs/03-refactor-catalog.md` for a catalog of refactorings safe to apply under a green suite, the smells that signal each, and how to keep tests passing throughout.

## Reporting back

When you finish (or pause at a checkpoint), tell the user where things stand honestly: which behaviors are covered and green, what's still on the test list, and the actual test output — not a claim of success without the run behind it. If a test is failing or you skipped a case, say so plainly. The whole value of TDD is trustworthy feedback; don't undercut it by overstating the result.

## Reference docs

- `${CLAUDE_PLUGIN_ROOT}/docs/01-dotnet-testing.md` — Stack detection, test project layout, running tests, reading output, greenfield xUnit setup
- `${CLAUDE_PLUGIN_ROOT}/docs/02-test-design.md` — Writing good failing tests: AAA, naming, test doubles, edge-case coverage
- `${CLAUDE_PLUGIN_ROOT}/docs/03-refactor-catalog.md` — Refactor-phase catalog: smells, safe refactorings, keeping the suite green
