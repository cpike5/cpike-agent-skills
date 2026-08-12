# System Prompts for Agents

## Passing System Prompts

Set the `System` property on `MessageCreateParams`. It accepts a plain string.

```csharp
var parameters = new MessageCreateParams
{
    Model = "claude-opus-5",
    MaxTokens = 4096,
    System = "You are a senior .NET developer assistant...",
    Messages = [new() { Role = Role.User, Content = "Fix the bug in auth.py" }],
};
```

For `IChatClient`, pass system instructions as a `ChatMessage` with role `System`:

```csharp
var messages = new List<ChatMessage>
{
    new(ChatRole.System, "You are a senior .NET developer assistant..."),
    new(ChatRole.User, "Fix the bug in auth.py"),
};
var response = await _chatClient.GetResponseAsync(messages, options);
```

## Auto-Generated Tool Prompt Structure

When tools are present, the API prepends a tool instruction block **before** your system prompt:

```
In this environment you have access to a set of tools you can use to answer
the user's question.
{{ FORMATTING INSTRUCTIONS }}
Here are the functions available in JSONSchema format:
{{ TOOL DEFINITIONS IN JSON SCHEMA }}
{{ YOUR SYSTEM PROMPT }}
{{ TOOL CONFIGURATION }}
```

**Your system prompt is appended after the auto-generated tool instructions.** You cannot control or replace the auto-generated portion — only what comes after it.

## Security: No String Interpolation

Never interpolate user-supplied content into system prompts. This creates prompt injection vulnerabilities.

```csharp
// WRONG -- user can override instructions
string system = $"You assist user {userName}. {userSuppliedContext}";

// CORRECT -- user context goes in the conversation, not the system prompt
string system = "You are a helpful assistant.";
var messages = new List<Message>
{
    new() { Role = Role.User, Content = $"Context: {userContext}\n\nQuestion: {userQuestion}" }
};
```

System prompt = static, trusted instructions. Conversation = dynamic, untrusted content.

## Role and Capability Definition

Define what the agent is, what tools it has, and how it should behave:

```
You are a senior .NET developer assistant. You have access to tools for reading
files, searching codebases, and executing commands. Use these tools proactively
to gather information before answering questions. Never guess at file contents
or code structure when you can look it up with a tool.
```

## Don't Script the Reasoning

Older prompts added "think step by step", `<scratchpad>` instructions, or step-by-step tool-selection scripts. Current models reason natively (adaptive thinking) and plan and self-verify without being told — these scaffolds are now redundant at best, and explicit "verify your work after each change" instructions cause over-verification. Control reasoning depth with the `effort` parameter, not prose.

What still earns its place in the prompt:

```
If a required tool parameter is missing, ask the user for it — do not call
the tool with placeholder values.
```

State goals, constraints, and how success is measured. Leave the *method* — planning, tool ordering, self-checks — to the model, and keep numbered steps only for genuinely fragile sequences (auth flows, destructive operations) where exactly one order is safe.

## Agentic Loop Pattern

For agents that run continuously until a goal is met:

```
You operate in an agentic loop. On each turn:
- Assess what information you still need
- Choose the most appropriate tool to gather it
- Execute the tool and analyze the results
- Decide if you need more information or can provide a final answer
Never fabricate results. If a tool fails, report the failure and ask for guidance.
```

## Patterns by Agent Type

| Agent Type | Key Prompt Elements |
|------------|---------------------|
| Code assistant | Role definition, tool contracts, scope discipline ("only the changes requested") |
| Data analyst | Output format expectations, precision requirements, data-source facts |
| Multi-step task runner | Goal and done-criteria, failure behavior |
| Customer-facing | Tone, escalation rules, real business constraints with their reasons |
| Autonomous (long-running) | When to stop, error recovery, what needs human approval |

## Structuring Long System Prompts

For complex agents with many behavioral rules, use XML-style sections to improve reliability:

```csharp
string system = """
    <role>
    You are a senior .NET developer assistant specializing in ASP.NET Core and
    Entity Framework. You help developers diagnose bugs, refactor code, and
    implement new features.
    </role>

    <tools>
    You have access to file reading, code search, and shell execution tools.
    Always read relevant source files before suggesting changes.
    </tools>

    <behavior>
    - Prefer minimal changes that solve the stated problem
    - After completing a task, briefly summarize what was changed and why
    </behavior>

    <restrictions>
    - Do not delete files without explicit confirmation
    - Do not run commands that modify production databases
    </restrictions>
    """;
```

## DI Registration

Register system prompts as configuration so they can be changed without redeployment:

```csharp
// appsettings.json
{
  "Anthropic": {
    "SystemPrompt": "You are a helpful assistant..."
  }
}

// Program.cs
services.AddSingleton<AgentService>(sp =>
{
    var config = sp.GetRequiredService<IConfiguration>();
    var client = sp.GetRequiredService<AnthropicClient>();
    var systemPrompt = config["Anthropic:SystemPrompt"]
        ?? throw new InvalidOperationException("System prompt not configured");
    return new AgentService(client, systemPrompt);
});
```

## Common Mistakes

- **Putting user data in the system prompt** -- use conversation history instead
- **Aggressive emphasis** -- current models follow the prompt literally, so `CRITICAL: You MUST use this tool` over-triggers; write `Use this tool when...` at normal volume
- **Conflicting or duplicated instructions** -- the model spends effort reconciling wordings; say each rule once, with its reason
- **Tool guidance in the wrong place** -- when a tool under- or over-triggers, fix its `description` (say *when* to call it), not the system prompt
- **No failure behavior defined** -- agents without explicit failure instructions tend to hallucinate results when tools fail
