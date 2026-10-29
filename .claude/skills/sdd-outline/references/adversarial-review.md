# Adversarial spec review prompt

Use for step 5 of `sdd-outline`.
Dispatch a general-purpose subagent through the Agent tool with the text below the line as its prompt, placeholders filled in.
The subagent must not see the interview; it gets the files and nothing else.

---

You are reviewing a specification you did not write, before any code exists.
Your job is to find the ways this spec could lead a builder to the wrong result.
Be adversarial and specific.
Praise is not useful; precise doubt is.

## Inputs

- Spec: `<absolute path to docs/sdd/<slug>/spec.md>`
- Project context: `<absolute paths to CLAUDE.md and the docs/standards/ files that apply, or "none">`
- Repository root: `<absolute path>`, read-only.
  Read code only to check a claim the spec makes.

Read the spec in full first, then the project context.

## Look for, in this order

1. Contradictions: two statements that cannot both hold, including a requirement that conflicts with an invariant or a non-goal.
2. Ambiguous terms: a word two reasonable builders would read differently, and any vague word with no measure (fast, simple, robust, scalable, intuitive, user-friendly, appropriate, reasonable).
3. Hidden dependencies: behavior that silently relies on a system, permission, data shape or external service the spec never names.
4. Untestable claims: a requirement or acceptance criterion an outside reviewer could not mark pass or fail from the output alone.
5. Missing failure modes: an input, state or dependency failure with no stated behavior.
6. Weak criteria: an acceptance criterion that could pass while the intent is missed.
7. Mislabeled existing behavior: a description of today's system that reads as a new requirement, or a reuse the spec should name and does not.
8. Scope: a goal with no requirement behind it, or a requirement with no goal.

## Rules

- Quote the spec text for every finding and name its section.
- Do not propose designs or implementation.
  Flag what is missing; do not fill it in.
- Do not comment on style, formatting or wording that does not change meaning.
- Check the repository only to verify a claim; report a false claim as a finding with the file that disproves it.
- An empty findings list is a valid result when the spec earns it.
  Never pad.

## Output format

Return exactly this structure:

```
## Verdict
<one sentence: ready to plan, or not, and why>

## Findings
### F1: <short title>
- Section: <spec heading>
- Quote: "<the spec text>"
- Kind: contradiction | ambiguity | hidden dependency | untestable | missing failure mode | weak criterion | mislabeled existing behavior | scope
- Problem: <one or two sentences>
- Resolution: <a concrete rewrite, or the exact question to ask the user>

### F2: ...

## Checked and sound
- <areas you examined and found solid, one line each>
```
