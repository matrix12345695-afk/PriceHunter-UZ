from pathlib import Path

PROJECT_ROOT = Path.cwd()

OUTPUT_DIR = PROJECT_ROOT / "project_snapshot"

IGNORE_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    ".pytest_cache",
    ".mypy_cache",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    ".ruff_cache",
}

IGNORE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".log",
    ".tmp",
    ".sqlite3",
    ".db",
}

TEXT_EXTENSIONS = {
    ".py",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
    ".md",
    ".txt",
    ".html",
    ".css",
    ".js",
    ".ts",
    ".sql",
    ".xml",
}

MAX_FILE_SIZE = 5 * 1024 * 1024