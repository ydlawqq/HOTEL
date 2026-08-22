from io import BytesIO

from llama_index.core import Document
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters
from pypdf import PdfReader

from .classes import State


def text_editor(text: str):
    if not text:
        return ''
    text = text.encode('utf-8').decode('unicode_escape').replace("\xa0", " ").strip()
    return text


async def get_chunks(state: State):
    filters = MetadataFilters(
        filters=[ExactMatchFilter(
            key='user_id', value=state['user']['id']
        )]
    )
    retriever = state['index'].as_retriever(
        similarity_top_k=3,
        vector_store_query_kwargs={
            'filters': filters,
        },
        mmr_kwargs={
            'k': 3,
            'fetch_k': 10,
        }
    )
    nodes = await retriever.aretrieve(state['new_query'])

    chunks = [n.text for n in nodes]
    return chunks


async def from_bytes(bytes: BytesIO, state: State) -> list[Document]:
    reader = PdfReader(bytes)
    docs = []
    for page in reader.pages:
        text = page.extract_text()
        if not text or not text.strip():
            continue
        doc = Document(
            text=text,
            metadata={
                'user_id': state['user']['id'],
                'user_name': state['user']['username']
            }
        )
        docs.append(doc)
    return docs