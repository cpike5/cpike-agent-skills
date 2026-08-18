# Simplified English

Reports get read by people who did not do the work: a client, a manager, a developer joining next
month, the author in six months. Technical accuracy is not the problem — most report prose fails
because the sentences are long, the voice is passive, and the same idea is named three different
ways.

This file is the default writing style for every report the skill produces, HTML and Markdown
alike. It borrows from Simplified Technical English (ASD-STE100) without adopting the full
specification: the rules below are the ones that carry most of the benefit.

**Simple is not vague.** Keep every identifier, number, and qualification exact. Simplify the
language around them, never the content.

## The rules

### 1. One idea per sentence, 20 words or fewer

If a sentence needs a comma to add a second clause, it is usually two sentences.

> ✗ The Jinja template's `validateDataIntegrity()` now calls `pollValidationStatus()`, which polls
> the status endpoint every 3 seconds and reloads the page once the job leaves the running state.

> ✓ `validateDataIntegrity()` now calls `pollValidationStatus()`. That function polls the status
> endpoint every 3 seconds. When the job stops running, the page reloads.

Sentences of 25+ words are the single most common defect. Count them.

### 2. Active voice, and name the actor

Passive voice hides who does the work, which is usually the fact the reader needs.

| Passive | Active |
| --- | --- |
| The check was reordered | The diff moves the check |
| Coverage was not added | Nobody added coverage |
| Blob I/O is offloaded to threads | `asyncio.to_thread` runs the blob calls |

Passive is allowed when the actor is genuinely unknown or irrelevant — "the file was renamed at
some point" — and nowhere else.

### 3. Present tense for what is true, past tense for what happened

Describe current behaviour in the present tense. Use the past tense only for events: what the
code did before the change, what the review found, what someone did.

### 4. One term for one thing

Pick one word per concept and repeat it. Synonym variety reads as elegance in an essay and as a
second concept in a report.

If the change moves work to a process pool, it is a **process pool** every time — not "the pool",
"a worker process", "out-of-process execution", and "the subprocess" in four consecutive
paragraphs. Same for the reader's nouns: **job**, **endpoint**, **request**, **scan**. Write the
list of terms down before writing the section if the domain has more than about six.

### 5. Cut the empty words

| Wordy | Plain |
| --- | --- |
| utilize, leverage | use |
| in order to | to |
| prior to / subsequent to | before / after |
| due to the fact that | because |
| in the event that | if |
| has the ability to / is able to | can |
| at this point in time | now |
| a number of | some, or the actual count |
| approximately | about |
| surface (verb) | show |
| facilitate | help |
| remediate | fix |
| functionality | what it does, or name the feature |
| methodology | method |
| perform validation on | validate |

Delete outright: *very, quite, fairly, essentially, effectively, arguably, notably, it is worth
noting that, it should be mentioned that, as previously stated*.

### 6. No noun stacks longer than three words

"Background job status endpoint poll interval" makes the reader parse before they read. Break it
with a preposition: "how often the page polls the job status endpoint".

### 7. Keep the small words

Do not write headline-ese in body text. Keep articles (*the*, *a*) and relative pronouns
(*that*, *which*) — they tell the reader where the clause boundary is.

> ✗ Check runs after cancellation check so cancelled scan returns clean result.
> ✓ The check runs after the cancellation check, so a cancelled scan returns a clean result.

### 8. Prefer a simple verb to a noun built from one

"Validation of the data occurs before upload" → "The app validates the data before upload".
Verbs carry the action; nouns made from verbs (*-tion*, *-ment*, *-ance*) bury it.

### 9. No metaphor and no idiom

"Move off the request path" is a useful, literal description — keep it. "Stalls the whole event
loop" is fine, because that is what happens. But *lift and shift, hand in glove, low-hanging
fruit, boil the ocean, on the same page, out of the box* say nothing precise and read badly for
anyone who works in English as a second language.

### 10. Explain an acronym or a domain term the first time

`GIL` is not common knowledge outside async Python. One clause is enough: "the GIL, the lock that
lets only one thread run Python at a time". Do it once, then use the term freely.

### 11. Paragraphs of six sentences or fewer

A card body is two tight paragraphs (see `${CLAUDE_PLUGIN_ROOT}/docs/04-editorial.md`). If a
paragraph runs longer, it is either two paragraphs or a list.

### 12. Turn conditions and sequences into lists

Three or more conditions in one sentence become a bulleted list. Steps that happen in order
become a numbered list or a `.seq` component. Prose is for argument, not for enumeration.

## What does not change

Simplified English governs the connective language. It does not soften the report:

- **Identifiers stay exact.** `document_scan_service.py`, `read_pir_book_in_process`,
  `300-second timeout`. Never paraphrase a name.
- **Numbers stay precise, and ranges stay ranges.** "90–130 h, central ~110" is plain and honest.
- **The headline stays a finding.** `04-editorial.md` still applies — flat statement, then the
  sharp half in `em`. Short sentences make that device work better, not worse.
- **Bold still carries the claim.** Bold text read alone must still deliver the findings.
- **Qualification stays.** "This holds only for a single worker process" is not a hedge; it is the
  finding. Cut the padding, never the caveat.

## Worked example

From a real report, before:

> All seven files serve one theme: moving blocking work off the async request path, either to a
> background task or to a worker thread/process.
>
> `.env` changed by 4 lines (3 added, 1 removed) but was intentionally left out of this report,
> since `.env` files commonly hold connection strings or secrets that should not be pasted into a
> report file.

After:

> All seven files do the same thing. They move blocking work off the async request path. The work
> goes to a background task, a worker thread, or a worker process.
>
> `.env` changed by 4 lines: 3 added, 1 removed. This report leaves it out, because `.env` files
> often hold connection strings and secrets. Read it with `git diff .env` before you commit.

Same facts, same precision, one term per concept, no sentence over 20 words.

## The check before delivery

Add these to the review in `${CLAUDE_PLUGIN_ROOT}/docs/01-html-workflow.md`:

1. Find the longest sentence in the report. If it is over 25 words, split it.
2. Search the body for *utilize*, *leverage*, *in order to*, *facilitate*, *functionality*. Each
   hit is a rewrite.
3. Read the first sentence of every card. Is it active, present tense, and under 20 words?
4. Pick the two main domain nouns. Is each one named the same way everywhere?
