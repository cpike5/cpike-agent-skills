# Output Formats

Choosing the right format and applying it correctly.

---

## Format Selection

If the user specifies a format, use it. If they don't, use the **content-type default** from `${CLAUDE_PLUGIN_ROOT}/docs/01-content-types.md`. When in doubt, lead with a TL;DR and follow with bullets — it works for almost everything and lets the user stop reading when they have enough.

---

## TL;DR

**One sentence.** Capture the single most important thing. This is the format users scan first; if it's wrong or vague, nothing else matters.

- Write the substance directly: "The proposal replaces the current auth system with JWT-based sessions starting Q3."
- Do not write: "This document covers the proposed changes to authentication."
- No hedge phrases: "In essence…", "Basically…", "At its core…"
- If the source genuinely has multiple co-equal main points, write two sentences.

**When to lead with it:** Always, unless the user asked for a different primary format (e.g. pure action-item list).

---

## Bullet Points (Key Points)

**3-7 bullets for most content; up to 10 for very dense material.** Each bullet is one self-contained idea.

Rules:
- Start each bullet with the fact or action, not the context: "Authentication is now JWT-based" not "Regarding authentication, the team decided to use JWT."
- Use parallel grammatical structure within a list.
- No sub-bullets unless nesting genuinely adds clarity (max one level deep).
- Order by importance (most critical first), not document order.

**When to use:** Default for technical docs, specs, meeting notes, changelogs, anything with discrete facts.

---

## Executive Summary

**A short prose section (3-8 sentences) written for decision-makers** who want enough context to act but won't read the detail.

Structure:
1. Situation — what prompted this (1 sentence)
2. Key finding or recommendation (1-2 sentences)
3. Impact or consequence (1 sentence)
4. Ask or next step (1 sentence, if applicable)

Rules:
- No jargon unless the audience is technical
- No hedge language ("it seems like", "possibly", "we might consider")
- State the recommendation directly; the detail document supports it
- Passive voice weakens executive summaries — use active voice

**When to use:** User explicitly asks for it, or content is a business proposal / strategy doc / incident report aimed at leadership.

---

## Action Items

**A standalone checklist** extracted from the content. Meant to be shared or tracked.

Format:
```
- [ ] [Owner] Task description — due [date] or "no deadline set"
```

Rules:
- Include only concrete, assignable actions — not aspirations or vague next steps
- If no owner is named in the source, write `[unassigned]`
- If no date is specified, write `[no deadline]` — do not invent deadlines
- Group by owner when there are more than 5 items across multiple people

**When to use:** Meeting notes, emails with asks, project plans, specs with implementation milestones.

---

## Key Insights

**An analytical bullet list** that goes beyond what the source explicitly states. Appropriate when the user wants interpretation, not just extraction.

Rules:
- Distinguish clearly between what the source says and what you're inferring
- Inferences should be well-supported, not speculative
- 3-5 insights maximum; more dilutes the value
- Each insight should be non-obvious — don't surface things the user could read in the first paragraph

**When to use:** Research papers, strategy docs, post-mortems, stories being evaluated critically.

---

## Narrative Summary

**A flowing prose paragraph (or 2-3 short paragraphs)** that reads like a human wrote it, not a structured extraction.

Rules:
- Match the tone of the original content (a lighthearted blog post warrants a lighter summary than a technical RFC)
- Use transitions between ideas — don't just concatenate facts
- Still lead with the most important point
- Avoid bullet-izing mid-paragraph; stay in prose

**When to use:** Stories, articles, social media threads, anything where the flow and narrative arc matter as much as the facts.

---

## Length Control

When the user specifies length, interpret it as:

| User says | What to produce |
|-----------|----------------|
| **Brief / short / quick** | TL;DR + 3-5 bullets max, or 2-3 sentences |
| **Standard** (default) | TL;DR + 5-7 bullets or 1-2 short paragraphs |
| **Detailed / thorough / comprehensive** | Full structure with all applicable sections; preserve nuance and sub-topics |
| **One-liner / one sentence** | Single sentence, no bullets |
| **One paragraph** | 4-6 sentence prose paragraph |

---

## Multiple Documents

When summarizing several documents together:

- **Per-document summaries first** (brief, one per doc) followed by a **cross-document synthesis** — what they agree on, where they differ, what collectively they imply
- Flag contradictions explicitly rather than smoothing them over
- Do not merge sources in ways that obscure which claim came from which document

---

## Format Anti-Patterns to Avoid

- **The double intro:** "This is a summary of X. X covers Y." — pick one, cut the other
- **The exhaustive list:** 15+ bullets that reproduce rather than distill the source
- **The opinion injection:** Evaluating the quality of the source unless asked to critique it
- **The false certainty hedge:** "This might possibly suggest that perhaps…" — if you're confident, state it; if you're not, say so once and move on
- **The document echo:** Summarizing section by section in document order rather than by importance
