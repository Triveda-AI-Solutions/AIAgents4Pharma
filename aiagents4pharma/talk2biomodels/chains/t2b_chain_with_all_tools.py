from aiagents4pharma.llms.openai_llm import gpt4_turbo_llm as llm
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from aiagents4pharma.talk2biomodels.tools import SearchModelsTool,SimulateModelTool,AskQuestionTool,PlotImageTool,ModelDescriptionTool,CustomPlotterTool,FetchParametersTool

# Load the prompt for the main agent
with open('talk2biomodels/chains/prompts/prompt_general.txt', 'r', encoding='utf-8') as file:
    prompt_content = file.read()

assistant_prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_content),
        ("placeholder", "{messages}")
    ])

# Set the streamlit session key for the sys bio model
ST_SYS_BIOMODEL_KEY = "last_model_object"

ask_question_tool = AskQuestionTool(st_session_key=ST_SYS_BIOMODEL_KEY)
with open('talk2biomodels/chains/prompts/prompt_ask_question.txt', 'r', encoding='utf-8') as file:
    prompt_content = file.read()
ask_question_tool.metadata = {
    "prompt": prompt_content
}

model_description_tool = ModelDescriptionTool(st_session_key=ST_SYS_BIOMODEL_KEY)
with open('talk2biomodels/chains/prompts/prompt_model_description.txt', 'r', encoding='utf-8') as file:
    prompt_content = file.read()
model_description_tool.metadata = {
    "prompt": prompt_content
}


all_tools = [
    SearchModelsTool(),
    SimulateModelTool(st_session_key=ST_SYS_BIOMODEL_KEY),
    ask_question_tool,
    PlotImageTool(st_session_key=ST_SYS_BIOMODEL_KEY),
    model_description_tool,
    CustomPlotterTool(st_session_key=ST_SYS_BIOMODEL_KEY),
    FetchParametersTool(st_session_key=ST_SYS_BIOMODEL_KEY)
]
print(assistant_prompt)
t2b_chain_with_all_tools = assistant_prompt | llm.bind_tools(all_tools)