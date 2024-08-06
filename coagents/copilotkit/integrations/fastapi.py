"""FastAPI integration"""

import uuid
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from ..sdk import CopilotKitSDK, CopilotKitSDKContext
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
        name = body.get("name")
        if name is None:
            raise HTTPException(status_code=400, detail="Name is required")

        parameters = body.get("parameters", {})

        return await handle_execute_action(
            sdk=sdk,
            context=context,
            name=name,
            parameters=parameters,
        )

    if method == 'POST' and path == 'agents/start':
        name = body.get("name")
        if name is None:
            raise HTTPException(status_code=400, detail="Name is required")

        thread_id = str(uuid.uuid4())
        parameters = body.get("parameters", {})
        properties = body.get("properties", {})

        return await handle_start_agent_execution(
            sdk=sdk,
            context=context,
            name=name,
            thread_id=thread_id,
            parameters=parameters,
            properties=properties,
        )

    if method == 'POST' and path == 'agents/continue':
        name = body.get("name")
        if name is None:
            raise HTTPException(status_code=400, detail="Name is required")

        thread_id = body.get("thread_id")
        if thread_id is None:
            raise HTTPException(status_code=400, detail="Thread ID is required")

        state = body.get("state", {})
        properties = body.get("properties", {})

        return await handle_continue_agent_execution(
            sdk=sdk,
            context=context,
            thread_id=thread_id,
            name=name,
            state=state,
            properties=properties,
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
        parameters: dict,
    ):
    """Handle execute action request with FastAPI"""
    try:
        result = await sdk.execute_action(
            context=context,
            name=name,
            parameters=parameters
        )
        return JSONResponse(content=result)
    except ActionNotFoundException as exc:
        return JSONResponse(content={"error": str(exc)}, status_code=404)
    except ActionExecutionException as exc:
        return JSONResponse(content={"error": str(exc)}, status_code=500)

async def handle_start_agent_execution( # pylint: disable=too-many-arguments
        *,
        sdk: CopilotKitSDK,
        context: CopilotKitSDKContext,
        name: str,
        thread_id: str,
        parameters: dict,
        properties: dict,
    ):
    """Handle start agent request with FastAPI"""
    try:
        events = sdk.start_agent_execution(
            context=context,
            name=name,
            thread_id=thread_id,
            parameters=parameters,
            properties=properties,
        )
        return StreamingResponse(events, media_type="application/json")
    except AgentNotFoundException as exc:
        return JSONResponse(content={"error": str(exc)}, status_code=404)
    except AgentExecutionException as exc:
        return JSONResponse(content={"error": str(exc)}, status_code=500)


def handle_continue_agent_execution( # pylint: disable=too-many-arguments
        *,
        sdk: CopilotKitSDK,
        context: CopilotKitSDKContext,
        thread_id: str,
        name: str,
        state: dict,
        properties: dict,
    ):
    """Handle continue agent execution request with FastAPI"""
    try:
        result = sdk.continue_agent_execution(
            context=context,
            thread_id=thread_id,
            name=name,
            state=state,
            properties=properties,
        )
        return JSONResponse(content=result)
    except AgentNotFoundException as exc:
        return JSONResponse(content={"error": str(exc)}, status_code=404)
    except AgentExecutionException as exc:
        return JSONResponse(content={"error": str(exc)}, status_code=500)
