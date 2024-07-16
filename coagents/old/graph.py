"""Graph for the demo"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .copilotkit import CopilotState, ask_user

class State(TypedDict):
    """State for the demo"""
    copilot: CopilotState

def introduce_yourself(_state):
    """Introduce yourself"""
    print("Hi, I'm your Co-Agent!")

def greet_user(state):
    """Greet the user"""
    print(f"Hello, {state['copilot']['ask_user']['answer']}!")

builder = StateGraph(State)

builder.add_node("introduce_yourself", introduce_yourself)
builder.add_node("ask_user", ask_user("What is your name?"))
builder.add_node("greet_user", greet_user)

builder.add_edge(START, "introduce_yourself")
builder.add_edge("introduce_yourself", "ask_user")
builder.add_edge("ask_user", "greet_user")
builder.add_edge("greet_user", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_after=["ask_user"])
