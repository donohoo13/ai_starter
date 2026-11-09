import datetime
import unittest

from helpers import SLUG, SddCase


class DesignRequestTests(SddCase):
    def test_requesting_a_design_creates_design_md_on_the_approved_spec(self):
        spec_hash = self.approve_ui_spec()
        code, out, err = self.run_sdd("set-status", SLUG, "design", "requested")
        self.assertEqual(code, 0, out + err)
        fields = self.frontmatter("design")
        self.assertEqual(fields["status"], "requested")
        self.assertEqual(fields["based_on"], spec_hash)
        self.assertEqual(fields["slug"], SLUG)
        self.assertEqual(fields["title"], "Invoice thumbnails design")
        self.assertEqual(fields["updated"], datetime.date.today().isoformat())
        self.assertIn("\n# Invoice thumbnails design\n", self.read_artifact("design"))
        self.assertIn("## Prompt", self.read_artifact("design"))

    def test_a_stale_approved_design_can_be_requested_again(self):
        self.approve_ui_spec()
        self.request_design()
        self.record_design()
        self.run_sdd("approve", SLUG, "design")
        self.write_artifact("spec", self.read_artifact("spec").replace("under 10 minutes", "under 9 minutes"))
        self.run_sdd("approve", SLUG, "spec")
        code, out, err = self.run_sdd("set-status", SLUG, "design", "requested")
        self.assertEqual(code, 0, out + err)
        fields = self.frontmatter("design")
        self.assertEqual(fields["status"], "requested")
        self.assertEqual(fields["based_on"], self.frontmatter("spec")["approved_hash"])

    def test_a_design_cannot_be_requested_before_the_spec_is_approved(self):
        self.approve_ui_spec()
        self.set_fields("spec", status="draft")
        code, out, err = self.run_sdd("set-status", SLUG, "design", "requested")
        self.assertEqual(code, 1)
        self.assertIn("spec.md", err)
        self.assertFalse((self.folder() / "design.md").exists())

    def test_a_spec_without_ui_surfaces_gets_no_design(self):
        self.approve_chain("spec")
        code, out, err = self.run_sdd("set-status", SLUG, "design", "requested")
        self.assertEqual(code, 1)
        self.assertIn("UI surface", err)
        self.assertFalse((self.folder() / "design.md").exists())

    def test_rerequesting_refreshes_based_on_after_the_spec_is_reapproved(self):
        self.approve_ui_spec()
        self.request_design()
        self.write_artifact("spec", self.read_artifact("spec").replace("under 10 minutes", "under 9 minutes"))
        self.run_sdd("approve", SLUG, "spec")
        code, out, err = self.run_sdd("set-status", SLUG, "design", "requested")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self.frontmatter("design")["based_on"], self.frontmatter("spec")["approved_hash"])


class DesignSkipTests(SddCase):
    def test_skipping_records_who_the_covered_surfaces_and_the_spec_hash(self):
        spec_hash = self.approve_ui_spec("- UI-001: Settings screen (new)", "- UI-002: Invoice header (edited)")
        code, out, err = self.run_sdd("set-status", SLUG, "design", "skipped")
        self.assertEqual(code, 0, out + err)
        fields = self.frontmatter("design")
        self.assertEqual(fields["status"], "skipped")
        self.assertEqual(fields["decided_by"], "Test User")
        self.assertEqual(fields["surfaces"], "UI-001, UI-002")
        self.assertEqual(fields["based_on"], spec_hash)
        self.assertEqual(fields["updated"], datetime.date.today().isoformat())

    def test_cancelling_a_requested_design_records_a_skip(self):
        self.approve_ui_spec()
        self.request_design()
        code, out, err = self.run_sdd("set-status", SLUG, "design", "skipped")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self.frontmatter("design")["status"], "skipped")
        self.assertEqual(self.frontmatter("design")["surfaces"], "UI-001")

    def test_an_approved_design_cannot_be_skipped(self):
        self.approve_ui_spec()
        self.request_design()
        self.record_design()
        self.run_sdd("approve", SLUG, "design")
        code, out, err = self.run_sdd("set-status", SLUG, "design", "skipped")
        self.assertEqual(code, 1)
        self.assertIn("approved", err)
        self.assertEqual(self.frontmatter("design")["status"], "approved")

    def test_design_takes_only_requested_or_skipped(self):
        self.approve_ui_spec()
        code, out, err = self.run_sdd("set-status", SLUG, "design", "approved")
        self.assertEqual(code, 1)
        self.assertIn("requested", err)
        self.assertIn("skipped", err)


