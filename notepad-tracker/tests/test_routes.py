import unittest
import tempfile

from pathlib import Path

from app import create_app


class TestRoutes(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_directory.name)

        self.app = create_app()
        self.app.config["TESTING"] = True

        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_directory.cleanup()

    def initialize_git(self):
        return self.client.post(
            "/api/git/init", json={"directory": str(self.directory)}
        )

    def create_file(self, filename="notes.txt", content="Hello"):
        return self.client.post(
            "/api/files/create",
            json={
                "directory": str(self.directory),
                "filename": filename,
                "content": content,
            },
        )

    def test_home_page(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)

    def test_get_files(self):
        (self.directory / "notes.txt").write_text("Hello", encoding="utf-8")

        (self.directory / "documents").mkdir()

        response = self.client.get(
            "/api/files", query_string={"path": str(self.directory)}
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(len(data["files"]), 2)
        self.assertEqual(data["files"][0]["name"], "documents")
        self.assertEqual(data["files"][1]["name"], "notes.txt")

    def test_get_files_without_path(self):
        response = self.client.get("/api/files")

        self.assertEqual(response.status_code, 400)

    def test_get_files_invalid_directory(self):
        response = self.client.get(
            "/api/files", query_string={"path": str(self.directory / "missing")}
        )

        self.assertEqual(response.status_code, 400)

    def test_open_file(self):
        file = self.directory / "notes.txt"
        file.write_text("Hello World", encoding="utf-8")

        response = self.client.post("/api/files/open", json={"path": str(file)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["content"], "Hello World")

    def test_open_file_without_path(self):
        response = self.client.post("/api/files/open", json={})

        self.assertEqual(response.status_code, 400)

    def test_initialize_git(self):
        response = self.initialize_git()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["initialized"])
        self.assertTrue((self.directory / ".git").exists())

    def test_create_file_without_git(self):
        response = self.create_file()

        self.assertEqual(response.status_code, 400)
        self.assertFalse((self.directory / "notes.txt").exists())

    def test_create_file(self):
        self.initialize_git()

        response = self.create_file()

        self.assertEqual(response.status_code, 201)

        data = response.get_json()

        self.assertEqual(data["message"], "File created successfully")
        self.assertTrue(data["git"]["committed"])

        file = self.directory / "notes.txt"

        self.assertTrue(file.exists())
        self.assertEqual(file.read_text(encoding="utf-8"), "Hello")

    def test_save_file(self):
        self.initialize_git()
        self.create_file()

        file = self.directory / "notes.txt"

        response = self.client.post(
            "/api/files/save", json={"path": str(file), "content": "Updated content"}
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(data["message"], "File saved successfully")
        self.assertTrue(data["git"]["committed"])

        self.assertEqual(file.read_text(encoding="utf-8"), "Updated content")

    def test_save_file_without_git(self):
        file = self.directory / "notes.txt"
        file.write_text("Original content", encoding="utf-8")

        response = self.client.post(
            "/api/files/save", json={"path": str(file), "content": "Updated content"}
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(file.read_text(encoding="utf-8"), "Original content")

    def test_git_history(self):
        self.initialize_git()
        self.create_file()

        file = self.directory / "notes.txt"

        self.client.post(
            "/api/files/save", json={"path": str(file), "content": "Updated content"}
        )

        response = self.client.post("/api/git/history", json={"path": str(file)})

        self.assertEqual(response.status_code, 200)

        history = response.get_json()["history"]

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["message"], "Update notes.txt")
        self.assertEqual(history[1]["message"], "Create notes.txt")

    def test_git_history_without_path(self):
        response = self.client.post("/api/git/history", json={})

        self.assertEqual(response.status_code, 400)

    def test_git_history_invalid_limit(self):
        self.initialize_git()
        self.create_file()

        response = self.client.post(
            "/api/git/history",
            json={"path": str(self.directory / "notes.txt"), "limit": 100},
        )

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
