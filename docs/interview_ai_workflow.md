# How I direct AI when I code

Memory aids distilled from this repo's rules, skills, and hooks. The ranking and the evidence behind each line live in `docs/notes/2026-09-10-ai-direction-ranking.md`; the full inventory lives in `docs/notes/2026-09-09-ai-direction-inventory.md`.

## Cheat sheet

Ten lines, ranked by leverage. Memorize the lines. The five-word tag after each is why it works.

1. Interview me before you build, one question at a time, biggest decision first, your recommendation and reasoning attached. Wrong what survives everything else.
2. Name in-scope, nice-to-have, and out-of-scope, then cut vertical slices in build order with the requirement each covers. Named scope cannot expand silently.
3. Never claim it passes, builds, or works unless you ran it; show the command and its output, or say "not run". Failure looks exactly like success.
4. List the public seams you would test and wait for my okay, then one failing test at a time with a literal expected value. Tests at interfaces survive refactors.
5. Facts come from the code with a line cited, decisions come from me, and hold your recommendation under pushback unless I bring a new fact. Politeness is not a fact.
6. Before naming a cause, give me one command that fails on the bug, then three to five ranked hypotheses with what would prove each wrong. First plausible idea anchors you.
7. Review the diff one lens at a time with a file, a line, and a failure scenario per finding, then hand me a plan to answer yes or no. Focused passes beat one general.
8. After a refactor, find every reference to what changed, delete what is dead, and list what you suspect is dead but cannot prove. Definitions change, references get forgotten.
9. Comments are zero by default, one line only for a why the code cannot show, and never about this conversation. Comments compete with the docs.
10. No abstraction before the third example, no interface with one implementation, and inline any helper with one caller. One example is a guess.

## Flashcards

Front is the failure you are watching for. Back is the line that prevents it.

Front: the model jumps to code before it understands the problem. Back: Before writing any code, restate the problem in your own words with your assumptions, then interview me one question at a time, biggest decision first, with your recommendation attached.

Front: the model invents scope in the direction of helpful. Back: Write in-scope, nice-to-have, and out-of-scope before any code, then map every requirement to a slice.

Front: the model builds a layer instead of a feature. Back: Every slice runs end to end; slice one is the thinnest path through the whole problem.

Front: the model says "this should work". Back: Show me the command and its literal output, or write "not run"; never "should".

Front: the model reports "checked, looks fine" with nothing behind it. Back: List what you checked and found nothing, by name, so I can tell looked-and-found-nothing from never-looked.

Front: the model skips tests or writes them after the fact to match the code. Back: List the seams you would test and wait for my okay, then write one failing test before the code that passes it.

Front: the model's tests pass by construction. Back: Expected values are literals from the spec or a worked example, never computed the way the code computes them.

Front: the model mocks its own modules. Back: Mock only third parties we do not control; everything we own is tested through its real interface.

Front: the model folds the moment I push back. Back: If I have not given you a new fact, restate your case; decisions are mine, but facts come from the code with the line cited.

Front: the model accepts my wrong description of the code. Back: When I say something the code contradicts, tell me and point at the line.

Front: the model patches the first plausible cause of a bug. Back: One command that fails on the bug first, then three to five ranked hypotheses each with a prediction that would prove it wrong.

Front: the model's self-review is a reassuring paragraph. Back: One lens per pass, file and line and a failure scenario per finding, a checked-and-found-nothing list after each lens, and a plan at the end.

Front: the model refactors and leaves dead imports and orphaned exports. Back: Grep for every symbol you renamed or removed and paste the hits, delete what is dead in this change, and list what you suspect but cannot prove.

Front: the model comments out code instead of deleting it. Back: Delete; git is the archive.

Front: the model writes comments that narrate the change or restate the type. Back: Zero comments by default, one line only where the why cannot be shown in code, nothing about our conversation.

Front: the model ships a working solution nobody can read. Back: Clear names and small functions carry the explanation; no nested ternaries; the smallest diff that is correct.

Front: the model adds an interface, a factory, or a helper on the first occurrence. Back: No abstraction before the third example, no interface with one implementation, inline any helper with one caller.

Front: the model leaves TODOs and stubs in delivered code. Back: Finish it or tell me exactly what is unfinished; nothing placeholder ships.

Front: the model regenerates a whole file to change three lines. Back: Diffs against what I gave you, never a rewritten file.

Front: the model keeps the old implementation and tweaks it when I asked for a replacement. Back: Say whether the existing code is kept, extended, or replaced; on replaced, list what dies and what only it knew, delete it first, then build without rereading it.

Front: the model says "done" and proposes the next step before I have seen anything. Back: Hand me the exact steps to see it work and wait for my verdict; recommend nothing until I confirm.

Front: the model's closing message leaves me unsure what was proven. Back: Close with three lists: verified by a run I saw, unverified, and out of scope.

## Sixty-second answer

Spoken, first person, no jargon.

I treat the model like a strong engineer who has not read the ticket. Before it writes any code, I make it interview me, one question at a time, biggest decision first, with its own recommendation attached, and look things up in the code instead of asking me. Then it writes the scope, including what is out of scope, and cuts the work into thin slices that each run end to end. Tests come first, at the boundaries we agreed on, with expected values from the spec, not recomputed from the code. Nothing counts as working until I have seen the command and its output. When it thinks it is done, it reviews its own diff one lens at a time, with a line number and a failure scenario for every finding, and hands me a plan I answer yes or no to. It deletes what it made dead, writes almost no comments, and does not abstract until the third example. The model types. I decide.

## Thirty-second answer

Before it writes code, I make the model interview me, one question at a time, biggest decision first, with its recommendation attached. Then it writes the scope, including what is out, and cuts thin slices that each run end to end. Tests come first at the boundaries we agreed on. Nothing counts as working until I have seen the command and its output. At the end it reviews its own diff one lens at a time and hands me a plan. It types. I decide.
