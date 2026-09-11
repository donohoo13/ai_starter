# AI direction ranking — Phase 2

The ten instructions from the Phase 1 inventory (`2026-09-09-ai-direction-inventory.md`) with the highest leverage, ranked. Leverage means: removing this one instruction degrades output the most, across the widest range of tasks. Start-of-task instructions outrank cleanup. Pure instructions outrank tooling-dependent ones, with one tooling-dependent instruction included because it is central and approximable by hand.

Row numbers in parentheses point at the inventory.

## One rule that governs how every line below is phrased

The repo has a rule about rules, and it is the reason the ten lines read the way they do (row 17, `CLAUDE.md` › Standards): "Write rules for AI as positive instructions: state the action to take and the concrete check that grounds it, not the behavior to ban... when a rule meets uncertainty, grant explicit permission to say 'unknown' rather than guess." `curate-context/SKILL.md:90` says the same at drafting time: "State the action, not the ban... A bare prohibition is the wording most likely to be ignored or over-applied." Every line below names an action and, where the check is mechanical, the check. In a bare chat this is the cheapest thing you control: phrase what you want as the act and the proof, not as the thing to avoid.

## The ranked ten

### 1. Interview me before you build

**The line.** Before writing any code, interview me one question at a time, biggest decision first, with your recommendation and reasoning attached to each question, and look up anything the code can answer instead of asking me.

**Why it works.** The model's default is to start producing code from the first plausible reading of the ask, which locks in the wrong "what" before anyone has checked it. Forcing one question at a time with a recommendation attached converts the model from a code generator into a peer who has to commit to a position and defend it, and biggest-decision-first means the answers to small questions cannot be invalidated by a later big one. Looking up facts instead of asking removes the questions that waste your time and leaves only the decisions that are actually yours.

**Evidence in this repo.** `grilling/SKILL.md:8`: "Walk down each branch of the decision tree, resolving dependencies between decisions one by one — take the largest, most load-bearing decisions first, since they shape every branch below. Ask one question at a time; a stack of questions is bewildering. With each question, give your recommendation and the reasoning behind it." `grilling/SKILL.md:10`: "If a fact can be found by exploring the codebase, look it up rather than asking." The skills README calls `grill-engineer` "roughly 8 of 10 sessions", and the whole suite is "one front door for interview sessions, five lenses behind it."

**The bare-chat version.** Type it almost verbatim: "Before any code, interview me: one question at a time, the biggest decisions first with your recommendation and reasoning attached to each." Paste the relevant files first so "look it up" has somewhere to look. What you lose: the lens routing (product vs design vs engineering), the codebase as ground truth beyond what you pasted, and the artifact exits. Roughly 80% survives because the interview mechanics are the whole effect; the lenses only change persona and fact sources.

**What it looks like when it is working.** The first reply is a single question with a recommendation under it, not a code block. If the first reply is code, the instruction did not take.

### 2. Name the scope, then cut vertical slices

**The line.** Write the scope as in-scope, nice-to-have, and out-of-scope so it cannot expand silently, then split the work into vertical slices that each run end to end in build order, and show me which slice covers each requirement.

**Why it works.** Without a named out-of-scope list the model invents scope in the direction of "helpful", and without a requirement-to-slice map it drops requirements between layers. Vertical slices force each unit to be runnable and demoable, so the first slice proves the shape of the whole solution and later slices cannot hide a missing integration. This is the instruction that turns the interview into an order of work, which is why it sits directly under the interview.

**Evidence in this repo.** `capture-task/assets/task-template.md:27`: "Out of scope (non-goals, named so the task does not expand silently)". `grill-engineer/SKILL.md:70`: "Slices are vertical tracer bullets: each a thin, complete, demoable cut through every layer it touches, listed in dependency order — list order IS the build order. Every requirement and acceptance criterion must map to a slice; an unmapped requirement is a dropped requirement." `tdd/SKILL.md:45` names the failure it prevents: "Horizontal slicing — writing all tests first, then all implementation. Bulk tests verify imagined behavior."

