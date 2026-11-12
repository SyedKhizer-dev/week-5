import unittest
import tempfile

from pathlib import Path

from app.file_manager import (
    validate_directory,
    validate_file,
    list_directory,
    read_file,
    create_file,
    save_file,
)


class TestFileManager(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()

        self.directory = Path(self.temp_directory.name)

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_validate_directory(self):

        result = validate_directory(self.directory)

        self.assertEqual(result, self.directory.resolve())

    def test_validate_directory_not_found(self):

        invalid_path = self.directory / "missing"

        with self.assertRaises(FileNotFoundError):
            validate_directory(invalid_path)

    def test_validate_file(self):

        file = self.directory / "notes.txt"

        file.write_text("Hello", encoding="utf-8")

        result = validate_file(file)

        self.assertEqual(result, file.resolve())

    def test_validate_file_not_found(self):

        file = self.directory / "missing.txt"

        with self.assertRaises(FileNotFoundError):
            validate_file(file)

    def test_list_directory(self):

        (self.directory / "notes.txt").write_text("Hello", encoding="utf-8")

        (self.directory / "folder").mkdir()

        result = list_directory(self.directory)

        self.assertEqual(len(result), 2)

        self.assertTrue(result[0]["is_directory"])

        self.assertEqual(result[1]["name"], "notes.txt")

    def test_list_directory_hides_git_folder(self):

        (self.directory / ".git").mkdir()

        result = list_directory(self.directory)

        self.assertEqual(result, [])

    def test_read_file(self):

        file = self.directory / "notes.txt"

        file.write_text("Hello World", encoding="utf-8")

        result = read_file(file)

        self.assertEqual(result, "Hello World")

    def test_create_file(self):

        result = create_file(self.directory, "notes.txt", "Hello World")

        self.assertTrue(result.exists())

        self.assertEqual(result.read_text(encoding="utf-8"), "Hello World")

    def test_create_file_already_exists(self):

        file = self.directory / "notes.txt"

        file.write_text("Existing content", encoding="utf-8")

        with self.assertRaises(FileExistsError):
            create_file(self.directory, "notes.txt")

    def test_create_file_invalid_filename(self):

        with self.assertRaises(ValueError):
            create_file(self.directory, "../notes.txt")

    def test_save_file(self):

        file = self.directory / "notes.txt"

        file.write_text("Old content", encoding="utf-8")

        save_file(file, "Updated content")

        self.assertEqual(file.read_text(encoding="utf-8"), "Updated content")

    def test_save_file_not_found(self):

        file = self.directory / "missing.txt"

        with self.assertRaises(FileNotFoundError):
            save_file(file, "Content")


if __name__ == "__main__":
    unittest.main()
