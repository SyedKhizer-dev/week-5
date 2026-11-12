import unittest
import tempfile

from pathlib import Path

from app.git_manager import (
    find_repository,
    initialize_repository,
    get_repository,
    commit_file,
    get_file_history,
)


class TestGitManager(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_directory.name)

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_find_repository_not_found(self):
        result = find_repository(self.directory)
        self.assertIsNone(result)

    def test_initialize_repository(self):
        result = initialize_repository(self.directory)

        self.assertTrue(result["initialized"])
        self.assertTrue((self.directory / ".git").exists())

    def test_initialize_existing_repository(self):
        initialize_repository(self.directory)

        result = initialize_repository(self.directory)

        self.assertFalse(result["initialized"])
        self.assertIn("existing", result["message"])

    def test_find_existing_repository(self):
        initialize_repository(self.directory)

        repo = find_repository(self.directory)

        try:
            self.assertIsNotNone(repo)
            self.assertEqual(
                Path(repo.working_tree_dir).resolve(), self.directory.resolve()
            )
        finally:
            repo.close()

    def test_get_repository_without_git(self):
        file = self.directory / "notes.txt"
        file.write_text("Hello", encoding="utf-8")

        with self.assertRaises(ValueError):
            get_repository(file)

    def test_commit_new_file(self):
        initialize_repository(self.directory)

        file = self.directory / "notes.txt"
        file.write_text("Hello World", encoding="utf-8")

        result = commit_file(file, "Create notes.txt")

        self.assertTrue(result["committed"])
        self.assertEqual(result["message"], "Create notes.txt")

        repo, _ = get_repository(file)

        try:
            self.assertEqual(repo.head.commit.message.strip(), "Create notes.txt")
        finally:
            repo.close()

    def test_no_commit_when_file_is_unchanged(self):
        initialize_repository(self.directory)

        file = self.directory / "notes.txt"
        file.write_text("Hello World", encoding="utf-8")

        commit_file(file, "Create notes.txt")

        result = commit_file(file, "Update notes.txt")

        self.assertFalse(result["committed"])
        self.assertEqual(result["message"], "No changes to commit")

    def test_commit_updated_file(self):
        initialize_repository(self.directory)

        file = self.directory / "notes.txt"
        file.write_text("Original content", encoding="utf-8")

        commit_file(file, "Create notes.txt")

        file.write_text("Updated content", encoding="utf-8")

        result = commit_file(file, "Update notes.txt")

        self.assertTrue(result["committed"])
        self.assertEqual(result["message"], "Update notes.txt")

    def test_get_file_history(self):
        initialize_repository(self.directory)

        file = self.directory / "notes.txt"
        file.write_text("First version", encoding="utf-8")

        commit_file(file, "Create notes.txt")

        file.write_text("Second version", encoding="utf-8")

        commit_file(file, "Update notes.txt")

        history = get_file_history(file)

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["message"], "Update notes.txt")
        self.assertEqual(history[1]["message"], "Create notes.txt")

    def test_empty_repository_history(self):
        initialize_repository(self.directory)

        file = self.directory / "notes.txt"
        file.write_text("Hello", encoding="utf-8")

        history = get_file_history(file)

        self.assertEqual(history, [])


if __name__ == "__main__":
    unittest.main()
