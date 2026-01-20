import datetime
import os
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, Update
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from fastapi import FastAPI
from fastapi.requests import Request

import uvicorn
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from Postgres.engine import async_session
from Postgres.repos.user_repo import UserRepos
from app.graph_main import graph

from llamaindex.vectors_bd import create_storage_context, create_index_query

from app.utils.some_attributs_for_bot import main_kb, FileStates
load_dotenv()


token = os.getenv('token_tg')

bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
l = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    url_webhook = 'https://shiny-news-lay.loca.lt' + '/webhook'
    await bot.set_webhook(url_webhook, allowed_updates=dp.resolve_used_update_types(), drop_pending_updates=True)
    app.state.graph = graph.compile()
    app.state.storage = await create_storage_context()
    app.state.index = create_index_query(app.state.storage)
    yield
    await bot.delete_webhook()
    l.clear()


app = FastAPI(lifespan=lifespan)

#app.mount('/static', StaticFiles(directory='static'), name='static')
#templates = Jinja2Templates(directory='templates')

async def graph_inv(mes: Message, session, state: FSMContext):
    return await app.state.graph.ainvoke({'tg_id': mes.from_user.id, 'mes': mes,
                                                'bot': bot, 'session': session, 'storage': app.state.storage, 'index': app.state.index, 'mode': await state.get_state()})




@dp.message(CommandStart())
async def start(mes: Message, state: FSMContext):
    await state.set_state(FileStates.talking)
    user_id = mes.from_user.id
    user_name = mes.from_user.first_name
    async with async_session() as session:
        user_class = UserRepos(session, user_id)
        await user_class.upsert_user(telegram_id=user_id, username=user_name, last_seen=datetime.datetime.now(datetime.timezone.utc))
        user = await user_class.get_user()
        await session.commit()


    resp = f'Привет {user_name}, я бот для суммаризации PDF'
    await mes.answer(resp, parse_mode=None, reply_markup=main_kb)


@dp.message(lambda mes: mes.text == "Загрузить документ")
async def ask_file(mes: Message, state: FSMContext):
    await mes.answer("Отлично! Пришли мне файл")
    await state.set_state(FileStates.waiting_for_file)


@dp.message(lambda mes: mes.text == "Искать по вашим файлам")
async def ask_text(mes: Message, state: FSMContext):
    await mes.answer("Что будем искать?")
    await state.set_state(FileStates.waiting_for_text_search)


@dp.message(FileStates.waiting_for_file)
async def handle_file(mes: Message, state: FSMContext):
    if mes.document:
        async with async_session() as session:
            result = await graph_inv(mes, session, state=state)

        await mes.answer(result['output'])
        await state.set_state(FileStates.talking)
    else:
        await mes.answer('Пришлите документ. Только pdf.')


@dp.message(FileStates.waiting_for_text_search)
async def text_for_search(mes: Message, state: FSMContext):
    async with async_session() as session:
        result = await graph_inv(mes, session, state=state)


    await mes.answer(result['output'])
    await state.set_state(FileStates.talking)


@dp.message(FileStates.talking)
async def all(mes: Message, state: FSMContext):
    async with async_session() as session:
        result = await graph_inv(mes, session, state=state)

        await session.commit()

    await mes.answer(result['output'])


    '''text = mes.text
    async with async_session() as session:
        user_ = UserRepos(session)
        user = await user_.get_user_by_tg_id(mes.from_user.id)

        history = HistoryMessages(session)
        chat_history = await history.get_history_by_id(user.id)
        response = agent_chain.invoke({
            'input': text, 'history': chat_history
        })

        await history.add_message(user_id=user.id, content=text, role='user')
        await history.add_message(user_id=user.id, content=response.content, role='agent')

        await session.commit()

    await mes.answer(response.content)'''







@app.post("/webhook")
async def webhook(request: Request) -> None:
    update = Update.model_validate(await request.json(), context={'bot': bot})
    await dp.feed_update(bot, update)


if __name__ == '__main__':
    uvicorn.run(app,host='0.0.0.0', port=8000 )