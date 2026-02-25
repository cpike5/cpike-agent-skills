# Agent Architecture Patterns

Anthropic's "Building Effective Agents" guide defines 7 patterns. Use the simplest pattern that solves the problem — complexity should be justified by requirements.

## Pattern Decision Tree

```
Single LLM call sufficient?
  └─ Yes → Augmented LLM (tools + retrieval)
  └─ No, is task structure fixed?
       └─ Yes, sequential → Prompt Chaining
       └─ Yes, categorized → Routing
       └─ Independent subtasks → Parallelization
       └─ No, open-ended
            └─ Needs critique loop → Evaluator-Optimizer
            └─ Needs worker delegation → Orchestrator-Workers
            └─ Fully autonomous → Autonomous Agent
```

## 1. Augmented LLM

**What:** A single LLM call enhanced with retrieval (RAG), tool use, and/or memory injection.

**When to use:** Most agents start here. Foundation for all other patterns.

```csharp
// DI-first augmented LLM
public class AugmentedAgent(IChatClient chatClient, IVectorStore vectorStore)
{
    public async Task<string> AskAsync(string question)
    {
        // Retrieve relevant context
        var context = await vectorStore.SearchAsync(question, topK: 5);
        var contextText = string.Join("\n\n", context.Select(c => c.Content));

        var messages = new List<ChatMessage>
        {
            new(ChatRole.System, "Answer using the provided context. If the context is insufficient, say so."),
            new(ChatRole.User, $"Context:\n{contextText}\n\nQuestion: {question}")
        };

        var response = await chatClient.GetResponseAsync(messages);
        return response.Message.Text ?? "";
    }
}
```

## 2. Prompt Chaining

**What:** A fixed sequence of LLM calls. Each output feeds into the next. Programmatic gates can short-circuit the chain.

**When to use:** Multi-step tasks with known, ordered subtasks (e.g., extract → validate → transform → write).

```csharp
public class DocumentPipeline(IChatClient chatClient)
{
    public async Task<string> ProcessAsync(string rawDocument)
    {
        // Step 1: Extract structured data
        var extracted = await chatClient.GetResponseAsync(
            $"Extract the key facts from this document as JSON:\n{rawDocument}");

        // Programmatic gate -- validate extraction succeeded
        if (!IsValidJson(extracted.Message.Text))
            throw new InvalidOperationException("Extraction failed, cannot continue");

        // Step 2: Validate and enrich
        var validated = await chatClient.GetResponseAsync(
            $"Validate and fill gaps in this data: {extracted.Message.Text}");

        // Step 3: Generate final output
        var output = await chatClient.GetResponseAsync(
            $"Format this data as a user-friendly report:\n{validated.Message.Text}");

        return output.Message.Text ?? "";
    }

    private static bool IsValidJson(string? text)
    {
        if (string.IsNullOrWhiteSpace(text)) return false;
        try { System.Text.Json.JsonDocument.Parse(text); return true; }
        catch { return false; }
    }
}
```

## 3. Routing

**What:** Classify input first, then route to a specialized handler (LLM or function) for that category.

**When to use:** Distinct input types needing different prompts, tools, or models.

```csharp
public enum RequestCategory { Technical, Billing, General }

public class RouterAgent(IChatClient classifier, IServiceProvider services)
{
    public async Task<string> HandleAsync(string userInput)
    {
        // Classify
        var classification = await classifier.GetResponseAsync(
            $"""
            Classify this request into exactly one category: Technical, Billing, General.
            Respond with only the category name.
            Request: {userInput}
            """);

        var category = Enum.Parse<RequestCategory>(
            classification.Message.Text?.Trim() ?? "General", ignoreCase: true);

        // Route to specialized handler
        return category switch
        {
            RequestCategory.Technical => await services
                .GetRequiredService<TechnicalSupportAgent>()
                .HandleAsync(userInput),
            RequestCategory.Billing => await services
                .GetRequiredService<BillingAgent>()
                .HandleAsync(userInput),
            _ => await services
                .GetRequiredService<GeneralAgent>()
                .HandleAsync(userInput),
        };
    }
}
```

## 4. Parallelization

**What:** Run multiple LLM operations simultaneously. Two sub-patterns:

- **Sectioning:** Split a large task into independent chunks, process in parallel, aggregate.
- **Voting:** Run the same prompt N times, pick the majority/best result.

**When to use:** Independent subtasks, need diversity of outputs, or throughput matters.

```csharp
public class ParallelAnalysisAgent(IChatClient chatClient)
{
    // Sectioning: analyze multiple documents simultaneously
    public async Task<string[]> AnalyzeDocumentsAsync(string[] documents)
    {
        var tasks = documents.Select(doc =>
            chatClient.GetResponseAsync($"Summarize this document:\n{doc}"));

        var results = await Task.WhenAll(tasks);
        return results.Select(r => r.Message.Text ?? "").ToArray();
    }

    // Voting: generate multiple responses, pick the best
    public async Task<string> VotingResponseAsync(string question, int votes = 3)
    {
        var tasks = Enumerable.Range(0, votes)
            .Select(_ => chatClient.GetResponseAsync(question));

        var candidates = await Task.WhenAll(tasks);
        var candidateTexts = candidates.Select(r => r.Message.Text ?? "");

        // Ask Claude to pick the best candidate
        var bestOf = await chatClient.GetResponseAsync(
            $"""
            Given these {votes} candidate answers to "{question}", pick the most accurate and helpful one.
            Respond with only the chosen answer text, not an explanation.

            Candidates:
            {string.Join("\n---\n", candidateTexts)}
            """);

        return bestOf.Message.Text ?? candidates[0].Message.Text ?? "";
    }
}
```

