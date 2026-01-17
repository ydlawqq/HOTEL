from Postgres.models import Documents
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, update, values

class DocumentsRepo:
    def __init__(self, session: AsyncSession):
        self.session= session


    async def add_document(self, **kwargs):
        stmt= insert(Documents).values(**kwargs)
        await self.session.execute(stmt)




