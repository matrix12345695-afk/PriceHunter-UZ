from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Fingerprint:
    """
    Описание отпечатка API.

    required:
        Поля, которые должны присутствовать.

    optional:
        Поля, повышающие уверенность.

    forbidden:
        Поля, снижающие вероятность совпадения.
    """

    name: str

    required: set[str] = field(default_factory=set)

    optional: set[str] = field(default_factory=set)

    forbidden: set[str] = field(default_factory=set)

    weight: int = 100


@dataclass(slots=True)
class FingerprintMatch:

    fingerprint: Fingerprint

    score: int

    matched_required: set[str]

    matched_optional: set[str]

    missing_required: set[str]

    forbidden_found: set[str]

    @property
    def success(self) -> bool:
        return len(self.missing_required) == 0

    @property
    def confidence(self) -> int:

        if self.score >= 95:
            return 5

        if self.score >= 80:
            return 4

        if self.score >= 60:
            return 3

        if self.score >= 40:
            return 2

        return 1

    @property
    def stars(self) -> str:
        return "★" * self.confidence


class FingerprintEngine:
    """
    Универсальный движок сравнения JSON
    с отпечатками API.
    """

    @staticmethod
    def flatten(
        obj: Any,
        result: set[str] | None = None,
    ) -> set[str]:

        if result is None:
            result = set()

        if isinstance(obj, dict):

            for key, value in obj.items():

                result.add(str(key))

                FingerprintEngine.flatten(
                    value,
                    result,
                )

        elif isinstance(obj, list):

            for item in obj:

                FingerprintEngine.flatten(
                    item,
                    result,
                )

        return result

    @classmethod
    def match(
        cls,
        fingerprint: Fingerprint,
        json_data: Any,
    ) -> FingerprintMatch:

        keys = cls.flatten(json_data)

        matched_required = (
            fingerprint.required & keys
        )

        missing_required = (
            fingerprint.required - keys
        )

        matched_optional = (
            fingerprint.optional & keys
        )

        forbidden_found = (
            fingerprint.forbidden & keys
        )

        score = 0

        #
        # Required
        #

        if fingerprint.required:

            score += int(
                len(matched_required)
                / len(fingerprint.required)
                * 70
            )

        #
        # Optional
        #

        if fingerprint.optional:

            score += int(
                len(matched_optional)
                / len(fingerprint.optional)
                * 30
            )

        #
        # Forbidden
        #

        score -= len(
            forbidden_found
        ) * 10

        score = max(
            0,
            min(
                100,
                score,
            ),
        )

        return FingerprintMatch(
            fingerprint=fingerprint,
            score=score,
            matched_required=matched_required,
            matched_optional=matched_optional,
            missing_required=missing_required,
            forbidden_found=forbidden_found,
        )

    @classmethod
    def best_match(
        cls,
        fingerprints: list[Fingerprint],
        json_data: Any,
    ) -> FingerprintMatch | None:

        best = None

        for fp in fingerprints:

            result = cls.match(
                fp,
                json_data,
            )

            if (
                best is None
                or result.score > best.score
            ):
                best = result

        return best