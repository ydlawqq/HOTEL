from io import BytesIO

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter

from Postgres.repos.Chat_repo import HistoryMessages
from Postgres.repos.user_repo import UserRepos
from app.nodes.agents import llm_mistral_medium, llm_mistral_small
from app.utils.classes import State
from app.utils.prompts import prompt_for_context, prompt_for_rewrite, prompt_test_agent
from app.utils.support_functions import from_bytes, get_chunks


parser = SentenceSplitter(
    chunk_size=1024,
    chunk_overlap=200
)


### entry point
async def init_user(state: State) -> dict:
    user_rep = UserRepos(state['session'], state['tg_id'])
    user_orm = await user_rep.get_user()
    user = {
        'id': user_orm.id,
        'username': user_orm.username
    }
    chat = HistoryMessages(state['session'], user['id'])
    history = [SystemMessage(prompt_test_agent)] + await chat.get_history_by_id()

    return {'user': user, 'messages': history, 'chat': chat}


async def pdf_is(state: State):
    file_id = state['mes'].document.file_id
    file = await state['bot'].get_file(file_id)
    bytes = await state['bot'].download_file(file.file_path)

    docs = await from_bytes(bytes, state)
    if not docs:
        return {'output': 'Не удалось извлечь текст из PDF. Файл повреждён или не содержит текста.'}

    index: VectorStoreIndex = state['index']
    nodes = await parser.aget_nodes_from_documents(docs)
    await index.ainsert_nodes(nodes)

    return {'write_in_vbd': 'done'}


async def ans(state: State):
    if state.get('write_in_vbd'):
        return {'output': 'Вектора добавлены'}
    else:
        return {'output': 'Вектора НЕ добавлены'}


async def just_talk(state: State):
    history = state['messages'] + [HumanMessage(state['mes'].text)]
    result = await llm_mistral_medium.ainvoke(history)
    answer = result.content
    await state['chat'].add_message([
        {'role': 'user', 'content': state['mes'].text},
        {'role': 'agent', 'content': answer}
    ])
    return {
        'output': answer,
        'messages': state['messages'] + [HumanMessage(state['mes'].text), AIMessage(answer)],
    }


async def search_in_documents(state: State):
    context = await get_chunks(state)
    prompt = await prompt_for_context.ainvoke({'input': state['mes'].text, 'context': context})
    response = await llm_mistral_medium.ainvoke(prompt)

    return {
        'output': response.content
    }


async def rewrite_query(state: State):
    messages = [SystemMessage(prompt_for_rewrite), HumanMessage(state['mes'].text)]
    result = await llm_mistral_small.ainvoke(messages)
    return {
        'new_query': result.content
    }