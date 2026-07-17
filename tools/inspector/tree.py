from pathlib import Path


class TreeBuilder:

    def build(self, root: Path) -> str:

        lines = []

        def walk(path: Path, prefix=""):

            children = sorted(path.iterdir())

            for index, child in enumerate(children):

                last = index == len(children) - 1

                connector = "└── " if last else "├── "

                lines.append(
                    prefix + connector + child.name
                )

                if child.is_dir():

                    walk(
                        child,
                        prefix + ("    " if last else "│   "),
                    )

        lines.append(root.name)

        walk(root)

        return "\n".join(lines)