**The bare-chat version.** After the interview: "Write the scope as in-scope, nice-to-have, and out-of-scope. Then list vertical slices, each one runnable end to end, in build order, and put the requirement each slice covers next to it." What you lose: the task file as a durable artifact across sessions, and the gates that refuse to build an under-specified file. In a single chat the scope block is the artifact, so keep it pinned in your own notes and paste it back if the conversation drifts.

**What it looks like when it is working.** A scope block with a non-empty out-of-scope list appears before any code, and every slice description ends in something you could run. A slice named "set up the data layer" means it has slid back to horizontal.

### 3. Evidence, or it did not happen

**The line.** Never tell me something passes, builds, is fixed, or is clean unless you ran the check, paste the command and its literal output, and if you could not run it say "not run".

**Why it works.** The model's most dangerous output is a confident claim shaped like a result, because nothing about it looks different from a real result. Requiring the command and its literal output makes a fabricated check visible as an absence, and requiring "not run" for an unrun check removes the one wording ("checked, looks fine") that is indistinguishable from work nobody did. This also disciplines the middle of the task, not just the end: a model that knows it must show output stops reasoning its way to numbers it could measure.

**Evidence in this repo.** `CLAUDE.md` › Standards: "Evidence before completion claims: do not state something passes, builds, is fixed, or was checked and found clean without running the command that proves it, and report that command and its literal output rather than the conclusion drawn from it. 'Should work' is not 'works', and a check that could not run is reported as not run — never as a clean result, which is the one wording indistinguishable from work nobody did." `review-board/references/output-format.md:31-33`: "Report what you did, never a verdict about absence... Compute rather than reason about a number you could measure; a measurable fact you argued your way to is the single highest-risk line you can write." `CHANGELOG.md` v1.5.0 records the incident that produced it: a review seat "checked a hard character limit, computed a byte count, reasoned correctly that multi-byte characters inflate bytes, and cleared the field as within its cap when it was 88 over — it never ran the one command that measures the thing."

**The bare-chat version.** When the model cannot execute anything, you are the runner, so the line becomes: "You can't run things here, so label every claim as verified-by-you, verified-by-me, or unverified. When something needs a check, give me the exact command and tell me what output proves it. Never write 'this should work'." What you lose: the model running checks itself, which means slower loops and your attention as the bottleneck. What survives is the important half, that no claim gets past without a label.

**What it looks like when it is working.** Every "it works" comes with a command and its output, or the words "not run". The phrase "should work" disappears from the transcript. When you ask "did you test this?" the answer is a paste, not a sentence.

### 4. Agree the seams, then red before green

**The line.** Before writing tests, list the public seams you would test and wait for my okay, then write one failing test at a seam, the least code that passes it, and expected values that come from a known-good literal rather than recomputed the way the code computes them.

**Why it works.** Left alone, the model tests internals, mocks its own collaborators, and writes assertions that recompute the expected value with the same logic as the code, so the suite passes by construction and protects nothing. Naming the seams first puts the tests on the interfaces that survive refactors and gives you tests you will read, because there are few of them and each one reads as a specification. Red-before-green with the least code stops speculative implementation, and the literal-expected-value rule is the single check that kills tautological tests.

**Evidence in this repo.** `tdd/SKILL.md:22`: "Test only at pre-agreed seams. Before writing any test, write down the seams under test and confirm them with the user. No test is written at an unconfirmed seam." `tdd/SKILL.md:49`: "Red before green. Write the failing test first, then only enough code to pass it. Don't anticipate future tests." `tdd/SKILL.md:44`: "Tautological — the assertion recomputes the expected value the way the code does... Expected values must come from an independent source of truth — a known-good literal, a worked example, the spec." `CLAUDE.md` › Development: "Test at the interface, not past it: callers and tests cross the same seam."

**The bare-chat version.** Verbatim works: "List the public seams you'd test and stop for my okay. Then one failing test at a seam, the least code to pass it, repeat. Expected values are literals, never computed the way the code computes them. Mock only third parties we don't control." What you lose: the dependency-bounded test runs and the full suite at the end, both of which you now run by hand. Nothing about seam selection or the anti-patterns depends on tooling.

**What it looks like when it is working.** The first code you see is a failing test whose assertion contains a literal, and the seam list arrived before it. If the first test mocks something the codebase owns, the instruction did not take.

