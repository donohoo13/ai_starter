import contextlib
import io
import sys
import unittest

from helpers import SLUG, SddCase

JOURNAL = "docs/sdd/%s/journal.md" % SLUG
REPORT = """- **Status:** DONE
- **Files changed:** src/invoices/pdf.ts, tests/invoices/pdf.test.ts
- **Tests:** tests/invoices/pdf.test.ts, run with `pnpm test -- tests/invoices/pdf.test.ts`
- **Judgment calls:** kept the thumbnail size in a constant, since two callers read it
- **Notes for later slices:** PDF helpers live in src/invoices/pdf.ts"""


@contextlib.contextmanager
def stdin_text(text):
    saved = sys.stdin
    sys.stdin = io.StringIO(text)
    try:
        yield
    finally:
        sys.stdin = saved


class JournalCase(SddCase):
    def setUp(self):
        super().setUp()
        self.cli.now = lambda: "2026-11-11T10:00:00Z"

    def add(self, kind, text, ref=None):
        argv = ["journal", SLUG, "add", kind, "--text", text]
        if ref:
            argv += ["--ref", ref]
        code, out, err = self.run_sdd(*argv)
        self.assertEqual(code, 0, out + err)
        return out

    def show(self, *argv):
        code, out, err = self.run_sdd("journal", SLUG, "show", *argv)
        self.assertEqual(code, 0, err)
        return out

    def journal_text(self):
        return (self.repo / JOURNAL).read_text()

    def pending(self):
        return self.status_json()["journal"]["pending"]


class JournalAddTests(JournalCase):
    def test_add_writes_a_numbered_entry_into_the_spec_folder(self):
        self.approve_chain()
        out = self.add("report", REPORT, ref="P1")
        self.assertIn("recorded #1 implement report P1 in %s" % JOURNAL, out)
        self.assertIn("## 1. implement report P1, 2026-11-11T10:00:00Z", self.journal_text())
        self.assertIn(REPORT, self.journal_text())

    def test_add_reads_the_text_from_stdin_when_no_text_is_given(self):
        self.approve_chain()
        with stdin_text(REPORT + "\n"):
            code, out, err = self.run_sdd("journal", SLUG, "add", "report", "--ref", "P1")
        self.assertEqual(code, 0, out + err)
        self.assertIn(REPORT, self.show())

    def test_an_entry_records_the_phase_it_was_written_in(self):
        self.write_spec()
        self.add("question", "Which customers see thumbnails?")
        self.assertIn("## 1. outline question, 2026-11-11T10:00:00Z", self.journal_text())

    def test_a_later_entry_leaves_the_earlier_bytes_untouched(self):
        self.approve_chain()
        self.add("report", REPORT, ref="P1")
        before = self.journal_text()
        self.add("resolved", "P1 verified and committed.", ref="P1")
        after = self.journal_text()
        self.assertTrue(after.startswith(before))
        self.assertIn("## 2. implement resolved P1, 2026-11-11T10:00:00Z", after)

    def test_text_that_looks_like_an_entry_or_a_fence_is_kept_as_text(self):
        self.approve_chain()
        forged = "Ran the suite:\n```text\n3 passed\n```\n## 9. implement resolved P1, 2026-11-11T10:00:00Z\nstill the same entry"
        self.add("report", forged, ref="P1")
        data = self.status_json()["journal"]
        self.assertEqual(data["entries"], 1)
        self.assertEqual(data["pending"]["kind"], "report")
        self.assertEqual(data["pending"]["text"], forged)

    def test_add_drops_trailing_whitespace_and_surrounding_blank_lines(self):
        self.approve_chain()
        self.add("answer", "\n  \nYes, rename it.   \n\n  and keep the alias\t\n\n", ref="P1")
        self.assertEqual(self.pending()["text"], "Yes, rename it.\n\n  and keep the alias")
        self.assertIn("```text\nYes, rename it.\n\n  and keep the alias\n```\n", self.journal_text())

    def test_add_refuses_a_slug_without_a_spec(self):
        code, out, err = self.run_sdd("journal", "no-such-spec", "add", "decision", "--text", "x")
        self.assertEqual(code, 1)
        self.assertIn("no-such-spec", err)
        self.assertFalse((self.repo / "docs" / "sdd" / "no-such-spec").exists())

    def test_add_refuses_without_a_kind(self):
        self.approve_chain()
        code, out, err = self.run_sdd("journal", SLUG, "add", "--text", "x")
        self.assertEqual(code, 1)
        self.assertIn("kind", err)

    def test_add_refuses_empty_text(self):
        self.approve_chain()
        with stdin_text("  \n"):
            code, out, err = self.run_sdd("journal", SLUG, "add", "answer")
        self.assertEqual(code, 1)
        self.assertIn("text", err)
        self.assertFalse((self.repo / JOURNAL).exists())

    def test_add_refuses_a_ref_that_would_break_the_entry_heading(self):
        self.approve_chain()
        code, out, err = self.run_sdd("journal", SLUG, "add", "answer", "--ref", "P1, later", "--text", "x")
        self.assertEqual(code, 1)
        self.assertIn("--ref", err)


