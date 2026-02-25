# System Prompts for Agents

## Passing System Prompts

Set the `System` property on `MessageCreateParams`. It accepts a plain string.

```csharp
var parameters = new MessageCreateParams
{
    Model = "claude-opus-4-6",
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

## Chain-of-Thought Prompting

Recommended for Claude Sonnet and Haiku models handling tool use. This pattern improves tool selection accuracy:

```
Answer the user's request using relevant tools if they are available. Before
calling a tool, analyze the request. First, identify which tool best addresses
the question. Second, verify that all required parameters are present or can
be inferred from context. If all required parameters are available, call the
tool. If a required parameter is missing, ask the user for it — do not call
the tool with placeholder values.
```

## Planning Pattern

For agents executing multi-step tasks:

```
When given a complex task:
1. Outline your plan before taking any action
2. Use tools to gather context before making changes
3. Verify your work after each change
4. If something goes wrong, stop and reassess before continuing
5. Report the final outcome with a summary of what was done
```

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
| Code assistant | Role definition, tool list, "gather context before changing" |
| Data analyst | Output format expectations, precision requirements, tool usage guidance |
| Multi-step task runner | Planning mandate, verification steps, failure behavior |
| Customer-facing | Tone, escalation rules, what NOT to do |
| Autonomous (long-running) | Loop behavior, when to stop, error recovery |

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
    - Explain your reasoning before making tool calls
    - After completing a task, summarize what was changed and why
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
- **Overly long system prompts** -- Claude can lose track of instructions buried deep in long prompts; use XML sections to structure them
- **Conflicting instructions** -- later instructions in the prompt tend to win; put the most critical rules at the top
- **Missing tool guidance** -- without tool usage instructions, Claude may call tools unnecessarily or not at all
- **No failure behavior defined** -- agents without explicit failure instructions tend to hallucinate results when tools fail
