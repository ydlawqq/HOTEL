import os

from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_ollama import ChatOllama

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