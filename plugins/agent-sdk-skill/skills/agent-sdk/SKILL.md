---
name: agent-sdk
description: "Use this skill when building Claude-powered agents in .NET, implementing tool use or function calling with the Anthropic C# SDK, creating agentic loops, engineering system prompts for agents, handling streaming responses, using extended thinking, managing conversation context and token budgets, designing agent architecture patterns (augmented LLM, prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer, autonomous agents), integrating MCP servers or Semantic Kernel, or working with the Anthropic SDK .NET patterns (AnthropicClient, IChatClient, UseFunctionInvocation, AIFunctionFactory). Invoke when: creating or configuring AnthropicClient, registering IChatClient in DI, defining tools with JSON Schema, handling tool_use/tool_result content blocks, building manual agentic loops, streaming with CreateStreaming or MessageContentAggregator, enabling extended thinking with ThinkingParameters, writing agent system prompts, implementing retry/error handling for Anthropic API, managing conversation history compaction, choosing between agent architecture patterns, connecting to MCP tool servers, or using multi-cloud (Bedrock/Foundry) deployments."
---

# Agent SDK Knowledge Base (.NET)

You are building AI agents using the Anthropic C# SDK in .NET. There is **no .NET Agent SDK** — agents must be built manually atop the Messages API. Read the relevant docs below based on what you're building.

## Quick Decision: What Pattern Do I Need?

| Need | Pattern | Doc |
|------|---------|-----|
| Simplest agent with auto tool loop | IChatClient + `UseFunctionInvocation()` | 06 |
| Full control over each tool call | Manual Messages API loop | 06 |
| Stream responses to user in real-time | Streaming agentic loop | 07 |
| Production service with DI | DI-friendly agent service | 02, 06 |
| Complex reasoning before acting | Extended thinking | 08 |
| Choose between SDK packages | SDK comparison | 01 |
| Connect to external tool servers | MCP integration | 13 |
| Multi-step orchestration | Architecture patterns | 12 |

## Reference Documentation

### Always Read First
- ${CLAUDE_PLUGIN_ROOT}/docs/01-sdk-landscape.md — Official vs unofficial SDK, feature comparison, selection guidance

### Setup & Foundations
- ${CLAUDE_PLUGIN_ROOT}/docs/02-client-setup-di.md — AnthropicClient, IChatClient, DI registration, IOptions, multi-cloud
- ${CLAUDE_PLUGIN_ROOT}/docs/03-messages-api.md — MessageCreateParams, content blocks, StopReason, token usage

### Tool Use
- ${CLAUDE_PLUGIN_ROOT}/docs/04-tool-definitions.md — JSON Schema, input_examples, strict mode, tool_choice, description best practices
- ${CLAUDE_PLUGIN_ROOT}/docs/05-tool-execution.md — tool_use/tool_result handling, IChatClient auto-invocation, manual dispatch

### Agent Patterns
- ${CLAUDE_PLUGIN_ROOT}/docs/06-agentic-loops.md — 4 loop patterns (auto, manual, streaming, DI service), max-iteration guards
- ${CLAUDE_PLUGIN_ROOT}/docs/12-architecture-patterns.md — Anthropic's 7 patterns with .NET implementation guidance

### Streaming & Thinking
- ${CLAUDE_PLUGIN_ROOT}/docs/07-streaming.md — CreateStreaming, MessageContentAggregator, delta processing
- ${CLAUDE_PLUGIN_ROOT}/docs/08-extended-thinking.md — ThinkingParameters, budget tokens, streaming thinking deltas

### Reliability & Context
- ${CLAUDE_PLUGIN_ROOT}/docs/09-system-prompts.md — Agent prompt engineering, role definition, chain-of-thought, auto-generated tool prompts
- ${CLAUDE_PLUGIN_ROOT}/docs/10-error-handling-retries.md — Exception hierarchy, built-in retries, Polly, graceful degradation
- ${CLAUDE_PLUGIN_ROOT}/docs/11-context-management.md — Token counting, sliding window, summarization compaction

### Advanced
- ${CLAUDE_PLUGIN_ROOT}/docs/13-advanced-features.md — MCP integration, programmatic tool calling, Bedrock/Foundry, Semantic Kernel

## Critical Rules (Common Mistakes)

1. **There is no .NET Agent SDK** — Don't look for one. Build agentic loops manually using the Messages API or use `UseFunctionInvocation()` with IChatClient.
2. **Always add max-iteration guards** — Every agentic loop must have a maximum iteration count (e.g., 10-25). Infinite loops burn tokens and money.
3. **Always check StopReason** — `end_turn` means done, `tool_use` means execute tools and continue. Ignoring this breaks the loop.
4. **Return ALL tool_results together** — When Claude makes parallel tool calls, execute all tools and return all results in a single user message. Never send partial results.
5. **Prefer UseFunctionInvocation()** — For most agents, IChatClient with `UseFunctionInvocation()` handles the tool loop automatically. Only use manual loops when you need per-iteration control.
6. **Write 3-4 sentence tool descriptions** — This is the single most important factor in tool performance. Include what it does, when to use it, and limitations.
7. **No string interpolation in system prompts** — Prevents prompt injection. Use parameterized tool inputs instead.
8. **Dispose streaming resources** — `IAsyncEnumerable` streams must be properly consumed or disposed. Use `await foreach` or `ConfigureAwait(false)`.
9. **Extended thinking needs streaming** — In the official SDK, extended thinking is only available via `CreateStreaming`, not the synchronous `Create` method.
10. **Register AnthropicClient and IChatClient as Singleton** — Both are thread-safe. Scoped/transient registration wastes resources.
11. **Never put API keys in code** — Use environment variables (`ANTHROPIC_API_KEY`), user secrets, or a vault.
12. **Capture tool errors as tool_result** — When a tool throws, catch the exception and return it as a `tool_result` with `is_error: true`. Don't let tool failures crash the loop.
