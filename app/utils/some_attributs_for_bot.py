from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, Update
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode




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
