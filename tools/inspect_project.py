from pathlib import Path

from inspector.config import OUTPUT_DIR
from inspector.config import PROJECT_ROOT

from inspector.exporter import JsonExporter
from inspector.graph import ImportGraph

from inspector.analyzer import ASTAnalyzer
from inspector.architecture import ArchitectureAnalyzer

from inspector.scanner import ProjectScanner
from inspector.statistics import Statistics
from inspector.tree import TreeBuilder
from inspector.utils import file_sha256
from inspector.dependency import DependencyAnalyzer
from inspector.component_detector import ComponentDetector
from inspector.project_graph import ProjectGraph

def read_file(path: Path) -> str:
    try:
        return path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
    except Exception:
        return ""


def main():

    print("=" * 70)
    print("PROJECT INSPECTOR PRO")
    print("=" * 70)
    print()

    scanner = ProjectScanner(PROJECT_ROOT)

    parser = ASTAnalyzer()

    exporter = JsonExporter()

    files = scanner.scan()

    print(f"Проект : {PROJECT_ROOT.name}")
    print(f"Файлов : {len(files)}")
    print()

    snapshot = {

        "project": {
            "name": PROJECT_ROOT.name,
            "root": str(PROJECT_ROOT),
        },

        "files": []

    }

    for index, path in enumerate(files, start=1):

        relative = str(
            path.relative_to(PROJECT_ROOT)
        )

        print(
            f"[{index}/{len(files)}] {relative}"
        )

        content = read_file(path)

        info = {

            "path": relative,

            "extension": path.suffix,

            "size": path.stat().st_size,

            "lines": len(
                content.splitlines()
            ),

            "sha256": file_sha256(path),

            "content": content,

        }

        if path.suffix == ".py":

            try:

                parsed = parser.analyze(path)

                info.update(parsed)

            except Exception as exc:

                info["parse_error"] = str(exc)

        snapshot["files"].append(info)

    print()
    print("Построение дерева проекта...")

    tree = TreeBuilder().build(
        PROJECT_ROOT
    )

    snapshot["tree"] = tree

    print("Подсчёт статистики...")

    statistics = Statistics().build(
        snapshot
    )

    snapshot["statistics"] = statistics

    print("Анализ архитектуры...")

    architecture = ArchitectureAnalyzer().analyze(
        snapshot
    )

    snapshot["architecture"] = architecture

    print("Анализ зависимостей...")

    dependencies = DependencyAnalyzer().build(
        snapshot
    )

    snapshot["dependencies"] = dependencies

    print("Определение компонентов...")

    detector = ComponentDetector()

    components = {}

    for file in snapshot["files"]:

        components[file["path"]] = detector.detect(file)

    snapshot["components"] = components

    print("Построение графа проекта...")

    project_graph = ProjectGraph().build(
        snapshot
    )

    snapshot["project_graph"] = project_graph

    print("Построение графа импортов...")

    graph = ImportGraph().build(
        snapshot
    )

    snapshot["import_graph"] = graph

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    exporter.export(
        snapshot,
        OUTPUT_DIR / "project_snapshot.json",
    )

    exporter.export(
        statistics,
        OUTPUT_DIR / "statistics.json",
    )

    exporter.export(
        architecture,
        OUTPUT_DIR / "architecture.json",
    )

    exporter.export(
        dependencies,
        OUTPUT_DIR / "dependencies.json",
    )

    exporter.export(
        components,
        OUTPUT_DIR / "components.json",
    )

    exporter.export(
        project_graph,
        OUTPUT_DIR / "project_graph.json",
    )

    exporter.export(
        graph,
        OUTPUT_DIR / "imports_graph.json",
    )

    (OUTPUT_DIR / "project_tree.txt").write_text(
        tree,
        encoding="utf-8",
    )

    print()
    print("=" * 70)
    print("ГОТОВО")
    print("=" * 70)
    print()

    print("Созданы файлы:")

    print(
        OUTPUT_DIR / "project_snapshot.json"
    )

    print(
        OUTPUT_DIR / "statistics.json"
    )

    print(
        OUTPUT_DIR / "architecture.json"
    )
    print(
        OUTPUT_DIR / "dependencies.json"
    )
    print(
        OUTPUT_DIR / "components.json"
    )
    print(
        OUTPUT_DIR / "project_graph.json"
    )

    print(
        OUTPUT_DIR / "imports_graph.json"
    )

    print(
        OUTPUT_DIR / "project_tree.txt"
    )

    print()

    print("Статистика:")

    for key, value in statistics.items():

        print(
            f"{key:20} : {value}"
        )


if __name__ == "__main__":
    main()