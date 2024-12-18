from langchain_openai import ChatOpenAI
from environs import Env
env = Env()
env.read_env("./.env")
gpt4_turbo_llm = ChatOpenAI(model="gpt-4-turbo-preview")