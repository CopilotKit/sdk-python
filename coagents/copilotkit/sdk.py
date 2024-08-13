"""CopilotKit SDK"""

from typing import List, Callable, Union, Optional, TypedDict, Any
from .agent import Agent
from .action import Action
from .types import Message
from .exc import (
    ActionNotFoundException,
    AgentNotFoundException,
    ActionExecutionException,
    AgentExecutionException
)


class CopilotKitSDKContext(TypedDict):
    """CopilotKit SDK Context"""
    properties: Any

class CopilotKitSDK:
    """CopilotKit SDK"""

    def __init__(
        self,
        *,
        actions: Optional[Union[List[Action], Callable[[], List[Action]]]] = None,
        agents: Optional[Union[List[Agent], Callable[[], List[Agent]]]] = None,
    ):
        self.agents = agents or []
        self.actions = actions or []

    def info(
        self,
        *,
        context: CopilotKitSDKContext
    ) -> List[Union[Action, Agent]]:
        """Returns information about available actions and agents"""

        actions = self.actions(context) if callable(self.actions) else self.actions
        agents = self.agents(context) if callable(self.agents) else self.agents

        result = {
            "actions": [action.dict_repr() for action in actions],
            "agents": [agent.dict_repr() for agent in agents]
        }
        return result
    
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
    ) -> dict:
        """Execute an action"""

        action = self._get_action(context=context, name=name)

        try:
            return action.execute(arguments=arguments)
        except Exception as error:
            raise ActionExecutionException(name, error) from error

    def _get_agent(
        self,
        *,
        context: CopilotKitSDKContext,
        name: str,
    ) -> Agent:
        """Get an agent by name"""
        agents = self.agents(context) if callable(self.agents) else self.agents
        agent = next((agent for agent in agents if agent.name == name), None)
        if agent is None:
            raise AgentNotFoundException(name)
        return agent

    def start_agent_execution( # pylint: disable=too-many-arguments
        self,
        *,
        context: CopilotKitSDKContext,
        name: str,
        thread_id: str,
        arguments: dict,
        messages: List[Message],
    ):
        """Start an agent execution"""
        agent = self._get_agent(context=context, name=name)        

        try:
            return agent.start_execution(
                thread_id=thread_id,
                arguments=arguments,
                messages=messages,
            )
        except Exception as error:           
            raise AgentExecutionException(name, error) from error

    def continue_agent_execution( # pylint: disable=too-many-arguments
        self,
        *,
        context: CopilotKitSDKContext,
        name: str,
        thread_id: str,
        node_name: str,
        state: dict,
        messages: List[Message],
    ):
        """Continue an agent execution"""
        agent = self._get_agent(context=context, name=name)

        try:
            return agent.continue_execution(
                thread_id=thread_id,
                node_name=node_name,
                state=state,
                messages=messages,
            )
        except Exception as error:            
            raise AgentExecutionException(name, error) from error