## 5. Orchestrator-Workers

**What:** A central orchestrator LLM decomposes tasks and delegates to worker LLMs. Workers report back; orchestrator synthesizes.

**When to use:** Complex tasks where the number and type of subtasks are not known upfront.

```csharp
public class OrchestratorAgent(IChatClient orchestrator, WorkerPool workers)
{
    public async Task<string> ExecuteAsync(string complexTask)
    {
        // Orchestrator plans the work
        var plan = await orchestrator.GetResponseAsync(
            $"""
            Break this task into independent subtasks. Return as JSON array of objects with
            "worker_type" and "task" fields.
            Task: {complexTask}
            """);

        var subtasks = ParseSubtasks(plan.Message.Text);

        // Workers execute in parallel
        var workerTasks = subtasks.Select(subtask =>
            workers.GetWorker(subtask.WorkerType).ExecuteAsync(subtask.Task));

        var results = await Task.WhenAll(workerTasks);

        // Orchestrator synthesizes results
        var synthesis = await orchestrator.GetResponseAsync(
            $"""
            Synthesize these worker results into a final answer for: {complexTask}

            Worker results:
            {string.Join("\n\n", results.Select((r, i) => $"Worker {i + 1}: {r}"))}
            """);

        return synthesis.Message.Text ?? "";
    }
}
```

## 6. Evaluator-Optimizer

**What:** A generator LLM produces output. An evaluator LLM critiques it. Loop until quality threshold met.

**When to use:** Tasks with clear quality criteria (code correctness, accuracy, tone).

```csharp
public class EvaluatorOptimizerAgent(IChatClient generator, IChatClient evaluator)
{
    public async Task<string> OptimizeAsync(string task, int maxRounds = 3)
    {
        var current = await generator.GetResponseAsync(task);
        var output = current.Message.Text ?? "";

        for (int round = 0; round < maxRounds; round++)
        {
            var evaluation = await evaluator.GetResponseAsync(
                $"""
                Evaluate this output for the task: {task}

                Output:
                {output}

                Respond with JSON: {{ "score": 0-10, "issues": ["..."], "passed": true/false }}
                """);

            var evalResult = ParseEvaluation(evaluation.Message.Text);

            if (evalResult.Passed)
                return output;

            // Feed critique back to generator
            var improved = await generator.GetResponseAsync(
                $"""
                Improve this output. Fix these issues: {string.Join(", ", evalResult.Issues)}

                Original task: {task}
                Current output: {output}
                """);

            output = improved.Message.Text ?? output;
        }

        return output; // Return best effort after maxRounds
    }
}
```

## 7. Autonomous Agent

**What:** Agent runs a tool-use loop independently until the goal is achieved. No fixed structure — Claude decides which tools to use and in what order.

**When to use:** Open-ended multi-step problems where the path to completion is unknown upfront.

```csharp
public class AutonomousAgent(AnthropicClient client, ILogger<AutonomousAgent> logger)
{
    private readonly Dictionary<string, Func<JsonElement, Task<string>>> _tools = new();

    public void RegisterTool(string name, Func<JsonElement, Task<string>> handler)
        => _tools[name] = handler;

    public async Task<string> RunAsync(string goal, MessageCreateParams baseParams, int maxIterations = 20)
    {
        var messages = new List<Message>
        {
            new() { Role = Role.User, Content = goal }
        };

        for (int i = 0; i < maxIterations; i++)
        {
            var parameters = baseParams with { Messages = messages.ToArray() };
            var response = await client.Messages.Create(parameters);

            messages.Add(new() { Role = Role.Assistant, Content = response.Content });

            if (response.StopReason == "end_turn")
            {
                logger.LogInformation("Agent completed in {Iterations} iterations", i + 1);
                return ExtractText(response.Content);
            }

            if (response.StopReason == "tool_use")
            {
                var toolResults = new List<object>();

                foreach (var block in response.Content)
                {
                    if (block.TryPickToolUse(out var toolUse))
                    {
                        logger.LogDebug("Executing tool: {Tool}", toolUse.Name);

                        string result;
                        try
                        {
                            result = _tools.TryGetValue(toolUse.Name, out var handler)
                                ? await handler(toolUse.Input)
                                : $"Unknown tool: {toolUse.Name}";
                        }
                        catch (Exception ex)
                        {
                            result = $"Tool failed: {ex.Message}";
                        }

                        toolResults.Add(new
                        {
                            type = "tool_result",
                            tool_use_id = toolUse.Id,
                            content = result
                        });
                    }
                }

                messages.Add(new() { Role = Role.User, Content = toolResults });
            }
        }

        return "Agent reached max iterations.";
    }

    private static string ExtractText(IEnumerable<ContentBlock> content)
        => string.Concat(content.OfType<TextBlock>().Select(b => b.Text));
}
```

## Pattern Comparison

| Pattern | LLM Calls | Latency | Complexity | Best For |
|---------|-----------|---------|------------|----------|
| Augmented LLM | 1 | Low | Low | Most use cases |
| Prompt Chaining | N (sequential) | Medium | Low | Fixed pipelines |
| Routing | 1 + handler | Low | Low | Categorized inputs |
| Parallelization | N (parallel) | Low | Medium | Independent tasks |
| Orchestrator-Workers | 2+ | Medium | High | Dynamic task decomposition |
| Evaluator-Optimizer | 2N | High | Medium | Quality-critical outputs |
| Autonomous Agent | Variable | Variable | High | Open-ended goals |
