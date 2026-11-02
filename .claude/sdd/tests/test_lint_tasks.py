import unittest

from helpers import SLUG, SddCase, TASKS_VERIFIED_ELSEWHERE, VALID_TASKS


class LintTasksTests(SddCase):
    def setUp(self):
        super().setUp()
        self.write_spec()
        spec_hash = self.mark_approved("spec")
        self.write_plan(based_on=spec_hash)
        self.plan_hash = self.mark_approved("plan")

    def lint(self, text=None, based_on=None):
        based_on = self.plan_hash if based_on is None else based_on
        self.write_tasks(based_on=based_on, text=None if text is None else text % {"slug": SLUG, "based_on": based_on})
        return self.run_sdd("lint", SLUG, "tasks")

    def test_valid_tasks_pass(self):
        code, out, err = self.lint()
        self.assertEqual(code, 0, out + err)
        self.assertIn("tasks.md: 0 errors, 0 warnings", out)

    def test_every_task_needs_requirements_seam_files_and_done_when(self):
        without_seam = VALID_TASKS.replace("  - Seam: request test on GET /invoices/:id.pdf\n", "")
        code, out, err = self.lint(without_seam)
        self.assertEqual(code, 1)
        self.assertIn("T001", out)
        self.assertIn("Seam", out)

    def test_referenced_ids_must_exist_in_the_spec(self):
        unknown = VALID_TASKS.replace("  - Requirements: FR-001, INV-001", "  - Requirements: FR-001, FR-009")
        code, out, err = self.lint(unknown)
        self.assertEqual(code, 1)
        self.assertIn("FR-009", out)

    def test_every_fr_needs_a_task(self):
        no_fr = VALID_TASKS.replace("  - Requirements: FR-001, NFR-001", "  - Requirements: NFR-001").replace("  - Requirements: FR-001, INV-001", "  - Requirements: INV-001")
        code, out, err = self.lint(no_fr)
        self.assertEqual(code, 1)
        self.assertIn("ERROR", out)
        self.assertIn("FR-001 has no task", out)

    def test_an_nfr_or_inv_without_a_task_or_entry_is_an_error(self):
        no_inv = VALID_TASKS.replace("  - Requirements: FR-001, INV-001", "  - Requirements: FR-001")
        code, out, err = self.lint(no_inv)
        self.assertEqual(code, 1)
        self.assertIn("ERROR", out)
        self.assertIn("INV-001 has no task and no Verified elsewhere entry", out)

    def test_a_verified_elsewhere_entry_covers_an_nfr(self):
        code, out, err = self.lint(TASKS_VERIFIED_ELSEWHERE)
        self.assertEqual(code, 0, out + err)
        self.assertIn("tasks.md: 0 errors, 0 warnings", out)

    def test_a_verified_elsewhere_entry_does_not_cover_an_fr(self):
        fr_elsewhere = VALID_TASKS.replace("  - Requirements: FR-001, NFR-001", "  - Requirements: NFR-001").replace(
            "  - Requirements: FR-001, INV-001", "  - Requirements: INV-001"
        ).replace("## Verified elsewhere\n- None", "## Verified elsewhere\n- FR-001: checked by hand. Decided by Test User.")
        code, out, err = self.lint(fr_elsewhere)
        self.assertEqual(code, 1)
        self.assertIn("FR-001 has no task", out)

    def test_a_verified_elsewhere_entry_with_an_unknown_id_is_an_error(self):
        unknown = TASKS_VERIFIED_ELSEWHERE.replace("- NFR-001: measured", "- NFR-009: measured")
        code, out, err = self.lint(unknown)
        self.assertEqual(code, 1)
        self.assertIn("Verified elsewhere names unknown requirement NFR-009", out)

    def test_every_slice_ends_with_a_close_out(self):
        no_close = VALID_TASKS.replace("- [ ] P1 close: full suite green, changes staged by explicit path, commit message proposed, user committed\n", "")
        code, out, err = self.lint(no_close)
        self.assertEqual(code, 1)
        self.assertIn("P1", out)
        self.assertIn("close-out", out)

    def test_parallel_tasks_share_no_files_and_no_dependency(self):
        both_parallel = VALID_TASKS.replace("- [ ] T001 Render", "- [ ] T001 [P] Render")
        shared = both_parallel.replace("  - Files: src/invoices/pdf-placeholder.ts, tests/invoices/pdf-placeholder.test.ts", "  - Files: src/invoices/pdf.ts, tests/invoices/pdf-placeholder.test.ts")
        code, out, err = self.lint(shared)
        self.assertEqual(code, 1)
        self.assertIn("src/invoices/pdf.ts", out)
        self.assertIn("[P]", out)
        dependent = both_parallel.replace("  - Seam: service test on InvoicePdf\n", "  - Seam: service test on InvoicePdf\n  - Depends on: T001\n")
        code, out, err = self.lint(dependent)
        self.assertEqual(code, 1)
        self.assertIn("T002", out)
        self.assertIn("depends on", out.lower())

    def test_test_only_task_warns(self):
        tests_only = VALID_TASKS.replace("  - Files: src/invoices/pdf.ts, tests/invoices/pdf.test.ts", "  - Files: tests/invoices/pdf.test.ts, tests/invoices/model.test.ts")
        code, out, err = self.lint(tests_only)
        self.assertEqual(code, 0, out)
        self.assertIn("WARN", out)
        self.assertIn("only test files", out)

    def test_duplicate_task_ids_are_an_error(self):
        duplicate = VALID_TASKS.replace("- [ ] T002 [P]", "- [ ] T001 [P]")
        code, out, err = self.lint(duplicate)
        self.assertEqual(code, 1)
        self.assertIn("duplicate task id T001", out)

    def test_based_on_must_match_the_plan_and_the_plan_must_be_approved(self):
        code, out, err = self.lint(based_on="000000000000")
        self.assertEqual(code, 1)
        self.assertIn("based_on", out)
        self.set_fields("plan", status="draft")
        code, out, err = self.lint()
        self.assertEqual(code, 1)
        self.assertIn("plan", out)
        self.assertIn("not approved", out)


if __name__ == "__main__":
    unittest.main()


class RemovedRequirementTests(SddCase):
    def test_a_task_may_not_cite_a_removed_requirement(self):
        self.write_spec()
        spec = self.read_artifact("spec").replace(
            "### Non-functional\n",
            "- FR-002: Removed. Superseded by FR-001.\n\n### Non-functional\n",
        )
        self.write_artifact("spec", spec)
        spec_hash = self.mark_approved("spec")
        self.write_plan(based_on=spec_hash)
        plan_hash = self.mark_approved("plan")
        self.write_tasks(based_on=plan_hash)
        code, out, err = self.run_sdd("lint", SLUG, "tasks")
        self.assertEqual(code, 0, out)
        citing = self.read_artifact("tasks").replace("  - Requirements: FR-001, INV-001", "  - Requirements: FR-002, INV-001")
        self.write_artifact("tasks", citing)
        code, out, err = self.run_sdd("lint", SLUG, "tasks")
        self.assertEqual(code, 1)
        self.assertIn("removed requirement FR-002", out)
        self.write_artifact("tasks", self.read_artifact("tasks").replace("  - Requirements: FR-002, INV-001", "  - Requirements: FR-001, INV-001").replace(
            "## Verified elsewhere\n- None", "## Verified elsewhere\n- FR-002: covered upstream. Decided by Test User."
        ))
        code, out, err = self.run_sdd("lint", SLUG, "tasks")
        self.assertEqual(code, 1)
        self.assertIn("Verified elsewhere names removed requirement FR-002", out)
