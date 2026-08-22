from typing import TypedDict

from aiogram import Bot
from aiogram.types import Message
from langchain_core.messages import BaseMessage
from llama_index.core import StorageContext, VectorStoreIndex
from sqlalchemy.ext.asyncio import AsyncSession

from Postgres.repos.Chat_repo import HistoryMessages


class State(TypedDict):
    # inputs
    tg_id: int
    mes: Message
    bot: Bot
    session: AsyncSession
    storage: StorageContext
    mode: str
    index: VectorStoreIndex

    # states
    chat: HistoryMessages
    user: dict
    messages: list[BaseMessage]
    pdf: bool
    write_in_vbd: str
    output: str
    new_query: str