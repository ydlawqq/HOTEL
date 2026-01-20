from typing import TypedDict, Optional
from aiogram.types import Message
from aiogram import Bot
from langchain_core.messages.human import BaseMessage, HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession
from llama_index.core import StorageContext, VectorStoreIndex
from Postgres.repos.Chat_repo import HistoryMessages




class State(TypedDict):
    #inputs
    tg_id: int
    input: HumanMessage
    mes: Message
    bot: Bot
    session: AsyncSession
    storage: StorageContext
    mode: str
    index: VectorStoreIndex

    #states
    chat: HistoryMessages
    user: dict
    messages: list[BaseMessage]
    pdf: bool
    write_in_vbd: str
    output: str
    new_query: str







