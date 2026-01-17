
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text, Text, Time, TIMESTAMP, Enum, CheckConstraint, BigInteger
import datetime


class Base(DeclarativeBase):
    pass



class Users(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger,nullable=False, unique=True)
    username: Mapped[str] = mapped_column()
    first_seen_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_seen: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True))

    messages: Mapped[list["Chat"]] = relationship(
        back_populates='user', cascade='all, delete-orphan'
    )
    documents: Mapped["Documents"] = relationship(back_populates='user')

class Chat(Base):
    __tablename__= 'messages'
    __table_args__ = (CheckConstraint(
        "role IN ('user', 'assistant', 'system')", name='valid_role'
    ),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20) , nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))

    user: Mapped["Users"] = relationship(
        back_populates='messages'
    )

class Documents(Base):
    __tablename__ = 'documents'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))
    summarize: Mapped[str] = mapped_column(nullable=False)
    added_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))

    user: Mapped["Users"] = relationship(back_populates='documents')



'''class ResumeOrm(Base):
    __tablename__ = 'resumes'
    id: Mapped[int] = mapped_column(primary_key=True)
    worker_id: Mapped[int] = mapped_column(ForeignKey(
        'workers.id', ondelete="CASCADE"
    ))
    title: Mapped[str]
    age: Mapped[int]
    solary: Mapped[int | None]
    workload: Mapped[Workload]
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc'  , NOW())"))

    worker: Mapped[list["WorkersOrm"]] = relationship(back_populates='resumes')
'''


'''async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)'''


'''async def z():
    await create_table()
    async with async_session_factory() as session:
        worker_bobr = WorkersOrm(username='Bobr')
        session.add(worker_bobr)
        bobr_resume = ResumeOrm(worker=worker_bobr ,title='С++ Разраб', age=11, solary=30000, workload=Workload.fulltime)
        session.add(bobr_resume)
        await session.commit()'''


