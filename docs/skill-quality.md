# Skill Quality Reference

Distilled from the Agent Skills specification (agentskills.io/specification), Anthropic's Agent Skills best-practices guide (platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), the Claude Code skills reference (code.claude.com/docs/en/skills), and the Agent Skills engineering post (anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills). Constraints name their source; anything unattributed is house style. When guidance here surprises, verify against those sources; they move faster than this file.

## Frontmatter

- Spec: `name` and `description` are required; every other field is optional.
- Spec: `name` is 1-64 chars, lowercase letters, numbers, and hyphens, no leading, trailing, or consecutive hyphens, matching the parent directory name. House style: gerund form (`processing-pdfs`, not `pdf-processor`, never `helper`/`utils`).
- Spec: `description` is 1-1024 chars. Claude Code truncates `description` plus `when_to_use` at 1,536 in the listing, and a per-listing budget drops whole descriptions before that cap, least-invoked first.
- Claude Code: project-skill command names come from the directory; frontmatter `name` is display-only. In plugin skills `name` sets the command's last segment.
- Claude Code extensions, all optional: `when_to_use` (trigger phrases, appended to `description` and sharing its cap), `paths` (globs narrowing automatic activation; never forces a load), `argument-hint`, `arguments` (named list backing `$name` placeholders), `disable-model-invocation: true` (manual `/name` only; removes the skill from context, so its description goes unread), `user-invocable: false`, `allowed-tools` / `disallowed-tools`, `model`, `effort`, `context: fork` plus `agent`, `background: false` (fork only), `shell`, `hooks`. The spec also defines `license`, `compatibility`, `metadata`.
- Malformed frontmatter YAML loads the body with empty metadata: `/name` still works but the skill never model-triggers. `claude --debug` surfaces the parse error.

## Description craft

- Third person ("Processes X", "Use when Y"). House style; no source ties grammatical person to discovery.
- State both what the skill does and when to use it. `when_to_use` extends the description in the listing; `paths` decides whether automatic activation is available at all.
- Name the concrete trigger contexts: file paths, phrases, task shapes. Include session-state triggers ("when editing files under X") alongside user-intent triggers ("when the user asks for Y") so mid-task situations fire, not just explicit requests.
- Specificity beats pushiness: "use whenever X, Y, or Z, even if the user never says W" earns its place only when each listed context is real.

## Structure

- Three-level progressive disclosure: metadata (in the listing) → SKILL.md body (loaded on invocation, and it stays for the session) → bundled files (loaded on demand, zero cost until read).
- Spec: body under 500 lines. House style: 500 is a ceiling, not a target; a body is as long as its job needs.
- Spec: references exactly one level deep; no reference→reference chains.
- Table of contents for any reference file past ~100 lines.
- Multi-domain skills organize by variant (`references/aws.md`, `references/gcp.md`) so a session reads only the branch it needs.
- `scripts/` for deterministic repeated work, `assets/` for files used in output, `references/` for knowledge. Ship a script when test sessions keep independently writing the same helper.

## Writing style

- Imperative voice; explain why over bare MUSTs, all-caps ALWAYS/NEVER and rigid structure are a yellow flag that the reasoning is missing.
- Match freedom to fragility: heuristic prose where many approaches work, a parameterized script where one pattern is preferred, an exact no-argument script where sequence deviation breaks things.
- Every bundled file states its mode: run ("Run `scripts/x.py`") vs read ("See `references/x.md` for the schema").
- No time-sensitive statements ("after August", "the new API"); park deprecated material in an explicitly labeled old-patterns section instead of interleaving it.
- Generalize past the motivating example; a skill overfit to the session that inspired it is useless everywhere else.

## Gut-check prompt craft

- Write prompts a real user would type: concrete file names, a line of backstory, casual phrasing, occasional typos. Abstract category labels ("Format this data") test nothing.
- Make prompts substantive enough that a session would genuinely benefit from consulting a skill; trivial one-step asks don't trigger skills regardless of description quality.
- Should-trigger set: vary phrasing and formality, include cases that never name the skill or its file type, and include one where this skill competes with a neighboring skill and should win.
- Should-not-trigger set: near-misses only, adjacent domains, shared keywords, contexts where another tool is correct. Obviously irrelevant negatives test nothing.
- State the expected behavior for every prompt so the user can judge pass or fail without interpreting.
