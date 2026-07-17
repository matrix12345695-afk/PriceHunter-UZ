from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .config import REPORT_DIR
from .utils import save_json, save_text


class Reporter:
    """
    Генератор отчётов API Explorer.
    """

    def __init__(self, recorder):

        self.recorder = recorder

    # ==========================================================
    # SUMMARY
    # ==========================================================

    def build_summary(self):

        requests = self.recorder.requests
        responses = self.recorder.responses

        summary = {
            "generated": datetime.now().isoformat(),
            "requests": len(requests),
            "responses": len(responses),
            "top_api": self.find_best_requests(),
        }

        save_json(
            REPORT_DIR / "summary.json",
            summary,
        )

        return summary

    # ==========================================================
    # API SCORE
    # ==========================================================

    def find_best_requests(self):

        requests = sorted(
            self.recorder.requests,
            key=lambda x: x["score"],
            reverse=True,
        )

        return requests[:20]

    # ==========================================================
    # TEXT REPORT
    # ==========================================================

    def build_report(self):

        lines = []

        lines.append("=" * 80)
        lines.append("PRICEHUNTER API EXPLORER")
        lines.append("=" * 80)
        lines.append("")

        lines.append(
            f"Generated: {datetime.now()}"
        )

        lines.append(
            f"Requests : {len(self.recorder.requests)}"
        )

        lines.append(
            f"Responses: {len(self.recorder.responses)}"
        )

        lines.append("")
        lines.append("=" * 80)
        lines.append("TOP API CANDIDATES")
        lines.append("=" * 80)
        lines.append("")

        for item in self.find_best_requests():

            stars = "★" * min(item["score"] // 10, 5)

            if not stars:
                stars = "☆"

            lines.append(stars)

            lines.append(item["url"])

            lines.append(
                f"Method : {item['method']}"
            )

            lines.append(
                f"Score  : {item['score']}"
            )

            lines.append("")

        save_text(
            REPORT_DIR / "report.txt",
            "\n".join(lines),
        )

    # ==========================================================
    # EXPORT
    # ==========================================================

    def export(self):

        self.build_summary()

        self.build_report()