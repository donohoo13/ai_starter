import unittest

from helpers import SLUG, SddCase, VALID_PLAN


class LintPlanTests(SddCase):
    def setUp(self):
        super().setUp()
        self.write_spec()
        self.spec_hash = self.mark_approved("spec")

    def lint(self, text=None, based_on=None):
        based_on = self.spec_hash if based_on is None else based_on
        if text is None:
            self.write_plan(based_on=based_on)
        else:
            self.write_artifact("plan", text % {"slug": SLUG, "based_on": based_on})
        return self.run_sdd("lint", SLUG, "plan")

    def test_valid_plan_passes(self):
        code, out, err = self.lint()
        self.assertEqual(code, 0, out + err)
        self.assertIn("plan.md: 0 errors", out)

    def test_empty_based_on_passes_until_approval(self):
        code, out, err = self.lint(based_on="")
        self.assertEqual(code, 0, out + err)

    def test_missing_template_section_is_an_error(self):
        without_rollout = VALID_PLAN.replace("## Rollout\n1. Ship without a flag. Rollback: revert\n\n", "")
        code, out, err = self.lint(without_rollout)
        self.assertEqual(code, 1)
        self.assertIn('missing section "Rollout"', out)

    def test_every_requirement_needs_a_traceability_row_with_a_seam(self):
        without_inv = VALID_PLAN.replace("| INV-001 | InvoicePdf | service test on InvoicePdf | tests/invoices/pdf-placeholder.test.ts |\n", "")
        code, out, err = self.lint(without_inv)
        self.assertEqual(code, 1)
        self.assertIn("INV-001", out)
        self.assertIn("Traceability", out)
        empty_seam = VALID_PLAN.replace("| NFR-001 | InvoicePdf | request test on GET /invoices/:id.pdf |", "| NFR-001 | InvoicePdf |  |")
        code, out, err = self.lint(empty_seam)
        self.assertEqual(code, 1)
        self.assertIn("NFR-001", out)
        self.assertIn("seam", out.lower())

    def test_based_on_must_match_the_spec_approved_hash(self):
        code, out, err = self.lint(based_on="000000000000")
        self.assertEqual(code, 1)
        self.assertIn("based_on", out)
        self.assertIn(self.spec_hash, out)

    def test_spec_must_be_approved_and_unchanged(self):
        self.set_fields("spec", status="draft")
        code, out, err = self.lint()
        self.assertEqual(code, 1)
        self.assertIn("spec", out)
        self.assertIn("not approved", out)
        self.set_fields("spec", status="approved")
        self.write_artifact("spec", self.read_artifact("spec").replace("under 10 minutes", "under 9 minutes"))
        code, out, err = self.lint()
        self.assertEqual(code, 1)
        self.assertIn("changed since approval", out)


if __name__ == "__main__":
    unittest.main()
