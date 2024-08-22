"""
Main chatbot node.
"""

import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import ToolMessage

from coagents.demos.autotale_ai.state import AgentState
from coagents.demos.autotale_ai.story.outline import set_outline
from coagents.demos.autotale_ai.story.characters import set_characters
from coagents.demos.autotale_ai.story.story import set_story
from coagents.copilotkit.langchain import configure_copilotkit
# pylint: disable=line-too-long

async def chatbot_node(state: AgentState, config: RunnableConfig):
    """
    The chatbot is responsible for answering the user's questions and selecting
    the next route.
    """

    config = configure_copilotkit(config, emit_messages=True)

    tools = [set_outline]

    if state.get("outline") is not None:
        tools.append(set_characters)

    if state.get("characters") is not None:
        tools.append(set_story)

    system_message = """
You help the user write a children's story. Please assist the user by either having a conversation or by 
taking the appropriate actions to advance the story writing process. Do not repeat the whole story again.

Your state consists of the following concepts:

- Outline: The outline of the story. 
- Characters: The characters that make up the story (depends on outline)
- Story: The final story result. (depends on outline & characters)

If the user asks you to make changes to any of these,
you MUST take into account dependencies and make the changes accordingly.

Example: If after coming up with the characters, the user requires changes in the outline, you must first 
regenerate the outline.

Dont bother the user too often, just call the tools.
Especially, dont' repeat the story and so on, just call the tools.
"""
    if state.get("outline") is not None:
        system_message += f"\n\nThe current outline is: {state['outline']}"

    if state.get("characters") is not None:
        system_message += f"\n\nThe current characters are: {json.dumps(state['characters'])}"

    if state.get("story") is not None:
        system_message += f"\n\nThe current story is: {json.dumps(state['story'])}"

    response = await ChatOpenAI(model="gpt-4o").bind_tools(tools, parallel_tool_calls=False).ainvoke([
        *state["messages"],
        SystemMessage(
            content=system_message
        )
    ], config)

    if not response.tool_calls:
        return {
            "messages": response,
        }

    return {
        "messages": [
            response,
            ToolMessage(
                name=response.tool_calls[0]["name"],
                content=json.dumps(response.tool_calls[0]["args"]),
                tool_call_id=response.tool_calls[0]["id"]
            )
        ],
    }

