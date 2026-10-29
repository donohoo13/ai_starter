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


class HashTests(SddCase):
    def hash_of(self, text):
        path = self.repo / "artifact.md"
        path.write_text(text)
        code, out, err = self.run_sdd("hash", str(path))
        self.assertEqual(code, 0, err)
        return out.strip()

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

    def test_body_edits_change_the_hash(self):
        self.assertNotEqual(self.hash_of(BODY), self.hash_of(BODY.replace("T001 one", "T001 two")))

    def test_missing_file_is_a_refusal(self):
        code, out, err = self.run_sdd("hash", str(self.repo / "nope.md"))
        self.assertEqual(code, 1)
        self.assertIn("nope.md", err)


if __name__ == "__main__":
    unittest.main()