### 5. Facts from the code, decisions from me, and hold your take

**The line.** When I state how the code works, check it and correct me with the file if I am wrong, leave every decision to me, and when I push back on your recommendation restate your case unless I have given you a new fact.

**Why it works.** The model folds at the first objection and accepts stated premises as true, which means your mistakes flow straight into the design and your first "are you sure?" erases a correct recommendation. Splitting facts from decisions gives the model a place to be firm (facts, with a citation) and a place to defer (decisions), so it stops doing both wrong at once. The "unless a new fact" clause is what stops the model from folding out of politeness while still letting you overrule it.

**Evidence in this repo.** `grilling/SKILL.md:10`: "verify the user's assertions against the code. The decisions are the user's — put each one to them and wait. Correct misunderstandings about how the code currently works, citing the specific files and patterns you found." `grilling/SKILL.md:12`: "When the code, your research, or the facts established in the session support your recommendation, state it in strong and unambiguous terms and hold it under pushback, restating the case rather than folding at the first objection. Drop the position only when the user brings a fact that changes it or explicitly tells you to move on. Deferring to an assertion the evidence contradicts is a failed session, not politeness." `domain-modeling/SKILL.md:58` applies the same split to boundaries: "surface the conflict as a decision instead of designing around it."

**The bare-chat version.** Verbatim, with pasted code as the ground truth: "If I say something about the code that the pasted code contradicts, tell me and point at the line. Decisions are mine. If I push back on your recommendation without a new fact, hold it and restate why." What you lose: nothing that matters. In an interview this is the line the grader sees most clearly, because it produces a visible moment where the model corrects the candidate and the candidate accepts it.

**What it looks like when it is working.** You get corrected with a file and line at least once, and a recommendation survives your first "are you sure?" with a restated case rather than "you're right, let me change that."

### 6. Build the loop before you theorize

**The line.** Before you tell me what is causing this bug, give me one command that fails on it, then three to five ranked hypotheses each with a prediction that would prove it wrong.

**Why it works.** The model's debugging default is to read code, pick the first plausible cause, and patch it, which fixes a nearby bug about half the time. Demanding a red-capable command first means every later theory gets tested rather than argued, and demanding several ranked hypotheses with falsifying predictions breaks the anchor on the first idea. The "prediction" clause is what separates a hypothesis from a vibe.

**Evidence in this repo.** `diagnose/SKILL.md:14`: "This is the skill. Everything else is mechanical. With a tight pass/fail signal that goes red on this bug, bisection, hypothesis-testing, and instrumentation all just consume it; without one, no amount of reading code will save you." `diagnose/SKILL.md:35`: "If you catch yourself reading code to build a theory before this command exists, stop — jumping straight to a hypothesis is the exact failure this skill prevents." `diagnose/SKILL.md:47`: "Generate 3–5 ranked hypotheses before testing any; single-hypothesis generation anchors on the first plausible idea. Each must be falsifiable — state its prediction." `CLAUDE.md` › Development: "Don't propose a bug fix from reading code alone."

**The bare-chat version.** Verbatim: "Don't tell me the cause yet. First give me one command that reproduces the failure, then 3–5 ranked hypotheses, each with what we'd observe if it's wrong. I'll run the command and report back." What you lose: the model running the loop and tightening it (faster, sharper, deterministic); you become the runner. The ranking and predictions lose nothing.

**What it looks like when it is working.** A reproduction command appears before any sentence beginning "I think the cause is." If the model's first message on a bug contains a diff, the instruction did not take.

### 7. Review your own diff as a board, then give me a plan

**The line.** Review your diff one lens at a time for correctness, security, reliability, maintainability, and performance, give every finding a file and line, an excerpt, and a concrete failure scenario, list what you checked and found nothing, and end with what you would fix and what you would leave and why.

**Why it works.** One general "review this" pass produces vague, unranked, half-invented findings and a reassuring "looks good". Separating the lenses makes the model look for different defect shapes on each pass instead of stopping at the first few it notices, and the evidence bar (location, excerpt, scenario) is what makes a finding checkable rather than a worry. Ending with a plan rather than a list forces the model to commit to dispositions, so you answer one yes/no instead of re-triaging its output.

