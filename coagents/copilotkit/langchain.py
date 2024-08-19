"""
LangChain specific utilities for CopilotKit
"""

from typing import List, Optional
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    BaseMessage,
    AIMessage,
    ToolMessage
)
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.config import ensure_config

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

def configure_copilotkit(
        config: Optional[RunnableConfig] = None,
        *,
        emit_tool_calls: bool = False,
        emit_messages: bool = False,
        emit_all: bool = False
    ):
    """
    Configure for LangChain for use in CopilotKit
    """
    tags = config.get("tags", []) if config else []

    if emit_tool_calls or emit_all:
        tags.append("copilotkit:emit-tool-calls")
    if emit_messages or emit_all:
        tags.append("copilotkit:emit-messages")

    config = (config or {}).copy()
    config["tags"] = tags
    return ensure_config(config)
