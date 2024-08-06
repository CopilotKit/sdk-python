"""Demo"""

from typing import TypedDict, Literal
from fastapi import FastAPI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .copilotkit import CopilotKitSDK, Action, LangGraphAgent, CoagentState, \
    coagent_ask, coagent_get_answer, coagent_send_message, coagent_execute, \
    coagent_get_result
from .copilotkit.integrations.fastapi import add_fastapi_endpoint

class State(TypedDict):
    """State"""
    name: str
    confirmed: bool
    coagent: CoagentState

def ask_user_for_name(state):
    """Ask the user for their name"""
    print("asking user for name", state)
    if "confirmed" in state and state["confirmed"] is False:
        return coagent_ask(state, "Come on, what is your real name? 🤨")

    return coagent_ask(state, "What is your name? 😊")

def confirm_user(state):
    """Confirm the user's name"""
    print("confirming user", state)
    state["name"] = coagent_get_answer(state)
    return coagent_execute(state, "confirmUserName", {"name": state["name"]})

def set_name_confirmed(state):
    """Set the name confirmed"""
    print("setting name confirmed", state)
    state["confirmed"] = coagent_get_result(state)
    return state

def greet_user(state):
    """Greet the user"""
    print("greeting user", state)
    return coagent_send_message(state, f"Hello {state['name']}, how can I help you?")

def route_confirmed(
    state: State,
) -> Literal["ask_user_for_name", "greet_user"]:
    """
    If the user confirms their name, greet them. Otherwise, ask for their name again.
    """
    print("routing", state)
    if state["confirmed"]:
        return "greet_user"
    return "ask_user_for_name"

builder = StateGraph(State)

builder.add_node("ask_user_for_name", ask_user_for_name)
builder.add_node("confirm_user", confirm_user)
builder.add_node("set_name_confirmed", set_name_confirmed)
builder.add_node("greet_user", greet_user)

builder.add_edge(START, "ask_user_for_name")
builder.add_edge("ask_user_for_name", "confirm_user")
builder.add_edge("confirm_user", "set_name_confirmed")
builder.add_conditional_edges("set_name_confirmed", route_confirmed)

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