import unittest

from helpers import BRANCH, REVIEW_TEMPLATE, SLUG, SddCase, TASKS_VERIFIED_ELSEWHERE


class StatusPhaseTests(SddCase):
    def test_missing_spec_is_outline(self):
        code, out, err = self.run_sdd("status", SLUG)
        self.assertEqual(code, 0, err)
        self.assertIn("phase: 1. Outline", out)
        self.assertIn("next skill: sdd-outline", out)
        self.assertIn("spec", out)
        self.assertIn("missing", out)

    def test_draft_spec_is_outline_and_counts_markers(self):
        self.write_spec()
        self.write_artifact("spec", self.read_artifact("spec") + "\n## Open questions\n- [NEEDS CLARIFICATION: which customers?]\n- [NEEDS CLARIFICATION: retention?]\n")
        data = self.status_json()
        self.assertEqual(data["phase"], "1. Outline")
        self.assertEqual(data["skill"], "sdd-outline")
        self.assertEqual(data["clarifications"], 2)
        self.assertEqual(data["artifacts"]["spec"]["status"], "draft")
        self.assertFalse(data["artifacts"]["spec"]["changed"])

    def test_approved_spec_without_plan_is_plan(self):
        self.write_spec()
        self.mark_approved("spec")
        data = self.status_json()
        self.assertEqual(data["phase"], "2. Plan")
        self.assertEqual(data["skill"], "sdd-plan")
        self.assertFalse(data["artifacts"]["plan"]["exists"])

    def test_editing_an_approved_spec_marks_it_changed_and_the_plan_stale(self):
        self.write_spec()
        spec_hash = self.mark_approved("spec")
        self.write_plan(based_on=spec_hash)
        self.mark_approved("plan")
        self.write_artifact("spec", self.read_artifact("spec").replace("under 10 minutes", "under 5 minutes"))
        data = self.status_json()
        self.assertTrue(data["artifacts"]["spec"]["changed"])
        self.assertTrue(data["artifacts"]["plan"]["stale"])
        self.assertEqual(data["phase"], "1. Outline")
        self.assertEqual(data["skill"], "sdd-outline")
        code, out, err = self.run_sdd("status", SLUG)
        self.assertIn("changed", out)
        self.assertIn("stale", out)

    def test_plan_based_on_an_older_spec_hash_is_stale(self):
        self.write_spec()
        self.mark_approved("spec")
        self.write_plan(based_on="000000000000")
        self.mark_approved("plan")
        data = self.status_json()
        self.assertTrue(data["artifacts"]["plan"]["stale"])
        self.assertEqual(data["phase"], "2. Plan")

    def test_approved_plan_without_tasks_is_tasks(self):
        self.write_spec()
        spec_hash = self.mark_approved("spec")
        self.write_plan(based_on=spec_hash)
        self.mark_approved("plan")
        data = self.status_json()
        self.assertEqual(data["phase"], "3. Tasks")
        self.assertEqual(data["skill"], "sdd-task")

    def chain_to_tasks(self):
        self.write_spec()
        spec_hash = self.mark_approved("spec")
        self.write_plan(based_on=spec_hash)
        plan_hash = self.mark_approved("plan")
        self.write_tasks(based_on=plan_hash)
        self.mark_approved("tasks")

    def test_approved_or_in_progress_tasks_is_implement_with_progress(self):
        self.chain_to_tasks()
        data = self.status_json()
        self.assertEqual(data["phase"], "4. Implement")
        self.assertEqual(data["skill"], "sdd-implement")
        self.assertEqual(data["tasks"], {"done": 0, "total": 2, "next": "T001 Render a thumbnail for each attachment in the invoice PDF"})
        self.set_fields("tasks", status="in-progress")
        text = self.read_artifact("tasks").replace("- [ ] T001", "- [x] T001")
        text = text.replace("  - Done when: `pnpm test -- tests/invoices/pdf.test.ts` passes\n", "  - Done when: `pnpm test -- tests/invoices/pdf.test.ts` passes\n  - Evidence: 4 examples, 0 failures\n")
        self.write_artifact("tasks", text)
        data = self.status_json()
        self.assertEqual(data["phase"], "4. Implement")
        self.assertFalse(data["artifacts"]["tasks"]["changed"])
        self.assertEqual(data["tasks"]["done"], 1)
        self.assertEqual(data["tasks"]["next"], "T002 [P] Render a placeholder when a attachment file is missing")
        code, out, err = self.run_sdd("status", SLUG)
        self.assertIn("1/2 done", out)
        self.assertIn("next: T002", out)

    def test_close_out_is_the_next_item_after_the_last_task(self):
        self.chain_to_tasks()
        text = self.read_artifact("tasks").replace("- [ ] T001", "- [x] T001").replace("- [ ] T002", "- [x] T002")
        self.write_artifact("tasks", text)
        data = self.status_json()
        self.assertEqual(data["tasks"]["done"], 2)
        self.assertTrue(data["tasks"]["next"].startswith("P1 close"))

    def test_done_tasks_without_review_is_validate(self):
        self.chain_to_tasks()
        self.set_fields("tasks", status="done")
        data = self.status_json()
        self.assertEqual(data["phase"], "5. Validate")
        self.assertEqual(data["skill"], "sdd-review")

    def test_open_review_is_validate_and_accepted_review_is_done(self):
        self.chain_to_tasks()
        self.set_fields("tasks", status="done")
        self.write_artifact("review", REVIEW_TEMPLATE)
        data = self.status_json()
        self.assertEqual(data["phase"], "5. Validate")
        self.set_fields("review", status="accepted")
        data = self.status_json()
        self.assertEqual(data["phase"], "Done")
        self.assertIsNone(data["skill"])

    def test_changed_tasks_route_back_to_tasks(self):
        self.chain_to_tasks()
        self.set_fields("tasks", status="in-progress")
        self.write_artifact("tasks", self.read_artifact("tasks").replace("Render a placeholder", "Render a grey box"))
        data = self.status_json()
        self.assertTrue(data["artifacts"]["tasks"]["changed"])
        self.assertEqual(data["phase"], "3. Tasks")

    def test_slug_defaults_to_the_current_branch(self):
        self.write_spec()
        code, out, err = self.run_sdd("status")
        self.assertEqual(code, 0, err)
        self.assertIn("slug: %s" % SLUG, out)
        self.assertIn(BRANCH, out)

    def test_json_carries_hashes(self):
        self.write_spec()
        spec_hash = self.mark_approved("spec")
        data = self.status_json()
        self.assertEqual(data["artifacts"]["spec"]["approved_hash"], spec_hash)
        self.assertEqual(data["artifacts"]["spec"]["hash"], spec_hash)
        self.assertEqual(data["slug"], SLUG)


if __name__ == "__main__":
    unittest.main()


class VerifiedElsewhereHashTests(SddCase):
    def test_editing_an_entry_after_approval_marks_tasks_changed(self):
        self.approve_chain("plan")
        self.write_tasks(based_on=self.frontmatter("plan")["approved_hash"], text=TASKS_VERIFIED_ELSEWHERE % {"slug": SLUG, "based_on": self.frontmatter("plan")["approved_hash"]})
        code, out, err = self.run_sdd("approve", SLUG, "tasks")
        self.assertEqual(code, 0, out + err)
        self.assertFalse(self.status_json()["artifacts"]["tasks"]["changed"])
        self.write_artifact("tasks", self.read_artifact("tasks").replace("measured by the load test in CI", "measured by a soak test once a quarter"))
        self.assertTrue(self.status_json()["artifacts"]["tasks"]["changed"])
        self.assertEqual(self.status_json()["phase"], "3. Tasks")
