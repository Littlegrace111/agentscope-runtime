# -*- coding: utf-8 -*-
"""
Multi-Sandbox Manager for AgentBay GUI Sandboxes

This module provides a manager class to handle multiple AgentBay
sandbox instances.
"""
import inspect
import logging
from typing import Any, Awaitable, Callable, Dict, Optional

from agentscope_runtime.sandbox.box.agentbay import (  # type: ignore
    AgentbayBrowserSandbox,
    AgentbayLinuxSandbox,
    AgentbayMobileSandbox,
    AgentbayWindowsSandbox,
)

logger = logging.getLogger(__name__)


class MultiSandboxManager:
    """管理多个 AgentBay 沙箱实例"""

    # 沙箱类型到类的映射
    SANDBOX_CLASSES = {
        "linux": AgentbayLinuxSandbox,
        "windows": AgentbayWindowsSandbox,
        "browser": AgentbayBrowserSandbox,
        "mobile": AgentbayMobileSandbox,
    }

    # 沙箱类型到 image_id 的映射
    IMAGE_IDS = {
        "linux": "linux_latest",
        "windows": "windows_latest",
        "browser": "browser_latest",
        "mobile": "mobile_latest",
    }

    def __init__(
        self,
        agentbay_api_key: str,
        session_id: str = "multi_sandbox",
        user_id: str = "user",
    ):
        """
        初始化多沙箱管理器

        Args:
            agentbay_api_key: AgentBay API Key
            session_id: 会话 ID
            user_id: 用户 ID
        """
        self.agentbay_api_key = agentbay_api_key
        self.session_id = session_id
        self.user_id = user_id
        self.sandboxes: Dict[str, Optional[Any]] = {
            "linux": None,
            "windows": None,
            "browser": None,
            "mobile": None,
        }
        # 维护 sandbox_id 到 sandbox_type 的映射
        self.sandbox_id_to_type: Dict[str, str] = {}
        self._sandbox_created_callback: Optional[
            Callable[[str, str], Awaitable[None] | None]
        ] = None

    def set_sandbox_created_callback(
        self,
        callback: Optional[Callable[[str, str], Awaitable[None] | None]],
    ) -> None:
        """
        设置沙箱创建回调函数

        Args:
            callback: 回调函数，参数为 (sandbox_id, sandbox_type)
        """
        self._sandbox_created_callback = callback

    async def _notify_sandbox_created(
        self,
        sandbox_id: str,
        sandbox_type: str,
    ) -> None:
        """
        调用沙箱创建回调

        Args:
            sandbox_id: 沙箱 ID
            sandbox_type: 沙箱类型
        """
        if not self._sandbox_created_callback:
            return

        callback = self._sandbox_created_callback
        try:
            result = callback(sandbox_id, sandbox_type)
            if inspect.isawaitable(result):
                await result
        except (RuntimeError, ValueError, AttributeError, TypeError) as exc:
            logger.error(
                "Error in sandbox created callback for %s (%s): %s",
                sandbox_id,
                sandbox_type,
                exc,
            )

    async def initialize_all_sandboxes(self) -> bool:
        """
        初始化所有 4 个 GUI 沙箱

        Returns:
            True if all sandboxes initialized successfully, False otherwise
        """
        try:
            logger.info("Initializing all GUI sandboxes...")

            # 为每个沙箱类型直接创建实例
            for sandbox_type in self.sandboxes:
                try:
                    logger.info("Creating %s sandbox...", sandbox_type)
                    sandbox_class = self.SANDBOX_CLASSES[sandbox_type]
                    image_id = self.IMAGE_IDS[sandbox_type]

                    # 直接创建沙箱实例（会自动创建云端会话）
                    sandbox = sandbox_class(
                        api_key=self.agentbay_api_key,
                        image_id=image_id,
                    )

                    # 检查沙箱是否成功创建
                    # 使用公共属性 sandbox_id 而不是受保护的 _sandbox_id
                    sandbox_id = sandbox.sandbox_id
                    if sandbox_id:
                        logger.info(
                            "%s sandbox created: %s",
                            sandbox_type,
                            sandbox_id,
                        )
                        self.sandboxes[sandbox_type] = sandbox
                        logger.info(
                            "%s sandbox initialized successfully",
                            sandbox_type,
                        )
                    else:
                        logger.error(
                            "Failed to create %s sandbox: "
                            "no sandbox_id returned",
                            sandbox_type,
                        )
                        continue

                except (RuntimeError, ValueError, AttributeError) as e:
                    # 捕获初始化过程中可能出现的运行时错误
                    logger.error(
                        "Error initializing %s sandbox: %s",
                        sandbox_type,
                        e,
                    )
                    continue

            # 检查是否至少有一个沙箱初始化成功
            initialized_count = sum(
                1 for s in self.sandboxes.values() if s is not None
            )
            logger.info("Initialized %d/4 sandboxes", initialized_count)

            return initialized_count > 0

        except (RuntimeError, ValueError, AttributeError) as e:
            # 捕获初始化过程中的运行时错误
            logger.error("Failed to initialize sandboxes: %s", e)
            return False

    async def ensure_sandbox(self, sandbox_type: str) -> Optional[Any]:
        """
        确保指定类型的沙箱已创建，如果不存在则按需创建

        Args:
            sandbox_type: 沙箱类型 ('linux', 'windows', 'browser', 'mobile')

        Returns:
            沙箱实例，如果创建失败则返回 None
        """
        # 如果沙箱已存在，直接返回
        if self.sandboxes.get(sandbox_type):
            return self.sandboxes[sandbox_type]

        # 按需创建沙箱
        try:
            logger.info("Creating %s sandbox on demand...", sandbox_type)

            if sandbox_type not in self.SANDBOX_CLASSES:
                logger.error("Unknown sandbox type: %s", sandbox_type)
                return None

            sandbox_class = self.SANDBOX_CLASSES[sandbox_type]
            image_id = self.IMAGE_IDS[sandbox_type]

            # 创建沙箱实例（会自动创建云端会话）
            sandbox = sandbox_class(
                api_key=self.agentbay_api_key,
                image_id=image_id,
            )

            # 检查沙箱是否成功创建
            sandbox_id = sandbox.sandbox_id
            if sandbox_id:
                logger.info(
                    "%s sandbox created: %s",
                    sandbox_type,
                    sandbox_id,
                )
                self.sandboxes[sandbox_type] = sandbox
                # 维护 sandbox_id 到 sandbox_type 的映射
                self.sandbox_id_to_type[sandbox_id] = sandbox_type
                await self._notify_sandbox_created(sandbox_id, sandbox_type)
                return sandbox
            else:
                logger.error(
                    "Failed to create %s sandbox: no sandbox_id returned",
                    sandbox_type,
                )
                return None

        except (RuntimeError, ValueError, AttributeError) as e:
            logger.error(
                "Error creating %s sandbox: %s",
                sandbox_type,
                e,
            )
            return None

    def get_sandbox(self, sandbox_type: str) -> Optional[Any]:
        """
        获取指定类型的沙箱（不自动创建）

        Args:
            sandbox_type: 沙箱类型 ('linux', 'windows', 'browser', 'mobile')

        Returns:
            沙箱实例，如果不存在则返回 None
        """
        return self.sandboxes.get(sandbox_type)

    def get_sandbox_by_id(self, sandbox_id: str) -> Optional[Any]:
        """
        通过 sandbox_id 获取沙箱实例

        Args:
            sandbox_id: 沙箱 ID

        Returns:
            沙箱实例，如果不存在则返回 None
        """
        # 通过 sandbox_id 查找对应的 sandbox_type
        sandbox_type = self.sandbox_id_to_type.get(sandbox_id)
        if sandbox_type:
            return self.sandboxes.get(sandbox_type)
        return None

    def get_sandbox_type_by_id(self, sandbox_id: str) -> Optional[str]:
        """
        通过 sandbox_id 获取沙箱类型

        Args:
            sandbox_id: 沙箱 ID

        Returns:
            沙箱类型，如果不存在则返回 None
        """
        return self.sandbox_id_to_type.get(sandbox_id)

    def get_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有沙箱的工具列表（包括未初始化的沙箱）

        对于未初始化的沙箱，通过创建临时实例（不初始化沙箱）来获取工具列表

        Returns:
            字典，键为沙箱类型，值为工具列表信息
        """
        tools = {}
        for sandbox_type in self.sandboxes:
            sandbox = self.sandboxes.get(sandbox_type)
            if sandbox:
                # 沙箱已初始化，直接获取工具列表
                try:
                    tools[sandbox_type] = sandbox.list_tools()
                except (RuntimeError, AttributeError) as e:
                    # 捕获获取工具列表时可能出现的运行时错误
                    logger.error(
                        "Error getting tools for %s: %s",
                        sandbox_type,
                        e,
                    )
                    tools[sandbox_type] = {"tools": [], "error": str(e)}
            else:
                # 沙箱未初始化，创建临时实例来获取工具列表
                # 注意：这里只创建 Python 对象，不会创建云端沙箱会话
                try:
                    sandbox_class = self.SANDBOX_CLASSES[sandbox_type]
                    # 创建一个临时实例，但不传入 api_key，这样不会初始化云端会话
                    # 或者传入一个占位符，让 list_tools 可以工作
                    # 实际上，list_tools 方法返回的是硬编码的工具列表，不依赖实例状态
                    # 但为了安全，我们创建一个最小化的实例
                    temp_sandbox = sandbox_class.__new__(sandbox_class)
                    # 设置必要的属性，避免访问 _sandbox_id 时出错
                    # 使用 object.__setattr__ 来设置受保护属性
                    object.__setattr__(  # noqa: SLF001
                        temp_sandbox,
                        "_sandbox_id",
                        None,
                    )
                    # 调用 list_tools 获取工具列表
                    tools_info = temp_sandbox.list_tools()
                    tools[sandbox_type] = tools_info
                except (
                    RuntimeError,
                    AttributeError,
                    ValueError,
                    TypeError,
                ) as e:
                    # 如果创建临时实例失败，记录错误但继续
                    logger.warning(
                        "Failed to get tools for uninitialized %s: %s",
                        sandbox_type,
                        e,
                    )
                    tools[sandbox_type] = {
                        "tools": [],
                        "status": "not_initialized",
                        "error": str(e),
                    }
        return tools

    def get_sandbox_info(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有沙箱的信息

        Returns:
            字典，包含每个沙箱的状态和信息
            键为 sandbox_id（如果已创建）或 sandbox_type（如果未创建）
        """
        info = {}
        # 按 sandbox_id 组织信息
        for sandbox_id, sandbox_type in self.sandbox_id_to_type.items():
            sandbox = self.sandboxes.get(sandbox_type)
            if sandbox:
                info[sandbox_id] = {
                    "sandbox_id": sandbox_id,
                    "sandbox_type": sandbox_type,
                    "image_id": self.IMAGE_IDS[sandbox_type],
                    "status": "active",
                    "tools_count": len(sandbox.list_tools().get("tools", [])),
                }
        # 添加未初始化的沙箱类型信息
        for sandbox_type, sandbox in self.sandboxes.items():
            if not sandbox:
                # 使用 sandbox_type 作为键（因为还没有 sandbox_id）
                info[sandbox_type] = {
                    "sandbox_id": None,
                    "sandbox_type": sandbox_type,
                    "image_id": self.IMAGE_IDS[sandbox_type],
                    "status": "not_initialized",
                    "tools_count": 0,
                }
        return info

    async def cleanup_all_sandboxes(self):
        """清理所有沙箱资源"""
        try:
            logger.info("Cleaning up all sandboxes...")

            # 删除每个沙箱
            for sandbox_type, sandbox in self.sandboxes.items():
                if sandbox:
                    try:
                        # 调用沙箱的公共清理方法
                        sandbox.cleanup()
                        logger.info("%s sandbox cleaned up", sandbox_type)
                    except (RuntimeError, AttributeError, ValueError) as e:
                        # 捕获清理过程中可能出现的运行时错误
                        logger.error(
                            "Error cleaning up %s sandbox: %s",
                            sandbox_type,
                            e,
                        )

            # 清空沙箱字典
            self.sandboxes = {
                "linux": None,
                "windows": None,
                "browser": None,
                "mobile": None,
            }

            logger.info("All sandboxes cleaned up successfully")

        except (RuntimeError, AttributeError, ValueError) as e:
            # 捕获清理过程中的运行时错误，确保清理过程不会中断
            logger.error("Error during cleanup: %s", e)
