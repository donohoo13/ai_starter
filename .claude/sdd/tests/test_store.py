"""Where the spec folder lives and whether git tracks it.

A repository is shared when some checkout of it tracks a file under docs/sdd/,
and private otherwise. The worktrees here are real ones, made by `git worktree add`.
"""
import json
import subprocess
import unittest
from pathlib import Path

from helpers import BIN, BRANCH, SLUG, SddCase, git

EXCLUDE_LINE = "/docs/sdd/"
SECOND_SLUG = "second-change"
SECOND_BRANCH = "feature/second-change"


def status_lines(checkout):
    return git(checkout, "status", "--porcelain", "--untracked-files=all").splitlines()


def commit(checkout, message):
    git(checkout, "commit", "-q", "-m", message)


class StoreCase(SddCase):
    def store_of(self, checkout):
        return Path(checkout).resolve() / "docs" / "sdd"

    def status_from(self, checkout, slug=SLUG):
        """`sdd status --json` run inside `checkout`, with what it printed on stderr."""
        code, out, err = self.run_sdd("status", slug, "--json", cwd=checkout)
        self.assertEqual(code, 0, err)
        return json.loads(out), err

    def init(self, slug=SLUG, cwd=None):
        code, out, err = self.run_sdd("init", slug, cwd=cwd)
        self.assertEqual(code, 0, err)
        return out, err


class SharedRepositoryTests(StoreCase):
    def test_status_reports_shared_and_the_checkouts_own_folder(self):
        self.write_spec()
        data, err = self.status_from(self.repo)
        self.assertEqual(data["mode"], "shared")
        self.assertEqual(data["folder"], str(self.store_of(self.repo) / SLUG))
        self.assertEqual(err, "")
        code, out, err = self.run_sdd("status", SLUG)
        self.assertIn("folder: %s" % (self.store_of(self.repo) / SLUG), out)
        self.assertIn("mode: shared", out)

    def test_root_prints_the_store_and_the_mode(self):
        code, out, err = self.run_sdd("root")
        self.assertEqual(code, 0, err)
        self.assertIn("store: %s" % self.store_of(self.repo), out)
        self.assertIn("mode: shared", out)

    def test_a_worktree_keeps_its_specs_in_its_own_folder(self):
        worktree = self.add_worktree(SECOND_BRANCH)
        out, err = self.init(SECOND_SLUG, cwd=worktree)
        self.assertTrue((worktree / "docs" / "sdd" / SECOND_SLUG / "spec.md").is_file())
        self.assertFalse((self.folder(SECOND_SLUG)).exists())
        data, err = self.status_from(worktree, SECOND_SLUG)
        self.assertEqual(data["mode"], "shared")
        self.assertEqual(data["folder"], str(self.store_of(worktree) / SECOND_SLUG))
        self.assertEqual(status_lines(worktree), ["?? docs/sdd/%s/spec.md" % SECOND_SLUG])

    def test_a_worktree_whose_branch_tracks_nothing_is_shared_while_another_checkout_does(self):
        worktree = self.add_worktree(SECOND_BRANCH)
        git(worktree, "rm", "-q", "docs/sdd/.gitkeep")
        commit(worktree, "drop the placeholder on this branch")
        out, err = self.init(SECOND_SLUG, cwd=worktree)
        self.assertIn("mode: shared", out)
        self.assertTrue((worktree / "docs" / "sdd" / SECOND_SLUG / "spec.md").is_file())
        self.assertNotIn(EXCLUDE_LINE, self.exclude_lines())


class PrivateCase(StoreCase):
    SHARED = False


