from pathlib import Path


class ArchitectureAnalyzer:

    LAYERS = {
        "models": "Model",
        "repositories": "Repository",
        "services": "Service",
        "providers": "Provider",
        "parsers": "Parser",
        "extractors": "Extractor",
        "workers": "Worker",
        "bot": "Telegram",
        "api": "FastAPI",
        "database": "Database",
        "core": "Core",
        "domain": "Domain",
    }

    def analyze(self, snapshot: dict) -> dict:

        architecture = {}

        for file in snapshot["files"]:

            path = Path(file["path"])

            layer = "Other"

            for part in path.parts:

                if part in self.LAYERS:

                    layer = self.LAYERS[part]

                    break

            architecture[file["path"]] = {
                "layer": layer,
                "classes": [
                    c["name"] if isinstance(c, dict) else c
                    for c in file.get("classes", [])
                ],
                "functions": [
                    f["name"] if isinstance(f, dict) else f
                    for f in file.get("functions", [])
                ],
                "async_functions": [
                    f["name"] if isinstance(f, dict) else f
                    for f in file.get("async_functions", [])
                ],
            }

        return architecture