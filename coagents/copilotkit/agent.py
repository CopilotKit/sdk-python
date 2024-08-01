"""Agents"""

import uuid
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
from langgraph.graph.graph import CompiledGraph
from .parameter import BaseParameter


class Agent(ABC):
    """Agent class for CopilotKit"""
    def __init__(
            self,
            *,
            name: str,
            description: Optional[str] = None,
            parameters: Optional[List[BaseParameter]] = None,
        ):
        self.name = name
        self.description = description
        self.parameters = parameters

    @abstractmethod
    async def run(
        self,
        *,
        thread_id: Optional[str] = None,
        parameters: Optional[Dict] = None,
        state: Optional[Any] = None
    ):
        """Run the agent"""


class LangGraphAgent(Agent):
    """LangGraph agent class for CopilotKit"""
    def __init__(
            self,
            *,
            name: str,
            graph: CompiledGraph,
            description: Optional[str] = None,
            parameters: Optional[List[BaseParameter]] = None
        ):
        super().__init__(name=name, description=description, parameters=parameters)
        self.graph = graph

    async def run(
            self,
            *,
            thread_id: Optional[str] = None,
            parameters: Optional[Dict] = None,
            state: Optional[Any] = None,
            node_name: Optional[str] = None
        ):

        print("got node name:", node_name)

        if thread_id:
            thread = {"configurable": {"thread_id": thread_id}}
            self.graph.update_state(thread, state if state is not None else {}, as_node=node_name)
            self.graph.invoke(None, thread, interrupt_after="*")
        else:
            thread_id = str(uuid.uuid4())
            thread = {"configurable": {"thread_id": thread_id}}
            parameters = parameters if parameters is not None else {}
            parameters["coagent"] = {}
            self.graph.invoke(parameters, thread, interrupt_after="*")

        new_state = self.graph.get_state(thread)
        new_node_name= list(new_state.metadata["writes"].keys())[0]

        print("sending node name:", new_node_name)

        return {
            "threadId": thread_id,
            "nodeName": new_node_name,
            "state": new_state.values,
            "running": new_state.next != (),
            "name": self.name,
        }

def coagent_ask(state, question: str, key: str = None):
    """Ask a question to the user"""
    return {
        **state,
        "coagent": {
            "execute": {
                "name": "ask",
                "arguments": {
                    "question": question,                   
                },
                **({"key": key} if key is not None else {})
            }
        }
    }

def coagent_get_answer(state, key: str=None):
    """Get the answer from the user"""
    if key is not None:
        if state["coagent"]["execute"]["key"] != key:
            raise KeyError(f"Key {key} not found")
    return state["coagent"]["execute"]["result"]["answer"]

def coagent_send_message(state, message: str):
    """Send a message to the user"""

    return {
        **state,
        "coagent": {
            "execute": {
                "name": "message",
                "arguments": {
                    "text": message
                }
            }
        }
    }

def coagent_execute(state, name: str, arguments: Dict):
    """Execute an action"""
    return {
        **state,
        "coagent": {
            "execute": {
                "name": name,
                "arguments": arguments
            }
        }
    }

def coagent_get_result(state):
    """Get the result of the action"""
    return state["coagent"]["execute"]["result"]