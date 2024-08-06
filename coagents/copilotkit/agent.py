"""Agents"""

from typing import Optional, List
from abc import ABC, abstractmethod
from langgraph.graph.graph import CompiledGraph
from langchain.load.dump import dumps as langchain_dumps
from .parameter import BaseParameter, normalize_parameters

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

    # TODO: agents always get the full message history

    @abstractmethod
    async def start_execution(
        self,
        *,
        thread_id: str,
        parameters: dict,
        properties: dict
    ):
        """Start the execution of the agent"""

    @abstractmethod
    async def continue_execution(
        self,
        *,
        thread_id: str,
        state: dict,
        properties: dict
    ):
        """Continue the execution of the agent"""

    def dict_repr(self):
        """Dict representation of the action"""
        return {
            'name': self.name,
            'description': self.description or '',
            'parameters': normalize_parameters(self.parameters),
        }


class LangGraphAgent(Agent):
    """LangGraph agent class for CopilotKit"""
    def __init__(
            self,
            *,
            name: str,
            agent: CompiledGraph,
            description: Optional[str] = None,
            parameters: Optional[List[BaseParameter]] = None
        ):
        super().__init__(name=name, description=description, parameters=parameters)
        self.agent = agent

    async def start_execution(
        self,
        *,
        thread_id: str,
        parameters: dict,
        properties: dict
    ):
        config = {"configurable": {"thread_id": thread_id}}
        async for event in self.agent.astream_events(parameters, config, version="v1"):            
            yield langchain_dumps({"langgraph": event}) + "\n"

    async def continue_execution(
        self,
        *,
        thread_id: str,
        state: dict,
        properties: dict
    ):
        config = {"configurable": {"thread_id": thread_id}}

        node_name = properties.get("node_name")
        if node_name is None:
            raise ValueError("Node name is required")

        self.agent.update_state(config, state, as_node=node_name)

        for event in self.agent.astream_events(None, config, version="v1"):
            yield langchain_dumps({"langgraph": event}) + "\n"

    def dict_repr(self):
        super_repr = super().dict_repr()
        return {
            **super_repr,
            'type': 'langgraph'
        }
