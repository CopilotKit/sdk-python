"""CopilotKit SDK"""

import pickle
from typing import TypedDict, List, Optional
from langgraph.graph.graph import CompiledGraph

THREAD_ID=42

class CopilotKitSDK:
    """CopilotKit SDK"""
    def __init__(self, agents: List[CompiledGraph]):
        self.agents = agents

    def run(self):
        """Run CopilotKit"""
        graph = self.agents[0]     

        # run the initial step and serialize the state  
        event = step_initial(graph)
        serialized_state = serialize_checkpointer(graph)

        # HIL: ask the user for input
        answer = None        
        if event["copilot"]["ask_user"]:
            answer = input(event["copilot"]["ask_user"]["question"] + " ")

        # continue from the serialized state
        step_continue(graph, serialized_state, answer)

class CopilotAskState(TypedDict):
    """State for asking the user"""
    question: str
    answer: Optional[str]


class CopilotState(TypedDict):
    """State for CopilotKit"""
    ask_user: Optional[CopilotAskState]

def thread(thread_id):
    """Thread"""
    return {"configurable": {"thread_id": thread_id}}

def step_initial(graph):
    """Initial step"""
    initial_input = {"copilot": {}}
    return graph.invoke(initial_input, thread(THREAD_ID))

def step_continue(graph, serialized_state, answer):
    """Continue step"""
    deserialize_checkpointer(graph, serialized_state)
    state = graph.get_state(thread(THREAD_ID)).values

    if (answer):
        graph.update_state(thread(THREAD_ID), {**state, "copilot": {
            **state.get("copilot", {}),
            "ask_user": {
                "question": state["copilot"]["ask_user"]["question"],
                "answer": answer
            }
        }})

    graph.invoke(None, thread(THREAD_ID))

def ask_user(question: str):
    """Ask user a question"""
    def ask_user_impl(state):
        return {
            **state,
            "copilot": {
                **state.get("copilot", {}),
                "ask_user": {
                    "question": question,
                    "answer": None
                }
            }
        }
    return ask_user_impl


def serialize_checkpointer(graph):
    """Serialize checkpointer to a variable"""
    return pickle.dumps(graph.checkpointer.storage)

def deserialize_checkpointer(graph, serialized_data):
    """Deserialize checkpointer from a variable"""
    graph.checkpointer.storage = pickle.loads(serialized_data)
