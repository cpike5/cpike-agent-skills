---
name: summarizer
description: "Summarize, digest, or condense any content — documents, emails, social media threads, technical specs, API docs, stories, meeting notes, research papers, legal text, changelogs, chat logs, or pasted text of any kind. Use this skill when the user asks to summarize, recap, get a TL;DR, extract key points, distill a document, write an executive summary, or condense long content. Also invoke when the user provides a block of text and wants it understood quickly, asks what something is about, or wants action items extracted from content. Covers adaptive output formats (TL;DR, bullet points, executive summary, narrative paragraph, key insights, action items), content-type detection, audience calibration, and length control (brief/standard/detailed)."
---

# Summarizer Skill

Distill content into clear, accurate, audience-appropriate summaries. Adapt to the content type and the user's request (format, length, audience, focus) — don't apply a one-size-fits-all template. For long source material, consider delegating the reading to the **summarizer** agent so the full text stays out of the main conversation.

What counts as "key information" differs by content type:

| Type | What matters most |
|------|------------------|
| **Email / email thread** | Decision reached, action items, who owns what, deadline |
| **Social media post / thread** | Core claim or narrative arc, context, sentiment |
| **Technical documentation** | Purpose, audience, key concepts, usage, caveats |
| **Specification / RFC / design doc** | Problem statement, proposed solution, constraints, open questions |
| **Story / fiction** | Plot arc, character development, themes, tone |
| **Meeting notes / transcript** | Decisions, action items, owners, blockers |
| **Research paper / article** | Thesis, methodology, findings, conclusions, limitations |
| **Legal / contract text** | Obligations, rights, key dates, risk areas — note unusual or high-risk clauses; don't give legal interpretations |
| **Changelog / release notes** | What changed, breaking changes, migration requirements |
| **Chat log / Slack thread** | Outcome, unresolved threads, action items |
| **Code / PR description** | What it does, why, what changed, review concerns |
| **News / blog post** | Who, what, when, why it matters |

Style: lead with the substance (no "This document discusses…" filler), preserve important caveats and qualifications, keep technical precision for technical audiences, match the source's tonal register, and give action items their own section with owners/deadlines when present. Default lead is a one-sentence TL;DR unless the user asked for a different format.

## Reference Documentation

- ${CLAUDE_PLUGIN_ROOT}/docs/01-content-types.md — Per-type guidance: what to extract, what to omit, common pitfalls.
- ${CLAUDE_PLUGIN_ROOT}/docs/02-output-formats.md — Format templates (TL;DR, bullets, executive summary, narrative, key insights, action items) and length control.
