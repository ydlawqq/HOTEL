
from sqlalchemy.ext.asyncio import AsyncSession
from Postgres.models import Users
from sqlalchemy import update, select
from sqlalchemy.dialects.postgresql import insert
import datetime

class UserRepos:
    def __init__(self, session: AsyncSession, tg_id):
        self.session = session
        self.tg_id = tg_id

    async def upsert_user(self, **kwargs):
        telegram_id = kwargs.get('telegram_id')
        stmt = insert(Users).values(**kwargs).on_conflict_do_update(index_elements=[Users.telegram_id], set_={
            'last_seen': datetime.datetime.now(datetime.timezone.utc)
        })
        await self.session.execute(stmt)

    async def get_user(self):
        stmt = select(Users).where(Users.telegram_id == self.tg_id)
        result = await self.session.execute(stmt) #only 1 user
        user = result.scalars().first()
        # user.att = new att
        return user




