"""
LangChain specific utilities for CopilotKit
"""

from typing import List, Optional, Any
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    BaseMessage,
    AIMessage,
    ToolMessage
)
from langchain_core.runnables import RunnableConfig, RunnableGenerator

from .types import Message, IntermediateStateConfig

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

def copilotkit_customize_config(
        base_config: Optional[RunnableConfig] = None,
        *,
        emit_tool_calls: bool = False,
        emit_messages: bool = False,
        emit_all: bool = False,
        emit_intermediate_state: Optional[List[IntermediateStateConfig]] = None
    ) -> RunnableConfig:
    """
    Configure for LangChain for use in CopilotKit
    """
    tags = base_config.get("tags", []).copy() if base_config else []
    metadata = base_config.get("metadata", {}).copy() if base_config else {}

    if emit_tool_calls or emit_all:
        tags.append("copilotkit:emit-tool-calls")
    elif emit_tool_calls is False:
        tags = [tag for tag in tags if tag != "copilotkit:emit-tool-calls"]

    if emit_messages or emit_all:
        tags.append("copilotkit:emit-messages")
    elif emit_messages is False:
        tags = [tag for tag in tags if tag != "copilotkit:emit-messages"]

    if emit_intermediate_state:
        metadata["copilotkit:emit-intermediate-state"] = emit_intermediate_state
    elif emit_intermediate_state and "copilotkit:emit-intermediate-state" in metadata:
        del metadata["copilotkit:emit-intermediate-state"]

    base_config = base_config or {}

    return {
        **base_config,
        "tags": tags,
        "metadata": metadata
    }

async def _exit_copilotkit_generator(state): # pylint: disable=unused-argument
    yield "Exit"


async def copilotkit_exit(config: RunnableConfig):
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

def _emit_copilotkit_state_generator(state):
    async def emit_state(_state: Any): # pylint: disable=unused-argument
        yield state
    return emit_state


async def copilotkit_emit_state(state: Any, config: RunnableConfig):
    """
    Emit CopilotKit state
    """
    gen = RunnableGenerator(_emit_copilotkit_state_generator(state)).with_config(
        tags=["copilotkit:force-emit-intermediate-state"],
        callbacks=config.get(
            "callbacks", []
        ),
    )
    async for _message in gen.astream({}):
        pass

    return True
