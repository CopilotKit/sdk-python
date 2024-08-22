"""
This is the main entry point for the autotale AI.
It defines the workflow graph and the entry point for the agent.
"""
# pylint: disable=line-too-long, unused-import

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import ToolMessage

from coagents.demos.autotale_ai.state import AgentState
from coagents.demos.autotale_ai.chatbot import chatbot_node
from coagents.demos.autotale_ai.story.outline import outline_node
from coagents.demos.autotale_ai.story.characters import characters_node
from coagents.demos.autotale_ai.story.story import story_node




def route_story_writing(state):
    """Route to story writing nodes."""
    print(state["messages"][-1])
    last_message = state["messages"][-1]

    if isinstance(last_message, ToolMessage):
        return last_message.name
    return END

# Define a new graph
workflow = StateGraph(AgentState)
workflow.add_node("chatbot_node", chatbot_node)
workflow.add_node("outline_node", outline_node)
workflow.add_node("characters_node", characters_node)
workflow.add_node("story_node", story_node)

# Chatbot
workflow.set_entry_point("chatbot_node")

workflow.add_conditional_edges(
    "chatbot_node", 
    route_story_writing,
    {
        "set_outline": "outline_node",
        "set_characters": "characters_node",
        "set_story": "story_node",
        END: END,
    }
)
workflow.add_edge(
    "outline_node",
    "chatbot_node"
)

workflow.add_edge(
    "characters_node",
    "chatbot_node"
)

workflow.add_edge(
    "story_node",
    "chatbot_node"
)

memory = MemorySaver()

graph = workflow.compile(checkpointer=memory)
