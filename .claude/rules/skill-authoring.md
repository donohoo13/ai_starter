---
paths:
  - ".claude/skills/**"
---

# Skill authoring

How every skill under `.claude/skills/` is created, edited, renamed, or deleted. A SKILL.md is a prompt that runs in many future sessions that know nothing about the conversation that shaped it, so a one-line tweak gets the same discipline as a rewrite.

Loads when a session reads a skill file, which covers every `Edit`. A `Write` creating a new skill and any Bash write or delete do not trigger the load, so `CLAUDE.md` names this file for a session to read by path first. A new skill or a structural rewrite also reads [`docs/skill-quality.md`](../../docs/skill-quality.md) in full first.

## Scope

Mine the session before interviewing: the conversation that triggered the change usually already holds the workflow, the correction, or the gap. Extract what the skill should enable, when it should trigger, and what it should produce; put only the real gaps to the user.

## Rules

- **The body runs at most 500 lines**, frontmatter excluded, measured before landing.
  Lines count only on a body written one sentence per line, per `CLAUDE.md`'s Markdown rule, since a paragraph held on one line hides its real length; a substantive edit reflows a body still in paragraph lines before measuring it, and a typo or link fix leaves the format alone.
  Under the ceiling there is no target: a body is as long as its job needs, and gating, chaining, or rationale that belongs in a reference file or nowhere is cut at any length.
- **The description is the trigger.** Third person, stating what the skill does and when to use it, with concrete contexts and trigger phrases spelled out. Phrase triggers around session state as well as user intent ("use when editing any file under X") so mid-task situations fire. Undertriggering is the default failure mode; specificity is the cure.
- **Progressive disclosure.** Metadata sits in the listing, the body loads on invocation and stays for the session, references load on demand. Push long or fragile detail into `references/` exactly one hop from SKILL.md; every bundled file states its mode, run or read.
- **Explain why over MUST.** Imperative voice with the reasoning attached; all-caps ALWAYS/NEVER is a yellow flag that the reasoning is missing. Generalize past the motivating example.
- **Self-contained.** A skill never tells the user which skill to run next; sequencing is theirs. Naming a skill it runs under the hood is fine.
- **Code work runs in agents.** A skill whose work writes or judges code dispatches it to a named agent in `.claude/agents/` and keeps its gates and every user interaction in the body, since a subagent cannot ask the user.
- **Load-time snapshots run under the session's restrictions.** A bang snapshot executes before the body loads, and a refused one aborts the whole load. Use the plainest command that yields the fact, no command substitution, and label what empty output means beside it.
- **Rewrite accreted prose; don't patch it.** When an edit inverts a rule or reframes a passage, rewrite that section as if written under the new thesis.

## Gut-check handoff

The session that wrote a skill is too warm to judge how it behaves cold. Close every create or substantive edit by handing the user test prompts for a fresh session: two or three realistic task prompts with the expected behavior stated, and, when the description changed, should-trigger and should-not-trigger prompts whose negatives are near-misses (adjacent domains, shared keywords). Typo and link fixes skip the handoff; a change to triggering or behavior never does.

## Landing

A change lands when the suite is coherent: the skill's entry in `.claude/skills/README.md` matches its behavior and triggering, the body measures under budget, and the gut-check prompts are handed over.
