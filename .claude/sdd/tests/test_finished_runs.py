import unittest

from helpers import SLUG, SddCase

REOPEN_COMMAND = "sdd set-status %s review open" % SLUG

LATE_TASK = """- [ ] T003 Cap each thumbnail at 200 px
  - Requirements: FR-001
  - Seam: request test on GET /invoices/:id.pdf
  - Files: src/invoices/pdf.ts, tests/invoices/pdf.test.ts
  - Done when: `pnpm test -- tests/invoices/pdf.test.ts` passes
"""


class FinishedRunCase(SddCase):
    """A run driven through the CLI to done, and the late changes a finished run takes."""

    def sdd(self, *argv):
        code, out, err = self.run_sdd(*argv)
        self.assertEqual(code, 0, out + err)
        return out

    def set_boxes(self, mark, *items):
        text = self.read_artifact("tasks")
        for item in items:
            text = text.replace("- [ ] " + item, "- [%s] %s" % (mark, item)).replace("- [x] " + item, "- [%s] %s" % (mark, item))
        self.write_artifact("tasks", text)

    def build_to_done(self):
        self.approve_chain("tasks")
        self.sdd("set-status", SLUG, "tasks", "in-progress")
        self.set_boxes("x", "T001", "T002", "P1 close")
        self.sdd("set-status", SLUG, "tasks", "done")

    def accept_review(self):
        self.write_review()
        self.sdd("set-status", SLUG, "review", "accepted")

    def add_late_task(self):
        """Revise the task list as `sdd-task` does after a late change: one new task in the built slice."""
        self.write_artifact("tasks", self.read_artifact("tasks").replace("- [x] P1 close", LATE_TASK + "- [x] P1 close"))

    def rebuild_after_late_task(self):
        self.add_late_task()
        self.set_boxes(" ", "P1 close")
        self.sdd("approve", SLUG, "tasks")
        self.sdd("set-status", SLUG, "tasks", "in-progress")
        self.set_boxes("x", "T003", "P1 close")
        self.sdd("set-status", SLUG, "tasks", "done")


class ClosedSliceTests(FinishedRunCase):
    def test_an_unchecked_task_under_a_checked_close_out_is_a_lint_error(self):
        self.approve_chain("tasks")
        self.set_boxes("x", "T001", "P1 close")
        code, out, err = self.run_sdd("lint", SLUG, "tasks")
        self.assertEqual(code, 1, out + err)
        self.assertIn("slice P1 is closed with unchecked work: T002", out)
        self.assertIn("uncheck its close-out so sdd-implement builds it", out)

    def test_a_slice_still_being_built_passes(self):
        self.approve_chain("tasks")
        self.set_boxes("x", "T001")
        self.assertIn("tasks.md: 0 errors", self.sdd("lint", SLUG, "tasks"))

    def test_a_task_added_to_a_closed_slice_is_approved_only_once_the_slice_reopens(self):
        self.build_to_done()
        self.add_late_task()
        code, out, err = self.run_sdd("approve", SLUG, "tasks")
        self.assertEqual(code, 1, out + err)
        self.assertIn("unchecked work: T003", out)
        self.assertEqual(self.frontmatter("tasks")["status"], "done")
        self.set_boxes(" ", "P1 close")
        self.sdd("approve", SLUG, "tasks")
        data = self.status_json()
        self.assertEqual(data["phase"], "5. Implement")
        self.assertEqual(data["tasks"]["next"], "T003 Cap each thumbnail at 200 px")


class AcceptedReviewTests(FinishedRunCase):
    def test_accepting_a_review_records_the_tasks_it_covers(self):
        self.build_to_done()
        self.accept_review()
        self.assertEqual(self.frontmatter("review")["based_on"], self.frontmatter("tasks")["approved_hash"])
        data = self.status_json()
        self.assertFalse(data["artifacts"]["review"]["stale"])
        self.assertEqual(data["phase"], "Done")

    def test_reapproved_tasks_stale_the_accepted_review_and_return_the_run_to_validate(self):
        self.build_to_done()
        self.accept_review()
        self.rebuild_after_late_task()
        data = self.status_json()
        self.assertTrue(data["artifacts"]["review"]["stale"])
        self.assertEqual(data["phase"], "6. Validate")
        self.assertEqual(data["skill"], "sdd-review")
        self.assertIn(REOPEN_COMMAND, data["note"])
        self.assertIn("run every review again", data["note"])
        out = self.sdd("status", SLUG)
        self.assertRegex(out, r"review +accepted +based_on \w{12} +stale")
        self.assertIn("note: ", out)

    def test_an_accepted_review_with_no_recorded_tasks_stays_done(self):
        self.build_to_done()
        self.write_review()
        self.set_fields("review", status="accepted")
        self.assertEqual(self.status_json()["phase"], "Done")


class ReopenTests(FinishedRunCase):
    def test_done_names_the_reopen_command(self):
        self.build_to_done()
        self.assertIsNone(self.status_json()["note"])
        self.accept_review()
        note = self.status_json()["note"]
        self.assertIn(REOPEN_COMMAND, note)
        self.assertIn("sdd-outline", note)
        out = self.sdd("status", SLUG)
        self.assertRegex(out, r"review +accepted +based_on \w{12} +current")
        self.assertIn("note: " + note, out)

    def test_reopening_an_accepted_review_returns_the_run_to_validate(self):
        self.build_to_done()
        self.accept_review()
        self.assertIn("review.md is now open", self.sdd("set-status", SLUG, "review", "open"))
        self.assertEqual(self.frontmatter("review")["status"], "open")
        data = self.status_json()
        self.assertEqual(data["phase"], "6. Validate")
        self.assertEqual(data["skill"], "sdd-review")
        self.assertIn("reopened", data["note"])
        self.assertIn("accept it again", data["note"])
        self.sdd("set-status", SLUG, "review", "accepted")
        self.assertEqual(self.status_json()["phase"], "Done")

    def test_a_review_reopened_before_the_tasks_changed_is_reviewed_again_in_full(self):
        self.build_to_done()
        self.accept_review()
        self.sdd("set-status", SLUG, "review", "open")
        self.rebuild_after_late_task()
        data = self.status_json()
        self.assertEqual(data["phase"], "6. Validate")
        self.assertTrue(data["artifacts"]["review"]["stale"])
        self.assertIn("run every review again", data["note"])
        self.sdd("set-status", SLUG, "review", "accepted")
        self.assertEqual(self.frontmatter("review")["based_on"], self.frontmatter("tasks")["approved_hash"])
        self.assertEqual(self.status_json()["phase"], "Done")

    def test_only_an_accepted_review_reopens(self):
        self.build_to_done()
        self.write_review()
        code, out, err = self.run_sdd("set-status", SLUG, "review", "open")
        self.assertEqual(code, 1)
        self.assertIn("it must be accepted before open", err)

    def test_a_stale_accepted_review_is_accepted_again_only_through_a_reopen(self):
        self.build_to_done()
        self.accept_review()
        self.rebuild_after_late_task()
        code, out, err = self.run_sdd("set-status", SLUG, "review", "accepted")
        self.assertEqual(code, 1)
        self.assertIn("it must be open before accepted", err)


if __name__ == "__main__":
    unittest.main()
