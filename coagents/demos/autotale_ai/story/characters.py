"""
Characters node.
"""

from typing import List
import json
from langchain_core.tools import tool

from coagents.demos.autotale_ai.state import AgentState, Character



@tool
def set_characters(characters: List[Character]):
    """
    Extract the book's main characters from the conversation.
    Make the appearance and traits of the characters as detailed as possible
    """
    return characters


def characters_node(state: AgentState):
    """
    The characters node is responsible for extracting the characters from the conversation.
    """
    last_message = state["messages"][-1]
    return {
        "characters": json.loads(last_message.content)["characters"]
    }
