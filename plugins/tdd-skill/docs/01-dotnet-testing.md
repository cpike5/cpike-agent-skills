# .NET Testing: Detect, Run, Read

This doc covers the mechanics of working with .NET tests in a TDD loop: figuring out what the project uses, running tests fast and narrowly, reading the output correctly, and bootstrapping a test project when none exists.

## Detect the existing stack

Match what's already there. Inspect the test project before writing a single test — the wrong framework or assertion style is friction for every future reader.

**Find the test project(s):** look for projects whose `.csproj` references `Microsoft.NET.Test.Sdk`, or directories/projects named `*.Tests`, `*.Test`, `*.UnitTests`, or under a `test/`/`tests/` folder. The solution file (`.sln`) lists them too.

**Read the `.csproj` `<PackageReference>` entries** to identify the three things that shape every test you'll write:

| Concern | Tell-tale package | What changes in your tests |
|---------|-------------------|----------------------------|
| Runner | `xunit` / `NUnit` / `MSTest.TestFramework` | Attributes and parameterized-test style |
| Assertions | `FluentAssertions` / `Shouldly` / (none = built-in) | `result.Should().Be(x)` vs `Assert.Equal(x, result)` |
| Mocking | `Moq` / `NSubstitute` / `FakeItEasy` | Substitute/mock creation syntax |

Also skim an existing test file or two to absorb the local conventions — naming, folder layout, base classes, fixtures. Conventions beat defaults.

### Attribute / assertion cheat-sheet by runner

**xUnit** (modern default):
```csharp
[Fact]                       // a single test
public void Add_TwoPositives_ReturnsSum() { }

[Theory]                     // parameterized
[InlineData(2, 3, 5)]
[InlineData(-1, 1, 0)]
public void Add_Cases(int a, int b, int expected) { }
```
No `[TestClass]` needed; the test runner discovers `[Fact]`/`[Theory]` methods. Per-test setup goes in the constructor; teardown via `IDisposable.Dispose`.

**NUnit**:
```csharp
[TestFixture]
public class CalculatorTests
{
    [SetUp] public void SetUp() { }
    [Test] public void Add_TwoPositives_ReturnsSum() { }

    [TestCase(2, 3, 5)]
    [TestCase(-1, 1, 0)]
    public void Add_Cases(int a, int b, int expected) { }
}
```
Idiomatic assertion: `Assert.That(result, Is.EqualTo(5))`.

**MSTest**:
```csharp
[TestClass]
public class CalculatorTests
{
    [TestInitialize] public void Init() { }
    [TestMethod] public void Add_TwoPositives_ReturnsSum() { }

    [DataTestMethod]
    [DataRow(2, 3, 5)]
    public void Add_Cases(int a, int b, int expected) { }
}
```

### Assertion style

- **FluentAssertions**: `result.Should().Be(5);` · `act.Should().Throw<ArgumentException>();` · `list.Should().ContainSingle().Which.Name.Should().Be("x");` — reads as a spec and gives rich failure messages. Use it if the project already has it.
- **Built-in**: `Assert.Equal(5, result);` (xUnit/MSTest) or `Assert.That(result, Is.EqualTo(5))` (NUnit). For exceptions, `Assert.Throws<ArgumentException>(() => act());`.

Pick whichever the project uses. Don't introduce FluentAssertions into a project that doesn't have it just for one test — consistency outweighs your preference.

### Mocking style

Reach for a test double only when the real collaborator is slow, non-deterministic, or has side effects you can't have in a test (network, clock, filesystem, payment gateway). Prefer the real thing otherwise — see `02-test-design.md`.

```csharp
// NSubstitute
var repo = Substitute.For<IOrderRepository>();
repo.GetById(42).Returns(new Order(42));

// Moq
var repo = new Mock<IOrderRepository>();
repo.Setup(r => r.GetById(42)).Returns(new Order(42));
// ... use repo.Object, verify with repo.Verify(...)
```

## Run tests — fast and narrow

In the Red and Green phases you want the *single* test you're working on, not the whole suite — fast feedback is the point.

**Run one test or a subset with `--filter`:**
```powershell
dotnet test --filter "FullyQualifiedName~Calculator.Add_TwoPositives"
dotnet test --filter "FullyQualifiedName~CalculatorTests"   # whole class
dotnet test --filter "Name~Add_Cases"                        # by method name substring
```
Filter operators: `=` exact, `!=` not, `~` contains. Properties: `FullyQualifiedName`, `Name`, `DisplayName`, plus trait-based `Category`/`TestCategory`.

**Target the test project** to skip restoring/building unrelated projects:
```powershell
dotnet test path/to/MyApp.Tests/MyApp.Tests.csproj --filter "FullyQualifiedName~Calculator"
```

**Speed knobs** once you've built at least once:
```powershell
dotnet test --no-restore --no-build --filter "..."   # after an initial build
```
Quieter output: add `-v q` (or `--verbosity quiet`). Build noise can bury the actual assertion failure.

**Run the full suite** at the end of Green (to confirm no regressions) and after refactoring:
```powershell
dotnet test path/to/MyApp.Tests/MyApp.Tests.csproj
```

## Read the output correctly

The point of the Red phase is confirming the test fails *for the right reason*. Distinguish these:

- **Assertion failure** (what you want in Red): `Assert.Equal() Failure: Expected: 5, Actual: 0` or FluentAssertions' `Expected result to be 5, but found 0`. The test ran, the behavior is wrong/missing. Good — now make it pass.
- **Compile error** (`error CS....`): the test didn't run at all. Often expected at first in TDD — you're referencing a type or method that doesn't exist yet. Create the minimal type/signature (throwing `NotImplementedException` or returning a default) so the test *compiles and then fails on the assertion*. That's true Red.
- **Wrong exception / NullReferenceException**: the test failed, but not where you intended. Investigate before implementing — your test setup may be wrong, or the failure is incidental.
- **Test not found / 0 tests ran**: filter typo, missing `[Fact]`/`[Test]` attribute, or the project didn't build. Check the filter and that the method is public and attributed.

A test that goes **green on the very first run**, before you wrote any implementation, is a red flag: the behavior may already exist, the assertion may be vacuous (asserting something always true), or you're testing the wrong thing. Stop and understand why.

## Greenfield: no test project yet

If the solution has no test project, default to **xUnit** and create one alongside the code:

```powershell
dotnet new xunit -n MyApp.Tests
dotnet sln add MyApp.Tests/MyApp.Tests.csproj
dotnet add MyApp.Tests/MyApp.Tests.csproj reference src/MyApp/MyApp.csproj
```

Conventional layout mirrors the production namespace: a test class `OrderServiceTests` for `OrderService`, in a folder structure that parallels `src/`. Add FluentAssertions and a mocking library only if you actually need them — start lean and introduce a dependency when a test demands it, not preemptively.
