---
name: summarizer
description: "Summarize, digest, or condense any content — documents, emails, social media threads, technical specs, API docs, stories, meeting notes, research papers, legal text, changelogs, chat logs, or pasted text of any kind. Use this skill when the user asks to summarize, recap, get a TL;DR, extract key points, distill a document, write an executive summary, or condense long content. Also invoke when the user provides a block of text and wants it understood quickly, asks what something is about, or wants action items extracted from content. Covers adaptive output formats (TL;DR, bullet points, executive summary, narrative paragraph, key insights, action items), content-type detection, audience calibration, and length control (brief/standard/detailed)."
---

# Summarizer Skill

Distill any content into clear, accurate, audience-appropriate summaries. The user provides content — pasted inline, as a file path, or described — and may specify an output format, length, and target audience. Adapt the output to the content type and the user's intent; don't apply a one-size-fits-all template.

---

## Step 1 — Identify Content Type

Read the content and classify it before writing anything. The summary structure, tone, and what counts as "key information" differ by type:

| Type | What matters most |
|------|------------------|
| **Email / email thread** | Decision reached, action items, who owns what, deadline |
| **Social media post / thread** | Core claim or narrative arc, context, sentiment |
| **Technical documentation** | Purpose, audience, key concepts, usage, caveats |
| **Specification / RFC / design doc** | Problem statement, proposed solution, constraints, open questions |
| **Story / fiction** | Plot arc, character development, themes, tone |
| **Meeting notes / transcript** | Decisions, action items, owners, blockers |
| **Research paper / article** | Thesis, methodology, findings, conclusions, limitations |
| **Legal / contract text** | Obligations, rights, key dates, risk areas |
| **Changelog / release notes** | What changed, breaking changes, migration requirements |
| **Chat log / Slack thread** | Outcome, unresolved threads, action items |
| **Code / PR description** | What it does, why, what changed, review concerns |
| **News / blog post** | Who, what, when, why it matters |

For mixed or ambiguous content, note the dominant type and adapt accordingly.

---

## Step 2 — Calibrate to the User's Request

Check for explicit signals about:

- **Format**: TL;DR, bullets, executive summary, narrative, action items, key insights — see `${CLAUDE_PLUGIN_ROOT}/docs/02-output-formats.md`
- **Length**: brief (1-3 sentences or 3-5 bullets), standard (default), detailed (preserve nuance, sub-sections)
- **Audience**: technical, executive, general — strip jargon for non-technical audiences; preserve it for technical ones
- **Focus**: "just the action items", "only the decisions", "explain it like I haven't read the spec"

If no format is specified, choose the most useful default for the content type (see format guidance in `${CLAUDE_PLUGIN_ROOT}/docs/02-output-formats.md`).

---

## Step 3 — Write the Summary

Rules that always hold:

- **Accuracy over brevity.** A shorter summary that omits the main point is worse than a slightly longer one. Never introduce information not in the source.
- **No filler phrases.** Avoid "This document discusses…", "The author explains that…", "In summary…" — lead with the substance.
- **Preserve important caveats and qualifications.** A spec that says "this approach is experimental" should carry that signal in the summary.
- **Action items belong in their own section** when present. Format them as a checklist or list with owners/deadlines when available.
- **Preserve technical precision for technical audiences.** Don't simplify "eventual consistency" to "it might be slow" for an engineer audience.
- **Match the tonal register.** A summary of a lighthearted social post should not read like a legal brief.

---

## Output Structure

For standard summaries use this structure (omit sections that don't apply):

**[TL;DR — one sentence]** (always include unless user asked for a different lead format)

**Key points** (bullets, 3-7 items; omit for very short content)

**Action items / decisions** (if present in source)

**Context / background** (if the user needs it to understand the key points)

For specialized formats (executive summary, narrative, etc.) defer to `${CLAUDE_PLUGIN_ROOT}/docs/02-output-formats.md`.

---

## Content-Type Detail

See `${CLAUDE_PLUGIN_ROOT}/docs/01-content-types.md` for per-type guidance on what to extract, what to omit, and common pitfalls for each content category.
