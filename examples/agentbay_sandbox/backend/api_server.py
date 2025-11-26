# -*- coding: utf-8 -*-
"""
FastAPI Server for Multi-Sandbox Agent

This module provides the FastAPI backend server with REST API and
WebSocket support.
"""
import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator, Coroutine, Dict, Optional, cast

# Third-party imports
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .agent_service import AgentService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan event handler for FastAPI application.

    Handles startup and shutdown events for the agent service.

    Args:
        fastapi_app: FastAPI application instance
    """
    # Startup
    dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
    agentbay_api_key = os.getenv("AGENTBAY_API_KEY")

    agent_service: Optional[AgentService] = None

    if not dashscope_api_key or not agentbay_api_key:
        logger.warning(
            "API keys not found in environment variables. "
            "Some features may not work.",
        )
    else:
        try:
            agent_service = AgentService(
                dashscope_api_key=dashscope_api_key,
                agentbay_api_key=agentbay_api_key,
            )
            success = await agent_service.initialize()
            if success:
                logger.info("Agent Service initialized successfully")
            else:
                logger.error("Failed to initialize Agent Service")
        except (RuntimeError, ValueError, AttributeError) as e:
            # 捕获初始化过程中的运行时错误
            logger.error("Error initializing Agent Service: %s", e)

    # Store agent_service in app.state
    fastapi_app.state.agent_service = agent_service

    yield

    # Shutdown
    if agent_service:
        await agent_service.cleanup()
        logger.info("Agent Service cleaned up")


# Create FastAPI app with lifespan handler
app = FastAPI(
    title="Multi-Sandbox Agent API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str
    session_id: Optional[str] = "default"
    user_id: Optional[str] = "user"


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str
    session_id: str


class SandboxInfoResponse(BaseModel):
    """Response model for sandbox info endpoint."""

    sandboxes: Dict[str, Any]


# Health check
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Multi-Sandbox Agent API", "status": "running"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    agent_service = getattr(app.state, "agent_service", None)
    return {
        "status": "healthy",
        "agent_initialized": agent_service is not None
        and agent_service.initialized,
    }


# Chat endpoints
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the agent and get a response"""
    agent_service = getattr(app.state, "agent_service", None)
    if not agent_service or not agent_service.initialized:
        raise HTTPException(
            status_code=503,
            detail="Agent Service not initialized",
        )

    try:
        response = await agent_service.chat(request.message)
        session_id = request.session_id or "default"
        return ChatResponse(response=response, session_id=session_id)
    except (RuntimeError, ValueError, AttributeError) as e:
        # 捕获对话过程中的运行时错误
        logger.error("Error in chat: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


async def _process_stream_tasks(
    message_task: Optional[asyncio.Task],
    event_task: Optional[asyncio.Task],
    message_stream: AsyncGenerator[str, None],
    event_queue: asyncio.Queue,
    emit_event: Any,
) -> AsyncGenerator[str, None]:
    """Process stream tasks and yield chunks."""
    stream_finished = False
    current_message_task = message_task
    current_event_task = event_task

    while True:
        tasks = _build_task_set(
            stream_finished,
            current_message_task,
            current_event_task,
        )
        if not tasks:
            break

        done, _ = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED,
        )

        if current_message_task and current_message_task in done:
            (
                chunk,
                current_message_task,
                stream_finished,
            ) = await _handle_message_task(
                current_message_task,
                message_stream,
            )
            if chunk:
                yield f"data: {chunk}\n\n"

        if current_event_task and current_event_task in done:
            async for event_chunk in _handle_event_task(
                current_event_task,
                emit_event,
            ):
                yield event_chunk
            current_event_task = asyncio.create_task(event_queue.get())

        if stream_finished and current_message_task is None:
            break


def _build_task_set(
    stream_finished: bool,
    message_task: Optional[asyncio.Task],
    event_task: Optional[asyncio.Task],
) -> set:
    """Build task set for asyncio.wait."""
    tasks = set()
    if not stream_finished and message_task:
        tasks.add(message_task)
    if event_task:
        tasks.add(event_task)
    return tasks


async def _handle_message_task(
    message_task: asyncio.Task,
    message_stream: AsyncGenerator[str, None],
) -> tuple[Optional[str], Optional[asyncio.Task], bool]:
    """Handle message task completion."""
    try:
        chunk = message_task.result()
        next_task = asyncio.create_task(
            cast(Coroutine[Any, Any, str], anext(message_stream)),
        )
        return chunk, next_task, False
    except StopAsyncIteration:
        return None, None, True