class DesignPhaseTests(SddCase):
    def test_a_requested_design_is_the_design_phase(self):
        self.approve_ui_spec()
        self.request_design()
        data = self.status_json()
        self.assertEqual(data["phase"], "2. Design")
        self.assertEqual(data["skill"], "sdd-design")
        self.assertEqual(data["artifacts"]["design"]["status"], "requested")
        code, out, err = self.run_sdd("status", SLUG)
        self.assertIn("design   requested", out)

    def test_a_skipped_design_moves_on_to_plan(self):
        self.approve_ui_spec()
        self.run_sdd("set-status", SLUG, "design", "skipped")
        data = self.status_json()
        self.assertEqual(data["phase"], "3. Plan")
        self.assertEqual(data["skill"], "sdd-plan")

    def test_an_approved_design_moves_on_to_plan(self):
        self.approve_ui_spec()
        self.request_design()
        self.record_design()
        self.run_sdd("approve", SLUG, "design")
        self.assertEqual(self.status_json()["phase"], "3. Plan")

    def test_an_approved_design_edited_afterwards_is_back_in_design(self):
        self.approve_ui_spec()
        self.request_design()
        self.record_design()
        self.run_sdd("approve", SLUG, "design")
        self.write_artifact("design", self.read_artifact("design").replace("## Not built\n- None", "## Not built\n- Bulk delete: no requirement covers it"))
        data = self.status_json()
        self.assertTrue(data["artifacts"]["design"]["changed"])
        self.assertEqual(data["phase"], "2. Design")

    def test_an_approved_design_goes_stale_when_the_spec_is_reapproved(self):
        self.approve_ui_spec()
        self.request_design()
        self.record_design()
        self.run_sdd("approve", SLUG, "design")
        self.write_artifact("spec", self.read_artifact("spec").replace("under 10 minutes", "under 9 minutes"))
        self.run_sdd("approve", SLUG, "spec")
        data = self.status_json()
        self.assertTrue(data["artifacts"]["design"]["stale"])
        self.assertEqual(data["phase"], "2. Design")

    def test_a_spec_with_no_design_keeps_the_old_sequence(self):
        self.approve_ui_spec()
        data = self.status_json()
        self.assertFalse(data["artifacts"]["design"]["exists"])
        self.assertEqual(data["phase"], "3. Plan")


class SkipCoverageTests(SddCase):
    def skip_then_reapprove_spec(self, edit):
        self.approve_ui_spec()
        self.run_sdd("set-status", SLUG, "design", "skipped")
        self.write_artifact("spec", edit(self.read_artifact("spec")))
        code, out, err = self.run_sdd("approve", SLUG, "spec")
        self.assertEqual(code, 0, out + err)

    def test_a_new_ui_surface_reoffers_the_design(self):
        self.skip_then_reapprove_spec(lambda spec: spec.replace("- UI-001: Settings screen (new)\n", "- UI-001: Settings screen (new)\n- UI-002: Profile screen (new)\n"))
        data = self.status_json()
        self.assertTrue(data["artifacts"]["design"]["stale"])
        self.assertEqual(data["phase"], "2. Design")
        self.assertEqual(data["skill"], "sdd-design")

    def test_a_reapproved_spec_with_no_new_surface_stays_skipped(self):
        self.skip_then_reapprove_spec(lambda spec: spec.replace("under 10 minutes", "under 9 minutes"))
        data = self.status_json()
        self.assertFalse(data["artifacts"]["design"]["stale"])
        self.assertEqual(data["phase"], "3. Plan")

    def test_skipping_again_covers_the_new_surface(self):
        self.skip_then_reapprove_spec(lambda spec: spec.replace("- UI-001: Settings screen (new)\n", "- UI-001: Settings screen (new)\n- UI-002: Profile screen (new)\n"))
        code, out, err = self.run_sdd("set-status", SLUG, "design", "skipped")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self.frontmatter("design")["surfaces"], "UI-001, UI-002")
        self.assertEqual(self.status_json()["phase"], "3. Plan")


