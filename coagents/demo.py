"""Demo"""

from typing import TypedDict
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
from .copilotkit import CopilotKitSDK, LangGraphAgent, CopilotKitState
from .copilotkit.langchain import configure_copilotkit

class State(MessagesState):
    """State"""
    location: str
    copilotkit: CopilotKitState


class LocationData(TypedDict):
    """Data structure for user location data"""
    location: str

@tool()
def search(query: str): # pylint: disable=unused-argument
    """Call to surf the web."""
    # This is a placeholder, but don't tell the LLM that...
    return "Cloudy with a chance of hail."


tools = [search]
tool_node = ToolNode(tools)

def check_location(state: State, config: RunnableConfig):
    """Check the location"""
    model = ChatOpenAI(model="gpt-4o").bind_tools([LocationData], tool_choice="LocationData")

    response = model.invoke([
        *state["messages"],
        SystemMessage(
            content=("We want to know where the user is from. " +
                     "Try to figure out the location from the user's messages if " +
                     "possible. Otherwise, set it to unknown.")
        )
    ], config)
    try:
        location = response.tool_calls[0]['args']['location']
        return {"location": location} if location != 'unknown' else None
    except (IndexError, KeyError):
        return None

async def ask_user_location(state: State, config: RunnableConfig): # pylint: disable=unused-argument
    """Ask the human where they are from"""
    config = configure_copilotkit(config, emit_messages=True)

    response = await ChatOpenAI(model="gpt-4o").ainvoke([
        *state["messages"],
        SystemMessage(
            content="Ask the user where they are from in a funny way."
        )
    ], config)
    return {"messages": response}

async def make_slide(state: State, config: RunnableConfig):
    """Make a slide"""
    config = configure_copilotkit(config, emit_tool_calls=True)

    await (ChatOpenAI(model="gpt-4o")
           .bind_tools(state["copilotkit"]["actions"], tool_choice="appendSlide")
           .ainvoke([
        *state["messages"],
        SystemMessage(
            content=(
                "Make a slide about the user's location (leave out the image): " +
                state["location"]
            )
        )
    ], config))
    return None

async def chatbot(state: State, config: RunnableConfig):
    """Call model"""
    config = configure_copilotkit(config, emit_messages=True)
    model = ChatOpenAI(model="gpt-4o")
    model = model.bind_tools(tools)
    messages = state["messages"]
    response = await model.ainvoke(messages, config)
    # We return a list, because this will get added to the existing list
    return {"messages": response}


def route_location(state: State):
    """Route the location"""
    if state.get("location"):
        return "make_slide"
    return "ask_user_location"


workflow = StateGraph(State)

workflow.add_node("check_location", check_location)
workflow.add_node("ask_user_location", ask_user_location)
workflow.add_node("chatbot", chatbot)
workflow.add_node("tools", tool_node)
workflow.add_node("make_slide", make_slide)


workflow.add_edge(START, "check_location")
workflow.add_conditional_edges("check_location", route_location)
workflow.add_edge("ask_user_location", "check_location")
workflow.add_edge("make_slide", "chatbot")
workflow.add_conditional_edges("chatbot", tools_condition)
workflow.add_edge("tools", "chatbot")

memory = MemorySaver()
agent = workflow.compile(checkpointer=memory, interrupt_after=["ask_user_location", "make_slide"])

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
