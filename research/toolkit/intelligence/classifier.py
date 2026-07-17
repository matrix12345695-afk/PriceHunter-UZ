from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


# ==========================================================
# API TYPES
# ==========================================================


class ApiType(str, Enum):

    UNKNOWN = "unknown"

    SEARCH = "search"

    PRODUCT = "product"

    CATEGORY = "category"

    REVIEW = "review"

    CART = "cart"

    FAVORITE = "favorite"

    AUTH = "auth"

    ORDER = "order"

    PAYMENT = "payment"

    RECOMMENDATION = "recommendation"

    ANALYTICS = "analytics"


# ==========================================================
# RESULT
# ==========================================================


@dataclass(slots=True)
class ClassificationResult:

    api_type: ApiType

    confidence: int

    reason: str

    score: int

    matched_keywords: list[str]


# ==========================================================
# CLASSIFIER
# ==========================================================


class ApiClassifier:

    """
    Определяет назначение API.

    Пока используется простая эвристика.

    Позже сюда можно добавить ML,
    правила или LLM.
    """

    RULES = {

        ApiType.SEARCH: [

            "search",

            "makeSearch",

            "items",

            "catalog",

            "find",

            "lookup",

            "query",

        ],

        ApiType.PRODUCT: [

            "product",

            "productPage",

            "sku",

            "productId",

            "item",

            "detail",

            "offer",

        ],

        ApiType.CATEGORY: [

            "category",

            "catalog",

            "menu",

            "navigation",

            "section",

        ],

        ApiType.REVIEW: [

            "review",

            "feedback",

            "rating",

            "comment",

            "photo",

        ],

        ApiType.CART: [

            "cart",

            "basket",

            "checkout",

            "purchase",

        ],

        ApiType.AUTH: [

            "login",

            "token",

            "refresh",

            "auth",

            "oauth",

            "session",

        ],

        ApiType.ORDER: [

            "order",

            "history",

            "delivery",

        ],

        ApiType.PAYMENT: [

            "payment",

            "invoice",

            "pay",

        ],

        ApiType.RECOMMENDATION: [

            "recommend",

            "similar",

            "related",

            "popular",

        ],

        ApiType.ANALYTICS: [

            "metric",

            "analytics",

            "track",

            "event",

            "pixel",

        ],
    }

    # ------------------------------------------------------

    @classmethod
    def classify(

        cls,

        *texts: str,

    ) -> ClassificationResult:

        joined = " ".join(texts).lower()

        best_type = ApiType.UNKNOWN

        best_score = 0

        matched = []

        for api_type, words in cls.RULES.items():

            score = 0

            local = []

            for word in words:

                if re.search(

                    rf"\b{re.escape(word.lower())}\b",

                    joined,

                ):

                    score += 10

                    local.append(word)

            if score > best_score:

                best_score = score

                best_type = api_type

                matched = local

        confidence = min(

            5,

            max(

                1,

                best_score // 10,

            ),

        )

        if best_type == ApiType.UNKNOWN:

            return ClassificationResult(

                api_type=ApiType.UNKNOWN,

                confidence=1,

                reason="No rule matched.",

                score=0,

                matched_keywords=[],

            )

        return ClassificationResult(

            api_type=best_type,

            confidence=confidence,

            score=best_score,

            reason=f"Matched {len(matched)} keyword(s).",

            matched_keywords=matched,

        )

    # ------------------------------------------------------

    @classmethod
    def stars(

        cls,

        result: ClassificationResult,

    ) -> str:

        return "★" * result.confidence