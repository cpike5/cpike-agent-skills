# SDK Landscape

## The Three Layers

There are three distinct layers for building Claude-powered agents in .NET. Understanding which to use is the first decision.

| Layer | Package | Version | Status |
|-------|---------|---------|--------|
| Official C# Client SDK | `Anthropic` (NuGet) | v12.4.0 | Beta, Anthropic-maintained |
| Unofficial C# SDK | `Anthropic.SDK` (NuGet) | v5.10.0 | Stable, community (tghamm) |
| Claude Agent SDK | `claude-agent-sdk` (npm/pip) | Production | **Python & TypeScript only** |

**Critical:** There is no .NET Agent SDK. Anthropic's Claude Agent SDK exists only for Python and TypeScript. .NET agents must be built manually on top of the Messages API.

---

## Official `Anthropic` Package

```bash
dotnet add package Anthropic
```

- GitHub: [anthropics/anthropic-sdk-csharp](https://github.com/anthropics/anthropic-sdk-csharp)
- Targets: .NET Standard 2.0+ (run on .NET 8+ recommended)
- License: MIT
- Status: Beta — APIs may change between versions

> **Version warning:** `Anthropic` NuGet versions 3.x and below were the community `tryAGI` SDK, now moved to `tryAGI.Anthropic`. Version 10+ is the official Anthropic SDK. Do not confuse them.

### What it provides

- Low-level Messages API wrapper
- Streaming via `IAsyncEnumerable<RawMessageStreamEvent>`
- `AsIChatClient()` adapter for `Microsoft.Extensions.AI` integration
- Extended thinking support
- Multi-cloud packages for Bedrock, Foundry, Vertex
- Built-in retry (2 retries by default, exponential backoff)

---

## Unofficial `Anthropic.SDK` Package

```bash
dotnet add package Anthropic.SDK
```

- GitHub: [tghamm/Anthropic.SDK](https://github.com/tghamm/Anthropic.SDK)
- Targets: .NET Standard 2.0, .NET 8.0, .NET 10.0
- Status: Community-maintained, not affiliated with Anthropic

### Feature comparison

| Feature | Official `Anthropic` | Unofficial `Anthropic.SDK` |
|---------|---------------------|---------------------------|
| `IChatClient` adapter | Yes (`AsIChatClient()`) | Yes (`.Messages` implements it directly) |
| Function calling via attributes | No | Yes (`AIFunctionFactory.Create`) |
| Extended thinking | Yes (content block streaming) | Yes (`ThinkingParameters`) |
| Token counting API | Not documented | Yes (`CountMessageTokensAsync`) |
| Semantic Kernel integration | Not documented | Documented with examples |
| Streaming method | `CreateStreaming()` | `StreamClaudeMessageAsync()` |
| Model enum | `Model.ClaudeSonnet4_5_20250929` | `AnthropicModels.Claude46Sonnet` |
| Multi-cloud | Bedrock, Foundry, Vertex packages | Not documented |
| Anthropic-maintained | Yes | No |

---

## Claude Agent SDK (No .NET Support)

The Agent SDK is Anthropic's production-grade agentic framework. It was launched May 22, 2025 as "Claude Code SDK" and renamed September 29, 2025.

**What it provides (unavailable in .NET):**

| Capability | Agent SDK | .NET alternative |
|-----------|-----------|-----------------|
| Built-in tools (Read, Edit, Bash, Grep, WebSearch) | Built-in | Must implement yourself |
| Agentic loop (gather → act → verify) | Built-in | Build manually with Messages API |
| Subagent spawning | Built-in | Must implement yourself |
| Session management (resume, fork) | Built-in | Must implement yourself |
| Hooks (PreToolUse, PostToolUse, Stop) | Built-in | Must implement yourself |
| Automatic context compaction | Built-in | Must implement yourself |
| MCP integration | Built-in | Via `IChatClient` + MCP C# SDK |
| Permission controls | Built-in | Must implement yourself |

---

## Package Selection Guide

| Scenario | Recommendation |
|----------|---------------|
| New project, production use | Official `Anthropic` — Anthropic-maintained, gets features first |
| Need token counting API | Unofficial `Anthropic.SDK` |
| Need Semantic Kernel integration | Unofficial `Anthropic.SDK` (documented examples) |
| Need AWS Bedrock or Azure Foundry | Official `Anthropic` + cloud extension package |
| Need `IChatClient` + `UseFunctionInvocation()` | Either (both support it) |
| Building multi-cloud portable code | Official `Anthropic` via `IChatClient` abstraction |

---

## Installation by Scenario

### Minimal (direct API calls only)

```bash
dotnet add package Anthropic
```

### With Microsoft.Extensions.AI

```bash
dotnet add package Anthropic
dotnet add package Microsoft.Extensions.AI
```

### AWS Bedrock

```bash
dotnet add package Anthropic.Bedrock
```

### Azure Foundry

```bash
dotnet add package Anthropic.Foundry

```

### Unofficial SDK

```bash
dotnet add package Anthropic.SDK
```

---

## .NET vs Python/TypeScript Gap Summary

Because the Claude Agent SDK is unavailable for .NET, you must build components that are provided automatically in Python and TypeScript:

1. **Agentic loop** — the cycle of sending a message, receiving a `tool_use` response, executing the tool, and sending a `tool_result` back
2. **Tool dispatch** — routing tool call requests to C# implementations
3. **Conversation history** — accumulating messages across iterations
4. **Context compaction** — summarizing old messages when approaching token limits
5. **Session management** — persisting and resuming agent state
6. **Hooks** — intercepting tool calls for logging, auth, or modification

.NET advantages over Python/TypeScript:

- `IChatClient` abstraction enables portable code across AI providers
- `UseFunctionInvocation()` middleware handles the agentic loop automatically for simple cases
- MCP C# SDK enables connecting to external tool servers
- Semantic Kernel integration for complex orchestration
- Strong typing, DI-first design, and ASP.NET integration

---

## Common Mistakes

- **Confusing package versions** — `Anthropic` v3.x on NuGet was a different community SDK. Always verify you have v10+ (official).
- **Expecting a .NET Agent SDK to exist** — it does not. Do not search for `claude-agent-sdk` on NuGet; it is not there.
- **Using the unofficial SDK for new projects without reason** — the official SDK is the right default; switch to unofficial only for specific missing features.
- **Registering `AnthropicClient` as Transient** — it is an HTTP client wrapper. Register as Singleton.
