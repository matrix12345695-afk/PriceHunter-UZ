from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class SearchState(StatesGroup):
    """
    Состояния поиска товаров.
    """

    waiting_query = State()
    viewing_results = State()
    viewing_product = State()