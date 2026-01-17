from io import BytesIO
from classes import State
from llama_index.core import Document
from pypdf import PdfReader
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from Postgres.repos.user_repo import UserRepos
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from agents import llm_mistral_small, llm_mistral_medium
from Postgres.repos.Chat_repo import HistoryMessages
from prompts import prompt_test_agent, prompt_for_rewrite, prompt_for_context
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, ExactMatchFilter

async def get_chunks(state: State):
    filters = MetadataFilters(
        filters=[ExactMatchFilter(
            key='user_id', value=state['user']['id']

        )]
    )

    retriever = state['query_engine'].as_retriever(
        similarity_top_k=5, vector_store_query_kwargs={
            'filters': filters
        }
    )
    nodes = await retriever.aretrieve(state['new_query'])



    chunks = [n.text for n in nodes]
    return chunks

async def from_bytes(bytes:  BytesIO, state: State):
    reader = PdfReader(bytes)
    docs = []
    for page in reader.pages:
        doc = Document(
            text=page.extract_text(),
            metadata={
                'user_id': state['user']['id'],
                'user_name': state['user']['username']
            }

        )
        docs.append(doc)
    return docs







### entry point
async def init_user(state: State)-> dict:
    pdf = 'no'
    if state['mes'].document:
        pdf = 'yes'

    user_rep = UserRepos(state['session'], state['tg_id'])
    user_orm = await user_rep.get_user()
    user = {
            'id': user_orm.id,
            'username': user_orm.username
    }
    chat = HistoryMessages(state['session'], user['id'])
    history = [SystemMessage(prompt_test_agent)] +  await chat.get_history_by_id()

    return {'user': user, 'messages': history, 'chat': chat}



async def pdf_is(state: State):
    file_id = state['mes'].document.file_id
    file = await state['bot'].get_file(file_id)
    bytes = await state['bot'].download_file(file.file_path)

    itg = await from_bytes(bytes, state)

    index = VectorStoreIndex.from_documents(documents=itg, storage_context=state['storage'])
    return {'write_in_vbd': 'done'}

async def ans(state: State):
    if state['write_in_vbd']:
        return {'output': 'Вектора добавлены'}
    else:
        return {'output': 'Вектора НЕ добавлены'}



async def just_talk(state: State):
    messages = state['messages'] + [HumanMessage(state['mes'].text)]
    result = await llm_mistral_medium.ainvoke(messages)
    answer = result.content
    await state['chat'].add_message([
        {'role': 'user', 'content': state['mes'].text},
        {'role': 'agent', 'content': answer }
    ])
    state['messages'].append(HumanMessage(state['mes'].text))
    state['messages'].append(AIMessage(answer))
    return {'output': answer}


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
    return \
        {
        'new_query': result.content
    }




