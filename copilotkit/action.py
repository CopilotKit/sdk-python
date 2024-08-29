"""Actions"""

from inspect import iscoroutinefunction
from typing import Optional, List, Callable
from .parameter import BaseParameter, normalize_parameters

class Action:  # pylint: disable=too-few-public-methods
    """Action class for CopilotKit"""
    def __init__(
            self,
            *,
            name: str,
            handler: Callable,
            description: Optional[str] = None,
            parameters: Optional[List[BaseParameter]] = None,
        ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler

    async def execute(
            self,
            *,
            arguments: dict
        ) -> dict:
        """Execute the action"""
        result = self.handler(**arguments)

        return {
            "result": await result if iscoroutinefunction(self.handler) else result
        }

    def dict_repr(self):
        """Dict representation of the action"""
        return {
            'name': self.name,
            'description': self.description or '',
            'parameters': normalize_parameters(self.parameters),
        }
