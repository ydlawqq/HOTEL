from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


file_button = KeyboardButton(text="Загрузить документ")
search_button = KeyboardButton(text="Искать по вашим файлам")
main_kb = ReplyKeyboardMarkup(
    keyboard=[[file_button], [search_button]],
    resize_keyboard=True
)


class FileStates(StatesGroup):
    waiting_for_file = State()
    waiting_for_text_search = State()
    talking = State()