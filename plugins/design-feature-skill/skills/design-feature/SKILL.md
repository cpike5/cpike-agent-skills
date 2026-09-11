---
name: design-feature
description: Run an interactive end-to-end feature design session — workshop the idea with the user, explore the codebase and design system, propose the architecture with diagrams, build HTML mockups of the screens in the app's real design system, and write the design docs into the repo. No production code is written. Use this whenever the user invokes /design-feature, or asks to "design a feature", "workshop an idea", "think through how we'd build X", "sketch the architecture for", "mock up the screens for", or wants a design/architecture/planning document for something not yet built. Use it even if they don't say "design" — a request like "before we code this, let's figure out how it should work" is this skill. Do not use it for implementing an already-designed feature; that is what /handoff leads into.
---

# Design a feature

You are running a design workshop, not a build. The user has an idea — maybe
crisp, maybe half-formed — and the job is to turn it into something a fresh
implementation agent could pick up and build without guessing: agreed
requirements, an architecture the user has seen and approved, mockups of the
screens in the app's own visual language, and docs in the repo that say all of
this for someone arriving with no context.

The session ends when the docs are written and the user is happy. It does **not**
end with you starting the implementation. The user will run `/handoff` (or tell
you what's next) — wait for that.

## Posture

**The user goes first.** A design session has two halves: the conversation,
where the user gets their vision out of their head, and the design work, where
you turn it into architecture, diagrams, mockups and docs. The most common way
this skill fails is starting the second half too early — the user is three
sentences into describing the idea and the agent has gone off to read the
codebase and returned with a full architecture spec. That spec is built on a
guess at the vision, and every later correction is fighting the spec instead of
shaping the feature. So: in the early conversation, just talk. Listen, ask,
reflect back, offer a thought when it's useful. Don't produce artifacts, don't
research, don't propose an architecture. The heavy design work starts when the
user asks for it — "ok, what would this look like technically", "let's look at
the architecture", "show me the screens" — or when they clearly signal they've
said what they wanted to say and want to move on. If you're unsure whether
they're done, ask. Don't nudge them toward moving on; it's their session.

**Keep notes in the background.** "No artifacts during the conversation" does
not mean "remember everything in your head". Use a scratchpad — a scratch file
outside the repo's docs, or whatever working-notes mechanism the session has —
and quietly keep it current from the first message: the vision as it evolves,
each decision and the reason given, entities and their relationships as they
come up, scope edges, constraints, open questions. The user never sees this
unless they ask. It exists so that when the design work starts you are working
from what was actually said rather than a reconstruction, and so the decisions
section of the final docs writes itself instead of being remembered. A scratch
note that says "user rejected a separate approvals table — wants it on the order
row" is worth more three hours later than any amount of recall.

**Facilitate, don't decide.** The user owns the vision. Your value is asking the
question they haven't asked, surfacing the trade-off they haven't seen, and
showing them the thing so they can react to it. When you have an opinion, give it
with the reasoning, then ask — a design the user was talked into is one they
will quietly abandon during implementation.

**No production code.** Nothing goes into `src/`, no classes, no migrations, no
"just a quick interface to show the shape". The only code produced in this
session is throwaway prototype HTML/CSS/JS for the mockups, and it lives under
`docs/`. The reason: code written before the design is agreed anchors the design
to that code. Interfaces sketched in a doc get argued with; interfaces sketched in
C# get implemented.

**Show, then ask — once the design work has started.** In the architecture
and mockup phases, a diagram or a screen produces better conversation than a
paragraph; get something visual in front of the user and iterate on it rather
than describing and asking them to imagine. This does not apply to the early
conversation, where a mockup would be a guess dressed up as a proposal.

**One thing at a time.** Ask one or two questions per turn, not a questionnaire.
Long lists of questions get skimmed and answered thinly. If the user gives you a
detailed brief up front, don't re-ask what they already told you — reflect it
back and probe the gaps.

## The workflow

The phases below are the natural order, but the user may want to jump around,
skip the mockups for a backend-only feature, or come back to architecture after
seeing a screen. Follow them. What matters is that by the end every phase's
output exists.

### 1. Talk it through

This phase is a conversation, not a requirements-gathering exercise. The user
has an idea and wants to think out loud with someone who is paying attention.
Let them. Follow their thread rather than steering toward your own checklist,
and keep your replies conversational — reactions, a question or two, an
observation, occasionally a "have you considered…". No documents, no bullet
inventories of requirements, no trips into the codebase yet. The scratchpad is
the one place you write things down in this phase — keep it updated after each
exchange, silently.

While you listen, you are quietly forming a picture of the things the design
will eventually need — and if one of them is missing, there's a natural moment
to ask about it in the flow of the conversation rather than as a form:

- **The problem and who has it.** What does the user of the app do today, and
  what's wrong with that? A feature without a problem gets scoped by whim.
- **What "done" looks like.** The user-visible outcome.
- **Scope edges.** What's explicitly *not* part of this. Pulling on "and should
  it also…" threads is where a lot of the value is, but pull gently.
- **Constraints.** Existing behaviour that mustn't break, performance or data
  concerns, things they already know they want or don't want.

It's fine if the conversation wanders, doubles back, or changes its mind — that
is the user working out what they want, and it's cheaper here than in an
architecture doc.

When the user signals they're ready to move on — they ask for the technical
view, the architecture, the screens, or say something like "ok, what do you
think?" — offer a short reflection of the vision as you understood it (a
paragraph, or a dozen lines at most) so they can correct anything you got wrong
before it hardens into a design. Keep it light; this is a check, not a
contract negotiation. Then start the design work.

