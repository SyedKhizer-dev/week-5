from flask import Blueprint, jsonify, request, render_template

from app.file_manager import list_directory, read_file, create_file, save_file

from app.git_manager import (
    find_repository,
    get_repository,
    commit_file,
    initialize_repository,
    get_file_history,
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/api/files", methods=["GET"])
def get_files():
    directory_path = request.args.get("path")

    if not directory_path:
        return jsonify({"error": "Directory path is required"}), 400

    try:
        files = list_directory(directory_path)

        return jsonify({"directory": directory_path, "files": files}), 200

    except (FileNotFoundError, NotADirectoryError, ValueError) as error:
        return jsonify({"error": str(error)}), 400


@main_bp.route("/api/files/open", methods=["POST"])
def open_file():
    data = request.get_json(silent=True) or {}
    file_path = data.get("path")

    if not file_path:
        return jsonify({"error": "File path is required"}), 400

    try:
        content = read_file(file_path)

        return jsonify({"path": file_path, "content": content}), 200

    except (FileNotFoundError, ValueError, UnicodeDecodeError) as error:
        return jsonify({"error": str(error)}), 400


@main_bp.route("/api/files/create", methods=["POST"])
def new_file():
    data = request.get_json(silent=True) or {}

    directory_path = data.get("directory")
    filename = data.get("filename")
    content = data.get("content", "")

    if not directory_path or not filename:
        return jsonify({"error": "Directory and filename are required"}), 400

    if not isinstance(content, str):
        return jsonify({"error": "Content must be a string"}), 400

    try:
        repo = find_repository(directory_path)

        if repo is None:
            return (
                jsonify(
                    {"error": "Initialize Git in this directory before creating files."}
                ),
                400,
            )

        repo.close()

        file = create_file(directory_path, filename, content)

        git_result = commit_file(file, f"Create {file.name}")

        return (
            jsonify(
                {
                    "message": "File created successfully",
                    "path": str(file),
                    "git": git_result,
                }
            ),
            201,
        )

    except (
        FileNotFoundError,
        NotADirectoryError,
        FileExistsError,
        ValueError,
    ) as error:
        return jsonify({"error": str(error)}), 400

    except Exception as error:
        return (
            jsonify(
                {
                    "error": "File was created, but Git commit failed",
                    "details": str(error),
                }
            ),
            500,
        )


@main_bp.route("/api/files/save", methods=["POST"])
def save_existing_file():
    data = request.get_json(silent=True) or {}

    file_path = data.get("path")
    content = data.get("content")

    if not file_path or content is None:
        return jsonify({"error": "File path and content are required"}), 400

    if not isinstance(content, str):
        return jsonify({"error": "Content must be a string"}), 400

    try:
        repo, _ = get_repository(file_path)
        repo.close()

        file = save_file(file_path, content)

        git_result = commit_file(file, f"Update {file.name}")

        return (
            jsonify(
                {
                    "message": "File saved successfully",
                    "path": str(file),
                    "git": git_result,
                }
            ),
            200,
        )

    except (
        FileNotFoundError,
        NotADirectoryError,
        ValueError,
        UnicodeDecodeError,
    ) as error:
        return jsonify({"error": str(error)}), 400

    except Exception as error:
        return (
            jsonify(
                {
                    "error": "File was saved, but Git commit failed",
                    "details": str(error),
                }
            ),
            500,
        )


@main_bp.route("/api/git/init", methods=["POST"])
def initialize_git():
    data = request.get_json(silent=True) or {}
    directory_path = data.get("directory")

    if not directory_path:
        return jsonify({"error": "Directory path is required"}), 400

    try:
        result = initialize_repository(directory_path)

        return jsonify(result), 200

    except (FileNotFoundError, NotADirectoryError, ValueError) as error:
        return jsonify({"error": str(error)}), 400

    except Exception as error:
        return (
            jsonify(
                {"error": "Could not initialize Git repository", "details": str(error)}
            ),
            500,
        )


@main_bp.route("/api/git/history", methods=["POST"])
def file_history():
    data = request.get_json(silent=True) or {}
    file_path = data.get("path")

    if not file_path:
        return jsonify({"error": "File path is required"}), 400

    try:
        limit = int(data.get("limit", 20))

        if limit < 1 or limit > 50:
            return jsonify({"error": "History limit must be between 1 and 50"}), 400

        history = get_file_history(file_path, limit)

        return jsonify({"path": file_path, "history": history}), 200

    except (ValueError, FileNotFoundError, NotADirectoryError) as error:
        return jsonify({"error": str(error)}), 400

    except Exception as error:
        return (
            jsonify({"error": "Could not retrieve Git history", "details": str(error)}),
            500,
        )