**Evidence in this repo.** This is the one tooling-dependent instruction on the list. `review-board/SKILL.md:11`: "Each seat gets one category, its own checklist, and a full context budget... because focused reviewers catch what one general pass misses." `review-board/SKILL.md:149`: "Evidence bar — `file:line`, an excerpt, and a concrete failure scenario... An empty findings list is a fine result; never invent findings to look busy." `review-board/SKILL.md:168`: "Have the spine to reject, and say why, because a pass that confirms everything was not a triage pass." `review-board/SKILL.md:181`: "Print the dispositions as a plan in three groups: Fixing, Capturing, Not addressing. Never a menu of per-finding questions." The checklists themselves are pure text: `references/correctness.md` through `references/adversarial.md`.

**The bare-chat version.** "Review your diff five times, one pass per lens: correctness, security, reliability, maintainability, performance. Each finding needs file and line, the excerpt, and a concrete input or state that produces the wrong outcome. After each pass, list what you checked and found nothing. Then give me a plan: what you'd fix, what you'd leave and why. I'll say yes or no." What you lose is real and the repo names it: the seats run in separate contexts, and the same model reviewing its own output anchors on its own reasoning. The v1.5.0 changelog cites Huang et al. that "models largely cannot self-correct reasoning without external feedback, so a second look by the same seat buys nothing." Expect the bare version to catch the recognizable shapes (empty catches, missing null checks, N+1) and miss the logic error it made on purpose. You also lose the reliability seat's escalation on concurrency and the security seat's full-file read. Still worth doing, and the "what I checked and found nothing" list is the half that survives intact.

**What it looks like when it is working.** Findings carry `file:line` and a scenario, a "checked, found nothing" list appears after each pass, and the message ends with a plan and a single question rather than a bulleted list of maybes.

### 8. After a refactor, find every reference and delete what is dead

**The line.** After any rename or removal, find every reference to what you changed, delete verified-dead code in the same change without commenting it out, and list anything you suspect is dead but cannot prove.

**Why it works.** A refactor leaves orphans because the model edits the definition and stops, and when it does notice dead code it comments it out "just in case", which is the worst of both. Forcing a reference sweep makes the blast radius explicit, and requiring a "suspected but unverified" list gives the model a legal place to put doubt other than leaving the code in. Deleting rather than commenting keeps git as the archive and the tree readable.

**Evidence in this repo.** `CLAUDE.md` › Development: "When a change orphans code (a replaced implementation, an unused export, a bypassed branch), verify deadness with LSP find-references plus a repo-wide grep for dynamic or string-keyed references... Remove verified-dead code inside the change's own blast radius in the same change — delete, never comment out; git history is the archive... Zero references alongside dynamic access, feature flags, serialized handler names, or a public API surface is 'suspected dead, unverified': report it, never remove it unprompted." `implement-task/SKILL.md:206-209`: "After multi-file changes, audit that schemas, constant maps, and import references were updated consistently. Verify orphaned code... removed or reported, never silently left."

**The bare-chat version.** "After the refactor, grep for every symbol you renamed or removed and paste the hits. Delete what's dead in this change; never comment it out. List anything you suspect is dead but can't prove from the grep." What you lose: find-references through the type system, so dynamic and string-keyed references are the model's guess. The repo's own rule already states the grep-only degraded path, so the bare version is the repo's fallback, not an approximation.

**What it looks like when it is working.** The diff includes deletions, not just additions, and the summary carries a list of removed symbols plus a "suspected, unverified" list. A `// TODO: remove` or a commented-out block means the instruction did not take.

### 9. Comments are zero by default

**The line.** Write no comments unless one carries a why the code cannot show, keep that one to a single line, and never mention this conversation in the code.

**Why it works.** The model narrates what the code does, restates types, and explains reasoning it just had in the chat, which bloats files and, in a codebase other models will read, plants prose that competes with the real design docs as an authority. A zero default with a narrow exception forces the explanation into names and structure, and the "never about this conversation" clause stops the most embarrassing category outright. The repo found that "comment the why" alone fails, because the offending comments were why-comments; the fix is a cost test, not a category.