class PrivateRepositoryTests(PrivateCase):
    def test_init_ignores_the_folder_through_the_local_exclude_file(self):
        out, err = self.init()
        self.assertTrue((self.folder() / "spec.md").is_file())
        self.assertIn(EXCLUDE_LINE, self.exclude_lines())
        self.assertFalse((self.repo / ".gitignore").exists())
        self.assertIn("added %s to" % EXCLUDE_LINE, err)
        self.assertEqual(status_lines(self.repo), [])

    def test_init_says_never_to_stage(self):
        out, err = self.init()
        self.assertIn("mode: private", out)
        self.assertIn("never stage", out)
        self.assertNotIn("stage it by explicit path", out)

    def test_git_add_all_leaves_the_spec_out_of_the_index(self):
        self.init()
        (self.repo / "README.md").write_text("# changed\n")
        git(self.repo, "add", "-A")
        self.assertEqual(git(self.repo, "diff", "--cached", "--name-only").split(), ["README.md"])

    def test_status_reports_private_and_the_folder(self):
        self.write_spec()
        data, err = self.status_from(self.repo)
        self.assertEqual(data["mode"], "private")
        self.assertEqual(data["folder"], str(self.store_of(self.repo) / SLUG))
        code, out, err = self.run_sdd("status", SLUG)
        self.assertIn("mode: private", out)
        self.assertIn("never stage", out)

    def test_any_command_ignores_a_spec_folder_that_exists_unignored(self):
        self.write_spec()
        self.assertEqual(status_lines(self.repo), ["?? docs/sdd/%s/spec.md" % SLUG])
        self.status_from(self.repo)
        self.assertEqual(status_lines(self.repo), [])

    def test_the_exclude_entry_is_written_once(self):
        self.init()
        self.init("another-change")
        self.status_from(self.repo)
        self.assertEqual(self.exclude_lines().count(EXCLUDE_LINE), 1)

    def test_a_folder_the_repository_already_ignores_gets_no_exclude_entry(self):
        (self.repo / ".gitignore").write_text("docs/sdd/\n")
        git(self.repo, "add", ".gitignore")
        commit(self.repo, "ignore the spec folder")
        out, err = self.init()
        self.assertNotIn(EXCLUDE_LINE, self.exclude_lines())
        self.assertEqual(err, "")
        self.assertEqual(status_lines(self.repo), [])

    def test_reading_commands_write_nothing_before_a_spec_exists(self):
        self.run_sdd("find")
        self.run_sdd("status", SLUG)
        self.run_sdd("root")
        self.assertNotIn(EXCLUDE_LINE, self.exclude_lines())
        self.assertFalse((self.repo / "docs").exists())


