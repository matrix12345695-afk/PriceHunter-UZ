from pathlib import Path

from .config import (
    IGNORE_DIRS,
    IGNORE_EXTENSIONS,
    MAX_FILE_SIZE,
)


class ProjectScanner:

    def __init__(self, root: Path):

        self.root = root

    def scan(self):

        files = []

        for path in self.root.rglob("*"):

            if not path.is_file():
                continue

            if any(part in IGNORE_DIRS for part in path.parts):
                continue

            if path.suffix.lower() in IGNORE_EXTENSIONS:
                continue

            try:

                if path.stat().st_size > MAX_FILE_SIZE:
                    continue

            except Exception:
                continue

            files.append(path)

        return sorted(files)