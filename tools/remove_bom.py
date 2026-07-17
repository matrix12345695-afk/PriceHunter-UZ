from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".idea",
    ".vscode",
    "node_modules",
    "build",
    "dist",
}

EXTENSIONS = {
    ".py",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
    ".md",
    ".txt",
    ".sql",
}


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def remove_bom(file_path: Path) -> bool:
    try:
        raw = file_path.read_bytes()

        BOM = b"\xef\xbb\xbf"

        if raw.startswith(BOM):
            raw = raw[len(BOM):]
            file_path.write_bytes(raw)
            return True

        return False

    except Exception as e:
        print(f"❌ {file_path}: {e}")
        return False


def main():

    fixed = 0
    checked = 0

    print("=" * 70)
    print("PriceHunter BOM Cleaner")
    print("=" * 70)

    for file in ROOT.rglob("*"):

        if not file.is_file():
            continue

        if should_skip(file):
            continue

        if file.suffix.lower() not in EXTENSIONS:
            continue

        checked += 1

        if remove_bom(file):
            fixed += 1
            print("✅", file.relative_to(ROOT))

    print()
    print("=" * 70)
    print("Готово")
    print("=" * 70)
    print(f"Проверено файлов : {checked}")
    print(f"Исправлено BOM   : {fixed}")


if __name__ == "__main__":
    main()