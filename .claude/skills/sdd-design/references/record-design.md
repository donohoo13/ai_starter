# Record a design

Read this when the user brings back a Design artifact link for a `requested` design, or a new link for an approved one, and when a re-check needs the misses-and-gaps procedure.
It turns the link into a saved snapshot under `<folder>/design/`, where `folder` is the spec folder's absolute path that `sdd status` reports, fills `design.md`'s record, and puts each miss and gap to the user.
Every failure below writes no snapshot and leaves the design `requested`, because a half-read design recorded as the approved one is worse than none.

## Read the artifact

1. **Tool.**
   The read needs the Artifact tool, which only a claude.ai-authenticated session has.
   Without it, say this session cannot read the link, leave the design `requested` for a session that can, and stop.
2. **Read the link** with the Artifact tool's `read` action and the link as `url`.
   When the read fails (not found, no access) or the result is not a Design artifact, report the reason and stop.
   When the result is a summary instead of the page, the artifact belongs to someone else: say so, ask the user to copy the design into their own account and bring that link back, and stop.
   Note the version id the result reports.
3. **List its files** with the `list` action, `scope: "files"` and the link as `url`.
   A Design artifact holds `project/canvas.json`, one `project/*.dc.html` file per artboard, and the copied design system under `project/ds/` when the canvas used one.
   When `project/canvas.json` or every `project/*.dc.html` file is missing, list the files you found, report that the layout is not one this procedure reads, and stop.
4. **Fetch** with the `read` action, the link as `url`, and `paths` naming `project/canvas.json`, every `project/*.dc.html` file, and the `tokens.json` under `project/ds/` when there is one.
   The tool saves each file locally and says where.

## Save the snapshot

1. Delete every `*.dc.html` file already under `<folder>/design/`, and an earlier `tokens.json`, so no artboard from an earlier read survives beside the new ones.
   Leave the user's PNG files alone.
2. Copy `canvas.json`, each `*.dc.html` file and, when fetched, `tokens.json` into `<folder>/design/` under their base names, byte for byte as served.
   Images the canvas holds are not fetched; the artboards' references to them stay links to the artifact.
3. Set `design.md`'s frontmatter: `link` to the link, `read` to today's date, `version` to the version id the read reported, and `design_system` to the design system `canvas.json` names (its link when it records one) or `none`.

## Check the design system

Compare the design system the canvas used with the link under `DESIGN.md`'s `## Claude Design System` section.
When they differ, or the canvas used none while `DESIGN.md` records one, report what `canvas.json` shows and ask the user to accept it or revise the design.
Revise leaves the design `requested` until they bring the revised link back.

## List the artboards

Under `## Artboards`, one line per `*.dc.html` file in `design/`, in the template's shape: the file, the UI ID, the screen and state from its title, the requirement IDs it serves, and the PNG named after the file's stem (`Main.png` beside `Main.dc.html`) or "no PNG".
Every artboard file under `design/` appears exactly once.
List a PNG the user adds later before asking for approval.

## Misses and gaps

Build the expected set from the spec: each UI surface and each state the spec names for it, with its requirement IDs.
Then compare it with the artboards, and put every miss and gap to the user with the AskUserQuestion tool, in batches of two to four, a recommendation listed first.

- **Miss**: a listed surface or named state that no artboard shows, such as an error state the spec names and the design lacks.
  Ask the user to revise the design or accept the miss.
  An accepted miss goes under `## Accepted misses` with its UI ID, state and requirement IDs, and is built from the design system without a mockup.
  A revision leaves the design `requested` until the revised link comes back.
- **Gap**: a screen, control or state the design shows that no requirement covers, such as a bulk-delete action the spec never mentions.
  Ask the user to add it to the spec or leave it out of this build.
  An addition routes to `sdd-outline`: name it, and leave the design `requested` until the spec is re-approved.
  An exclusion goes under `## Not built` with the item and why, and nothing downstream builds it.

Copy, sample data and pixel detail are not misses or gaps; the snapshot is a reference for layout, flow and states.
Write "None" under each of `## Accepted misses`, `## Not built` and `## Skip reason` that has no entry, then return to the skill's Approve step.