**Evidence in this repo.** `~/.claude/CLAUDE.md` › Code style: "Comment budget: zero by default. You may add one single-line comment only if removing it would make a non-obvious constraint or external workaround unclear." `CLAUDE.md` › Development: "Write a comment only when it prevents a dangerous action, or caches a fact that costs six or more jumps through files or symbols to reconstruct — or that no file in the repo can answer at all — stated in one line." `CHANGELOG.md` v1.4.1 records the cause: an instance reported "multi-line comments restating design rationale fully reconstructible from the theme file... which bloat files and — worse in an AI-maintained codebase — read as prescriptions to later sessions."

**The bare-chat version.** Verbatim: "Zero comments by default. One line, only where the why can't be shown in code. Nothing about our conversation in the code." What you lose: nothing.

**What it looks like when it is working.** Diffs with almost no green comment lines, and none that begin "Updated to", "Now we", or "As discussed".

### 10. No abstraction before the third example

**The line.** Duplicate rather than abstract until the third occurrence, add no interface that has one implementation, and inline any helper that has one caller.

**Why it works.** The model reaches for factories, ports, and helpers on the first occurrence because they look like good engineering, and a grader reading a take-home sees speculative structure before they see the solution. Three concrete checks (count the occurrences, count the implementations, count the callers) replace a vague "keep it simple" with something the model can actually apply, and the deletion test in particular catches the one-caller wrapper that every model writes.

**Evidence in this repo.** `CLAUDE.md` › Development: "Follow the Rule of Three: first occurrence, write it naturally; second, keep the duplicate (don't abstract yet); third, refactor into an abstraction... choose duplication over the wrong abstraction, never fear the right one." Same section: "Introduce a seam only when something actually varies across it: one adapter is a hypothetical seam, two are a real one. A port or interface with a single implementation and no second caller in sight is speculative indirection." And the deletion test: "delete it and inline its body at the call site; if that duplicates real complexity across callers it earned its interface and stays, and if the complexity just relocates intact to one caller the interface pays for nothing, so inline it."

**The bare-chat version.** Verbatim: "No abstraction before the third example. No interface with one implementation. Any helper with one caller gets inlined." What you lose: nothing.

**What it looks like when it is working.** No `interface` with a single `implements`, no `utils` file with one export, no config object for a case that never varies. When you ask "why is this a separate function?" the answer names a second caller.

## Why the top three are the top three

They are the only three that cannot be recovered by anything downstream, and between them they cover the start, the middle, and the end of every task.

- **Interviewing first** (1) is the only instruction that prevents building the wrong thing at all. Every other rule on the list improves a solution to the problem the model understood; this one is what makes the model understand the right problem. The repo's own structure is the argument: five lenses, one router, and a stated 8-of-10 sessions running through it. A wrong "what" survives perfect tests, a perfect review, and perfect comments.
- **Scope and slices** (2) is what converts the interview into buildable order and is the cheapest place to catch scope invention. The repo makes it load-bearing twice, "named so the task does not expand silently" and "an unmapped requirement is a dropped requirement", because dropped and invented scope are the two failures a grader notices first and the two that cost most to fix late.
- **Evidence over claims** (3) is the one rule the repo promoted payload-wide after measuring its absence, and it is the only rule that governs every other rule's output: a test is only a test if it was run, a review finding is only a finding if it has a location, a "deleted the dead code" is only true if the grep was pasted. The changelog's whole first year is a catalog of the failure it names, "the failure is shaped like success, with no error, no warning, and a clean-looking result."

Four sits just below because tests depend on the seams the interview settled. Five is a behavior modifier on one rather than a step of its own. Six is the highest-leverage line on the list for bug work and would be top three on a debugging-only ranking, but it does not apply to greenfield tasks.

## Worth knowing, ranked below the ten

These are real, repo-grounded, and narrower than the ten. Each gets the same five fields in short form.