async def _handle_event_task(
    event_task: asyncio.Task,
    emit_event: Any,
) -> AsyncGenerator[str, None]:
    """Handle event task completion and yield event chunks."""
    event_payload = event_task.result()
    async for event_chunk in emit_event(event_payload):
        yield event_chunk


async def _process_remaining_events(
    event_queue: asyncio.Queue,
    emit_event: Any,
) -> AsyncGenerator[str, None]:
    """Process remaining events in queue."""
    while not event_queue.empty():
        event_payload = await event_queue.get()
        async for event_chunk in emit_event(event_payload):
            yield event_chunk


def _cleanup_tasks(
    message_task: Optional[asyncio.Task],
    event_task: Optional[asyncio.Task],
    agent_service: Any,
    event_queue: asyncio.Queue,
) -> None:
    """Clean up tasks and unregister event listener."""
    if message_task:
        message_task.cancel()
    if event_task:
        event_task.cancel()
    agent_service.unregister_event_listener(event_queue)


@app.get("/api/chat/stream")
async def chat_stream(message: str, _session_id: str = "default"):
    """
    Stream chat response using Server-Sent Events (SSE)

    Args:
        message: User message to send to the agent
        _session_id: Session ID (currently unused, kept for API consistency)
    """
    agent_service = getattr(app.state, "agent_service", None)
    if not agent_service or not agent_service.initialized:
        raise HTTPException(
            status_code=503,
            detail="Agent Service not initialized",
        )

    event_queue: asyncio.Queue = asyncio.Queue()
    agent_service.register_event_listener(event_queue)

    async def emit_event(
        event_payload: Dict[str, Any],
    ) -> AsyncGenerator[str, None]:
        event_name = event_payload.get("event", "message")
        event_data = event_payload.get("data", {})
        yield (
            f"event: {event_name}\n"
            f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"
        )

    async def generate() -> AsyncGenerator[str, None]:
        message_stream = agent_service.chat_stream(message)
        message_task: Optional[asyncio.Task] = asyncio.create_task(
            cast(Coroutine[Any, Any, str], anext(message_stream)),
        )
        event_task: Optional[asyncio.Task] = asyncio.create_task(
            event_queue.get(),
        )
        try:
            async for chunk in _process_stream_tasks(
                message_task,
                event_task,
                message_stream,
                event_queue,
                emit_event,
            ):
                yield chunk

            # Process remaining events
            async for event_chunk in _process_remaining_events(
                event_queue,
                emit_event,
            ):
                yield event_chunk

            yield "data: [DONE]\n\n"
        except (RuntimeError, ValueError, AttributeError) as e:
            logger.error("Error in chat_stream: %s", e)
            yield f"data: Error: {str(e)}\n\n"
        finally:
            _cleanup_tasks(
                message_task,
                event_task,
                agent_service,
                event_queue,
            )

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()

    agent_service = getattr(app.state, "agent_service", None)
    if not agent_service or not agent_service.initialized:
        await websocket.send_json({"error": "Agent Service not initialized"})
        await websocket.close()
        return

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message = data.get("message", "")

            if not message:
                continue

            # Send response chunks
            async for chunk in agent_service.chat_stream(message):
                await websocket.send_json({"type": "chunk", "content": chunk})

            # Send completion signal
            await websocket.send_json({"type": "done"})

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except (RuntimeError, ValueError, AttributeError) as e:
        # 捕获 WebSocket 对话过程中的运行时错误
        logger.error("Error in WebSocket chat: %s", e)
        await websocket.send_json({"error": str(e)})


# Sandbox management endpoints
@app.get("/api/sandboxes", response_model=SandboxInfoResponse)
async def list_sandboxes():
    """Get list of all sandboxes"""
    agent_service = getattr(app.state, "agent_service", None)
    if not agent_service or not agent_service.initialized:
        raise HTTPException(
            status_code=503,
            detail="Agent Service not initialized",
        )

    try:
        sandbox_info = agent_service.get_sandbox_info()
        return SandboxInfoResponse(sandboxes=sandbox_info)
    except (RuntimeError, ValueError, AttributeError) as e:
        # 捕获获取沙箱信息过程中的运行时错误
        logger.error("Error getting sandbox info: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/sandboxes")
