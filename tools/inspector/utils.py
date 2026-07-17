from hashlib import sha256
from pathlib import Path


def file_sha256(path: Path) -> str:

    h = sha256()

    with open(path, "rb") as f:

        while True:

            chunk = f.read(65536)

            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()