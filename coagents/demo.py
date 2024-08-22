"""Demo"""

from fastapi import FastAPI
import uvicorn
from .copilotkit.integrations.fastapi import add_fastapi_endpoint
from .copilotkit import CopilotKitSDK, LangGraphAgent
from .demos.autotale_ai.agent import graph

app = FastAPI()
sdk = CopilotKitSDK(
    agents=[
        LangGraphAgent(
            name="childrensBookAgent",
            description="Write a children's book.",
            parameters=[],
            agent=graph,
        )
    ],
)

add_fastapi_endpoint(app, sdk, "/copilotkit")

def main():
    """Run the uvicorn server."""
    uvicorn.run("coagents.demo:app", host="127.0.0.1", port=8000, reload=True)
