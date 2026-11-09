# Design prompt template

Read this when `sdd-design` writes or revises a design prompt.
Fill the template at the end from the approved spec and `DESIGN.md` by the rules below, write the result under `design.md`'s `## Prompt`, and show the same text in the conversation as one fenced block.

## Filling rules

### It stands alone

The prompt runs after `/design` in a Claude Code session or pasted into a Claude chat, where nothing from this repository is visible.

- Leave out every repository path, file name, shell command, skill or helper name, and any reference to a document, file or conversation outside the prompt.
  The design system's link is the one exception.
- Keep requirement IDs (`FR-002`) and UI IDs (`UI-001`): they tie each artboard back to the spec when the design is recorded.
- Replace every `<...>` in the template; none survives into the prompt.

### What it carries

- **Goal and audience**: from the spec's Summary, Goals and Problem and context, in product words a designer would use.
- **Screens and states**: one entry per line of the spec's UI surfaces section, with its UI ID, its name, and whether it is new or edited.
  Under each, list every state the spec names for that surface, reading the requirements, the user scenarios and the Edge cases and failure behavior section, so the empty, loading and error states land beside the default one.
  Give each state the requirement IDs it serves.
- **Devices and widths**: the ones the spec requires.
  When the spec fixes none, ask for each screen at a phone width and a desktop width, the two widths a render check covers.
- **Do not design**: each spec non-goal restated in product terms, with no path, command or tool name.
  A non-goal with nothing a designer could draw, such as a release or tooling decision, is left out rather than translated into jargon.
- **Design system**: exactly one of three cases, decided by `DESIGN.md`.
  1. `DESIGN.md` records a Claude design system link under `## Claude Design System`: name that design system by its link and restate none of its color, typography, spacing or radius tokens, since the design copies them from the system and a restated value can only drift from it.
     When the Artifact tool is available, read the link first; when it no longer reads, warn the user and fall through to case 2.
  2. `DESIGN.md` is filled but records no link: carry its Overview, Key Characteristics and Do's and Don'ts text, so the design follows the project's own character.
  3. `DESIGN.md` is absent or still holds bracket placeholders: state that the project has no design decisions yet, so the design conversation proposes them instead of inventing a brand silently.
- **Accessibility and usability**: always the WCAG 2.2 AA floors in the template, plus the target size, reading width and motion timing `DESIGN.md` sets.
  Where `DESIGN.md` is absent, unfilled or silent on one of them, use the starting value `docs/standards/ux-standards.md` labels for it, read at run time rather than remembered.
  A `DESIGN.md` value below its floor is replaced by the floor, and the user is told which line fell short.
- **Copy**: customer-facing copy uses no em-dash, which the project bans in customer-facing text.
- **Process**: two or three directions on one named primary screen first, then the complete design in the direction the user picks, one artboard per screen and state.
  The primary screen is the surface the spec's first user scenario centers on, or else the first new surface listed.
- **Closing line**: ask the user to bring the approved design's link back.

### What it never carries

- Secrets, credentials, keys, customer PII, or restricted material such as vulnerability reports, because the prompt leaves the machine.
  When the spec's examples hold real names, emails or account data, write invented sample data instead.
- The em-dash character (U+2014), anywhere in the prompt.
  Search the finished text for it before writing it out.

## Template

```text
Design <the feature in plain product words> for <the audience>.

Goal
<One to three sentences on what the user is trying to do and why this change exists.>

Screens and states
<For each UI surface:>
<UI-001> <Screen name> (<new or edited>)
- <State>: <what the user sees and can do>. Serves <FR-001, FR-002>.
- <Empty, loading or error state>: <what the user sees and can do>. Serves <FR-003>.

Devices and widths
<The devices or widths the spec requires, or: Show each screen at a phone width and a desktop width.>

Do not design
- <A non-goal, in product terms.>

Design system
<Exactly one of the three lines below, by case.>
Use the design system at <link>. Take every color, type, spacing and radius value from it.
This product has no shared design system yet. Follow its design direction: <Overview, Key Characteristics, and Do's and Don'ts text>
This product has no design decisions yet. Propose a palette, type, spacing and voice that fit the goal and audience, and keep them consistent across every screen.

Accessibility and usability
- Text contrast at least 4.5:1, or 3:1 for large text (WCAG 2.2 AA, 1.4.3).
- Controls, icons, focus indicators and meaningful graphics at least 3:1 against their surroundings (1.4.11).
- Every interactive target at least <target size>, and never smaller than 24 by 24 CSS pixels (2.5.8).
- A visible focus indicator on every interactive element, never hidden behind sticky content (2.4.7, 2.4.11).
- Every action reachable by keyboard (2.1.1).
- Body text no wider than <reading width>.
- Motion within <motion timing>.
- Copy uses no em-dash: use a comma, a period or a rewrite instead.

How to work
1. First show two or three distinct directions for <primary screen>, in its default state only, and wait for me to pick one.
2. Then design every screen and state above in the chosen direction: one artboard per screen and state, each titled with its UI ID, screen and state, like "<UI-001> <Settings> / <empty>".
3. Use invented sample data.

When I approve the design, I will copy its link and bring it back to the project that asked for it.
```
