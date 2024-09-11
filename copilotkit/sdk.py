"""CopilotKit SDK"""

from typing import List, Callable, Union, Optional, TypedDict, Any, Coroutine
from .agent import Agent, AgentDict
from .action import Action, ActionDict, ActionResultDict
from .types import Message
from .exc import (
    ActionNotFoundException,
    AgentNotFoundException,
    ActionExecutionException,
    AgentExecutionException
)

class InfoDict(TypedDict):
    """Info dictionary"""
    actions: List[ActionDict]
    agents: List[AgentDict]

class CopilotKitSDKContext(TypedDict):
    """CopilotKit SDK Context"""
    properties: Any

class CopilotKitSDK:
    """CopilotKit SDK"""

    def __init__(
        self,
        *,
        actions: Optional[
            Union[
                List[Action],
                Callable[[CopilotKitSDKContext], List[Action]]
            ]
        ] = None,
        agents: Optional[
            Union[
                List[Agent],
                Callable[[CopilotKitSDKContext], List[Agent]]
            ]
        ] = None,
    ):
        self.agents = agents or []
        self.actions = actions or []

    def info(
        self,
        *,
        context: CopilotKitSDKContext
    ) -> InfoDict:
        """Returns information about available actions and agents"""

        actions = self.actions(context) if callable(self.actions) else self.actions
        agents = self.agents(context) if callable(self.agents) else self.agents

        return {
            "actions": [action.dict_repr() for action in actions],
            "agents": [agent.dict_repr() for agent in agents]
        }

    def _get_action(
        self,
        *,
        context: CopilotKitSDKContext,
        name: str,
    ) -> Action:
        """Get an action by name"""
        actions = self.actions(context) if callable(self.actions) else self.actions
        action = next((action for action in actions if action.name == name), None)
        if action is None:
            raise ActionNotFoundException(name)
        return action

    def execute_action(
            self,
            *,
            context: CopilotKitSDKContext,
            name: str,
            arguments: dict,
    ) -> Coroutine[Any, Any, ActionResultDict]:
        """Execute an action"""

        action = self._get_action(context=context, name=name)

        try:
            return action.execute(arguments=arguments)
        except Exception as error:
            raise ActionExecutionException(name, error) from error

    def execute_agent( # pylint: disable=too-many-arguments
        self,
        *,
        context: CopilotKitSDKContext,
        name: str,
        thread_id: str,
        node_name: str,
        state: dict,
        messages: List[Message],
        actions: List[ActionDict],
    ) -> Any:
        """Execute an agent"""
        agents = self.agents(context) if callable(self.agents) else self.agents
        agent = next((agent for agent in agents if agent.name == name), None)
        if agent is None:
            raise AgentNotFoundException(name)

        try:
            return agent.execute(
                thread_id=thread_id,
                node_name=node_name,
                state=state,
                messages=messages,
                actions=actions,
            )
        except Exception as error:
            raise AgentExecutionException(name, error) from error