class PrivateWorktreeTests(PrivateCase):
    """Every worktree of a private repository shares the main checkout's folder."""

    def setUp(self):
        super().setUp()
        self.worktree = self.add_worktree(SECOND_BRANCH)

    def write_second_spec(self):
        return self.write_spec(slug=SECOND_SLUG, branch=SECOND_BRANCH)

    def test_init_from_a_worktree_creates_the_spec_in_the_main_checkout(self):
        out, err = self.init(SECOND_SLUG, cwd=self.worktree)
        self.assertTrue((self.folder(SECOND_SLUG) / "spec.md").is_file())
        self.assertFalse((self.worktree / "docs").exists())
        self.assertEqual(self.frontmatter("spec", slug=SECOND_SLUG)["branch"], SECOND_BRANCH)
        self.assertIn("created %s" % (self.store_of(self.repo) / SECOND_SLUG / "spec.md"), out)
        self.assertIn("mode: private", out)
        self.assertEqual(status_lines(self.worktree), [])
        self.assertEqual(status_lines(self.repo), [])

    def test_two_worktrees_read_the_same_spec(self):
        self.write_spec()
        third = self.add_worktree("feature/third-change")
        for checkout in (self.repo, self.worktree, third):
            data, err = self.status_from(checkout)
            self.assertEqual(data["mode"], "private")
            self.assertEqual(data["folder"], str(self.store_of(self.repo) / SLUG))
            self.assertTrue(data["artifacts"]["spec"]["exists"], checkout)

    def test_find_matches_the_branch_of_the_worktree_it_runs_in(self):
        self.write_spec()
        self.write_second_spec()
        code, out, err = self.run_sdd("find", cwd=self.worktree)
        self.assertEqual((code, out.strip()), (0, SECOND_SLUG), err)
        code, out, err = self.run_sdd("find")
        self.assertEqual((code, out.strip()), (0, SLUG), err)

    def test_an_approval_recorded_in_a_worktree_is_read_from_the_main_checkout(self):
        self.write_second_spec()
        code, out, err = self.run_sdd("approve", SECOND_SLUG, "spec", cwd=self.worktree)
        self.assertEqual(code, 0, out + err)
        data, err = self.status_from(self.repo, SECOND_SLUG)
        self.assertEqual(data["artifacts"]["spec"]["status"], "approved")

    def test_a_journal_entry_added_in_a_worktree_lands_in_the_shared_folder(self):
        self.write_second_spec()
        journal = self.store_of(self.repo) / SECOND_SLUG / "journal.md"
        code, out, err = self.run_sdd(
            "journal", SECOND_SLUG, "add", "decision", "--text", "Keep the cap at 200.", cwd=self.worktree
        )
        self.assertEqual(code, 0, out + err)
        self.assertIn("Keep the cap at 200.", journal.read_text())
        self.assertIn(str(journal), out)
        data, err = self.status_from(self.worktree, SECOND_SLUG)
        self.assertEqual(data["journal"]["path"], str(journal))

    def test_a_spec_survives_removing_its_worktree(self):
        self.init(SECOND_SLUG, cwd=self.worktree)
        git(self.repo, "worktree", "remove", str(self.worktree))
        self.assertFalse(self.worktree.exists())
        data, err = self.status_from(self.repo, SECOND_SLUG)
        self.assertTrue(data["artifacts"]["spec"]["exists"])

    def test_uncommitted_in_a_worktree_lists_that_worktrees_work_and_no_spec_file(self):
        self.write_second_spec()
        self.write_review(slug=SECOND_SLUG)
        (self.repo / "README.md").write_text("# changed in the main checkout\n")
        (self.worktree / "app.txt").write_text("code\n")
        code, out, err = self.run_sdd("uncommitted", SECOND_SLUG, cwd=self.worktree)
        self.assertEqual(code, 0, out + err)
        lines = out.splitlines()
        self.assertEqual(lines[0], "?? app.txt")
        self.assertTrue(lines[1].startswith("1 uncommitted path"), lines)
        self.assertEqual(len(lines), 2)

    def test_the_folder_is_found_from_a_subdirectory_of_a_worktree(self):
        self.write_spec()
        subdirectory = self.worktree / "app"
        subdirectory.mkdir()
        data, err = self.status_from(subdirectory)
        self.assertEqual(data["folder"], str(self.store_of(self.repo) / SLUG))

    def test_a_spec_folder_left_inside_a_worktree_is_reported(self):
        self.write_spec()
        stray = self.worktree / "docs" / "sdd" / "stray-change"
        stray.mkdir(parents=True)
        (stray / "spec.md").write_text("---\nslug: stray-change\n---\n")
        data, err = self.status_from(self.worktree)
        self.assertIn("warning", err)
        self.assertIn("stray-change", err)
        self.assertIn(str(self.store_of(self.repo)), err)
        data, err = self.status_from(self.repo)
        self.assertEqual(err, "")

    def test_the_program_run_inside_a_worktree_names_the_main_checkouts_store(self):
        result = subprocess.run([str(BIN), "root"], cwd=self.worktree, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("root: %s" % self.worktree, result.stdout)
        self.assertIn("store: %s" % self.store_of(self.repo), result.stdout)
        self.assertIn("mode: private", result.stdout)


class PrivateBecomesSharedTests(PrivateCase):
    def test_committing_gitkeep_unhides_the_folder(self):
        self.init()
        self.assertIn(EXCLUDE_LINE, self.exclude_lines())
        self.track_gitkeep(self.repo)
        commit(self.repo, "track the spec folder")
        data, err = self.status_from(self.repo)
        self.assertEqual(data["mode"], "shared")
        self.assertEqual(data["folder"], str(self.store_of(self.repo) / SLUG))
        self.assertNotIn(EXCLUDE_LINE, self.exclude_lines())
        self.assertIn("removed %s from" % EXCLUDE_LINE, err)
        self.assertEqual(status_lines(self.repo), ["?? docs/sdd/%s/spec.md" % SLUG])
        git(self.repo, "add", "docs/sdd/%s/spec.md" % SLUG)

    def test_a_staged_gitkeep_is_enough(self):
        self.init()
        self.track_gitkeep(self.repo)
        data, err = self.status_from(self.repo)
        self.assertEqual(data["mode"], "shared")
        self.assertNotIn(EXCLUDE_LINE, self.exclude_lines())

    def test_the_users_own_exclude_lines_are_kept(self):
        exclude = self.repo / ".git" / "info" / "exclude"
        exclude.parent.mkdir(exist_ok=True)
        exclude.write_text("*.log")
        self.init()
        self.assertEqual(self.exclude_lines()[0], "*.log")
        self.assertIn(EXCLUDE_LINE, self.exclude_lines())
        self.track_gitkeep(self.repo)
        self.status_from(self.repo)
        self.assertEqual(self.exclude_lines(), ["*.log"])

    def test_gitkeep_committed_in_one_worktree_makes_every_checkout_shared(self):
        self.init()
        worktree = self.add_worktree(SECOND_BRANCH)
        self.track_gitkeep(worktree)
        commit(worktree, "track the spec folder")
        data, err = self.status_from(self.repo)
        self.assertEqual(data["mode"], "shared")
        self.assertEqual(data["folder"], str(self.store_of(self.repo) / SLUG))
        self.assertNotIn(EXCLUDE_LINE, self.exclude_lines())
        data, err = self.status_from(worktree, SECOND_SLUG)
        self.assertEqual(data["mode"], "shared")
        self.assertEqual(data["folder"], str(self.store_of(worktree) / SECOND_SLUG))
        self.assertNotIn(EXCLUDE_LINE, self.exclude_lines())


class GitDirectoryApartFromItsCheckoutTests(PrivateCase):
    """Git lists such a git directory, not the checkout, as the main worktree, so a linked worktree cannot find the checkout."""

    def setUp(self):
        super().setUp()
        base = Path(self.tmp.name).resolve()
        self.main = base / "apart"
        git(base, "init", "-q", "-b", "main", "--separate-git-dir", str(base / "apart.git"), str(self.main))
        (self.main / "README.md").write_text("# apart\n")
        git(self.main, "add", "README.md")
        git(self.main, "-c", "user.name=Test User", "-c", "user.email=test@example.com", "commit", "-q", "-m", "init")

    def test_the_main_checkout_keeps_its_own_folder(self):
        code, out, err = self.run_sdd("init", SLUG, "--branch", BRANCH, cwd=self.main)
        self.assertEqual(code, 0, err)
        self.assertTrue((self.main / "docs" / "sdd" / SLUG / "spec.md").is_file())
        self.assertEqual(status_lines(self.main), [])

    def test_a_linked_worktree_is_refused_rather_than_given_a_folder_inside_the_git_directory(self):
        linked = self.main.parent / "apart-linked"
        git(self.main, "worktree", "add", "-q", "-b", SECOND_BRANCH, str(linked))
        code, out, err = self.run_sdd("init", SECOND_SLUG, cwd=linked)
        self.assertEqual(code, 1)
        self.assertIn("main checkout", err)
        self.assertFalse((self.main.parent / "apart.git" / "docs").exists())
        self.assertFalse((linked / "docs").exists())


class SharedBecomesPrivateTests(StoreCase):
    def test_deleting_the_only_tracked_file_hides_the_folder(self):
        self.write_spec()
        self.assertEqual(status_lines(self.repo), ["?? docs/sdd/%s/spec.md" % SLUG])
        git(self.repo, "rm", "-q", "docs/sdd/.gitkeep")
        commit(self.repo, "drop the placeholder")
        data, err = self.status_from(self.repo)
        self.assertEqual(data["mode"], "private")
        self.assertTrue(data["artifacts"]["spec"]["exists"])
        self.assertIn(EXCLUDE_LINE, self.exclude_lines())
        self.assertIn("added %s to" % EXCLUDE_LINE, err)
        self.assertEqual(status_lines(self.repo), [])

    def test_a_committed_spec_keeps_the_repository_shared_without_gitkeep(self):
        self.write_spec()
        git(self.repo, "add", "docs/sdd/%s/spec.md" % SLUG)
        git(self.repo, "rm", "-q", "docs/sdd/.gitkeep")
        commit(self.repo, "spec in, placeholder out")
        data, err = self.status_from(self.repo)
        self.assertEqual(data["mode"], "shared")
        self.assertNotIn(EXCLUDE_LINE, self.exclude_lines())


class RepositoryWithoutCommitsTests(StoreCase):
    def setUp(self):
        super().setUp()
        self.fresh = Path(self.tmp.name).resolve() / "fresh"
        self.fresh.mkdir()
        git(self.fresh, "init", "-q", "-b", "main")

    def fresh_exclude_lines(self):
        return (self.fresh / ".git" / "info" / "exclude").read_text().splitlines()

    def test_it_is_private_while_nothing_under_the_folder_is_staged(self):
        code, out, err = self.run_sdd("init", SLUG, "--branch", BRANCH, cwd=self.fresh)
        self.assertEqual(code, 0, err)
        self.assertIn("mode: private", out)
        self.assertTrue((self.fresh / "docs" / "sdd" / SLUG / "spec.md").is_file())
        self.assertIn(EXCLUDE_LINE, self.fresh_exclude_lines())
        self.assertEqual(status_lines(self.fresh), [])

    def test_an_untracked_gitkeep_does_not_make_it_shared(self):
        (self.fresh / "docs" / "sdd").mkdir(parents=True)
        (self.fresh / "docs" / "sdd" / ".gitkeep").write_text("")
        code, out, err = self.run_sdd("init", SLUG, "--branch", BRANCH, cwd=self.fresh)
        self.assertIn("mode: private", out)

    def test_a_staged_gitkeep_makes_it_shared_before_the_first_commit(self):
        self.track_gitkeep(self.fresh)
        code, out, err = self.run_sdd("init", SLUG, "--branch", BRANCH, cwd=self.fresh)
        self.assertEqual(code, 0, err)
        self.assertIn("mode: shared", out)
        self.assertNotIn(EXCLUDE_LINE, self.fresh_exclude_lines())
        self.assertIn("?? docs/sdd/%s/spec.md" % SLUG, status_lines(self.fresh))


class OutsideGitTests(StoreCase):
    def setUp(self):
        super().setUp()
        self.plain = Path(self.tmp.name).resolve() / "plain"
        self.plain.mkdir()

    def test_the_folder_sits_under_the_current_directory_and_nothing_is_staged(self):
        code, out, err = self.run_sdd("init", SLUG, "--branch", BRANCH, cwd=self.plain)
        self.assertEqual(code, 0, err)
        self.assertIn("mode: private", out)
        self.assertIn("not a git repository", out)
        data, err = self.status_from(self.plain)
        self.assertEqual(data["mode"], "private")
        self.assertEqual(data["folder"], str(self.plain / "docs" / "sdd" / SLUG))
        self.assertEqual(err, "")
        self.assertFalse((self.plain / ".git").exists())


class BareCloneCase(StoreCase):
    """A bare repository has no main checkout, so a private spec has no folder that outlives the worktrees."""

    def worktree_of_a_bare_clone(self):
        bare = Path(self.tmp.name).resolve() / "bare.git"
        git(self.repo, "clone", "-q", "--bare", str(self.repo), str(bare))
        worktree = Path(self.tmp.name).resolve() / "bare-worktree"
        git(bare, "worktree", "add", "-q", "-b", SECOND_BRANCH, str(worktree), "main")
        return worktree


class SharedBareCloneTests(BareCloneCase):
    def test_a_worktree_uses_its_own_folder(self):
        worktree = self.worktree_of_a_bare_clone()
        out, err = self.init(SECOND_SLUG, cwd=worktree)
        self.assertIn("mode: shared", out)
        self.assertTrue((worktree / "docs" / "sdd" / SECOND_SLUG / "spec.md").is_file())


class PrivateBareCloneTests(BareCloneCase):
    SHARED = False

    def test_a_worktree_is_refused_with_the_reason(self):
        worktree = self.worktree_of_a_bare_clone()
        code, out, err = self.run_sdd("init", SECOND_SLUG, cwd=worktree)
        self.assertEqual(code, 1)
        self.assertIn("bare", err)
        self.assertFalse((worktree / "docs").exists())


if __name__ == "__main__":
    unittest.main()
