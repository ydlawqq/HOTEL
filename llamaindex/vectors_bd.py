import os

from dotenv import load_dotenv
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.embeddings.mistralai import MistralAIEmbedding
from llama_index.llms.mistralai import MistralAI
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import AsyncQdrantClient, QdrantClient
from qdrant_client.models import Distance, VectorParams

load_dotenv()

api = os.getenv('mistral')
qdrant_url = os.getenv('QDRANT_URL', 'http://127.0.0.1:6333')

emb = MistralAIEmbedding(api_key=api, model_name='mistral-embed')

Settings.embed_model = emb
Settings.llm = MistralAI(api_key=api, model='mistral-medium-latest')

aqclient = AsyncQdrantClient(url=qdrant_url)
qclient = QdrantClient(url=qdrant_url)

vectorstore = QdrantVectorStore(
    aclient=aqclient,
    client=qclient,
    collection_name='docs',
)


async def create_storage_context():
    if not await aqclient.collection_exists("docs"):
        await aqclient.create_collection(
            collection_name="docs",
            vectors_config=VectorParams(
                size=1024,  # размер эмбеддингов вашей модели
                distance=Distance.COSINE,
            )
        )
    return StorageContext.from_defaults(vector_store=vectorstore)


async def create_index_query(context):
    return VectorStoreIndex.from_vector_store(
        vector_store=vectorstore,
        storage_context=context,
    )