**Incumbent verdict and the demolition pass** (rows 103, 118, 205, 206). Line: when replacing existing code, say up front whether the old implementation is untouched, extended, or replaced, and on "replaced" list what dies and what only it knew, delete it first, then build without reading it. Why: measured deletion avoidance, "models locate the right file over 90% of the time and remove the required line about half as often, and roughly a third of otherwise-correct patches wrap old code in a conditional rather than deleting it" (`implement-task/references/demolition.md:3`). Evidence: `grill-engineer/SKILL.md:54`, "Ask what happens to the existing implementation, never what the work is called"; `demolition-executor.md:10`, "Open none of the files on the list." Bare-chat version: "Before we touch this, is the existing implementation kept, extended, or replaced? If replaced: list the files that die, write down anything only that code knew as a requirement on the new one, delete them, then build. Don't reread the old code once it's gone." What you lose: the context firewall, because the same chat that read the old code writes the new one, and the repo is explicit that this is the whole mechanism ("Two agent invocations with separate contexts are the mechanism, not a division of labor"). Expect it to work at maybe half strength. Sign it is working: the deletion commit lands before the first new line, and the new code does not mirror the old file's structure. Ranked below the ten because it only applies to brownfield replacement.

**Ceremony scales with size; discipline never does** (row 94). Line: a one-line change still gets the questions, the failing test, and the check, but not the artifacts. Evidence: `grill-engineer/SKILL.md:11`. Bare-chat version is the line itself. Sign: a tiny fix still arrives as test-then-code with output pasted. Ranked below because it is a modifier on 1, 3, and 4 rather than a step.

**Not done until I have seen it work** (rows 100, 126). Line: when you think it is done, hand me exact steps to exercise it and wait for my verdict before proposing anything next. Evidence: `grill-engineer/SKILL.md:27`, "Green checks prove the code does what the tests say; only the user can confirm it does what they meant, so recommend nothing downstream... until they confirm." In a bare chat you are already the executor, so this collapses into 3; the surviving behavior is the model stopping instead of saying "next I'll...". Sign: the message ends with steps and a question, not a next step.

**Settle the what before the how** (row 90). Line: if the outcome is still fuzzy, talk about what it should be for the user before any design. Evidence: `grill-me/SKILL.md:57`, product-first "even when phrased in engineering vocabulary, because the mis-routing costs are asymmetric." This is a special case of 1 and usually fires as the first question of the interview.

**Present the plan and keep going** (row 120). Line: before each slice, list the files, sequence, test seams, and risks, then say "Proceeding unless you interrupt" and continue in the same message. Evidence: `implement-task/SKILL.md:153`, and the v2.7.0 changelog measured plans stopping "for a check-in roughly half the time." Only useful once you trust the model's plans; in an interview you probably want the gate.

**Stubs never ship** (row 36). Line: no TODOs, stubs, or placeholder logic in delivered code; finish it or say what is unfinished. Evidence: `CLAUDE.md` › Development. Sign: `grep TODO` on the diff returns nothing. Small, but graders grep for it.

**Smallest correct patch, no nested ternaries** (rows 4, 72). Line: give me the smallest diff that is correct, and never nest a ternary. Evidence: `~/.claude/CLAUDE.md` › Communication; `.claude/rules/javascript-typescript.md`, "Never nest ternary expressions... Use early-return guards, an `if`/`else if` chain, or a lookup map." Both are one-liners worth having in the cold-start script but neither changes the shape of a task.

## Decorative, or close to it

Instructions in the repo that do not change coding output enough to recite. Blunt by request.

- **The persona flourishes.** "Dry wit, subtle snark if a request is trivial or contradictory" (`~/.claude/CLAUDE.md` › Persona) changes tone, not code. "Have a take" in the same section does change output and is folded into line 5. Keep the file, do not recite the snark.
- **`notes/DESIGN_PRINCIPLES.md`.** Untracked, so not part of the payload, and it would fail the repo's own admission bar: `curate-context/SKILL.md:54` rejects "Generic best practice or restated framework default." The model already knows KISS, DRY, YAGNI, and SOLID; reciting them buys nothing. The one non-generic line in it, "don't force SOLID... composition over class hierarchies," is already covered by line 10.
- **"Confirm with the user to address root causes, not symptoms"** (`CLAUDE.md` › Standards). Soft verb, no check, and the work is done by "Don't propose a bug fix from reading code alone" and by `diagnose`. By the repo's own rule against soft verbs (row 16) this line should have been cut.
- **The Markdown section** (rows 52–54). Real mechanical hygiene for this repo's docs. Never say it in an interview.
- **Data handling** (rows 60–62). Generic except for the security-event field list. A model logs no secrets without being told.
- **The 300-word cap and plain-language rule** (rows 1, 13). Both are conversation rules and both are correct for conversation. Neither belongs in a take-home writeup, where you want depth, so do not carry them into artifacts. The repo already scopes them: "Conversation only; artifacts keep precise terms."
- **Objective time sourcing** (row 14). Prevents invented durations. Real, small, and irrelevant to a graded coding session unless you ask for estimates, which you should not.
- **The rule-writing meta-rules** (rows 16, 18, 19, 20). They govern maintaining the repo, not directing a model on a task. Row 17 is the exception and is covered at the top of this document.
- **The confirming-understanding protocol** (row 5). Personal ergonomics for how you like to be answered. It works, and nobody grading you will see it.

