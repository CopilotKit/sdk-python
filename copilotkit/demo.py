"""Demo"""

from fastapi import FastAPI
import uvicorn
from .integrations.fastapi import add_fastapi_endpoint
from . import CopilotKitSDK, LangGraphAgent
from .demos.autotale_ai.agent import graph

app = FastAPI()
sdk = CopilotKitSDK(
    agents=[
        LangGraphAgent(
            name="childrensBookAgent",
            description="Write a children's book.",
            agent=graph,
        )
    ],
)

add_fastapi_endpoint(app, sdk, "/copilotkit")

def main():
    """Run the uvicorn server."""
    uvicorn.run("copilotkit.demo:app", host="127.0.0.1", port=8000, reload=True)
