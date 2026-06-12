# Content Type Reference

Per-type guidance for what to extract, what to drop, and common pitfalls.

---

## Emails and Email Threads

**Extract:**
- The decision reached (or that no decision was reached)
- Action items with owner and deadline
- Open questions or blockers that weren't resolved
- The core ask if the email is a request

**Drop:**
- Pleasantries, sign-offs, forwarded footers
- Repeated context from reply chains (summarize once, not per reply)
- CC politics (who was included is usually not summary-relevant)

**Pitfall:** Multi-reply threads often reverse-chronologically bury the decision. Read the full thread; the resolution is usually near the bottom.

**Default format:** Action items list + 1-2 sentence decision summary.

---

## Social Media Posts and Threads

**Extract:**
- The core claim, argument, or story being told
- Context needed to understand it (referenced events, people, platform conventions)
- Sentiment or tone if it's material to the content
- Thread arc — the opening hook vs. the actual conclusion

**Drop:**
- Quote-tweet nesting that just adds noise
- Engagement bait ("RT if you agree")
- Platform-specific metadata (likes, follower counts) unless directly relevant

**Pitfall:** Threads often bury the actual thesis. The first tweet is the hook; the substance is deeper. Don't summarize just the opening tweet.

**Default format:** 2-4 sentence narrative capturing the arc.

---

## Technical Documentation

**Extract:**
- What the thing is and what problem it solves
- Who the intended audience/user is
- Key concepts, terms, or mental models needed to use it
- Important caveats, version requirements, or breaking changes
- The most common usage pattern

**Drop:**
- Boilerplate installation steps (mention they exist; don't list them)
- Exhaustive API surface (mention breadth; highlight the key endpoints)
- Change history unless that's the focus

**Pitfall:** Docs often start with motivation and background. The actual "how it works" is often buried in the middle. Surface the operational model, not just the intro.

**Default format:** Short narrative + bullets for key concepts + caveats section if present.

---

## Specifications, RFCs, Design Docs

**Extract:**
- Problem statement / motivation — why this was written
- Proposed solution at the right level of abstraction
- Key constraints or non-goals (what this explicitly does not do)
- Open questions or alternatives considered and rejected
- Impact and migration requirements if present

**Drop:**
- Author headers, document history, approval blocks
- Highly detailed implementation steps (note they exist; don't reproduce)

**Pitfall:** Specs often list alternatives before the chosen approach. Make it clear in the summary which option was chosen vs. considered.

**Default format:** Problem → Solution → Constraints → Open questions (bulleted).

---

## Stories and Fiction

**Extract:**
- Plot summary: what happens, in order, at the right level of abstraction
- Character arc: how the protagonist(s) change
- Central conflict and how it's resolved (or not)
- Themes if they're prominent
- Tone and style notes if the user is evaluating the work

**Drop:**
- Dialogue verbatim (paraphrase the exchange)
- Scene-by-scene description of quiet moments that don't advance plot or character

**Pitfall:** Don't impose themes the text doesn't support. Summarize what's there; don't editorialize.

**Default format:** Brief narrative arc paragraph. If evaluating the work, add a tonal note.

---

## Meeting Notes and Transcripts

**Extract:**
- Decisions made (the most important output)
- Action items with owner and due date
- Blockers or risks raised
- Topics that were tabled or deferred
- Attendance only if relevant to authority/quorum

**Drop:**
- Small talk and off-topic tangents
- Repeated discussion before the decision
- Verbatim quotes (unless a specific quote is material)

**Pitfall:** Transcripts are long and decisions are easy to miss. Scan for signal words: "agreed", "decided", "action item", "will", "by [date]".

**Default format:** Decisions section + Action items checklist (owner, due date).

---

## Research Papers and Articles

**Extract:**
- Research question or thesis
- Methodology (brief — enough to evaluate the finding)
- Key findings
- Conclusions and their confidence level
- Limitations or caveats the authors raise
- Implications or what this changes

**Drop:**
- Literature review in full (note what it builds on; don't reproduce it)
- Statistical tables in full (cite findings; note how they were measured)

**Pitfall:** Abstract and conclusion are not always consistent. Read both; the conclusion often has nuance the abstract smooths over.

**Default format:** Thesis → Methodology (1 sentence) → Findings (bullets) → Limitations.

---

## Legal and Contract Text

**Extract:**
- Core obligations for each party
- Rights granted and conditions
- Key dates, milestones, and termination provisions
- Liability limits, indemnification, and risk areas
- Definitions that change the ordinary meaning of words

**Drop:**
- Boilerplate recitals ("WHEREAS…")
- Standard governing law / jurisdiction clauses unless unusual

**Pitfall:** Legal language uses "shall", "may", and "will" with precise meanings — preserve the modal verbs when summarizing obligations. "The licensor may terminate" is different from "the licensor shall terminate."

**Note:** This skill provides summaries for understanding, not legal advice. Flag when a clause is unusual or high-risk rather than interpreting legal consequences.

**Default format:** Obligations per party (bulleted) + key dates + risk flags.

---

## Changelogs and Release Notes

**Extract:**
- Breaking changes (always surface these first)
- New features — what they do and who they benefit
- Bug fixes for issues that are widely known or high-impact
- Deprecations and their timelines
- Migration steps if required

**Drop:**
- Internal refactors with no user-facing impact
- Dependency bumps without functional changes
- Very minor/cosmetic fixes

**Pitfall:** Changelog entries are written for developers who already know the product. For non-technical audiences, translate "fixed null reference in AuthMiddleware" into what it means to users.

**Default format:** Breaking changes first (flagged), then new features, then notable fixes.

---

## Chat Logs and Slack Threads

**Extract:**
- The question or topic that started the thread
- The answer or conclusion reached
- Action items or follow-ups
- Unresolved sub-threads (flag rather than resolve)

**Drop:**
- Reaction emojis and acknowledgment messages ("👍", "thanks!")
- Off-topic side conversations
- Message-by-message narration

**Pitfall:** Threads often fork. Identify the main thread vs. side conversations before summarizing.

**Default format:** 2-3 sentence outcome + action items if present.

---

## Code and Pull Requests

**Extract:**
- What the change does (functional description)
- Why it was made (motivation / linked issue)
- What the key implementation choices were
- Any review concerns, open questions, or flagged risks
- Breaking changes or migration notes

**Drop:**
- Line-by-line description of trivial changes
- Auto-generated content (changelogs, lockfiles)

**Default format:** 1 sentence what + 1 sentence why + bullets for notable choices or concerns.

---

## News Articles and Blog Posts

**Extract:**
- What happened / what's being claimed
- Who is involved
- Why it matters (stated or implied)
- Key evidence or supporting points
- Source credibility signals if visible (named experts, primary sources)

**Drop:**
- Filler context paragraphs that don't add facts
- Author bio and related-article links

**Default format:** 3-5 sentence narrative (who, what, why it matters).
