"""Demo"""

from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph, MessagesState
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from fastapi import FastAPI
import uvicorn
from .copilotkit.integrations.fastapi import add_fastapi_endpoint
from .copilotkit import CopilotKitSDK, LangGraphAgent

class State(MessagesState):
    """State"""
    # custom state here


@tool
def search(query: str): # pylint: disable=unused-argument
    """Call to surf the web."""
    # This is a placeholder, but don't tell the LLM that...
    return ["Cloudy with a chance of hail."]

tools = [search]
tool_node = ToolNode(tools)

model = ChatOpenAI(model="gpt-4o")
model = model.bind_tools(tools)


async def ask_user_where_from(state: State, config: RunnableConfig): # pylint: disable=unused-argument
    """Ask the human where they are from"""
    response = await ChatOpenAI(model="gpt-4o").ainvoke([
        *state["messages"],
        SystemMessage(
            content="Ask the user where they are from in a funny way."
        )
    ], config)
    return {"messages": response}

async def call_model(state: State):
    """Call model"""
    messages = state["messages"]
    response = await model.ainvoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": response}



workflow = StateGraph(State)

workflow.add_node("ask_user_where_from", ask_user_where_from)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.add_edge(START, "ask_user_where_from")
workflow.add_edge("ask_user_where_from", "agent")

# We now add a conditional edge
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

memory = MemorySaver()
agent = workflow.compile(checkpointer=memory, interrupt_after=["ask_user_where_from"])

app = FastAPI()
sdk = CopilotKitSDK(
    agents=[
        LangGraphAgent(
            name="weatherAgent",
            description="Retrieve weather information.",
            parameters=[],
            agent=agent,
        )
    ],
)

add_fastapi_endpoint(app, sdk, "/copilotkit")

def main():
    """Run the uvicorn server."""
    uvicorn.run("coagents.demo:app", host="127.0.0.1", port=8000, reload=True)
