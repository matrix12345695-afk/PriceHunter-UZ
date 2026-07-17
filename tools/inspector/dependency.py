from __future__ import annotations

from collections import defaultdict


class DependencyAnalyzer:
    """
    Строит карту зависимостей проекта.

    Например:

    SearchService
        ├── ProductRepository
        ├── PriceRepository
        └── MarketplaceManager
    """

    def build(self, snapshot: dict) -> dict:

        dependencies = defaultdict(list)

        for file in snapshot["files"]:

            imports = file.get("imports", [])

            for module in imports:

                if module.startswith("app."):

                    dependencies[file["path"]].append(module)

        return dict(dependencies)