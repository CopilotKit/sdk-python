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
            state: Optional[Any] = None
        ):
        if thread_id:
            thread = {"configurable": {"thread_id": thread_id}}
            self.graph.update_state(thread, state if state is not None else {})
            self.graph.invoke(None, thread, interrupt_after="*")
        else:
            thread_id = str(uuid.uuid4())
            thread = {"configurable": {"thread_id": thread_id}}
            self.graph.invoke(parameters, thread, interrupt_after="*")

        new_state = self.graph.get_state(thread)

        return {
            "threadId": thread_id,
            "state": new_state.values,
            "running": new_state.next != ()
        }
