"""FastAPI integration"""

from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from ..sdk import CopilotKitSDK, CopilotKitSDKContext


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
        print(exc)
        raise HTTPException(status_code=400, detail="Request body is required") from exc

    path = request.path_params.get('path')
    method = request.method
    context = {"properties": body.get("properties", {})}

    if method == 'POST' and path == 'actions/list':
        return await handle_list_actions(sdk=sdk, context=context)
    elif method == 'POST' and path == 'actions/execute':
        name = body.get("name")
        if name is None:
            raise HTTPException(status_code=400, detail="Name is required")

        parameters = body.get("parameters", {})
        state = body.get("agentState")
        thread_id = body.get("agentThreadId")

        return await handle_execute_action(
            sdk=sdk,
            context=context,
            name=name,
            parameters=parameters,
            state=state,
            thread_id=thread_id
        )

    raise HTTPException(status_code=404, detail="Not found")


async def handle_list_actions(*, sdk: CopilotKitSDK, context: CopilotKitSDKContext):
    """Handle FastAPI request"""
    result = sdk.list_actions(context=context)
    return JSONResponse(content=result)

async def handle_execute_action(
        sdk: CopilotKitSDK,
        context: CopilotKitSDKContext,
        name: str,
        parameters: dict,
        state: Optional[dict] = None,
        thread_id: Optional[str] = None
    ):
    """Handle FastAPI request"""
    try:
        result = await sdk.execute_action(
            context=context,
            name=name,
            parameters=parameters,
            state=state,
            thread_id=thread_id
        )
        return JSONResponse(content=result)
    except KeyError as _e:
        return JSONResponse(content={"error": "Action not found"}, status_code=404)
    except RuntimeError as exc:
        return JSONResponse(content={"error": str(exc)}, status_code=400)
