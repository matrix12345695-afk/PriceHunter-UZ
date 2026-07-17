class Statistics:

    def build(self, snapshot):

        stats = {

            "files": 0,

            "python_files": 0,

            "classes": 0,

            "functions": 0,

            "imports": 0,

            "lines": 0,

        }

        stats["files"] = len(
            snapshot["files"]
        )

        for file in snapshot["files"]:

            stats["lines"] += file.get(
                "lines",
                0,
            )

            if file["extension"] == ".py":

                stats["python_files"] += 1

            stats["classes"] += len(
                file.get("classes", [])
            )

            stats["functions"] += len(
                file.get("functions", [])
            )

            stats["imports"] += len(
                file.get("imports", [])
            )

        return stats