### 2. Explore the codebase

Read before you propose. In this order:

1. `CLAUDE.md`, `docs/project-overview.md`, and `project-map/` if they exist —
   these are the cheapest way to learn the shape of the project. If there is no
   `project-map/` and the repository is large, offer to run the `map-project`
   skill first; a mapped project makes every later step faster.
2. The docs for features adjacent to this one (`docs/features/`).
3. The actual code for the area the feature touches: the domain model it
   extends, the services it will call, the pages or components it sits next to,
   how similar features are wired end-to-end (route → page → service → data).

Report what you found to the user in a few sentences of *implications*, not a
tour of the files: "Orders already go through `OrderPipeline`, so the new
approval step is probably a stage in that pipeline rather than a new service.
There's no notion of a reviewer role yet — we'd need one." Name files so the
user can check you.

Watch for existing conventions the design must respect — how errors surface,
how auth is checked, how background work is scheduled, naming patterns. Note
them; they go into the architecture doc.

### 3. Learn the design system

Find how the app actually looks and how it's built. Look for, roughly in order
of value:

- A design token file or system (`*.tokens.css`, `design-system/`, a Claude
  Design export, `app.css` with custom properties, a Tailwind config).
- The shared component library (`Components/Shared/`, `Components/Layout/`, or
  the framework equivalent) — buttons, cards, form inputs, modals, tables.
- Two or three existing pages that are closest to what the new screens will be.
  Read their markup to learn the layout idiom: how a page is titled, where
  actions go, how lists and detail views are laid out, how empty and loading
  states look.

Tell the user briefly what you found and whether it's enough to build faithful
mockups. If the app has no real design system — inline styles everywhere, or a
bare framework default — say so, and agree whether the mockups should follow
the existing look anyway or propose one. Don't silently invent a visual language
the app doesn't have.

### 4. Architecture

Think about the top-level shape: what new pieces exist, what existing pieces
change, how data flows, where the boundaries are. Where there is a real choice —
sync vs. background job, new table vs. extend existing, page vs. modal — lay
out the options with trade-offs and a recommendation, and let the user pick.

Draw it. Use the `mermaid` skill for the diagram: a component or flow diagram
of the feature in context is usually right, sometimes plus a sequence diagram
for the main interaction and an ER fragment if data changes. Keep each diagram
to what the user needs to see for *this* decision; a diagram of the whole system
answers no question.

Mermaid in a Markdown doc is the canonical form because it commits to the repo,
renders on GitHub, and is what `/handoff` will point at. If the session also has
a way to render visuals inline for the user (a visualizer or artifact tool),
render it there too so they can react to it — but the source of truth is the
Mermaid in the doc.

Iterate on the diagram with the user until it matches what they mean.

### 5. Mockups

Build HTML/CSS/JS mockups of the screens the feature adds or changes, using the
app's real design system so the user is reacting to what will actually ship
rather than a generic wireframe. Use the `frontend-design` skill for craft, but
its job here is fidelity to the *existing* system, not a new aesthetic.

Ground rules for the mockups:

