import ast
from pathlib import Path


class PythonParser:

    def parse(self, file_path: Path) -> dict:

        source = file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        tree = ast.parse(source)

        imports = []
        classes = []
        functions = []

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):

                for alias in node.names:

                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):

                module = node.module or ""

                for alias in node.names:

                    imports.append(
                        f"{module}.{alias.name}"
                    )

            elif isinstance(node, ast.ClassDef):

                classes.append(node.name)

            elif isinstance(node, ast.FunctionDef):

                functions.append(node.name)

            elif isinstance(node, ast.AsyncFunctionDef):

                functions.append(node.name)

        return {

            "imports": sorted(set(imports)),
            "classes": classes,
            "functions": functions,

        }