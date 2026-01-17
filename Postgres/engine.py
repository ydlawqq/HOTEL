import datetime
import os

from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine, text, Table, Column, Integer, String, MetaData, update, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from dotenv import load_dotenv


load_dotenv()
url = os.getenv('engine')

async_engine = create_async_engine(
    url='postgresql+asyncpg://ydlawq:retrofm.ru1@localhost:5432/ai_agent',
    pool_size=5,
    max_overflow=10,
    echo=False
)


async_session = async_sessionmaker(async_engine)




class DatabaseConnect:
    def __init__(self, ses: async_sessionmaker, model):
        self.session_factory = ses
        self.model = model

    async def update_or_create_user(self, **kwargs):
        telegram_id = kwargs.get('telegram_id')
        try:
            async with self.session_factory() as session:
                new_user = self.model(**kwargs)
                session.add(new_user)
                await session.commit()
        except IntegrityError:
            async with self.session_factory() as session:
                stmt = update(self.model).where(self.model.telegram_id==telegram_id).values(last_seen=datetime.datetime.now())
                await session.execute(stmt)
                await session.commit()

    async def get_user(self, tg_id):
        async with self.session_factory() as session:
            stmt = select(self.model).where(self.model.telegram_id==tg_id)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def add_to_history_bag(self, **kwargs):
        pass











