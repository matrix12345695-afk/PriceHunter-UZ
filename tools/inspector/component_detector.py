from pathlib import Path


class ComponentDetector:

    def detect(self, file: dict) -> dict:

        path = Path(file["path"])

        component = "Unknown"

        classes = file.get("classes", [])

        imports = file.get("imports", [])

        #
        # SQLAlchemy Model
        #

        if "models" in path.parts:

            component = "Model"

        #
        # Repository
        #

        elif "repositories" in path.parts:

            component = "Repository"

        #
        # Service
        #

        elif "services" in path.parts:

            component = "Service"

        #
        # Provider
        #

        elif "providers" in path.parts:

            component = "Provider"

        #
        # Parser
        #

        elif "parsers" in path.parts:

            component = "Parser"

        #
        # Extractor
        #

        elif "extractors" in path.parts:

            component = "Extractor"

        #
        # Worker
        #

        elif "workers" in path.parts:

            component = "Worker"

        #
        # Telegram
        #

        elif "bot" in path.parts:

            component = "Telegram"

        #
        # Database
        #

        elif "database" in path.parts:

            component = "Database"

        #
        # FastAPI
        #

        elif "api" in path.parts:

            component = "FastAPI"

        #
        # Alembic
        #

        elif "alembic" in path.parts:

            component = "Migration"

        #
        # Дополнительные признаки
        #

        if any("Router" in i for i in imports):

            component = "Telegram Router"

        if any("APIRouter" in i for i in imports):

            component = "FastAPI Router"

        if any("DeclarativeBase" in i for i in imports):

            component = "SQLAlchemy Base"

        return {

            "component": component,

            "classes": len(classes),

            "imports": len(imports),

            "functions": len(file.get("functions", [])),

            "async_functions": len(
                file.get("async_functions", [])
            ),

        }