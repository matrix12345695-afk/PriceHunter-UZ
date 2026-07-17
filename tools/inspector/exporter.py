import json

from pathlib import Path


class JsonExporter:

    def export(

        self,

        data: dict,

        output: Path,

    ):

        output.parent.mkdir(

            parents=True,

            exist_ok=True,

        )

        output.write_text(

            json.dumps(

                data,

                indent=4,

                ensure_ascii=False,

            ),

            encoding="utf-8",

        )