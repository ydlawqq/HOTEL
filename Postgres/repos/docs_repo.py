from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from Postgres.models import Documents


class DocumentsRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_document(self, **kwargs):
        stmt = insert(Documents).values(**kwargs)
        await self.session.execute(stmt)