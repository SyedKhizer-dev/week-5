from pathlib import Path

from git import Repo, Actor
from git.exc import InvalidGitRepositoryError, NoSuchPathError


def find_repository(directory_path):
    directory = Path(directory_path).expanduser().resolve(strict=True)

    if not directory.is_dir():
        raise NotADirectoryError("The provided path is not a directory")

    try:
        return Repo(str(directory), search_parent_directories=True)

    except (InvalidGitRepositoryError, NoSuchPathError):
        return None


def initialize_repository(directory_path):
    directory = Path(directory_path).expanduser().resolve(strict=True)

    if not directory.is_dir():
        raise NotADirectoryError("The provided path is not a directory")

    existing_repo = find_repository(directory)

    if existing_repo:
        repository_path = str(Path(existing_repo.working_tree_dir).resolve())
        existing_repo.close()

        return {
            "initialized": False,
            "message": "An existing Git repository was found",
            "repository": repository_path,
        }

    repo = Repo.init(str(directory))
    repository_path = str(Path(repo.working_tree_dir).resolve())
    repo.close()

    return {
        "initialized": True,
        "message": "Git repository initialized successfully",
        "repository": repository_path,
    }


def get_repository(file_path):
    file = Path(file_path).expanduser().resolve(strict=True)

    if not file.is_file():
        raise ValueError("The provided path is not a file")

    repo = find_repository(file.parent)

    if repo is None:
        raise ValueError(
            "No Git repository found. Initialize Git in the selected directory first."
        )

    return repo, file


def commit_file(file_path, message=None):
    repo, file = get_repository(file_path)

    try:
        repository_root = Path(repo.working_tree_dir).resolve()
        relative_path = file.relative_to(repository_root).as_posix()

        status = repo.git.status("--porcelain", "--", relative_path)

        if not status:
            return {"committed": False, "message": "No changes to commit"}

        if message is None:
            message = f"Update {file.name}"

        author = Actor("Notepad Tracker", "notepad-tracker@localhost")

        with repo.git.custom_environment(
            GIT_AUTHOR_NAME=author.name,
            GIT_AUTHOR_EMAIL=author.email,
            GIT_COMMITTER_NAME=author.name,
            GIT_COMMITTER_EMAIL=author.email,
        ):
            repo.git.add("--", relative_path)

            repo.git.commit("-m", message, "--only", "--", relative_path)

        latest_commit = repo.head.commit

        return {
            "committed": True,
            "commit_hash": latest_commit.hexsha,
            "message": latest_commit.message.strip(),
            "repository": str(repository_root),
            "file": relative_path,
        }

    finally:
        repo.close()


def get_file_history(file_path, limit=20):
    repo, file = get_repository(file_path)

    try:
        if not repo.head.is_valid():
            return []

        repository_root = Path(repo.working_tree_dir).resolve()
        relative_path = file.relative_to(repository_root).as_posix()

        commits = repo.iter_commits(paths=relative_path, max_count=limit)

        history = []

        for commit in commits:
            history.append(
                {
                    "commit_hash": commit.hexsha,
                    "short_hash": commit.hexsha[:7],
                    "message": commit.message.strip(),
                    "author": commit.author.name,
                    "date": commit.committed_datetime.isoformat(),
                }
            )

        return history

    finally:
        repo.close()
