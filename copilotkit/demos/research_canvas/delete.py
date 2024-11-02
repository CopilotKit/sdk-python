"""Delete Resources"""

from typing import cast
from copilotkit.demos.research_canvas.state import AgentState
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import ToolMessage, AIMessage
async def delete_node(state: AgentState, config: RunnableConfig): # pylint: disable=unused-argument
    """
    Delete Node
    """
    return state

async def perform_delete_node(state: AgentState, config: RunnableConfig): # pylint: disable=unused-argument
    """
    Perform Delete Node
    """
    ai_message = cast(AIMessage, state["messages"][-2])
    tool_message = cast(ToolMessage, state["messages"][-1])
    if tool_message.content == "YES":
        urls = ai_message.tool_calls[0]["args"]["urls"]
        state["resources"] = [
            resource for resource in state["resources"] if resource["url"] not in urls
        ]

    return state