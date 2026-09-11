---
name: skill-creator
description: Author, edit, and review Claude Code skills with the discipline that makes them reliable, lean imperative SKILL.md bodies under a hard character budget, trigger-accurate third-person descriptions, progressive disclosure into references, and a gut-check handoff of test prompts the user runs in a fresh session. Use before creating, editing, renaming, or deleting anything under `.claude/skills/`, including one-line SKILL.md tweaks landed mid-task, and when a skill misfires, undertriggers, or needs its description sharpened.
---

# Skill Creator

The authoring discipline for skills. Load it before touching any file under `.claude/skills/`, whatever brought the change; the `guard-skill-edit` PreToolUse hook denies `Edit` and `Write` there until it is loaded (a Bash write is outside its matcher). A SKILL.md is a prompt that runs in many future sessions that know nothing about the conversation that shaped it, which is why a one-line tweak gets the same discipline as a rewrite.

## Scope first

Mine the session before interviewing: the conversation that triggered the change usually already holds the workflow, the correction, or the gap. Extract what the skill should enable, when it should trigger, and what it should produce; put only the real gaps to the user. A new skill or a structural rewrite means reading `references/skill-quality.md` in full first, as reference.

## Authoring rules

- **The budget is 5000 characters of body**, frontmatter excluded, measured before landing. A skill over budget is carrying gating, chaining, or rationale that belongs in a reference file or nowhere; cut until it fits.
- **The description is the trigger.** Third person, stating what the skill does and when to use it, with concrete contexts and trigger phrases spelled out. Phrase triggers around session state as well as user intent ("use when editing any file under X") so mid-task situations fire. Undertriggering is the default failure mode; specificity is the cure.
- **Progressive disclosure.** Metadata sits in the listing, the body loads on invocation and stays for the session, references load on demand. Push long or fragile detail into `references/` exactly one hop from SKILL.md; every bundled file states its mode, run or read.
- **Explain why over MUST.** Imperative voice with the reasoning attached. All-caps ALWAYS/NEVER and rigid enumerations are a yellow flag that the reasoning is missing. Generalize past the motivating example: a skill runs across many prompts, not the one that inspired it.
- **Self-contained.** A skill never tells the user which skill to run next; sequencing is theirs. Naming a skill it runs under the hood is fine.
- **Load-time snapshots run under the session's restrictions.** A bang snapshot executes before the body loads, and a refused one aborts the whole load. Use the plainest command that yields the fact, no command substitution, and label what empty output means beside it.
- **Rewrite accreted prose; don't patch it.** When an edit inverts a rule or reframes a passage, rewrite that section as if written under the new thesis. Coherence of the final text outranks minimality of the diff.

## Gut-check handoff

This skill never tests its own output: the session that wrote a skill is too warm to judge how it behaves cold. Close every create or substantive edit by handing the user test prompts for a fresh session: two or three realistic task prompts with the expected behavior stated, and, when the description changed, should-trigger and should-not-trigger prompts whose negatives are near-misses (adjacent domains, shared keywords), never obviously irrelevant asks. Prompt craft lives in `references/skill-quality.md`. Typo and link fixes skip the handoff; a change to triggering or behavior never does.

## Landing checklist

A change lands when the suite is coherent, not when the SKILL.md reads well: the skill's entry in `.claude/skills/README.md` matches its behavior and triggering, the body measures under budget, and the gut-check prompts are handed over.
