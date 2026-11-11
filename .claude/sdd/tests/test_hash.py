import unittest

from helpers import SddCase

BODY = """---
title: x
status: draft
approved_hash:
---

# x

- [ ] T001 one
  - Done when: a
- [ ] P1 close: all
"""

DOCUMENT = """---
title: x
status: approved
approved_hash: abc
---

# x

## Section

%s
"""

FORMATTER_REWRITES = {
    "a blank line after a heading": (
        "### Goals\n- G1: Reviews finish in under 10 minutes.",
        "### Goals\n\n- G1: Reviews finish in under 10 minutes.",
    ),
    "table padding and divider width": (
        "| Term | Meaning |\n|---|:-:|\n| Thumbnail | A 96 px preview |\n| | empty first cell |",
        "| Term      |     Meaning      |\n| --------- | :--------------: |\n| Thumbnail | A 96 px preview  |\n|           | empty first cell |",
    ),
    "the bullet character and nesting width": (
        "* one\n    * nested\n        + deeper\n+ another list",
        "- one\n  - nested\n    - deeper\n\n* another list",
    ),
    "ordered list numbers": ("1. one\n1. two\n1. three", "1. one\n2. two\n3. three"),
    "an ordered list renumbered from its start": ("Steps follow.\n\n10. ten\n11. eleven", "Steps follow.\n\n1. ten\n1. eleven"),
    "the emphasis character": ("*must* and __never__ and ***both***", "_must_ and **never** and **_both_**"),
    "a literal star read as emphasis": ("a literal * star, 2 * 3 * 4", "a literal _ star, 2 _ 3 _ 4"),
    "an escape added before a literal": ("a glob *.ts and an _id field", "a glob \\*.ts and an \\_id field"),
    "an escape removed": ("snake\\_case, 50\\% and a \\| b", "snake_case, 50% and a | b"),
    "a backslash escaped": ("the folder C:\\Users\\me", "the folder C:\\\\Users\\\\me"),
    "a paragraph wrapped": (
        "A sentence that a formatter set to wrap prose breaks across two lines.",
        "A sentence that a formatter set to wrap prose breaks\nacross two lines.",
    ),
    "a list item wrapped": ("- item text that continues", "- item text\n  that continues"),
    "a paragraph wrapped before a pipe": ("- a union type string | null in prose", "- a union type string\n  | null in prose"),
    "a numbered line folded into its paragraph": ("Remaining steps:\n3. Do X", "Remaining steps: 3. Do X"),
    "a numbered line escaped in its paragraph": ("Remaining steps:\n3. Do X", "Remaining steps:\n3\\. Do X"),
    "the rule style": ("above\n\n***\n\nbelow", "above\n\n---\n\nbelow"),
    "a spaced rule": ("above\n\n- - -\n\nbelow", "above\n\n" + "_" * 70 + "\n\nbelow"),
    "the fence character": ("~~~sh\npnpm test\n~~~", "```sh\npnpm test\n```"),
    "the fence length": ("````text\nplain\n````", "```text\nplain\n```"),
    "a fenced block indented with its list item": (
        "1. Run:\n\n    ```sh\n    pnpm test\n    ```",
        "1. Run:\n\n   ```sh\n   pnpm test\n   ```",
    ),
    "whitespace inside fenced code": (
        '```json\n{"error":{"code":"not_found"},"items":[1,2]}\n```',
        '```json\n{ "error": { "code": "not_found" }, "items": [1, 2] }\n```',
    ),
    "markdown inside a markdown fence": (
        "````markdown\n#### Inner\n* bullet with *emphasis*\n\n```sh\npnpm test\n```\n````",
        "````markdown\n#### Inner\n\n- bullet with _emphasis_\n\n```sh\npnpm test\n```\n````",
    ),
    "a quote marker on a lazy line": ("> quoted\ncontinued", "> quoted\n> continued"),
    "the hard break style": ("line one  \nline two", "line one\\\nline two"),
    "an escape beside a code span": (
        'run `grep "a\\|b"` on snake\\_case, then \\`quote\\`',
        'run `grep "a\\|b"` on snake_case, then \\`quote\\`',
    ),
    "trailing whitespace and line endings": ("one \ntwo", "one\ntwo\n\n"),
}

