import datetime
import unittest

from helpers import SLUG, SddCase


class ApproveTests(SddCase):
    def test_approving_a_clean_spec_records_status_hash_and_date(self):
        self.write_spec()
        code, out, err = self.run_sdd("approve", SLUG, "spec")
        self.assertEqual(code, 0, err)
        fields = self.frontmatter("spec")
        self.assertEqual(fields["status"], "approved")
        self.assertEqual(fields["approved_hash"], self.cli.content_hash(self.read_artifact("spec")))
        self.assertEqual(fields["updated"], datetime.date.today().isoformat())
        self.assertIn(fields["approved_hash"], out)
        self.assertNotIn("based_on", fields)

    def test_a_spec_with_a_marker_cannot_be_approved(self):
        self.write_spec()
        self.write_artifact("spec", self.read_artifact("spec") + "\n## Open questions\n- [NEEDS CLARIFICATION: retention?]\n")
        code, out, err = self.run_sdd("approve", SLUG, "spec")
        self.assertEqual(code, 1)
        self.assertIn("NEEDS CLARIFICATION", out)
        self.assertIn("lint", err)
        self.assertEqual(self.frontmatter("spec")["status"], "draft")

    def test_plan_needs_an_approved_current_spec(self):
        self.write_spec()
        self.write_plan()
        code, out, err = self.run_sdd("approve", SLUG, "plan")
        self.assertEqual(code, 1)
        self.assertIn("spec.md is not approved", out + err)
        code, out, err = self.run_sdd("approve", SLUG, "spec")
        self.assertEqual(code, 0, err)
        code, out, err = self.run_sdd("approve", SLUG, "plan")
        self.assertEqual(code, 0, err)
        fields = self.frontmatter("plan")
        self.assertEqual(fields["status"], "approved")
        self.assertEqual(fields["based_on"], self.frontmatter("spec")["approved_hash"])
        self.assertEqual(fields["approved_hash"], self.cli.content_hash(self.read_artifact("plan")))

    def test_plan_is_refused_when_the_spec_changed_since_approval(self):
        self.approve_chain("spec")
        self.write_artifact("spec", self.read_artifact("spec").replace("under 10 minutes", "under 9 minutes"))
        self.write_plan()
        code, out, err = self.run_sdd("approve", SLUG, "plan")
        self.assertEqual(code, 1)
        self.assertIn("changed since approval", out + err)

    def test_tasks_record_the_plan_hash(self):
        self.approve_chain("tasks")
        fields = self.frontmatter("tasks")
        self.assertEqual(fields["status"], "approved")
        self.assertEqual(fields["based_on"], self.frontmatter("plan")["approved_hash"])

    def test_reapproving_a_changed_spec_records_the_new_hash(self):
        self.approve_chain("spec")
        old = self.frontmatter("spec")["approved_hash"]
        self.write_artifact("spec", self.read_artifact("spec").replace("under 10 minutes", "under 9 minutes"))
        code, out, err = self.run_sdd("approve", SLUG, "spec")
        self.assertEqual(code, 0, err)
        new = self.frontmatter("spec")["approved_hash"]
        self.assertNotEqual(old, new)
        self.assertFalse(self.status_json()["artifacts"]["spec"]["changed"])

    def test_missing_artifact_is_a_refusal(self):
        self.write_spec()
        code, out, err = self.run_sdd("approve", SLUG, "plan")
        self.assertEqual(code, 1)
        self.assertIn("plan.md", out + err)


class SetStatusTests(SddCase):
    def test_tasks_move_to_in_progress_only_from_approved(self):
        self.approve_chain("plan")
        self.write_tasks(based_on=self.frontmatter("plan")["approved_hash"])
        code, out, err = self.run_sdd("set-status", SLUG, "tasks", "in-progress")
        self.assertEqual(code, 1)
        self.assertIn("approved", err)
        self.run_sdd("approve", SLUG, "tasks")
        code, out, err = self.run_sdd("set-status", SLUG, "tasks", "in-progress")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.frontmatter("tasks")["status"], "in-progress")
        self.assertEqual(self.frontmatter("tasks")["updated"], datetime.date.today().isoformat())

    def test_done_is_refused_while_an_item_is_unchecked(self):
        self.approve_chain("tasks")
        self.run_sdd("set-status", SLUG, "tasks", "in-progress")
        text = self.read_artifact("tasks").replace("- [ ] T001", "- [x] T001").replace("- [ ] T002", "- [x] T002")
        self.write_artifact("tasks", text)
        code, out, err = self.run_sdd("set-status", SLUG, "tasks", "done")
        self.assertEqual(code, 1)
        self.assertIn("P1 close", err)
        self.assertEqual(self.frontmatter("tasks")["status"], "in-progress")
        self.write_artifact("tasks", text.replace("- [ ] P1 close", "- [x] P1 close"))
        code, out, err = self.run_sdd("set-status", SLUG, "tasks", "done")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.frontmatter("tasks")["status"], "done")
        self.assertEqual(self.status_json()["phase"], "5. Validate")

    def test_review_moves_to_accepted(self):
        self.approve_chain("tasks")
        code, out, err = self.run_sdd("set-status", SLUG, "review", "accepted")
        self.assertEqual(code, 1)
        self.assertIn("review.md", err)
        self.write_review()
        code, out, err = self.run_sdd("set-status", SLUG, "review", "accepted")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.frontmatter("review")["status"], "accepted")

    def test_rejects_statuses_that_do_not_belong_to_the_artifact(self):
        self.approve_chain("tasks")
        code, out, err = self.run_sdd("set-status", SLUG, "tasks", "accepted")
        self.assertEqual(code, 1)
        self.assertIn("accepted", err)
        code, out, err = self.run_sdd("set-status", SLUG, "review", "done")
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()


class StaleUpstreamTests(SddCase):
    def make_plan_stale(self):
        self.approve_chain("plan")
        self.write_artifact("spec", self.read_artifact("spec").replace("under 10 minutes", "under 9 minutes"))
        code, out, err = self.run_sdd("approve", SLUG, "spec")
        self.assertEqual(code, 0, err)
        self.assertTrue(self.status_json()["artifacts"]["plan"]["stale"])

    def test_tasks_cannot_be_approved_while_the_plan_is_stale(self):
        self.make_plan_stale()
        self.write_tasks(based_on=self.frontmatter("plan")["approved_hash"])
        code, out, err = self.run_sdd("lint", SLUG, "tasks")
        self.assertEqual(code, 1)
        self.assertIn("plan.md is stale", out)
        code, out, err = self.run_sdd("approve", SLUG, "tasks")
        self.assertEqual(code, 1)
        self.assertEqual(self.frontmatter("tasks")["status"], "draft")

    def test_refreshing_based_on_lets_a_stale_plan_be_reapproved(self):
        self.make_plan_stale()
        code, out, err = self.run_sdd("approve", SLUG, "plan")
        self.assertEqual(code, 1)
        self.assertIn("based_on", out)
        self.set_fields("plan", based_on=self.frontmatter("spec")["approved_hash"])
        code, out, err = self.run_sdd("approve", SLUG, "plan")
        self.assertEqual(code, 0, out + err)
        self.assertFalse(self.status_json()["artifacts"]["plan"]["stale"])
        self.assertEqual(self.status_json()["phase"], "3. Tasks")
