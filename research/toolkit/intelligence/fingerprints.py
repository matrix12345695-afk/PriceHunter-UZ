from __future__ import annotations

from .fingerprint import Fingerprint


# ==========================================================
# PRODUCT
# ==========================================================

PRODUCT = Fingerprint(

    name="Product",

    required={
        "title",
        "price",
    },

    optional={
        "seller",
        "images",
        "rating",
        "reviews",
        "sku",
        "stock",
        "brand",
        "currency",
        "discount",
        "oldPrice",
        "description",
    },
)


# ==========================================================
# SEARCH
# ==========================================================

SEARCH = Fingerprint(

    name="Search",

    required={
        "items",
    },

    optional={
        "products",
        "pagination",
        "total",
        "page",
        "pages",
        "filters",
        "sort",
        "facets",
        "count",
        "query",
    },
)


# ==========================================================
# CATEGORY
# ==========================================================

CATEGORY = Fingerprint(

    name="Category",

    required={
        "categories",
    },

    optional={
        "children",
        "parent",
        "slug",
        "name",
        "icon",
        "image",
    },
)


# ==========================================================
# REVIEW
# ==========================================================

REVIEW = Fingerprint(

    name="Review",

    required={
        "rating",
    },

    optional={
        "comment",
        "author",
        "photos",
        "likes",
        "date",
        "feedback",
        "text",
    },
)


# ==========================================================
# CART
# ==========================================================

CART = Fingerprint(

    name="Cart",

    required={
        "items",
    },

    optional={
        "total",
        "price",
        "quantity",
        "discount",
        "delivery",
        "coupon",
    },
)


# ==========================================================
# FAVORITES
# ==========================================================

FAVORITES = Fingerprint(

    name="Favorites",

    required={
        "favorites",
    },

    optional={
        "items",
        "count",
        "productId",
    },
)


# ==========================================================
# RECOMMENDATIONS
# ==========================================================

RECOMMENDATIONS = Fingerprint(

    name="Recommendations",

    required={
        "products",
    },

    optional={
        "similar",
        "recommended",
        "popular",
        "related",
        "items",
    },
)


# ==========================================================
# SELLER
# ==========================================================

SELLER = Fingerprint(

    name="Seller",

    required={
        "seller",
    },

    optional={
        "name",
        "rating",
        "reviews",
        "address",
        "phone",
        "verified",
    },
)


# ==========================================================
# ORDER
# ==========================================================

ORDER = Fingerprint(

    name="Order",

    required={
        "orderId",
    },

    optional={
        "status",
        "delivery",
        "payment",
        "items",
        "price",
    },
)


# ==========================================================
# PAYMENT
# ==========================================================

PAYMENT = Fingerprint(

    name="Payment",

    required={
        "payment",
    },

    optional={
        "amount",
        "currency",
        "invoice",
        "status",
        "provider",
    },
)


# ==========================================================
# USER
# ==========================================================

USER = Fingerprint(

    name="User",

    required={
        "user",
    },

    optional={
        "id",
        "name",
        "email",
        "phone",
        "avatar",
    },
)


# ==========================================================
# ALL
# ==========================================================

ALL_FINGERPRINTS = [

    PRODUCT,

    SEARCH,

    CATEGORY,

    REVIEW,

    CART,

    FAVORITES,

    RECOMMENDATIONS,

    SELLER,

    ORDER,

    PAYMENT,

    USER,

]