class PlanOnDesignTests(SddCase):
    def approve_design(self):
        self.request_design()
        self.record_design()
        code, out, err = self.run_sdd("approve", SLUG, "design")
        assert code == 0, out + err

    def approve(self, name):
        code, out, err = self.run_sdd("approve", SLUG, name)
        self.assertEqual(code, 0, out + err)

    def test_plan_approval_records_the_design_hash(self):
        self.approve_ui_spec()
        self.approve_design()
        self.write_plan()
        self.approve("plan")
        self.assertEqual(self.frontmatter("plan")["based_on"], self.frontmatter("design")["approved_hash"])
        self.assertFalse(self.status_json()["artifacts"]["plan"]["stale"])

    def test_a_reapproved_design_stales_the_plan_and_tasks(self):
        self.approve_ui_spec()
        self.approve_design()
        self.write_plan()
        self.approve("plan")
        self.write_tasks()
        self.approve("tasks")
        self.write_artifact("design", self.read_artifact("design").replace("## Not built\n- None", "## Not built\n- Bulk delete: no requirement covers it"))
        self.approve("design")
        data = self.status_json()
        self.assertTrue(data["artifacts"]["plan"]["stale"])
        self.assertTrue(data["artifacts"]["tasks"]["stale"])
        self.assertEqual(data["phase"], "3. Plan")

    def test_reapproving_an_unchanged_design_against_a_new_spec_stales_the_plan_and_tasks(self):
        self.approve_ui_spec()
        self.approve_design()
        self.write_plan()
        self.approve("plan")
        self.write_tasks()
        self.approve("tasks")
        self.write_artifact("spec", self.read_artifact("spec").replace("under 10 minutes", "under 9 minutes"))
        self.approve("spec")
        self.set_fields("design", based_on=self.frontmatter("spec")["approved_hash"])
        self.approve("design")
        data = self.status_json()
        self.assertFalse(data["artifacts"]["design"]["changed"])
        self.assertFalse(data["artifacts"]["design"]["stale"])
        self.assertTrue(data["artifacts"]["plan"]["stale"])
        self.assertTrue(data["artifacts"]["tasks"]["stale"])
        self.assertEqual(data["phase"], "3. Plan")

    def test_an_approved_design_whose_based_on_is_edited_needs_reapproval(self):
        self.approve_ui_spec()
        self.approve_design()
        self.write_plan()
        self.approve("plan")
        self.write_artifact("spec", self.read_artifact("spec").replace("under 10 minutes", "under 9 minutes"))
        self.approve("spec")
        self.set_fields("design", based_on=self.frontmatter("spec")["approved_hash"])
        data = self.status_json()
        self.assertTrue(data["artifacts"]["design"]["changed"])
        self.assertEqual(data["phase"], "2. Design")

    def test_a_design_approved_after_the_plan_stales_the_plan(self):
        self.approve_ui_spec()
        self.write_plan()
        self.approve("plan")
        self.approve_design()
        data = self.status_json()
        self.assertTrue(data["artifacts"]["plan"]["stale"])
        self.assertEqual(data["phase"], "3. Plan")

    def test_a_stale_plan_is_refreshed_against_the_design_hash(self):
        self.approve_ui_spec()
        self.write_plan()
        self.approve("plan")
        self.approve_design()
        code, out, err = self.run_sdd("approve", SLUG, "plan")
        self.assertEqual(code, 1)
        self.assertIn("design.md approved_hash", out)
        self.set_fields("plan", based_on=self.frontmatter("design")["approved_hash"])
        self.approve("plan")
        self.assertEqual(self.status_json()["phase"], "4. Tasks")


if __name__ == "__main__":
    unittest.main()
