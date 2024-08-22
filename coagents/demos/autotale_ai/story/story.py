"""
Story node.
"""

from typing import List
import json
import asyncio

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

from openai import AsyncOpenAI

from coagents.demos.autotale_ai.state import AgentState, Character


async def _generate_image(image_description: str):
    """
    Generate an image for a page.
    """
    client = AsyncOpenAI()

    response = await client.images.generate(
        model="dall-e-3",
        prompt=image_description,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return response.data[0].url

class ImageDescription(BaseModel):
    """
    Represents the description of an image of a character in the story.
    """
    description: str

async def _generate_page_image_description(
        messages: list,
        page_content: str,
        characters: List[Character],
        config: RunnableConfig
    ):
    """
    Generate a description of the image of a character.
    """

    system_message = SystemMessage(
        content= f"""
The user and the AI are having a conversation about writing a children's story.
It's your job to generate a vivid description of a page in the story.
Make the description as detailed as possible.
These are the characters in the story: \n\n
{characters}
This is the page content: \n\n
{page_content}
Imagine an image of the page. Describe the looks of the page in great detail.
Also describe the setting in which the image is taken.
Make sure to include the name of the characters and full description of the characters in your output.
If the user mentioned a specific style for the images in the conversation, YOU MUST 
include that style in your description. Describe the style in detail, it's important.
        """
    )
    model = ChatOpenAI(model="gpt-4o").with_structured_output(ImageDescription)
    response = await model.ainvoke([
        *messages,
        system_message
    ], config)

    return response.description

class StoryPage(BaseModel):
    """
    Represents a page in the children's story. Keep it simple, 3-4 sentences per page.
    """
    content: str = Field(..., description="A single page in the story")

@tool
def set_story(pages: List[StoryPage]):
    """
    Considering the outline and characters, write a story.
    Keep it simple, 3-4 sentences per page.
    """
    return pages

async def story_node(state: AgentState, config: RunnableConfig):
    """
    The story node is responsible for extracting the story from the conversation.
    """
    last_message = state["messages"][-1]
    pages = json.loads(last_message.content)["pages"]
    characters = state.get("characters", [])

    async def generate_page(page):
        description = await _generate_page_image_description(
            state["messages"],
            page["content"],
            characters,
            config
        )
        image_url = await _generate_image(description)
        return {
            "content": page["content"],
            "image_url": image_url
        }

    tasks = [generate_page(page) for page in pages]
    story = await asyncio.gather(*tasks)

    return {
        "story": story
    }
