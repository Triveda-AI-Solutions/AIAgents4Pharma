from aiagents4pharma.llms.openai_llm import gpt4_turbo_llm as llm
from langchain_core.prompts import ChatPromptTemplate
from aiagents4pharma.talk2biomodels.tools import SearchModelsTool,SimulateModelTool,AskQuestionTool,PlotImageTool,ModelDescriptionTool,CustomPlotterTool,FetchParametersTool

from aiagents4pharma.talk2biomodels.chains.prompts import prompt_general, prompt_ask_question, prompt_model_description

assistant_prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_general),
        ("placeholder", "{messages}")
    ])

# Set the streamlit session key for the sys bio model
ST_SYS_BIOMODEL_KEY = "last_model_object"

ask_question_tool = AskQuestionTool(st_session_key=ST_SYS_BIOMODEL_KEY)
ask_question_tool.metadata = {
    "prompt": prompt_ask_question
}

model_description_tool = ModelDescriptionTool()
model_description_tool.metadata = {
    "prompt": prompt_model_description
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
t2b_chain_with_all_tools = assistant_prompt | llm.bind_tools(all_tools)