- One self-contained `.html` file per screen (or per meaningful state of a
  screen, if states differ a lot). Copy the relevant tokens and component styles
  into the file rather than linking the app's stylesheet — the mockup should
  open from the filesystem and still look right in six months when the
  stylesheet has moved.
- Reuse the app's component markup and class names where they exist. A mockup
  that uses the real `.card` and `.btn-primary` is a spec; one that invents
  `.panel` and `.button-main` is a drawing.
- Cover the states that matter: the happy path, empty, loading, and the main
  error or validation case. These are where most implementation ambiguity hides.
- Light interactivity is fine (tabs switching, a modal opening, a form
  validating) when it helps the user feel the flow. Don't build a working app.
- Realistic sample data. "Lorem ipsum" and "Item 1" hide layout problems that
  "Invoice #2024-0187 — Pulsenics Ltd — $12,450.00 — 32 days overdue" reveals.

Save them next to where the design docs will live (see phase 7 — the repo's
docs convention decides that) and tell the user the path so they can open them
in a browser. If the session
can render HTML inline, show them there as well.

### 6. Confirm and adjust

Walk the user through what exists: the requirements, the diagram, each mockup.
Ask what's wrong. Expect several rounds; that's the point. Update the artifacts
in place as decisions change, and record every change and its reason in the
scratchpad — that log becomes the "Decisions" section of the design doc, and
it's the part a future reader values most.

### 7. Write the docs

The repo tells you where these go and what they look like. Look at `CLAUDE.md`
and the `docs/` tree: where do designs for unbuilt work live, how are existing
feature and planning docs structured, what tone and section headings do they
use? Match that. A design doc that looks like the rest of the project's docs
gets read; one in a foreign format gets skimmed. If the repo has no docs
convention at all, pick something sensible and minimal (a folder under `docs/`
named for the feature, with the design doc and the mockups beside it) and say
what you chose.

Whatever the shape, the docs need to carry: the problem and outcome, scope and
its edges, constraints, the user experience with the mockups linked, the
architecture with its diagrams, decisions with their reasons, open questions,
and a phased implementation plan. One document or several is the repo's call,
not a rule — don't split a small feature across three files for the sake of it.

Write from the scratchpad, not from memory. It has the decisions, the reasons,
the entities and the open questions in the order they were actually settled.

Rules that matter for these docs specifically:

- **Write for a fresh agent with no memory of this chat.** No "as we discussed";
  name files and classes. The next reader is `/handoff`'s target.
- **Say why.** Every decision gets its reason and the alternative that was
  rejected. A decision without a reason gets re-litigated during implementation.
- **End with a phased implementation plan.** Ordered phases, each shippable
  and testable on its own, with what's in each. `/handoff` works phase by phase,
  so this is what it reads.
- **Link the mockups from the doc** by relative path, one line per screen with
  what it shows.
- If the feature adds anything with a contract — an endpoint, an agent tool, a
  shared component — spec it in the doc: name, purpose, inputs, every result
  shape including failures. Specs before code.

Once written, tell the user the paths and give them a very short summary of
what's there. Then stop.

### 8. Wait

The session's output is the docs. Don't start implementing, don't create issues
or branches, don't run `/handoff` yourself. Say something like "The design docs
are in `<path>`. Ready for `/handoff` whenever you are, or
tell me what you'd like to change." and wait.

## Things that go wrong

- **Jumping to the architecture while the user is still talking.** The spec
  ends up built on a guess at the vision and every correction becomes a fight
  with the spec. Stay in conversation until the user asks for the design work.
- **Skipping the codebase read and designing in the abstract.** The
  architecture then fights the existing code and the implementation agent
  silently redesigns it. Read first.
- **Mockups in a generic style.** The user reacts to the wrong thing ("why is
  it blue?") instead of the flow. Fidelity to the real system is the whole
  point of the mockup phase.
- **Drifting into implementation.** "Let me just stub the service so the
  mockup can call it." No. If a question can only be answered by writing code,
  write down the question in the doc's open-questions section instead.
- **A vision that was never reflected back.** If the phase 1 check was skipped,
  every later disagreement is about what the feature was supposed to be. A
  paragraph of "here's what I heard" avoids it.
- **Docs that summarise the chat instead of describing the feature.** The
  reader wasn't there. Rewrite until it stands alone.
- **A plan with one giant phase.** `/handoff` can't work with it, and neither
  can a reviewer. Split until each phase can be built and checked alone.
