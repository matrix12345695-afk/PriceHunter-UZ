from aiogram.filters.callback_data import CallbackData


# ============================
# Товар
# ============================

class ProductCallback(CallbackData, prefix="product"):
    """
    Открыть карточку товара.
    """

    product_id: int


# ============================
# История цен
# ============================

class HistoryCallback(CallbackData, prefix="history"):
    """
    История изменения цены.
    """

    product_id: int


# ============================
# Подписка
# ============================

class SubscribeCallback(CallbackData, prefix="subscribe"):
    """
    Подписаться / отписаться.
    """

    product_id: int


# ============================
# Навигация
# ============================

class NavigationCallback(CallbackData, prefix="nav"):
    """
    Универсальная навигация.

    page:
        search
        product
        history
        profile
        settings
        subscriptions
    """

    page: str

    product_id: int = 0

    offset: int = 0


# ============================
# Пагинация
# ============================

class PaginationCallback(CallbackData, prefix="page"):
    """
    Листание страниц.
    """

    page: int


# ============================
# Избранное
# ============================

class FavoriteCallback(CallbackData, prefix="favorite"):
    """
    Добавить / удалить избранное.
    """

    product_id: int


# ============================
# Сравнение
# ============================

class CompareCallback(CallbackData, prefix="compare"):
    """
    Добавить товар в сравнение.
    """

    product_id: int