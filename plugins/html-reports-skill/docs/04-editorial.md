# Making an HTML report look designed

Components and a matching palette get a report to *competent*. What separates a report someone
forwards from one they skim is editorial: what the headline says, how dense the page is, and how
few decisions the eye has to make. This file is that layer. Read it once before writing the body
fragment.

None of it needs new CSS. Everything here is `base.css` plus judgement.

This file covers how the page is arranged. `${CLAUDE_PLUGIN_ROOT}/docs/05-plain-language.md` covers
how the sentences are written — simplified English, which is the default for every report. Read
both. Short, active sentences make the devices below work better, not worse.

## The look: rules, not boxes

`base.css` draws a report the way a good print page is set. Hierarchy comes from type — a large
display headline, display-size numerals in the KPI row, uppercase tracked labels — and from
hairline rules: one heavy rule under the masthead and over each table, hairlines between rows.
Almost nothing is enclosed in a box, and nothing casts a shadow except the tooltip, which floats.

Keep it that way when writing the body:

- **Do not wrap things to make them look important.** A `.kpis` row, a table, a `.seq` and a
  `.checklist` are already designed to sit on the page unboxed. Putting them inside a `.card`
  adds a border around a component that already has its own rules and reads as clutter.
- **`.card` is for grouping**, not decoration: "the short version" summary, a set of figures that
  must be read as one unit. One or two per report is typical.
- **Never add inline `style` for borders, shadows, radii or colours.** The tokens carry the look
  in both schemes and in print; an inline `box-shadow` or `border-radius: 12px` is the fastest
  way back to a dashboard. The only inline style the components expect is `--hue` on a `.sc`.
- **Colour is spent, not sprinkled.** Waterfall totals are ink; only the movements take colour.
  Gantt bars and legends use the series in order. Everything else is ink, two greys and a rule.

## The headline names the document

The masthead `h1` is a title, not a line of commentary. Write what the report is about, the way
you would name a file someone has to find again in a year.

```html
<h1>Room build-out survey</h1>
<h1>Q3 ingest pipeline audit</h1>
<h1>Cold-chain scheduling estimate — Bergen site</h1>
```

Name the subject, and add the scope that makes it unambiguous: which system, which period, which
site. That is the whole job. A title that could sit in a table of contents next to twenty others
and still be picked out is a good title.

Do not write a headline that argues, warns, or turns. These read as marketing, not as a report:

> ✗ Two chips, one afternoon.
> ✗ The house has ten rooms. *Four of them are hollow.*
> ✗ Ten rooms, four of them hollow

The findings go in the body, where they are next to their evidence. A reader who meets the
conclusion before the scope has no way to judge it.

The same rule governs `h2` section headings and `.eyebrow` labels: *Findings*, *Scope*, *Cost*,
*Part two*. Name the section's contents. Do not preview its verdict.

`base.css` italicises `h1 em` in the accent colour. Use it only for a genuine subtitle that is
part of the name — `<h1>Ingest pipeline audit <em>— second pass</em></h1>` — and leave it out
otherwise. Most reports never need it.

## The standfirst says what was examined

`.sub` gets two sentences: what was examined, on what axes, and what the reader gets. Plain
statements, no rhetorical turn.

> ✓ This review covers the 14 ingest jobs that run on the nightly schedule. It scores each on
> runtime, failure rate and recovery cost, and recommends which three to rewrite first.

> ✗ Miss the 24-hour window and you start again.

A consequence line belongs in the body of the finding that establishes it, not in the masthead.

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

- Read the `h1` alone. Does it name what the report is about, without arguing anything?
- Read only the bold text and the headings top to bottom. Do the findings survive?
- Run the simplified-English check in `${CLAUDE_PLUGIN_ROOT}/docs/05-plain-language.md`.
- Is there a screenful anywhere with no number, no component and no claim? Cut it.
- Does every visual prove something the caption states? A chart nobody would act on is decoration.
- Would the reader know, at any point, what they are being asked to decide?
