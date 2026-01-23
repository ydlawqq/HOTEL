from io import BytesIO
from .classes import State
from llama_index.core import Document
from pypdf import PdfReader
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter




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
        search_type='mmr',
      vector_store_query_kwargs={
            'filters': filters,
            'k': 3, 'fetch_k': 10
        }
    )
    nodes = await retriever.aretrieve(state['new_query'])



    chunks = [n.text for n in nodes]
    return chunks

async def from_bytes(bytes:  BytesIO, state: State)-> list[Document]:
    reader = PdfReader(bytes) ## найти нормальный пдф парсер!
    docs = []
    for page in reader.pages:
        text = page.extract_text()
        doc = Document(
            text=text,
            metadata={
                'user_id': state['user']['id'],
                'user_name': state['user']['username']
            }

        )
        docs.append(doc)
    return docs
