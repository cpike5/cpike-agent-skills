# Making an HTML report look designed

Components and a matching palette get a report to *competent*. What separates a report someone
forwards from one they skim is editorial: what the headline says, how dense the page is, and how
few decisions the eye has to make. This file is that layer. Read it once before writing the body
fragment.

None of it needs new CSS. Everything here is `base.css` plus judgement.

## The headline is a finding, not a subject

The masthead `h1` is the most-read line in the document. Spend it on the conclusion.

```html
<h1>The house has ten rooms.<br><em>Four of them are hollow.</em></h1>
```

The device: a flat statement, then the sharp half in `em`, which `base.css` sets in italic in the
accent colour. Two lines, one turn. "Room build-out survey" is a filename, not a headline.

Then `.sub` — the standfirst — says in two sentences what was examined, on what axes, and what
the reader gets. It is the only place in the document that is allowed to be a summary of the
document.

## Say what the document is not, twice

Once in the masthead (a `.banner`, or in `.meta`), once in the footer. "Pre-quote review — not a
quotation." "Planning estimates, not a quotation." "Read-only; no code was changed." This is the
cheapest credibility in the format and the most commonly skipped.

The footer's other job is provenance: which branch, which commit, which files the claims were
read from, and which parts are judgement rather than measurement. Name them.

## Structure the reader can hold

Give a long report **three or four parts**, each opening with an `.eyebrow` — `Part one`,
`Part two` — above the `h2`. The eyebrow costs one line and turns a scroll into a document.

The shape that works for almost any review:

1. **The survey.** What is there, scored — a `.scorecard` or a table.
2. **The recommendations.** `.ranked` items in `.tier`s, ordered by leverage.
3. **The running order.** A `.seq`, sequenced so each step makes the next cheaper.

Each part's `.lede` states its own basis of judgement — "ranked by what each unlocks per unit of
work, not by size". A reader who disagrees with the ranking then knows exactly what they are
disagreeing with.

## Density is a feature

The failure mode of a themed report is air: big cards, three words each, a page and a half of
scrolling per idea. Aim for the density of a good print page — a `.scorecard` of ten entities in
one screenful, a `.kpis` row of four figures, items whose body is two tight paragraphs.

Practically:

- **Every card earns its border.** If a card holds one sentence, it is a sentence.
- **Prose stays inside `--measure`.** Body copy is capped at that line length by the components;
  do not widen it. Full-bleed rows are for grids and charts, not text.
- **A second paragraph in an item takes `.small`** — the finding reads dark, the mechanics read
  quiet. Two weights of text per item, no more.
- **`code` the identifiers.** File paths, class names, tokens, IDs. Nothing signals "this was
  read, not guessed" faster than a correct `Room.razor:186`.

## Accent with intent

The palette gives six series colours. Use them to encode something the reader can decode — one
hue per domain, per owner, per status — and say what the encoding is in a `.legend`. A grid where
every card is a different colour for decoration is noise that looks like meaning.

Semantic colour stays semantic: `.pill warn` / `.note risk` for bad news, `good` for landed work.
Do not spend `--warn` on an accent.

## Numbers

Four to six figures in the `.kpis` row, each one appearing again in the body with its derivation.
Write ranges rather than false precision — "90–130 h, central ~110". A `0` is often the strongest
figure on the page ("0 ways for the assistant to reach the user first"); do not soften it into a
sentence.

## Match the product, including its restraint

If the application is dark-only, the report is dark-only — `--mode dark`, no theme toggle (see
`${CLAUDE_PLUGIN_ROOT}/docs/02-theming.md`). If the application's headings are serif, set
`--font-display` to the serif preset. The report should look like it was made by the same people
who made the thing it describes, and that includes not having features the product does not.

## Before delivering

Beyond the mechanical checks in `${CLAUDE_PLUGIN_ROOT}/docs/01-html-workflow.md`:

- Read only the bold text and the headings top to bottom. Do the findings survive?
- Is there a screenful anywhere with no number, no component and no claim? Cut it.
- Does every visual prove something the caption states? A chart nobody would act on is decoration.
- Would the reader know, at any point, what they are being asked to decide?
