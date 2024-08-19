"""FastAPI integration"""

from typing import List
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from ..sdk import CopilotKitSDK, CopilotKitSDKContext
from ..types import Message
from ..exc import (
    ActionNotFoundException,
    ActionExecutionException,
    AgentNotFoundException,
    AgentExecutionException,
)


def add_fastapi_endpoint(fastapi_app: FastAPI, sdk: CopilotKitSDK, prefix: str):
    """Add FastAPI endpoint"""
    async def make_handler(request: Request):
        return await handler(request, sdk)

    # Ensure the prefix starts with a slash and remove trailing slashes
    normalized_prefix = '/' + prefix.strip('/')

    fastapi_app.add_api_route(
        f"{normalized_prefix}/{{path:path}}",
        make_handler,
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    )

def body_get_or_raise(body: any, key: str):
    """Get value from body or raise an error"""
    value = body.get(key)
    if value is None:
        raise HTTPException(status_code=400, detail=f"{key} is required")
    return value


async def handler(request: Request, sdk: CopilotKitSDK):
    """Handle FastAPI request"""

    try:
        body = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Request body is required") from exc

    path = request.path_params.get('path')
    method = request.method
    context = {"properties": body.get("properties", {})}

    if method == 'POST' and path == 'info':
        return await handle_info(sdk=sdk, context=context)

    if method == 'POST' and path == 'actions/execute':
        name = body_get_or_raise(body, "name")
        arguments = body.get("arguments", {})

        return await handle_execute_action(
            sdk=sdk,
            context=context,
            name=name,
            arguments=arguments,
        )

    if method == 'POST' and path == 'agents/execute':
        thread_id = body.get("threadId")
        node_name = body.get("nodeName")

        name = body_get_or_raise(body, "name")
        state = body_get_or_raise(body, "state")
        messages = body_get_or_raise(body, "messages")
        actions = body.get("actions", [])

        return handle_execute_agent(
            sdk=sdk,
            context=context,
            thread_id=thread_id,
            node_name=node_name,
            name=name,
            state=state,
            messages=messages,
            actions=actions,
        )


    raise HTTPException(status_code=404, detail="Not found")


async def handle_info(*, sdk: CopilotKitSDK, context: CopilotKitSDKContext):
    """Handle info request with FastAPI"""
    result = sdk.info(context=context)
    return JSONResponse(content=result)

async def handle_execute_action(
        *,
        sdk: CopilotKitSDK,
        context: CopilotKitSDKContext,
        name: str,
        arguments: dict,
    ):
    """Handle execute action request with FastAPI"""
    try:
        result = await sdk.execute_action(
            context=context,
            name=name,
            arguments=arguments
        )
        return JSONResponse(content=result)
    except ActionNotFoundException as exc:
        return JSONResponse(content={"error": str(exc)}, status_code=404)
    except ActionExecutionException as exc:
        return JSONResponse(content={"error": str(exc)}, status_code=500)

def handle_execute_agent( # pylint: disable=too-many-arguments
        *,
        sdk: CopilotKitSDK,
        context: CopilotKitSDKContext,
        thread_id: str,
        node_name: str,
        name: str,
        state: dict,
        messages: List[Message],
        actions: List[any],
    ):
    """Handle continue agent execution request with FastAPI"""
    try:
        events = sdk.execute_agent(
            context=context,
            thread_id=thread_id,
            name=name,
            node_name=node_name,
            state=state,
            messages=messages,
            actions=actions,
        )
        return StreamingResponse(events, media_type="application/json")
    except AgentNotFoundException as exc:
        return JSONResponse(content={"error": str(exc)}, status_code=404)
    except AgentExecutionException as exc:
        return JSONResponse(content={"error": str(exc)}, status_code=500)
