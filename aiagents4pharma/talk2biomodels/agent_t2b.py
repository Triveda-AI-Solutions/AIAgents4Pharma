from langchain_core.runnables import Runnable
from aiagents4pharma.agent_state.t2b_state import T2bState


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

from chains import t2b_chain_with_all_tools, all_tools



assistant_with_all_tools_instance = AssistantBaseClass(t2b_chain_with_all_tools)
    
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition
from aiagents4pharma.agent_state.t2b_state import T2bState as State

builder = StateGraph(State)


# Define nodes: these do the work
builder.add_node("single_agent", assistant_with_all_tools_instance)
builder.add_node("tools", create_tool_node_with_fallback(all_tools))
# Define edges: these determine how the control flow moves
builder.add_edge(START, "single_agent")
builder.add_conditional_edges(
    "single_agent",
    tools_condition,
)
builder.add_edge("tools", "single_agent")

memory = MemorySaver()
app = builder.compile(checkpointer=memory)