import unittest

from helpers import SLUG, SddCase, VALID_SPEC, BRANCH

SPEC = VALID_SPEC % {"slug": SLUG, "branch": BRANCH}


class LintSpecTests(SddCase):
    def lint(self, text=SPEC):
        self.write_spec(text)
        return self.run_sdd("lint", SLUG, "spec")

    def test_valid_spec_passes(self):
        code, out, err = self.lint()
        self.assertEqual(code, 0, out + err)
        self.assertIn("0 errors", out)
        self.assertNotIn("WARN", out)

    def test_missing_always_section_is_an_error(self):
        code, out, err = self.lint(SPEC.replace("## Non-goals\n- Editing attachments.\n\n", ""))
        self.assertEqual(code, 1)
        self.assertIn('missing section "Non-goals"', out)

    def test_missing_frontmatter_field_is_an_error(self):
        code, out, err = self.lint(SPEC.replace("owner: Test User\n", ""))
        self.assertEqual(code, 1)
        self.assertIn('missing frontmatter field "owner"', out)

    def test_description_needs_one_or_two_sentences_and_the_result_is(self):
        three = SPEC.replace("fewer blank pages.", "fewer blank pages. Reviewers are happier.")
        code, out, err = self.lint(three)
        self.assertEqual(code, 1)
        self.assertIn("description", out)
        self.assertIn("sentences", out)
        wrong_opener = SPEC.replace("The result is faster reviews", "Reviews get faster")
        code, out, err = self.lint(wrong_opener)
        self.assertEqual(code, 1)
        self.assertIn('"The result is"', out)

    def test_description_length_warns_above_45_and_fails_at_50(self):
        filler = " ".join(["word"] * 22)
        long_second = SPEC.replace("The result is faster reviews and fewer blank pages.", "The result is faster reviews and fewer blank pages for %s." % filler)
        code, out, err = self.lint(long_second)
        self.assertEqual(code, 0, out)
        self.assertIn("WARN", out)
        self.assertIn("45", out)
        filler = " ".join(["word"] * 26)
        too_long = SPEC.replace("The result is faster reviews and fewer blank pages.", "The result is faster reviews and fewer blank pages for %s." % filler)
        code, out, err = self.lint(too_long)
        self.assertEqual(code, 1)
        self.assertIn("50", out)

    def test_summary_needs_five_to_seven_sentences_in_one_paragraph(self):
        short = SPEC.replace(" The PDF generator will render a thumbnail for each attachment with pdf-lib. Thumbnails let reviewers judge a attachment from the list. The finished PDF shows every attachment inline.", "")
        code, out, err = self.lint(short)
        self.assertEqual(code, 1)
        self.assertIn("summary", out.lower())
        self.assertIn("sentences", out)
        split = SPEC.replace("Finance approves invoices a day late as a result. ", "Finance approves invoices a day late as a result.\n\n")
        code, out, err = self.lint(split)
        self.assertEqual(code, 1)
        self.assertIn("one paragraph", out)

    def test_requirement_ids_must_be_well_formed_and_unique(self):
        duplicate = SPEC.replace("- NFR-001: p95", "- FR-001: p95")
        code, out, err = self.lint(duplicate)
        self.assertEqual(code, 1)
        self.assertIn("duplicate", out)
        self.assertIn("FR-001", out)
        malformed = SPEC.replace("- INV-001:", "- INV-1:")
        code, out, err = self.lint(malformed)
        self.assertEqual(code, 1)
        self.assertIn("INV-1", out)

    def test_every_fr_needs_an_acceptance_line(self):
        no_acceptance = SPEC.replace("  - Acceptance: Given an invoice with 300 attachments, when the PDF renders, then every thumbnail appears within 10 seconds.\n", "")
        code, out, err = self.lint(no_acceptance)
        self.assertEqual(code, 1)
        self.assertIn("FR-001", out)
        self.assertIn("Acceptance", out)

    def test_clarification_marker_is_an_error_with_its_line(self):
        marked = SPEC + "\n## Open questions\n- [NEEDS CLARIFICATION: which customers?]\n"
        code, out, err = self.lint(marked)
        self.assertEqual(code, 1)
        line = marked.count("\n", 0, marked.index("[NEEDS")) + 1
        self.assertIn("spec.md:%d" % line, out)
        self.assertIn("NEEDS CLARIFICATION", out)

    def test_vague_word_without_a_number_warns(self):
        vague = SPEC.replace("- G1: Reviews finish in under 10 minutes.", "- G1: Reviews feel fast.")
        code, out, err = self.lint(vague)
        self.assertEqual(code, 0, out)
        self.assertIn("WARN", out)
        self.assertIn("fast", out)
        measured = SPEC.replace("- G1: Reviews finish in under 10 minutes.", "- G1: Reviews are fast: under 10 minutes.")
        code, out, err = self.lint(measured)
        self.assertNotIn("WARN", out)

    def test_lint_without_artifact_covers_what_exists(self):
        self.write_spec(SPEC + "\n- [NEEDS CLARIFICATION: x]\n")
        code, out, err = self.run_sdd("lint", SLUG)
        self.assertEqual(code, 1)
        self.assertIn("spec.md", out)

    def test_unknown_slug_is_a_refusal(self):
        code, out, err = self.run_sdd("lint", "nope", "spec")
        self.assertEqual(code, 1)
        self.assertIn("nope", err)


if __name__ == "__main__":
    unittest.main()
