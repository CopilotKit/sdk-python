"""Demo"""

from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from fastapi import FastAPI
import uvicorn
from .copilotkit.integrations.fastapi import add_fastapi_endpoint
from .copilotkit import CopilotKitSDK, Action, LangGraphAgent

class State(TypedDict):
    """State"""
    messages: Annotated[list, add_messages]
    test_property_xxx: str


@tool
def search(query: str): # pylint: disable=unused-argument
    """Call to surf the web."""
    # This is a placeholder, but don't tell the LLM that...
    return ["Cloudy with a chance of hail."]


tools = [search]
tool_node = ToolNode(tools)
model = ChatOpenAI(model="gpt-4o")
model = model.bind_tools(tools)


def should_continue(state: State) -> Literal["__end__", "tools"]:
    """Should continue"""
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return END

    return "tools"


async def call_model(state: State, config: RunnableConfig):
    """Call model"""
    messages = state["messages"]
    response = await model.ainvoke(messages, config)
    return {"messages": response}

workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
)

workflow.add_edge("tools", "agent")

memory = MemorySaver()
agent = workflow.compile(checkpointer=memory)

def check_weather(city: str):
    """Check the weather"""
    print(f"Checking weather for {city}")
    return f"The weather in {city} is Cloudy with a chance of hail."

app = FastAPI()
sdk = CopilotKitSDK(
    actions=[
        Action(
            name="checkWeather",
            handler=check_weather,
            description="Check the weather",
            parameters=[
                {
                    "name": "city",
                    "type": "string",
                    "description": "The city to check the weather for"
                }
            ]
        )
    ],
    agents=[
        LangGraphAgent(
            name="weatherAgent",
            description="Retrieve weather information.",
            parameters=[
                {
                    "name": "messages",
                    "type": "string[]",
                    "description": "The messages to send to the agent"
                }
            ],
            agent=agent,
        )
    ],
)

add_fastapi_endpoint(app, sdk, "/copilotkit")

def main():
    """Run the uvicorn server."""
    uvicorn.run("coagents.demo:app", host="127.0.0.1", port=8000, reload=True)
