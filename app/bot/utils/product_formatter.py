from __future__ import annotations

from app.models.product import Product


def format_price(price: int | None) -> str:
    """
    Красивое форматирование цены.
    """

    if price is None:
        return "Не указана"

    return f"{price:,}".replace(",", " ")


def format_product(product: Product) -> str:
    """
    Формирует красивую карточку товара.
    """

    text = []

    text.append(f"📦 <b>{product.title}</b>")
    text.append("")

    #
    # Цена
    #

    if product.current_price is not None:

        price = format_price(product.current_price)

        currency = product.currency or ""

        text.append(f"💰 <b>{price} {currency}</b>")

    else:

        text.append("💰 Цена неизвестна")

    #
    # Магазин
    #

    if product.store:

        text.append(f"🏪 {product.store.name}")

    #
    # Скидка
    #

    if product.has_discount:

        text.append("")

        text.append(
            f"🔥 Скидка {product.discount_percent}%"
        )

        text.append(
            f"💸 Экономия {format_price(product.discount_amount)} {product.currency}"
        )

    #
    # Ссылка
    #

    if product.url:

        text.append("")

        text.append(
            f"🔗 {product.url}"
        )

    return "\n".join(text)