import json
from pathlib import Path


def ensure_directory(path: Path) -> None:
    """
    Создать папку при необходимости.
    """

    path.mkdir(
        parents=True,
        exist_ok=True,
    )


def save_json(path: Path, data) -> None:
    """
    Сохранить JSON.
    """

    ensure_directory(path.parent)

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )


def save_text(path: Path, text: str) -> None:
    """
    Сохранить текст.
    """

    ensure_directory(path.parent)

    path.write_text(
        text,
        encoding="utf-8",
    )


def pretty_size(size: int) -> str:
    """
    Красивый размер файла.
    """

    units = [
        "B",
        "KB",
        "MB",
        "GB",
    ]

    value = float(size)

    for unit in units:

        if value < 1024:
            return f"{value:.1f} {unit}"

        value /= 1024

    return f"{value:.1f} TB"