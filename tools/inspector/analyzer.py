from __future__ import annotations

import ast
from pathlib import Path


class ASTAnalyzer:

    def analyze(self, file_path: Path) -> dict:

        source = file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        tree = ast.parse(source)

        result = {
            "imports": [],
            "classes": [],
            "functions": [],
            "async_functions": [],
            "variables": [],
            "constants": [],
            "todo": [],
        }

        for node in ast.walk(tree):

            #
            # import x
            #
            if isinstance(node, ast.Import):

                for alias in node.names:

                    result["imports"].append(
                        alias.name
                    )

            #
            # from x import y
            #
            elif isinstance(node, ast.ImportFrom):

                module = node.module or ""

                for alias in node.names:

                    result["imports"].append(
                        f"{module}.{alias.name}"
                    )

            #
            # class
            #
            elif isinstance(node, ast.ClassDef):

                cls = {

                    "name": node.name,

                    "line": node.lineno,

                    "methods": [],

                }

                for child in node.body:

                    if isinstance(
                        child,
                        (
                            ast.FunctionDef,
                            ast.AsyncFunctionDef,
                        ),
                    ):

                        cls["methods"].append(
                            child.name
                        )

                result["classes"].append(cls)

            #
            # function
            #
            elif isinstance(node, ast.FunctionDef):

                result["functions"].append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                    }
                )

            #
            # async function
            #
            elif isinstance(node, ast.AsyncFunctionDef):

                result["async_functions"].append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                    }
                )

            #
            # variables
            #
            elif isinstance(node, ast.Assign):

                for target in node.targets:

                    if isinstance(
                        target,
                        ast.Name,
                    ):

                        if target.id.isupper():

                            result[
                                "constants"
                            ].append(
                                target.id
                            )

                        else:

                            result[
                                "variables"
                            ].append(
                                target.id
                            )

        #
        # TODO search
        #

        for index, line in enumerate(
            source.splitlines(),
            start=1,
        ):

            text = line.upper()

            if (
                "TODO" in text
                or "FIXME" in text
                or "BUG" in text
                or "HACK" in text
            ):

                result["todo"].append(
                    {
                        "line": index,
                        "text": line.strip(),
                    }
                )

        return result