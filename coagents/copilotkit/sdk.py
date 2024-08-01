"""CopilotKit SDK"""

from typing import List, Callable, Union, Optional, TypedDict, Any
from .agent import Agent
from .action import Action


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
        self.agents = agents
        self.actions = actions

    def get_actions(
        self,
        *
        context: CopilotKitSDKContext
    ) -> List[Union[Action, Agent]]:
        """Get all available actions"""
        result = []
        if self.actions:
            if callable(self.actions):
                result.extend(self.actions(context))
            else:
                result.extend(self.actions)
        if self.agents:
            if callable(self.agents):
                result.extend(self.agents(context))
            else:
                result.extend(self.agents)
        return result

    def list_actions(
        self,
        *,
        context: CopilotKitSDKContext
    ) -> List[Any]:
        """List all available actions and agents"""

        result = self.get_actions(context)
        actions =  [
            {
                "name": item.name,
                "description": item.description,
                "parameters": item.parameters if item.parameters is not None else []
            }
            for item in result
        ]
        return {"actions": actions}


    async def execute_action(
            self,
            *,
            context: CopilotKitSDKContext,
            name: str,
            parameters: dict,
            state: Optional[Any] = None,
            thread_id: Optional[str] = None,
            node_name: Optional[str] = None
        ) -> dict:
        """Execute an action"""

        actions = self.get_actions(context)

        action_or_agent = next((action for action in actions if action.name == name), None)       
        if action_or_agent is None:
            raise KeyError("Action not found")

        if isinstance(action_or_agent, Action):
            action = action_or_agent
            result = await action.execute(parameters=parameters)
        elif isinstance(action_or_agent, Agent):
            agent = action_or_agent
            result = await agent.run(parameters=parameters, state=state, thread_id=thread_id, node_name=node_name)
        else:
            raise ValueError("Not implemented")

        return result
