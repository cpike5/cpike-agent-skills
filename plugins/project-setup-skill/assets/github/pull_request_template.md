<!--
PR template. GitHub pre-fills this on new PRs opened in the web UI; when a PR is
opened by tooling (an agent, a script, the API), mirror these sections in the body.

Keep the headings. Drop a section only when it genuinely has nothing to say — and
if you drop "Deliberately Not Done", that itself is a claim that nothing was left
out. Prose for the why, bullets for the what.
-->

## Summary

<!--
One or two paragraphs: what this PR does and why it exists — the user-visible
behaviour or the problem being fixed, not a restatement of the diff. If it
implements a plan, review, or issue, link it here. A small single-root-cause fix
may use this section alone.
-->

## Key Changes

<!--
Bulleted, grouped by area. Lead each bullet with the area in bold and name the
file(s) so a reviewer can jump straight there:
- **API** (`FooController.cs`): …
- **UI** (`FooPanel.razor`): …
- **Migration**: `AddFooBar` — what the schema change is
- **Docs**: which pages were added or updated
-->

## Implementation Details

<!--
The decisions a reviewer would otherwise reverse-engineer from the diff: why this
approach over the obvious one, backward-compatibility notes, edge cases handled,
framework quirks worked around. Prose or short bold-led bullets.
-->

## Deliberately Not Done

<!--
Scope you saw and chose to leave out, with the reason and where it is recorded as
a follow-up (an issue, a "follow-ups" section in a doc). Omit if there is nothing.
-->

## Verification

<!--
What was actually run, not what should be. Commands, test counts, new test files.
For UI work: that it was driven in the running app at desktop and mobile
breakpoints. State plainly if something could not be verified — an unverified
claim here costs more than an honest gap.
-->
