from aiagents4pharma.llms.openai_llm import gpt4_turbo_llm as llm
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from aiagents4pharma.talk2biomodels.tools.search_models import SearchModelsTool

# Load the prompt for the main agent
with open('talk2biomodels/chains/prompts/prompt_general.txt', 'r', encoding='utf-8') as file:
    prompt_content = file.read()

assistant_prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_content),
        ("placeholder", "{messages}")
    ])

all_tools = [
    SearchModelsTool()
]
print(assistant_prompt)
t2b_chain_with_all_tools = assistant_prompt | llm.bind_tools(all_tools)