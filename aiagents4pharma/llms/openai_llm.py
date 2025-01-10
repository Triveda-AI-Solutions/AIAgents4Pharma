from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()
gpt4_turbo_llm = ChatOpenAI(model="gpt-4-turbo-preview")