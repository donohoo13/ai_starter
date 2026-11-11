import datetime
import unittest

from formatted import FORMATTED_PLAN_BODY, FORMATTED_SPEC_BODY, FORMATTED_TASKS_BODY
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
        self.assertEqual(fields["approved_hash"], self.status_json()["artifacts"]["plan"]["hash"])

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

    def test_approving_a_recorded_design_records_its_hash_and_the_spec_hash(self):
        spec_hash = self.approve_ui_spec()
        self.request_design()
        self.record_design()
        code, out, err = self.run_sdd("approve", SLUG, "design")
        self.assertEqual(code, 0, out + err)
        fields = self.frontmatter("design")
        self.assertEqual(fields["status"], "approved")
        self.assertEqual(fields["approved_hash"], self.status_json()["artifacts"]["design"]["hash"])
        self.assertEqual(fields["based_on"], spec_hash)

    def test_a_design_with_an_unfilled_template_is_not_approved(self):
        self.approve_ui_spec()
        self.request_design()
        self.set_fields("design", link="https://claude.ai/artifact/abc123", version="v7", read="2026-11-09")
        code, out, err = self.run_sdd("approve", SLUG, "design")
        self.assertEqual(code, 1)
        self.assertIn("unfilled template placeholder", out)
        self.assertEqual(self.frontmatter("design")["status"], "requested")

    def test_a_design_missing_its_link_version_or_read_is_not_approved(self):
        self.approve_ui_spec()
        self.request_design()
        for missing in ("link", "version", "read"):
            with self.subTest(missing=missing):
                self.record_design(**{missing: ""})
                code, out, err = self.run_sdd("approve", SLUG, "design")
                self.assertEqual(code, 1)
                self.assertIn(missing, err)
                self.assertEqual(self.frontmatter("design")["status"], "requested")

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
        self.assertEqual(self.status_json()["phase"], "6. Validate")

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
        self.assertEqual(self.status_json()["phase"], "4. Tasks")

    def test_reapproving_an_unchanged_plan_against_a_new_spec_stales_the_tasks(self):
        self.approve_chain("tasks")
        self.write_artifact("spec", self.read_artifact("spec").replace("under 10 minutes", "under 9 minutes"))
        self.run_sdd("approve", SLUG, "spec")
        self.set_fields("plan", based_on=self.frontmatter("spec")["approved_hash"])
        code, out, err = self.run_sdd("approve", SLUG, "plan")
        self.assertEqual(code, 0, out + err)
        data = self.status_json()
        self.assertFalse(data["artifacts"]["plan"]["changed"])
        self.assertFalse(data["artifacts"]["plan"]["stale"])
        self.assertTrue(data["artifacts"]["tasks"]["stale"])
        self.assertEqual(data["phase"], "4. Tasks")

    def test_an_approved_plan_whose_based_on_is_edited_needs_reapproval(self):
        self.approve_chain("plan")
        self.write_artifact("spec", self.read_artifact("spec").replace("under 10 minutes", "under 9 minutes"))
        self.run_sdd("approve", SLUG, "spec")
        self.set_fields("plan", based_on=self.frontmatter("spec")["approved_hash"])
        data = self.status_json()
        self.assertTrue(data["artifacts"]["plan"]["changed"])
        self.assertEqual(data["phase"], "3. Plan")


class ChainCase(SddCase):
    def hash_as_written(self, name, based_on=None):
        """The hash an earlier helper recorded: over the body byte for byte, and over based_on once it was covered."""
        covered = self.cli.body_as_written(self.read_artifact(name))
        if based_on is not None:
            covered += "based_on: %s\n" % based_on
        return self.cli.digest(covered)

    def assert_chain_is_current(self, *names):
        data = self.status_json()
        for name in names:
            with self.subTest(artifact=name):
                self.assertFalse(data["artifacts"][name]["changed"])
                self.assertFalse(data["artifacts"][name]["stale"])
        self.assertEqual(data["phase"], "5. Implement")


class ReformattedArtifactTests(ChainCase):
    def approve_then_reformat_chain(self):
        """Approve spec, plan and tasks, then rewrite each body as the pre-commit hook does when the artifact is committed."""
        self.approve_chain("tasks")
        self.replace_body("spec", FORMATTED_SPEC_BODY)
        self.replace_body("plan", FORMATTED_PLAN_BODY)
        self.replace_body("tasks", FORMATTED_TASKS_BODY)

    def test_artifacts_a_formatter_rewrote_stay_approved(self):
        self.approve_then_reformat_chain()
        self.assert_chain_is_current("spec", "plan", "tasks")

    def test_a_plan_approves_on_a_spec_a_formatter_rewrote(self):
        self.approve_chain("spec")
        self.replace_body("spec", FORMATTED_SPEC_BODY)
        self.write_plan()
        code, out, err = self.run_sdd("approve", SLUG, "plan")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self.frontmatter("plan")["based_on"], self.frontmatter("spec")["approved_hash"])

    def test_an_edit_to_a_reformatted_artifact_still_needs_reapproval(self):
        self.approve_then_reformat_chain()
        self.replace_body("spec", FORMATTED_SPEC_BODY.replace("under 10 minutes", "under 5 minutes"))
        data = self.status_json()
        self.assertTrue(data["artifacts"]["spec"]["changed"])
        self.assertTrue(data["artifacts"]["plan"]["stale"])
        self.assertEqual(data["phase"], "1. Outline")


class EarlierApprovalTests(ChainCase):
    def test_approvals_recorded_as_a_body_only_hash_stay_current(self):
        self.approve_chain("tasks")
        plan_hash = self.hash_as_written("plan")
        self.set_fields("plan", approved_hash=plan_hash)
        self.set_fields("tasks", based_on=plan_hash, approved_hash=self.hash_as_written("tasks"))
        self.assert_chain_is_current("plan", "tasks")

    def test_approvals_recorded_before_the_hash_ignored_formatting_stay_current(self):
        self.approve_chain("tasks")
        spec_hash = self.hash_as_written("spec")
        plan_hash = self.hash_as_written("plan", based_on=spec_hash)
        self.set_fields("spec", approved_hash=spec_hash)
        self.set_fields("plan", based_on=spec_hash, approved_hash=plan_hash)
        self.set_fields("tasks", based_on=plan_hash, approved_hash=self.hash_as_written("tasks", based_on=plan_hash))
        self.assert_chain_is_current("spec", "plan", "tasks")

    def test_an_edit_to_an_artifact_approved_before_the_hash_ignored_formatting_needs_reapproval(self):
        self.approve_chain("plan")
        spec_hash = self.frontmatter("spec")["approved_hash"]
        self.set_fields("plan", approved_hash=self.hash_as_written("plan", based_on=spec_hash))
        self.write_artifact("plan", self.read_artifact("plan").replace("pdf-lib 1.17", "pdf-lib 2.0"))
        data = self.status_json()
        self.assertTrue(data["artifacts"]["plan"]["changed"])
        self.assertEqual(data["phase"], "3. Plan")


if __name__ == "__main__":
    unittest.main()
