from pathlib import Path


def validate_directory(directory_path):
    directory = Path(directory_path).expanduser().resolve(strict=True)

    if not directory.exists():
        raise FileNotFoundError("Directory does not exist")

    if not directory.is_dir():
        raise NotADirectoryError("The provided path is not a directory")

    return directory


def validate_file(file_path):
    file = Path(file_path).expanduser().resolve(strict=True)

    if not file.exists():
        raise FileNotFoundError("File does not exist")

    if not file.is_file():
        raise ValueError("The provided path is not a file")

    return file


def list_directory(directory_path):
    directory = validate_directory(directory_path)

    items = []

    for item in directory.iterdir():
        if item.name == ".git":
            continue

        items.append(
            {
                "name": item.name,
                "path": str(item.resolve()),
                "is_directory": item.is_dir(),
            }
        )

    return sorted(
        items, key=lambda item: (not item["is_directory"], item["name"].lower())
    )


def read_file(file_path):
    file = validate_file(file_path)

    return file.read_text(encoding="utf-8")


def create_file(directory_path, filename, content=""):
    directory = validate_directory(directory_path)

    if not filename or filename in {".", ".."}:
        raise ValueError("Invalid filename")

    if Path(filename).name != filename or "/" in filename or "\\" in filename:
        raise ValueError("Filename must not contain directory paths")

    file = directory / filename

    if file.exists():
        raise FileExistsError("A file with this name already exists")

    file.write_text(content, encoding="utf-8")

    return file.resolve()


def save_file(file_path, content):
    file = validate_file(file_path)

    file.write_text(content, encoding="utf-8")

    return file
