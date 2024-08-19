"""Agents"""

from typing import Optional, List
from abc import ABC, abstractmethod
import uuid
from langgraph.graph.graph import CompiledGraph
from langchain.load.dump import dumps as langchain_dumps
from langchain.load.load import load as langchain_load

from langchain.schema import SystemMessage
from .parameter import BaseParameter, normalize_parameters
from .types import Message
from .langchain import copilotkit_messages_to_langchain



class Agent(ABC):
    """Agent class for CopilotKit"""
    def __init__(
            self,
            *,
            name: str,
            description: Optional[str] = None,
            parameters: Optional[List[BaseParameter]] = None,
            merge_state: Optional[callable] = None
        ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.merge_state = merge_state

    @abstractmethod
    def execute(
        self,
        *,
        state: dict,
        messages: List[Message],
        thread_id: Optional[str] = None,
        node_name: Optional[str] = None,
    ):
        """Execute the agent"""

    def dict_repr(self):
        """Dict representation of the action"""
        return {
            'name': self.name,
            'description': self.description or '',
            'parameters': normalize_parameters(self.parameters),
        }

def langgraph_default_merge_state( # pylint: disable=unused-argument
        *,
        state: dict,
        messages: List[Message],
        actions: List[any]
    ):
    """Default merge state for LangGraph"""
    if len(messages) > 0 and isinstance(messages[0], SystemMessage):
        # remove system message
        messages = messages[1:]

    # merge with existing messages
    merged_messages = list(map(langchain_load, state.get("messages", [])))
    existing_message_ids = {message.id for message in merged_messages}

    for message in messages:
        if message.id not in existing_message_ids:
            merged_messages.append(message)

    return {
        **state,
        "messages": merged_messages,
        "copilotkit": {
            "actions": actions
        }
    }

class LangGraphAgent(Agent):
    """LangGraph agent class for CopilotKit"""
    def __init__(
            self,
            *,
            name: str,
            agent: CompiledGraph,
            description: Optional[str] = None,
            parameters: Optional[List[BaseParameter]] = None,
            merge_state: Optional[callable] = langgraph_default_merge_state
        ):
        super().__init__(
            name=name,
            description=description,
            parameters=parameters,
            merge_state=merge_state
        )
        self.agent = agent

    def _state_sync_event(self, thread_id: str, node_name: str, state: dict, running: bool):
        return langchain_dumps({
            "event": "on_copilotkit_state_sync",
            "thread_id": thread_id,
            "agent_name": self.name,
            "node_name": node_name,
            "state": state,
            "running": running,
            "role": "assistant"
        })

    def execute( # pylint: disable=too-many-arguments
        self,
        *,
        state: dict,
        messages: List[Message],
        thread_id: Optional[str] = None,
        node_name: Optional[str] = None,
        actions: Optional[List[any]] = None,
    ):
        langchain_messages = copilotkit_messages_to_langchain(messages)
        state = self.merge_state(
            state=state,
            messages=langchain_messages,
            actions=actions
        )

        mode = "continue" if thread_id and node_name else "start"
        thread_id = thread_id or str(uuid.uuid4())

        config = {"configurable": {"thread_id": thread_id}}
        if mode == "continue":
            self.agent.update_state(config, state, as_node=node_name)

        return self._stream_events(
            mode=mode,
            thread_id=thread_id,
            state=state,
            node_name=node_name
        )

    async def _stream_events(self, *, mode: str, thread_id: str, state: dict, node_name: str):

        config = {"configurable": {"thread_id": thread_id}}
        yield self._state_sync_event(thread_id, node_name or "__start__", state, True) + "\n"

        initial_state = state if mode == "start" else None
        async for event in self.agent.astream_events(initial_state, config, version="v1"):
            node_name = event.get("name")
            event_type = event.get("event")
            tags = event.get("tags", [])
            if "copilotkit:hidden" in tags:
                continue
            if not((event_type == "on_chain_start" and node_name == "LangGraph") or
                node_name == "__start__"):
                updated_state = self.agent.get_state(config).values
                if updated_state != state:
                    state = updated_state
                    yield self._state_sync_event(thread_id, node_name, state, True) + "\n"
            yield langchain_dumps(event) + "\n"

        state = self.agent.get_state(config)
        running = state.next != ()

        node_name = list(state.metadata["writes"].keys())[0]
        yield self._state_sync_event(thread_id, node_name, state.values, running) + "\n"



    def dict_repr(self):
        super_repr = super().dict_repr()
        return {
            **super_repr,
            'type': 'langgraph'
        }
