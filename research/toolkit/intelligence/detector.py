from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .classifier import (
    ApiClassifier,
    ApiType,
    ClassificationResult,
)

from .fingerprint import (
    FingerprintEngine,
    FingerprintMatch,
)

from .fingerprints import (
    ALL_FINGERPRINTS,
)


# ==========================================================
# RESULT
# ==========================================================


@dataclass(slots=True)
class DetectionResult:

    api_type: ApiType

    confidence: int

    score: int

    stars: str

    classifier: ClassificationResult | None

    fingerprint: FingerprintMatch | None

    reason: str


# ==========================================================
# DETECTOR
# ==========================================================


class ApiDetector:
    """
    Главный интеллект Toolkit.

    Использует одновременно

        • operationName
        • URL
        • GraphQL query
        • JSON schema

    После чего выбирает наиболее вероятный API.
    """

    # ------------------------------------------------------

    @classmethod
    def detect(

        cls,

        operation_name: str = "",

        url: str = "",

        graphql_query: str = "",

        response_json: Any | None = None,

    ) -> DetectionResult:

        #
        # Step 1
        # Keyword classifier
        #

        classifier = ApiClassifier.classify(

            operation_name,

            url,

            graphql_query,

        )

        #
        # Step 2
        # JSON fingerprint
        #

        fingerprint = None

        if response_json is not None:

            fingerprint = FingerprintEngine.best_match(

                ALL_FINGERPRINTS,

                response_json,

            )

        #
        # Step 3
        # Merge
        #

        api_type = classifier.api_type

        confidence = classifier.confidence

        score = classifier.score

        reason = classifier.reason

        #
        # Fingerprint may override classifier
        #

        if fingerprint is not None:

            if fingerprint.score >= score:

                score = fingerprint.score

                confidence = fingerprint.confidence

                reason = (

                    f"Matched fingerprint "

                    f"{fingerprint.fingerprint.name}"

                )

                #
                # convert fingerprint name
                #

                try:

                    api_type = ApiType(

                        fingerprint.fingerprint.name.lower()

                    )

                except Exception:

                    pass

        stars = "★" * confidence

        return DetectionResult(

            api_type=api_type,

            confidence=confidence,

            score=score,

            stars=stars,

            classifier=classifier,

            fingerprint=fingerprint,

            reason=reason,

        )

    # ------------------------------------------------------

    @classmethod
    def pretty(

        cls,

        result: DetectionResult,

    ) -> str:

        lines = [

            "",

            "=" * 60,

            "API DETECTION",

            "=" * 60,

            "",

            f"Type       : {result.api_type.value}",

            f"Score      : {result.score}",

            f"Confidence : {result.confidence}",

            f"Stars      : {result.stars}",

            "",

            f"Reason     : {result.reason}",

        ]

        if result.classifier:

            lines.extend(

                [

                    "",

                    "Keyword classifier",

                    f"  Score : {result.classifier.score}",

                    f"  Match : {result.classifier.matched_keywords}",

                ]

            )

        if result.fingerprint:

            fp = result.fingerprint

            lines.extend(

                [

                    "",

                    "Fingerprint",

                    f"  Name      : {fp.fingerprint.name}",

                    f"  Score     : {fp.score}",

                    f"  Required  : {sorted(fp.matched_required)}",

                    f"  Optional  : {sorted(fp.matched_optional)}",

                    f"  Missing   : {sorted(fp.missing_required)}",

                ]

            )

        return "\n".join(lines)