## Not in the repo, worth adding

Kept out of the ranked list per the ground rules. Each is a gap a bare-chat session feels that the tooled repo does not.

- **Restate the problem with assumptions before the interview.** The repo opens with "Grilling on <subject>, until <objective>" but never asks the model to say back what it thinks the problem is and what it is assuming. In a bare chat, "restate the problem in your own words and list every assumption you're making" is the cheapest check that the model read the prompt you read. Closest existing line: row 84.
- **Label uncertainty in code, not only in claims.** The evidence rule labels claims and `research-analyst` labels evidence tiers (documented, consensus, inference), but nothing asks the model to mark the lines of code it is unsure of. "Mark any line you're not confident in with a note in your message, not in the code" would surface guesses before they ship. Closest existing line: row 17's permission to say "unknown".
- **A running decisions ledger for long chats.** The repo's answer to context loss is artifacts and hard stops between sessions. A bare chat has neither, so "every ten messages, restate the decisions we've made as a numbered list" is the approximation of the task file. Closest existing line: row 97, "Session context is capital."
- **Show diffs, not files.** Global rule 4 asks for the smallest patch, but nothing says "output unified diffs against what I pasted, never a regenerated file." In a chat without an edit tool this is the difference between a change you can review and one you have to diff yourself. Closest existing line: row 4.

# Cold-start scripts — Phase 3

Two ordered message sequences, typed before touching the problem. Each message is one to three sentences in the words you would type. The bracket after each message names the ranked line it deploys (L1 through L10 from Phase 2, plus the "worth adding" items as WA) so the mapping is memorizable.

Assumptions for both scripts: a bare chat with no tool access, so you are the runner for every command. Where the model can execute (Claude Code, an IDE agent), the messages marked **runner** flip: tell the model to run it and paste the output itself, and the rest of the script is unchanged.

## Script A: 90-minute TypeScript take-home, grader watching

Nine messages, sent in order. Messages 1 through 4 happen before any code exists and should take the first fifteen minutes; that is the part the grader is scoring.

1. **Rules of engagement.** "Standing rules for this session: no code until I say build; every claim that something passes, builds, or works comes with the command and its literal output, or the words 'not run'; zero comments unless a why cannot be shown in code; no abstraction before the third example and no interface with one implementation; and when I say something the code contradicts, tell me with the line." [L3, L9, L10, L5]

2. **Frame the problem back.** Paste the problem statement verbatim, then: "Restate this problem in your own words in one paragraph, list every assumption you are making, and list everything the statement leaves undefined. No solution yet." [WA: restate with assumptions; precondition for L1]

3. **Interview.** "Now interview me: one question at a time, the biggest decision first, your recommendation and reasoning attached to each. Where the problem statement or the pasted code already answers a question, use that instead of asking. Stop when you could write the scope without guessing." [L1, L5]

4. **Scope and slices.** "Write the scope as in-scope, nice-to-have, and out-of-scope. Then list vertical slices in build order with the requirement each one covers, where slice 1 is the thinnest path that runs end to end through the whole problem, not a layer." [L2]

5. **Seams, then okay.** "Before slice 1: list the files you will create or touch, the public seams you would test, and the risks. Wait for my okay on the seams before writing a test." [L4, plan gate]

