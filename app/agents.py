from langchain_core.messages.human import HumanMessage
from langchain_core.messages.system import SystemMessage
from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from dotenv import load_dotenv
import os
load_dotenv()

api = os.getenv('mistral')


### LLMs
llm_mistral_small = ChatMistralAI(
    model_name='mistral-small',
    api_key=api
)
llm_mistral_medium = ChatMistralAI(
    model_name='mistral-large-latest',
    api_key=api

)


llm_ollama = ChatOllama(
    model='llama3.2:3b'
)

embedding = MistralAIEmbeddings(
    api_key=api, model='mistral-embed'
)



### CHAINS





#res = simple_chain_v1.invoke({'input': 'Привет', 'history': ''})