async def create_sandbox(sandbox_type: str):
    """
    Create a sandbox of the specified type and return sandbox_id

    Args:
        sandbox_type: Sandbox type ('linux', 'windows', 'browser', 'mobile')

    Returns:
        Dictionary containing sandbox_id and related information
    """
    agent_service = getattr(app.state, "agent_service", None)
    if not agent_service or not agent_service.initialized:
        raise HTTPException(
            status_code=503,
            detail="Agent Service not initialized",
        )

    if sandbox_type not in ["linux", "windows", "browser", "mobile"]:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid sandbox type: {sandbox_type}. "
                "Valid types: linux, windows, browser, mobile"
            ),
        )

    try:
        result = await agent_service.create_sandbox(sandbox_type)
        if result and result.get("success"):
            return result
        else:
            error_msg = (
                result.get("error", "Failed to create sandbox")
                if result
                else "Failed to create sandbox"
            )
            raise HTTPException(status_code=500, detail=error_msg)
    except HTTPException as e:
        raise e
    except (RuntimeError, ValueError, AttributeError) as e:
        # 捕获创建沙箱过程中的运行时错误
        logger.error("Error creating sandbox: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/sandboxes/{sandbox_id}/screenshot")
async def get_screenshot(sandbox_id: str):
    """Get screenshot from a specific sandbox"""
    agent_service = getattr(app.state, "agent_service", None)
    if not agent_service or not agent_service.initialized:
        raise HTTPException(
            status_code=503,
            detail="Agent Service not initialized",
        )

    try:
        screenshot_info = await agent_service.get_screenshot(sandbox_id)
        if screenshot_info and screenshot_info.get("success"):
            return screenshot_info
        else:
            error_msg = (
                screenshot_info.get("error", "Screenshot not available")
                if screenshot_info
                else "Screenshot not available"
            )
            raise HTTPException(status_code=404, detail=error_msg)
    except HTTPException as e:
        raise e
    except (RuntimeError, ValueError, AttributeError) as e:
        # 捕获获取截图过程中的运行时错误
        logger.error("Error getting screenshot: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/sandboxes/{sandbox_id}/resource_url")
async def get_resource_url(sandbox_id: str):
    """Get resource URL for a specific sandbox"""
    agent_service = getattr(app.state, "agent_service", None)
    if not agent_service or not agent_service.initialized:
        raise HTTPException(
            status_code=503,
            detail="Agent Service not initialized",
        )

    try:
        resource_url_info = await agent_service.get_resource_url(sandbox_id)
        if resource_url_info and resource_url_info.get("success"):
            return resource_url_info
        else:
            error_msg = (
                resource_url_info.get("error", "Unknown error")
                if resource_url_info
                else "Failed to get resource URL"
            )
            raise HTTPException(status_code=404, detail=error_msg)
    except HTTPException as e:
        raise e
    except (RuntimeError, ValueError, AttributeError) as e:
        # 捕获获取 resource_url 过程中的运行时错误
        logger.error("Error getting resource_url: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/sandboxes/{sandbox_id}/tools")
async def list_tools(sandbox_id: str):
    """Get available tools for a specific sandbox"""
    agent_service = getattr(app.state, "agent_service", None)
    if not agent_service or not agent_service.initialized:
        raise HTTPException(
            status_code=503,
            detail="Agent Service not initialized",
        )

    try:
        # 通过 sandbox_id 获取沙箱类型
        sandbox_manager = agent_service.sandbox_manager
        if not sandbox_manager:
            raise HTTPException(
                status_code=503,
                detail="Sandbox manager not available",
            )

        sandbox_type = sandbox_manager.get_sandbox_type_by_id(sandbox_id)
        if not sandbox_type:
            raise HTTPException(
                status_code=404,
                detail=f"Sandbox {sandbox_id} not found",
            )

        tools_info = agent_service.get_tools_info()
        # Filter tools by sandbox type
        filtered_tools = {
            name: info
            for name, info in tools_info.items()
            if info.get("sandbox_type") == sandbox_type
        }
        return {
            "sandbox_id": sandbox_id,
            "sandbox_type": sandbox_type,
            "tools": filtered_tools,
        }
    except HTTPException as e:
        raise e
    except (RuntimeError, ValueError, AttributeError) as e:
        # 捕获获取工具信息过程中的运行时错误
        logger.error("Error getting tools: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/tools")
async def list_all_tools():
    """Get all available tools"""
    agent_service = getattr(app.state, "agent_service", None)
    if not agent_service or not agent_service.initialized:
        raise HTTPException(
            status_code=503,
            detail="Agent Service not initialized",
        )

    try:
        tools_info = agent_service.get_tools_info()
        return {"tools": tools_info}
    except (RuntimeError, ValueError, AttributeError) as e:
        # 捕获获取所有工具信息过程中的运行时错误
        logger.error("Error getting all tools: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
