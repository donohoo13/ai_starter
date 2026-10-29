import unittest

from helpers import SLUG, SddCase, TEMPLATES, VALID_PLAN, VALID_SPEC, BRANCH

SPEC = VALID_SPEC % {"slug": SLUG, "branch": BRANCH}


class PlaceholderLintTests(SddCase):
    """Every `<...>` token that appears in an artifact's template is an unfilled placeholder."""

    def test_the_raw_spec_template_fails_lint(self):
        self.write_spec(TEMPLATES["spec"])
        code, out, err = self.run_sdd("lint", SLUG, "spec")
        self.assertEqual(code, 1)
        self.assertIn("placeholder", out)
        self.assertIn("<1–2 sentences; see section 7>", out)
        self.assertIn("<Feature name>", out)
        self.assertIn("<trigger>", out)

    def test_the_raw_plan_template_with_one_row_fails_lint_and_cannot_be_approved(self):
        self.write_spec()
        spec_hash = self.mark_approved("spec")
        plan = TEMPLATES["plan"].replace("based_on:\n", "based_on: %s\n" % spec_hash).replace(
            "| --- | --- | --- | --- |\n",
            "| --- | --- | --- | --- |\n| FR-001 | InvoicePdf | request test | tests/invoices/pdf.test.ts |\n| NFR-001 | InvoicePdf | request test | spec |\n| INV-001 | InvoicePdf | service test | spec |\n",
        )
        self.write_artifact("plan", plan)
        code, out, err = self.run_sdd("lint", SLUG, "plan")
        self.assertEqual(code, 1)
        self.assertIn("placeholder", out)
        self.assertIn("plan.md:10: unfilled template placeholder <Feature name>", out)
        code, out, err = self.run_sdd("approve", SLUG, "plan")
        self.assertEqual(code, 1)
        self.assertEqual(self.frontmatter("plan")["status"], "draft")

    def test_the_raw_tasks_template_fails_lint(self):
        self.approve_chain("plan")
        self.write_tasks(text=TEMPLATES["tasks"].replace("based_on:\n", "based_on: %s\n" % self.frontmatter("plan")["approved_hash"]))
        code, out, err = self.run_sdd("lint", SLUG, "tasks")
        self.assertEqual(code, 1)
        self.assertIn("placeholder", out)
        self.assertIn("<one observable behavior>", out)
        self.assertIn("<ID>", out)

    def test_the_raw_review_template_fails_lint(self):
        self.approve_chain("tasks")
        self.write_review(TEMPLATES["review"])
        code, out, err = self.run_sdd("lint", SLUG, "review")
        self.assertEqual(code, 1)
        self.assertIn("placeholder", out)
        self.assertIn("<base branch>", out)
        self.assertIn("<One paragraph; see section 7.>", out)

    def test_filled_artifacts_pass_and_plain_lint_includes_review_when_it_exists(self):
        self.approve_chain("tasks")
        code, out, err = self.run_sdd("lint", SLUG)
        self.assertEqual(code, 0, out + err)
        self.assertNotIn("review.md", out)
        self.write_review()
        code, out, err = self.run_sdd("lint", SLUG)
        self.assertEqual(code, 0, out + err)
        self.assertIn("review.md: 0 errors", out)
        self.assertNotIn("placeholder", out)

    def test_angle_brackets_that_are_not_template_tokens_pass(self):
        greeting = SPEC.replace(
            "the system shall render a thumbnail for each attachment.",
            'the system shall render a thumbnail for each attachment and the caption "Hi, <first name>".',
        )
        self.write_spec(greeting)
        code, out, err = self.run_sdd("lint", SLUG, "spec")
        self.assertEqual(code, 0, out + err)
        self.assertNotIn("placeholder", out)
        self.mark_approved("spec")
        tagged = VALID_PLAN.replace("GET /invoices/:id.pdf unchanged.", "GET /invoices/:id.pdf unchanged; the body wraps each image in <figure>.")
        self.write_artifact("plan", tagged % {"slug": SLUG, "based_on": self.frontmatter("spec")["approved_hash"]})
        code, out, err = self.run_sdd("lint", SLUG, "plan")
        self.assertEqual(code, 0, out + err)

    def test_review_lint_requires_the_template_fields_and_sections(self):
        self.approve_chain("tasks")
        self.write_review()
        text = self.read_artifact("review").replace("effort: high\n", "").replace("## Reads well\n- InvoicePdf reads top to bottom\n\n", "")
        self.write_artifact("review", text)
        code, out, err = self.run_sdd("lint", SLUG, "review")
        self.assertEqual(code, 1)
        self.assertIn('missing frontmatter field "effort"', out)
        self.assertIn('missing section "Reads well"', out)


class ReviewAcceptanceTests(SddCase):
    def test_review_cannot_be_accepted_while_lint_reports_errors(self):
        self.approve_chain("tasks")
        self.write_review(TEMPLATES["review"])
        code, out, err = self.run_sdd("set-status", SLUG, "review", "accepted")
        self.assertEqual(code, 1)
        self.assertIn("placeholder", out)
        self.assertIn("lint", err)
        self.assertEqual(self.frontmatter("review")["status"], "open")
        self.write_review()
        code, out, err = self.run_sdd("set-status", SLUG, "review", "accepted")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self.frontmatter("review")["status"], "accepted")
        self.assertEqual(self.status_json()["artifacts"]["review"]["status"], "accepted")


if __name__ == "__main__":
    unittest.main()
