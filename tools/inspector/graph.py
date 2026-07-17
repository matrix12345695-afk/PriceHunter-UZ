class ImportGraph:

    def build(self, snapshot):

        graph = {}

        for file in snapshot["files"]:

            if file["extension"] != ".py":
                continue

            graph[file["path"]] = file.get(
                "imports",
                [],
            )

        return graph