REAL_EDITS = {
    "a word": ("the system shall render a thumbnail", "the system shall render a placeholder"),
    "a number": ("within 10 seconds", "within 15 seconds"),
    "a comparison": ("p95 < 200 ms", "p95 > 200 ms"),
    "a removed word": ("shall never show a raw exception", "shall show a raw exception"),
    "an added sentence": ("One.", "One.\nTwo."),
    "the order of two lines": ("- first\n- second", "- second\n- first"),
    "two words joined": ("Depends on: T001 T002", "Depends on: T001T002"),
    "a number split": ("at most 100 rows", "at most 10 0 rows"),
    "a hyphen": ("FR-001", "FR001"),
    "a heading's level": ("### Goals", "#### Goals"),
    "a word moved out of a heading": ("### Goals for\nreviewers", "### Goals\nfor reviewers"),
    "a list item made prose": ("- G1: a goal", "G1: a goal"),
    "a bullet list made numbered": ("- one\n- two", "1. one\n2. two"),
    "a table cell boundary": ("| a | b c |", "| a b | c |"),
    "an escaped pipe made a cell boundary": ("| a \\| b |", "| a | b |"),
    "a table column's alignment": ("| a |\n| :-- |", "| a |\n| --: |"),
    "code inside a fence": ("```sh\npnpm test\n```", "```sh\npnpm build\n```"),
    "an underscore inside a fence": ("```sh\nexport MAX_RETRIES=3\n```", "```sh\nexport MAX*RETRIES=3\n```"),
    "a fence's language": ("```sh\nx\n```", "```js\nx\n```"),
    "an underscore inside a code span": ("`snake_case`", "`snake*case`"),
    "a backslash inside a code span": ("`a\\.b`", "`a.b`"),
    "emphasis added": ("it must hold", "it **must** hold"),
    "a number that starts a wrapped line": ("in the year\n2026. Then", "in the year\n2027. Then"),
    "a rule removed": ("above\n\n---\n\nbelow", "above\n\nbelow"),
}


class HashCase(SddCase):
    def hash_of(self, text):
        path = self.repo / "artifact.md"
        path.write_text(text)
        code, out, err = self.run_sdd("hash", str(path))
        self.assertEqual(code, 0, err)
        return out.strip()


class HashTests(HashCase):
    def test_prints_twelve_hex_characters(self):
        digest = self.hash_of(BODY)
        self.assertRegex(digest, r"^[0-9a-f]{12}$")

    def test_frontmatter_changes_do_not_change_the_hash(self):
        changed = BODY.replace("status: draft", "status: approved").replace("approved_hash:", "approved_hash: abc")
        self.assertEqual(self.hash_of(BODY), self.hash_of(changed))

    def test_checking_a_box_does_not_change_the_hash(self):
        self.assertEqual(self.hash_of(BODY), self.hash_of(BODY.replace("- [ ] T001", "- [x] T001")))
        self.assertEqual(self.hash_of(BODY), self.hash_of(BODY.replace("- [ ] T001", "- [X] T001")))

    def test_trailing_whitespace_does_not_change_the_hash(self):
        padded = BODY.replace("one\n", "one   \n") + "\n\n"
        self.assertEqual(self.hash_of(BODY), self.hash_of(padded))

    def test_evidence_notes_and_follow_ups_do_not_change_the_hash(self):
        with_notes = BODY.replace("  - Done when: a\n", "  - Done when: a\n  - Evidence: pnpm test passed 3 tests\n")
        with_notes += "\n## Follow-ups (out of scope)\n- found a bug in billing\n"
        self.assertEqual(self.hash_of(BODY), self.hash_of(with_notes))

    def test_an_evidence_note_a_formatter_wrapped_does_not_change_the_hash(self):
        wrapped = BODY.replace(
            "  - Done when: a\n",
            "  - Done when: a\n  - Evidence: pnpm test passed 3 tests, and the full suite\n    passed 412 tests\n",
        )
        self.assertEqual(self.hash_of(BODY), self.hash_of(wrapped))

    def test_a_line_after_an_evidence_note_still_counts(self):
        with_note = BODY.replace("  - Done when: a\n", "  - Evidence: passed\n  - Done when: a\n")
        self.assertEqual(self.hash_of(BODY), self.hash_of(with_note))
        self.assertNotEqual(self.hash_of(BODY), self.hash_of(with_note.replace("Done when: a", "Done when: b")))

    def test_body_edits_change_the_hash(self):
        self.assertNotEqual(self.hash_of(BODY), self.hash_of(BODY.replace("T001 one", "T001 two")))

    def test_missing_file_is_a_refusal(self):
        code, out, err = self.run_sdd("hash", str(self.repo / "nope.md"))
        self.assertEqual(code, 1)
        self.assertIn("nope.md", err)


class FormattingTests(HashCase):
    def test_what_a_formatter_rewrites_does_not_change_the_hash(self):
        for rewrite, (written, formatted) in FORMATTER_REWRITES.items():
            with self.subTest(rewrite=rewrite):
                self.assertEqual(self.hash_of(DOCUMENT % written), self.hash_of(DOCUMENT % formatted))

    def test_a_real_edit_changes_the_hash(self):
        for edit, (approved, edited) in REAL_EDITS.items():
            with self.subTest(edit=edit):
                self.assertNotEqual(self.hash_of(DOCUMENT % approved), self.hash_of(DOCUMENT % edited))

    def test_a_real_edit_changes_the_hash_of_a_reformatted_body(self):
        written, formatted = FORMATTER_REWRITES["table padding and divider width"]
        edited = formatted.replace("A 96 px preview ", "A 64 px preview ")
        self.assertNotEqual(self.hash_of(DOCUMENT % written), self.hash_of(DOCUMENT % edited))


if __name__ == "__main__":
    unittest.main()
