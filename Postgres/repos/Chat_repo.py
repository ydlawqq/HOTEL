import time

from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import HumanMessage, AIMessage
from sqlalchemy import insert, select
from Postgres.models import Chat


class HistoryMessages:
    def __init__(self, session: AsyncSession, user_id: int):
        self.session = session
        self.user_id = user_id

    async def add_message(self, messages:list[dict]):
        stmt = insert(Chat)
        values = [
            {**msg, 'user_id': self.user_id} for msg in messages
        ]
        await self.session.execute(stmt, values)

    async def get_history_by_id(self)-> list:

        stmt = select(Chat.role, Chat.content).where(Chat.user_id==self.user_id).order_by(Chat.created_at.desc()).limit(10)
        result = await self.session.execute(stmt)
        return [HumanMessage(content) if role=='user' else AIMessage(content) for role, content in reversed(result.fetchall())]









