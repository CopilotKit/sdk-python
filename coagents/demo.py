"""Demo"""

from typing import TypedDict
from fastapi import FastAPI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .copilotkit import CopilotKitSDK, Action, LangGraphAgent, CopilotState
from .copilotkit.integrations.fastapi import add_fastapi_endpoint

class State(TypedDict):
    """State"""
    name: str
    copilot: CopilotState

def ask_user_for_name(state):
    """Ask the user for their name"""
    print("Hi, I'm your Co-Agent!")
    return {
        **state,
        "copilot": {
            "ask": {
                "question": "What is your name?"
            }
        }
    }

def greet_user(state):
    """Greet the user"""
    name = state['copilot']['ask']['answer']
    return {
        **state,
        "name": name,
        "copilot": {
            "message": {
                "text": f"Hello {name}, how can I help you?"
            }
        }
    }


builder = StateGraph(State)

builder.add_node("ask_user_for_name", ask_user_for_name)
builder.add_node("greet_user", greet_user)

builder.add_edge(START, "ask_user_for_name")
builder.add_edge("ask_user_for_name", "greet_user")
builder.add_edge("greet_user", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

def greet(name):
    """Greet the user"""
    print("greeting user", name)
    return f"{name} has been greeted."

app = FastAPI()
sdk = CopilotKitSDK(
    actions=[
        Action(
            name="greet",
            handler=greet,
            description="Greet the User",
            parameters=[
                {
                    "name": "name",
                    "type": "string",
                    "description": "The name to greet"
                }
            ]
        )
    ],
    agents=[
        LangGraphAgent(
            name="askUser",
            description="Ask the user for their name and greet",
            parameters=[],
            graph=graph,
        )
    ],
)

add_fastapi_endpoint(app, sdk, "/copilotkit")