6. **Build slice 1.** "Build: one failing test at the first seam, the least code that passes it, then the next test. Expected values are literals taken from the problem statement's examples, never computed the way the code computes them. Give me each test command and, once I paste the output, continue." [L4, L3] **runner**

7. **Verify against the statement.** "Read the problem statement again and check slice 1 against it clause by clause: for each requirement say covered, partial, or not yet, and for each example input in the statement say what our code returns and whether that matches. Do not fix anything in this message." [correctness checklist, row 138: "Flag both directions: intended behavior that is missing, and unrequested behavior that snuck in"]

8. **Remaining slices.** "Continue slice by slice the same way. Before each slice give me files, seams, and risks in five lines, then keep going unless I interrupt; after each slice, run step 7 again for the requirements that slice claimed." [L2, L4, row 120 "Proceeding unless you interrupt", L3] **runner**

9. **Board review and sweep.** "Review the whole diff one lens at a time: correctness against the problem statement, security, reliability, maintainability, performance. Each finding needs file, line, the excerpt, and a concrete input or state that produces the wrong outcome; after each lens list what you checked and found nothing. Then the mechanical sweep: grep for every symbol you renamed or removed and paste the hits, grep for TODO, commented-out code, nested ternaries, and `any`, and end with a plan of what you would fix and what you would leave and why, which I will answer yes or no." [L7, L8, L9, stubs and ternaries from the below-the-ten list]

10. **Close.** "Run the full test suite and the typecheck and paste both outputs. Then give me three lists: verified by a pasted run, unverified, and out of scope, plus the exact commands a grader runs to see it work." [L3, closing-summary rule row 15] **runner**

If time runs short, cut from the middle, never the ends: drop slices from message 8 and say so in message 10's out-of-scope list. Messages 1 through 4 and message 10 are what the grader reads.

## Script B: 30-minute live round, chat sidebar only

Six messages. Compressed, because the round is short and the sidebar cannot run anything. The grader here sees whether you direct or dictate, so the visible moments are message 2 (the model asks you something you did not think of) and message 5 (the model catches its own gap).

1. **Rules and the problem in one message.** Paste the prompt and any code, then: "For the next thirty minutes: no code until I say build; you cannot run anything, so label every claim verified-by-me or unverified; give me diffs against what I pasted, never whole files; zero comments. Restate the problem in one paragraph with your assumptions and unknowns, then ask me your single biggest question with your recommendation." [L3, WA: diffs not files, L9, WA: restate, L1]

2. **Answer, then scope.** Answer the question, then: "Scope in three lines: in, out, and the thinnest slice that runs end to end. Name the one public seam we will test and the literal expected value from the prompt's example." [L2, L4]

3. **Build.** "Build: the failing test at that seam first, then the least code that passes it, as a diff. Give me the exact command to run and what output means pass." [L4, L3] **runner**

4. **Verify against the statement.** Paste the output, then: "Check the code against the prompt clause by clause: covered, partial, or missing. If I said anything about the code that the code contradicts, say so with the line. Fix the gaps in order, smallest diff each." [row 138, L5, row 4]

5. **Two-lens review.** "Two-minute review, correctness and reliability lenses only: file, line, and a concrete failure scenario per finding, then a 'checked, found nothing' list, then what you would fix in the time left and what you would leave." [L7 compressed to the two highest-yield seats]

6. **Close.** "Closing, one sentence each: what my runs verified, what is unverified, what is out of scope, and the one thing you would do next with ten more minutes." [L3, row 15]

If the round is a bug rather than a build, replace messages 2 and 3 with L6: "Before you tell me the cause, give me one command that fails on this bug, then three to five ranked hypotheses each with what we would observe if it is wrong; I will run the command and report back." Then continue from message 4 with the fix.

## What the two scripts share

- Both open with rules before the problem, because rules typed after the first code block arrive too late to shape it.
- Both frame the problem back before the first question, because the interview only works if the model and you read the same prompt.
- Both put the verify-against-the-statement step immediately after the first slice, not at the end, because a wrong reading caught at slice 1 costs one slice and caught at the end costs the session.
- Both close with three lists (verified, unverified, out of scope), which is the repo's closing-summary rule (row 15) applied to a coding session: every item names the response it invites, and nothing is left ambiguous about what was proven.