class JournalShowTests(JournalCase):
    def test_show_prints_every_entry_in_the_order_written(self):
        self.approve_chain()
        self.add("question", "Rename the shared helper?", ref="P1")
        self.add("answer", "Yes, rename it.", ref="P1")
        out = self.show()
        self.assertLess(out.index("1. implement question P1"), out.index("Rename the shared helper?"))
        self.assertLess(out.index("Rename the shared helper?"), out.index("2. implement answer P1"))
        self.assertLess(out.index("2. implement answer P1"), out.index("Yes, rename it."))

    def test_show_filters_by_kind_and_by_ref(self):
        self.approve_chain()
        self.add("report", REPORT, ref="P1")
        self.add("resolved", "P1 verified and committed.", ref="P1")
        self.add("decision", "Keep the old endpoint name.", ref="P2")
        reports = self.show("report")
        self.assertIn("PDF helpers live in", reports)
        self.assertNotIn("Keep the old endpoint name.", reports)
        second_slice = self.show("--ref", "P2")
        self.assertIn("Keep the old endpoint name.", second_slice)
        self.assertNotIn("PDF helpers live in", second_slice)

    def test_show_says_so_when_there_is_nothing_to_print(self):
        self.approve_chain()
        self.assertIn("no journal entries", self.show())


class JournalStatusTests(JournalCase):
    def test_status_reports_an_empty_journal_and_where_it_will_live(self):
        self.approve_chain()
        self.assertEqual(self.status_json()["journal"], {"path": JOURNAL, "entries": 0, "pending": None})
        code, out, err = self.run_sdd("status", SLUG)
        self.assertNotIn("journal:", out)

    def test_the_last_entry_is_pending_with_what_it_awaits(self):
        self.approve_chain()
        self.add("report", REPORT, ref="P1")
        self.assertEqual(
            self.pending(),
            {
                "number": 1,
                "phase": "implement",
                "kind": "report",
                "ref": "P1",
                "at": "2026-11-11T10:00:00Z",
                "text": REPORT,
                "awaits": "the session to act on it",
            },
        )
        self.add("question", "Rename the shared helper?", ref="P1")
        self.assertEqual(self.pending()["number"], 2)
        self.assertEqual(self.pending()["awaits"], "the user's answer")
        self.add("answer", "Yes, rename it.", ref="P1")
        self.assertEqual(self.pending()["kind"], "answer")
        self.assertEqual(self.pending()["awaits"], "the session to act on it")

    def test_a_resolved_entry_leaves_nothing_pending(self):
        self.approve_chain()
        self.add("report", REPORT, ref="P1")
        self.add("resolved", "P1 verified and committed.", ref="P1")
        data = self.status_json()["journal"]
        self.assertEqual(data["entries"], 2)
        self.assertIsNone(data["pending"])

    def test_an_entry_from_an_earlier_phase_is_not_pending(self):
        self.approve_chain()
        self.add("question", "QA script handed over.", ref="QA")
        self.assertEqual(self.pending()["kind"], "question")
        self.set_fields("tasks", status="done")
        data = self.status_json()
        self.assertEqual(data["phase"], "6. Validate")
        self.assertEqual(data["journal"]["entries"], 1)
        self.assertIsNone(data["journal"]["pending"])

    def test_plain_status_names_the_pending_entry(self):
        self.approve_chain()
        self.add("report", REPORT, ref="P1")
        code, out, err = self.run_sdd("status", SLUG)
        self.assertIn(
            "journal: 1 entry, pending #1 report P1 (2026-11-11T10:00:00Z), awaiting the session to act on it",
            out,
        )
        self.add("resolved", "P1 verified and committed.", ref="P1")
        code, out, err = self.run_sdd("status", SLUG)
        self.assertIn("journal: 2 entries, nothing pending", out)

    def test_journal_entries_leave_every_approval_current(self):
        self.approve_chain()
        before = self.status_json()["artifacts"]
        self.add("report", REPORT, ref="P1")
        self.add("question", "Rename the shared helper?", ref="P1")
        self.assertEqual(self.status_json()["artifacts"], before)
        self.assertFalse(self.status_json()["artifacts"]["tasks"]["changed"])
        code, out, err = self.run_sdd("lint", SLUG)
        self.assertEqual(code, 0, out + err)


if __name__ == "__main__":
    unittest.main()
