from collections import defaultdict


class ProjectGraph:

    def build(self, snapshot: dict):

        graph = defaultdict(list)

        reverse = defaultdict(list)

        for file in snapshot["files"]:

            source = file["path"]

            for dep in file.get("imports", []):

                if dep.startswith("app."):

                    graph[source].append(dep)

                    reverse[dep].append(source)

        return {

            "forward": dict(graph),

            "reverse": dict(reverse),

        }