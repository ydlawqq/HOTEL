
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext
from llama_index.llms.mistralai import MistralAI
from llama_index.embeddings.mistralai import MistralAIEmbedding
import os
from qdrant_client import QdrantClient, models, AsyncQdrantClient
from qdrant_client.models import VectorParams
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv
load_dotenv()

api = os.getenv('mistral')


emb = MistralAIEmbedding(api_key=api, model_name='mistral-embed')



Settings.embed_model = emb
Settings.llm = MistralAI(api_key=api, model='mistral-medium-latest')

aqclient = AsyncQdrantClient(
        url='http://127.0.0.1:6333',
    )

qclient = QdrantClient(
    url='http://127.0.0.1:6333'
)

vectorstore = QdrantVectorStore(
        aclient=aqclient,
        client=qclient,
        collection_name='docs',
    )


async def create_storage_context():
    try:
        await aqclient.get_collection("docs")
    except Exception:    # напрямую проверяем
            await aqclient.create_collection(
            collection_name="docs",
            vectors_config=VectorParams(
                size=1024,  # размер эмбеддингов вашей модели
                distance=models.Distance.COSINE,
            )
        )

    return StorageContext.from_defaults(vector_store=vectorstore)





async def create_index_query(context):
    return  VectorStoreIndex.from_vector_store(vector_store=vectorstore,
                                               storage_context=context)




'''async def get_chunks():
    filters = MetadataFilters(
        filters=[ExactMatchFilter(
            key='user_id', value=46

        )]
    )
    index = await create_index_query()
    retriever = index.as_retriever(
        similarity_top_k=5, vector_store_query_kwargs={
            'filters': filters
        }
    )
    nodes = await retriever.aretrieve('Дженерики')



    chunks = [n.text for n in nodes]
    return chunks



async def s():
    z = await get_chunks()
    print(z)

'''


#d = Document(text=t, metadata={'user_id': 333})

#i = create_storage_context()

#index = VectorStoreIndex.from_documents(documents=[d], storage_context=i)







'''
llm = MistralAI(
    model='mistral-small-latest',
    api_key=api

)
embed = MistralAIEmbedding(
    model='mistral-embed',
    api_key=api
)

Settings.llm = llm
Settings.embed_model = embed


documents = SimpleDirectoryReader("/home/ydlawq/p313/HOTEL/files").load_data()



vectorstore = QdrantVectorStore(
    client=qclient,
    collection_name='docs',
)

storage_context = StorageContext.from_defaults(vector_store=vectorstore)

index = VectorStoreIndex.from_documents(documents=documents, storage_context=storage_context)


query_engine = index.as_query_engine()

response = query_engine.query("Что такое дженерики?")


'''

