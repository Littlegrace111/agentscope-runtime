# -*- coding: utf-8 -*-
"""
Agent Service for Multi-Sandbox Agent

This module provides the AgentScope agent service that integrates with
multiple sandboxes and handles user interactions.
"""
import asyncio
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

from agentscope import agent, init  # type: ignore
from agentscope.formatter import DashScopeChatFormatter  # type: ignore
from agentscope.message import Msg  # type: ignore
from agentscope.model import DashScopeChatModel  # type: ignore
from agentscope.pipeline import stream_printing_messages  # type: ignore

from .multi_sandbox_manager import MultiSandboxManager
from .prompt_builder import create_system_prompt
from .tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


class AgentService:
    """智能体服务，封装 AgentScope Agent 和多沙箱管理"""

    def __init__(
        self,
        dashscope_api_key: str,
        agentbay_api_key: str,
        model_name: str = "qwen-max",
        session_id: str = "agent_session",
        user_id: str = "user",
    ):
        """
        初始化智能体服务

        Args:
            dashscope_api_key: DashScope API Key
            agentbay_api_key: AgentBay API Key
            model_name: 模型名称，默认为 qwen-max
            session_id: 会话 ID
            user_id: 用户 ID
        """
        self.dashscope_api_key = dashscope_api_key
        self.agentbay_api_key = agentbay_api_key
        self.model_name = model_name
        self.session_id = session_id
        self.user_id = user_id

        self.sandbox_manager: Optional[MultiSandboxManager] = None
        self.tool_registry: Optional[ToolRegistry] = None
        self.agent: Optional[Any] = None
        self.initialized = False
        self._event_listeners: List[asyncio.Queue] = []

    async def initialize(self) -> bool:
        """
        初始化智能体服务

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing Agent Service...")

            # 初始化 AgentScope
            init(
                project="agentbay_multi_sandbox",
                name="agentbay_multi_sandbox",
                logging_path="agentbay_multi_sandbox.log",
                logging_level="DEBUG",
                studio_url="http://localhost:3000",
            )

            # 创建多沙箱管理器（不预先初始化沙箱）
            self.sandbox_manager = MultiSandboxManager(
                agentbay_api_key=self.agentbay_api_key,
                session_id=self.session_id,
                user_id=self.user_id,
            )
            self.sandbox_manager.set_sandbox_created_callback(
                self._on_sandbox_created,
            )

            # 注意：沙箱将按需创建，不在启动时预先初始化
            logger.info(
                "Sandbox manager created. Sandboxes will be created "
                "on demand when needed.",
            )

            # 创建工具注册器
            self.tool_registry = ToolRegistry(self.sandbox_manager)

            # 注册所有工具（异步方法，因为可能需要临时创建沙箱）
            toolkit = await self.tool_registry.register_all_tools()

            # 创建 DashScope 模型
            model = DashScopeChatModel(
                model_name=self.model_name,
                api_key=self.dashscope_api_key,
            )

            # 创建 DashScope formatter
            formatter = DashScopeChatFormatter()

            # 创建系统提示词
            sys_prompt = self._create_system_prompt()

            # 创建 ReActAgent
            self.agent = agent.ReActAgent(
                name="MultiSandboxAssistant",
                sys_prompt=sys_prompt,
                model=model,
                formatter=formatter,
                toolkit=toolkit,
            )

            self.initialized = True
            logger.info("Agent Service initialized successfully")
            return True

        except (
            RuntimeError,
            ValueError,
            AttributeError,
            TypeError,
        ) as e:
            # 捕获初始化过程中可能出现的运行时错误
            logger.error("Failed to initialize Agent Service: %s", e)
            return False

    def _create_system_prompt(self) -> str:
        """
        创建系统提示词

        Returns:
            系统提示词字符串
        """
        # 获取所有沙箱的工具信息
        if not self.sandbox_manager:
            return "Agent service not properly initialized."
        all_tools = self.sandbox_manager.get_all_tools()
        return create_system_prompt(all_tools)

    async def chat(self, message: str) -> str:
        """
        与智能体对话（非流式）

        Args:
            message: 用户消息

        Returns:
            智能体回复
        """
        if not self.initialized or not self.agent:
            raise RuntimeError("Agent Service not initialized")

        try:
            user_msg = Msg(name="user", role="user", content=message)
            response = await self.agent.reply(user_msg)
            return (
                response.content
                if hasattr(response, "content")
                else str(response)
            )
        except (RuntimeError, AttributeError, ValueError) as e:
            # 捕获对话过程中的运行时错误
            logger.error("Error in chat: %s", e)
            raise

    async def chat_stream(self, message: str) -> AsyncGenerator[str, None]:
        """
        与智能体流式对话

        Args:
            message: 用户消息

        Yields:
            智能体回复的文本片段
        """
        if not self.initialized or not self.agent:
            raise RuntimeError("Agent Service not initialized")

        try:
            user_msg = Msg(name="user", role="user", content=message)
            local_truncate_memory = ""

            async for msg, _last in stream_printing_messages(
                agents=[self.agent],
                coroutine_task=self.agent(user_msg),
            ):
                async for chunk in self._process_message(
                    msg,
                    local_truncate_memory,
                ):
                    yield chunk
                    # Update memory after yielding
                    if isinstance(chunk, str):
                        local_truncate_memory = (
                            local_truncate_memory + chunk
                            if local_truncate_memory
                            else chunk
                        )

        except (RuntimeError, AttributeError, ValueError) as e:
            logger.error("Error in chat_stream: %s", e)
            yield f"Error: {str(e)}"

    async def _process_message(
        self,
        msg: Any,
        local_truncate_memory: str,
    ) -> AsyncGenerator[str, None]:
        """Process a message and yield text chunks."""
        if hasattr(msg, "content"):
            async for chunk in self._process_content(
                msg.content,
                local_truncate_memory,
            ):
                yield chunk
        elif isinstance(msg, str):
            async for chunk in self._process_string_content(
                msg,
                local_truncate_memory,
            ):
                yield chunk

    async def _process_content(
        self,
        content: Any,
        local_truncate_memory: str,
    ) -> AsyncGenerator[str, None]:
        """Process content (string or list) and yield text chunks."""
        if isinstance(content, str):
            async for chunk in self._process_string_content(
                content,
                local_truncate_memory,
            ):
                yield chunk
        elif isinstance(content, list):
            async for chunk in self._process_list_content(
                content,
                local_truncate_memory,
            ):
                yield chunk

    async def _process_string_content(
        self,
        content: str,
        local_truncate_memory: str,
    ) -> AsyncGenerator[str, None]:
        """Process string content and extract incremental text."""
        if not content or content == local_truncate_memory:
            return

        if content.startswith(local_truncate_memory):
            new_content = content[len(local_truncate_memory) :]
            if new_content:
                yield new_content
        else:
            # 内容不连续，可能是新消息
            yield content

    async def _process_list_content(
        self,
        content_list: List[Any],
        local_truncate_memory: str,
    ) -> AsyncGenerator[str, None]:
        """Process list content and yield text chunks."""
        for element in content_list:
            if isinstance(element, str) and element:
                # 字符串元素：已经是增量，直接 yield
                yield element
            elif isinstance(element, dict):
                async for chunk in self._process_dict_element(
                    element,
                    local_truncate_memory,
                ):
                    yield chunk

    async def _process_dict_element(
        self,
        element: Dict[str, Any],
        local_truncate_memory: str,
    ) -> AsyncGenerator[str, None]:
        """Process dictionary element and extract text content."""
        element_type = element.get("type", "")
        if element_type != "text":
            return

        text = element.get("text", "")
        if not text:
            return

        # 使用 removeprefix 提取增量
        new_text = text.removeprefix(local_truncate_memory)
        if new_text:
            yield new_text

    def get_sandbox_info(self) -> Dict[str, Any]:
        """
        获取沙箱信息

        Returns:
            沙箱信息字典
        """
        if not self.sandbox_manager:
            return {}
        return self.sandbox_manager.get_sandbox_info()

    async def create_sandbox(
        self,
        sandbox_type: str,
    ) -> Optional[Dict[str, Any]]:
        """
        创建指定类型的沙箱

        Args:
            sandbox_type: 沙箱类型 ('linux', 'windows', 'browser', 'mobile')

        Returns:
            包含 sandbox_id 的字典，如果失败则返回 None
        """
        if not self.sandbox_manager:
            return {
                "success": False,
                "error": "Agent service not properly initialized.",
            }

        if sandbox_type not in ["linux", "windows", "browser", "mobile"]:
            return {
                "success": False,
                "error": f"Invalid sandbox type: {sandbox_type}",
            }

        try:
            # 确保沙箱已创建（按需创建）
            sandbox = await self.sandbox_manager.ensure_sandbox(sandbox_type)
            if not sandbox:
                return {
                    "success": False,
                    "error": (f"Failed to create sandbox {sandbox_type}."),
                }

            sandbox_id = sandbox.sandbox_id
            if sandbox_id:
                return {
                    "success": True,
                    "sandbox_id": sandbox_id,
                    "sandbox_type": sandbox_type,
                    "image_id": self.sandbox_manager.IMAGE_IDS[sandbox_type],
                }
            else:
                return {
                    "success": False,
                    "error": "Sandbox created but no sandbox_id returned",
                }

        except (RuntimeError, ValueError, AttributeError) as e:
            # 捕获创建沙箱过程中的运行时错误
            logger.error(
                "Error creating sandbox %s: %s",
                sandbox_type,
                e,
            )
            return {
                "success": False,
                "error": str(e),
            }

    def get_tools_info(self) -> Dict[str, Any]:
        """
        获取工具信息

        Returns:
            工具信息字典
        """
        if not self.tool_registry:
            return {}
        return self.tool_registry.get_registered_tools()

    async def get_screenshot(
        self,
        sandbox_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        获取指定沙箱的截图

        Args:
            sandbox_id: 沙箱 ID

        Returns:
            截图信息字典，包含 base64 编码的图片
        """
        if not self.sandbox_manager:
            return {
                "success": False,
                "error": "Agent service not properly initialized.",
            }

        # 通过 sandbox_id 查找沙箱
        sandbox = self.sandbox_manager.get_sandbox_by_id(sandbox_id)
        if not sandbox:
            return {
                "success": False,
                "error": f"Sandbox {sandbox_id} not found.",
            }

        # 获取沙箱类型
        sandbox_type = self.sandbox_manager.get_sandbox_type_by_id(sandbox_id)

        try:
            # 根据沙箱类型调用不同的截图工具
            if sandbox_type == "browser":
                result = sandbox.call_tool("browser_screenshot", {})
            elif sandbox_type in ["linux", "windows"]:
                result = sandbox.call_tool("screenshot", {})
            elif sandbox_type == "mobile":
                result = sandbox.call_tool("mobile_screenshot", {})
            else:
                return {
                    "success": False,
                    "error": f"Unknown sandbox type: {sandbox_type}",
                }

            if result.get("success"):
                screenshot = result.get("screenshot", "")
                screenshot_url = result.get("screenshot_url", "")
                return {
                    "success": True,
                    "screenshot": screenshot,
                    "screenshot_url": screenshot_url,
                    "sandbox_id": sandbox_id,
                    "sandbox_type": sandbox_type,
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                }

        except (RuntimeError, AttributeError, ValueError) as e:
            # 捕获获取截图过程中的运行时错误
            logger.error(
                "Error getting screenshot from %s: %s",
                sandbox_id,
                e,
            )
            return {
                "success": False,
                "error": str(e),
            }

    async def get_resource_url(
        self,
        sandbox_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        获取指定沙箱的 resource_url

        Args:
            sandbox_id: 沙箱 ID

        Returns:
            包含 resource_url 的字典，如果失败则返回 None
        """
        if not self.sandbox_manager:
            return {
                "success": False,
                "error": "Agent service not properly initialized.",
            }

        # 通过 sandbox_id 查找沙箱
        sandbox = self.sandbox_manager.get_sandbox_by_id(sandbox_id)
        if not sandbox:
            return {
                "success": False,
                "error": f"Sandbox {sandbox_id} not found.",
            }

        # 获取沙箱类型
        sandbox_type = self.sandbox_manager.get_sandbox_type_by_id(sandbox_id)

        try:
            # 通过 cloud_client 获取 session，然后调用 info() 获取 resource_url
            get_result = sandbox.cloud_client.get(sandbox_id)
            if not get_result.success:
                return {
                    "success": False,
                    "error": f"Sandbox {sandbox_id} not found",
                }

            session = get_result.session
            info_result = session.info()

            if info_result.success and info_result.data:
                info = info_result.data
                return {
                    "success": True,
                    "resource_url": info.resource_url,
                    "sandbox_id": info.session_id,
                    "resource_id": info.resource_id,
                    "app_id": info.app_id,
                    "resource_type": info.resource_type,
                    "sandbox_type": sandbox_type,
                }
            else:
                return {
                    "success": False,
                    "error": (
                        info_result.error_message
                        if hasattr(info_result, "error_message")
                        else "Failed to get session info"
                    ),
                }

        except (RuntimeError, AttributeError, ValueError) as e:
            # 捕获获取 resource_url 过程中的运行时错误
            logger.error(
                "Error getting resource_url from %s: %s",
                sandbox_id,
                e,
            )
            return {
                "success": False,
                "error": str(e),
            }

    async def cleanup(self):
        """清理资源"""
        try:
            if self.sandbox_manager:
                await self.sandbox_manager.cleanup_all_sandboxes()
            logger.info("Agent Service cleaned up")
        except (RuntimeError, AttributeError, ValueError) as e:
            # 捕获清理过程中的运行时错误
            logger.error("Error during cleanup: %s", e)

    def register_event_listener(self, queue: asyncio.Queue) -> None:
        """Register SSE event listener queue."""
        if queue not in self._event_listeners:
            self._event_listeners.append(queue)

    def unregister_event_listener(self, queue: asyncio.Queue) -> None:
        """Remove SSE event listener queue."""
        if queue in self._event_listeners:
            self._event_listeners.remove(queue)

    async def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit event to all registered listeners."""
        if not self._event_listeners:
            return

        event_payload = {
            "event": event_type,
            "data": data,
        }
        for listener in list(self._event_listeners):
            await listener.put(event_payload)

    async def _on_sandbox_created(
        self,
        sandbox_id: str,
        sandbox_type: str,
    ) -> None:
        """Handle sandbox creation events."""
        resource_info = await self.get_resource_url(sandbox_id)
        if resource_info and resource_info.get("success"):
            data = {
                "sandbox_id": sandbox_id,
                "sandbox_type": sandbox_type,
                "resource_url": resource_info.get("resource_url"),
                "image_id": resource_info.get("image_id"),
                "resource_id": resource_info.get("resource_id"),
                "app_id": resource_info.get("app_id"),
                "resource_type": resource_info.get("resource_type"),
                "status": "active",
            }
        else:
            data = {
                "sandbox_id": sandbox_id,
                "sandbox_type": sandbox_type,
                "resource_url": None,
                "status": "active",
                "error": (
                    resource_info.get("error")
                    if isinstance(resource_info, dict)
                    else "Failed to fetch resource URL"
                ),
            }

        await self._emit_event("sandbox_resource", data)
