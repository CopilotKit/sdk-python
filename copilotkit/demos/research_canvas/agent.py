"""
This is the main entry point for the AI.
It defines the workflow graph and the entry point for the agent.
"""
# pylint: disable=line-too-long, unused-import
import json
from typing import cast

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from copilotkit.langchain import human_in_the_loop
from copilotkit.demos.research_canvas.state import AgentState
from copilotkit.demos.research_canvas.download import download_node
from copilotkit.demos.research_canvas.chat import chat_node
from copilotkit.demos.research_canvas.search import search_node
from copilotkit.demos.research_canvas.delete import delete_node

# Define a new graph
workflow = StateGraph(AgentState)
workflow.add_node("download", download_node)
workflow.add_node("chat_node", chat_node)
workflow.add_node("search_node", search_node)
workflow.add_node("delete_node", delete_node)
workflow.add_node("ask_delete_node", human_in_the_loop)

def route(state):
    """Route after the chat node."""

    messages = state.get("messages", [])
    if messages and isinstance(messages[-1], AIMessage):
        ai_message = cast(AIMessage, messages[-1])

        if ai_message.tool_calls and ai_message.tool_calls[0]["name"] == "Search":
            return "search_node"
        if ai_message.tool_calls and ai_message.tool_calls[0]["name"] == "DeleteResources":
            return "ask_delete_node"
    if messages and isinstance(messages[-1], ToolMessage):
        return "chat_node"

    return END


memory = MemorySaver()
workflow.set_entry_point("download")
workflow.add_edge("download", "chat_node")
workflow.add_conditional_edges("chat_node", route, ["search_node", "chat_node", "ask_delete_node", END])
workflow.add_edge("ask_delete_node", "delete_node")
workflow.add_edge("delete_node", "chat_node")
workflow.add_edge("search_node", "download")
graph = workflow.compile(checkpointer=memory)
