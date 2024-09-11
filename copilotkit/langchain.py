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
from langchain_core.runnables import RunnableConfig, RunnableGenerator

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
        emit_all: bool = False,
        emit_intermediate_state: Optional[list] = None
    ):
    """
    Configure for LangChain for use in CopilotKit
    """
    tags = config.get("tags", []) if config else []
    metadata = config.get("metadata", {}) if config else {}

    if emit_tool_calls or emit_all:
        tags.append("copilotkit:emit-tool-calls")
    if emit_messages or emit_all:
        tags.append("copilotkit:emit-messages")

    if emit_intermediate_state:
        metadata["copilotkit:emit-intermediate-state"] = emit_intermediate_state

    config = config or {}

    return {
        **config,
        "tags": tags,
        "metadata": metadata
    }

async def _exit_copilotkit_generator(state): # pylint: disable=unused-argument
    yield "Exit"


async def exit_copilotkit(config: RunnableConfig):
    """
    Exit CopilotKit
    """
    # For some reason, we need to use this workaround to get custom events to work
    # dispatch_custom_event and friends don't seem to do anything
    gen = RunnableGenerator(_exit_copilotkit_generator).with_config(
        tags=["copilotkit:exit"],
        callbacks=config.get(
            "callbacks", []
        ),
    )
    async for _message in gen.astream({}):
        pass
    
    return True
