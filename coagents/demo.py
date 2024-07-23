"""Demo"""

from typing import TypedDict
from fastapi import FastAPI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .copilotkit import CopilotKitSDK, Action, LangGraphAgent, CoagentState, \
    coagent_ask, coagent_get_answer, coagent_send_message
from .copilotkit.integrations.fastapi import add_fastapi_endpoint

class State(TypedDict):
    """State"""
    name: str
    coagent: CoagentState


def ask_user_for_name(state):
    """Ask the user for their name"""
    return coagent_ask(state, "What is your name?")
    # return {
    #     **state,
    #     "coagent": {
    #         "execute": {
    #             "name": "ask",
    #             "arguments": {
    #                 "question": "What is your name?"
    #             }
    #         }
    #     }
    # }

def greet_user(state):
    """Greet the user"""
    name = coagent_get_answer(state)
    state["name"] = name
    return coagent_send_message(state, f"Hello {name}, how can I help you?")
    # name = state['coagent']['execute']['result']['answer']
    # return {
    #     **state,
    #     "name": name,
    #     "coagent": {
    #         "execute": {
    #             "name": "message",
    #             "arguments": {
    #                 "text": f"Hello {name}, how can I help you?"
    #             }
    #         }
    #     }
    # }


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
