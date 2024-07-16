"""Actions"""

import inspect
from typing import Optional, List, Callable
from .parameter import BaseParameter

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
            parameters: dict
        ) -> dict:
        """Execute the action"""
        try:
            if inspect.iscoroutinefunction(self.handler):
                result = await self.handler(**parameters)
            else:
                result = self.handler(**parameters)
        except Exception as exc:
            message = str(exc).removeprefix('<lambda>()')
            raise RuntimeError(message) from exc
        return {"result": result}