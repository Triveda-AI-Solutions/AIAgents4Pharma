import sys
import os
current_dir = os.path.dirname(__file__)
package_path = os.path.join(current_dir, "..", "..")
package_path = os.path.abspath(os.path.normpath(package_path))
sys.path.append(package_path)

from langchain_core.runnables import Runnable
from aiagents4pharma.agent_state import T2bState
import json

class AssistantBaseClass:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: T2bState):
        while True:
            result = self.runnable.invoke(state)
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}

from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode

def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }

def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )

def tool_message_formatter(tool_output: str) -> dict:
    return json.loads(tool_output["messages"][-1].content)

from aiagents4pharma.talk2biomodels.chains import t2b_chain_with_all_tools, all_tools

assistant_with_all_tools_instance = AssistantBaseClass(t2b_chain_with_all_tools)
    
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition
from aiagents4pharma.agent_state.t2b_state import T2bState

builder = StateGraph(T2bState)


# Define nodes: these do the work
builder.add_node("t2b_agent", assistant_with_all_tools_instance)
builder.add_node("tools", create_tool_node_with_fallback(all_tools))
builder.add_node("format_message", tool_message_formatter)

# Define edges: these determine how the control flow moves
builder.add_edge(START, "t2b_agent")
builder.add_edge(
    "t2b_agent",
    "tools",
)
builder.add_edge("tools", "format_message")
builder.add_edge("format_message", END)

memory = MemorySaver()
app = builder.compile(checkpointer=memory)