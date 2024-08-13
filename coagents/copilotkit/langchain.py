"""
LangChain specific utilities for CopilotKit
"""

from typing import List
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    BaseMessage,
    AIMessage,
    ToolMessage
)
from .types import Message

def copilotkit_messages_to_langchain(messages: List[Message]) -> List[BaseMessage]:
    """
    Convert CopilotKit messages to LangChain messages
    """
    result = []
    for message in messages:
        if "content" in message:
            if message["role"] == "user":
                result.append(HumanMessage(content=message["content"], id=message["id"]))
            elif message["role"] == "system":
                result.append(SystemMessage(content=message["content"], id=message["id"]))
            elif message["role"] == "assistant":
                result.append(AIMessage(content=message["content"], id=message["id"]))
        elif "arguments" in message:
            tool_call = {
                "name": message["name"],
                "args": message["arguments"],
                "id": message["id"],
            }
            result.append(AIMessage(id=message["id"], content="", tool_calls=[tool_call]))           
        elif "actionExecutionId" in message:
            result.append(ToolMessage(
                id=message["id"],
                content=message["result"],
                name=message["actionName"],
                tool_call_id=message["actionExecutionId"]
            ))
    return result