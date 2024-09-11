"""Test Joker Agent"""

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph import MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, ToolMessage


from copilotkit.langchain import configure_copilotkit, exit_copilotkit

class JokeAgentState(MessagesState):
    """Joke Agent State"""
    joke: str

async def joke_node(state: JokeAgentState, config: RunnableConfig):
    """
    Make a joke.
    """

    config = configure_copilotkit(
        config,
        emit_messages=True,
        emit_intermediate_state=[
            {
                "state_key": "joke",
                "tool": "make_joke",
                "tool_argument": "the_joke"
            },
        ]
    )

    system_message = "You make funny jokes."

    joke_tool = {
        'name': 'make_joke',
        'description': """Make a funny joke.""",
        'parameters': {
            'type': 'object',
            'properties': {
                'the_joke': {
                    'description': """The joke""",
                    'type': 'string',                    
                }
            },
            'required': ['the_joke']
        }
    }

    joke_model = ChatOpenAI(model="gpt-4o").bind_tools(
        [joke_tool],
        parallel_tool_calls=False,
        tool_choice="make_joke"
    )

    response = await joke_model.ainvoke([
        *state["messages"],
        SystemMessage(
            content=system_message
        )
    ], config)

    tool_calls = response.tool_calls

    joke = tool_calls[0]["args"]["the_joke"]

    await exit_copilotkit(config)

    return {
        "messages": [
            response,
            ToolMessage(
                name=tool_calls[0]["name"],
                content=joke,
                tool_call_id=tool_calls[0]["id"]
            )
        ],
        "joke": joke,
    }

workflow = StateGraph(JokeAgentState)
workflow.add_node("joke_node", joke_node)
workflow.set_entry_point("joke_node")

workflow.add_edge("joke_node", END)
memory = MemorySaver()
joke_graph = workflow.compile(checkpointer=memory)
