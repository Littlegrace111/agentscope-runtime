# -*- coding: utf-8 -*-
"""
Tool Registry for Multi-Sandbox Agent

This module provides tool registration functionality that dynamically
discovers tools from multiple sandboxes and registers them to AgentScope
Toolkit.
"""
import logging
from functools import wraps
from typing import Any, Callable, Dict

# Third-party imports
from agentscope.tool import Toolkit, ToolResponse  # type: ignore

from .multi_sandbox_manager import MultiSandboxManager

logger = logging.getLogger(__name__)


class ToolRegistry:
    """工具注册器，用于将多沙箱工具注册到 AgentScope Toolkit"""

    def __init__(self, sandbox_manager: MultiSandboxManager):
        """
        初始化工具注册器

        Args:
            sandbox_manager: 多沙箱管理器实例
        """
        self.sandbox_manager = sandbox_manager
        self.toolkit = Toolkit()
        self.registered_tools: Dict[str, Dict[str, Any]] = {}

    def _create_tool_wrapper(
        self,
        sandbox_type: str,
        tool_name: str,
        tool_info: Dict[str, Any],
    ) -> Callable:
        """
        创建工具包装函数

        Args:
            sandbox_type: 沙箱类型
            tool_name: 工具名称
            tool_info: 工具信息

        Returns:
            包装后的工具函数
        """

        @wraps(lambda *args, **kwargs: None)
        async def tool_wrapper(**kwargs) -> ToolResponse:
            """
            工具包装函数，调用对应沙箱的工具

            Args:
                **kwargs: 工具参数

            Returns:
                ToolResponse 对象
            """
            try:
                # 确保沙箱已创建（按需创建）
                sandbox = await self.sandbox_manager.ensure_sandbox(
                    sandbox_type,
                )
                if not sandbox:
                    return ToolResponse(
                        content=(
                            f"❌ Failed to create or access "
                            f"sandbox '{sandbox_type}'. "
                            "Please check the sandbox configuration."
                        ),
                    )

                # 调用沙箱工具
                result = sandbox.call_tool(tool_name, kwargs)

                # 处理返回结果
                if result.get("success"):
                    output = result.get("output", "")
                    content = result.get("content", "")
                    data = result.get("data", {})
                    screenshot = result.get("screenshot", "")

                    # 构建响应内容
                    response_parts = []
                    if output:
                        response_parts.append(f"✅ Output:\n{output}")
                    if content:
                        response_parts.append(f"✅ Content:\n{content}")
                    if data:
                        response_parts.append(f"✅ Data: {data}")
                    if screenshot:
                        response_parts.append("✅ Screenshot captured")

                    response_content = (
                        "\n".join(response_parts)
                        if response_parts
                        else "✅ Operation completed successfully"
                    )

                    return ToolResponse(content=response_content)
                else:
                    error = result.get("error", "Unknown error")
                    return ToolResponse(
                        content=f"❌ Operation failed: {error}",
                    )

            except (RuntimeError, ValueError, AttributeError) as e:
                # 捕获工具调用过程中的运行时错误
                logger.error(
                    "Error calling tool %s_%s: %s",
                    sandbox_type,
                    tool_name,
                    e,
                )
                return ToolResponse(
                    content=f"❌ Error: {str(e)}",
                )

        # 设置函数名称和文档字符串
        tool_wrapper.__name__ = f"{sandbox_type}_{tool_name}"
        tool_wrapper.__doc__ = (
            f"Execute {tool_name} on {sandbox_type} sandbox.\n\n"
            f"Sandbox: {sandbox_type}\n"
            f"Tool: {tool_name}\n"
            f"Parameters: {tool_info.get('parameters', 'N/A')}"
        )

        return tool_wrapper

    async def register_all_tools(self) -> Toolkit:
        """
        注册所有沙箱的工具到 Toolkit

        Returns:
            配置好的 Toolkit 实例
        """
        logger.info("Registering tools from all sandboxes...")

        # 获取所有沙箱的工具列表
        # 注意：如果沙箱未初始化，get_all_tools 会返回空列表
        # 但工具仍然会被注册，实际使用时沙箱会按需创建
        all_tools = self.sandbox_manager.get_all_tools()

        # 为每个工具创建包装函数并注册
        for sandbox_type, tools_info in all_tools.items():
            # 跳过有错误的沙箱
            if (
                "error" in tools_info
                and tools_info.get("status") != "not_initialized"
            ):
                logger.warning(
                    "Skipping %s due to error: %s",
                    sandbox_type,
                    tools_info["error"],
                )
                continue

            tools = tools_info.get("tools", [])

            # 注意：get_all_tools() 已经能够从未初始化的沙箱获取工具列表
            # 通过创建临时实例（不初始化云端会话）来调用 list_tools()
            # 因此这里不需要再临时创建沙箱

            logger.info(
                "Registering %d tools from %s sandbox",
                len(tools),
                sandbox_type,
            )

            for tool_name in tools:
                try:
                    # 创建工具包装函数
                    tool_wrapper = self._create_tool_wrapper(
                        sandbox_type=sandbox_type,
                        tool_name=tool_name,
                        tool_info={"parameters": "See sandbox documentation"},
                    )

                    # 生成工具描述
                    tool_description = (
                        f"Execute {tool_name} on {sandbox_type} sandbox. "
                        f"This tool operates on the {sandbox_type} GUI "
                        f"environment. Use this tool when you need to "
                        f"perform operations on {sandbox_type}."
                    )

                    # 注册工具
                    self.toolkit.register_tool_function(
                        tool_wrapper,
                        func_description=tool_description,
                    )

                    # 记录已注册的工具
                    full_tool_name = f"{sandbox_type}_{tool_name}"
                    self.registered_tools[full_tool_name] = {
                        "sandbox_type": sandbox_type,
                        "tool_name": tool_name,
                        "description": tool_description,
                    }

                    logger.debug("Registered tool: %s", full_tool_name)

                except (RuntimeError, ValueError, AttributeError) as e:
                    # 捕获工具注册过程中的运行时错误
                    logger.error(
                        "Error registering tool %s_%s: %s",
                        sandbox_type,
                        tool_name,
                        e,
                    )
                    continue

        logger.info("Total %d tools registered", len(self.registered_tools))
        return self.toolkit

    def get_registered_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        获取已注册的工具列表

        Returns:
            已注册工具的字典
        """
        return self.registered_tools

    def get_toolkit(self) -> Toolkit:
        """
        获取配置好的 Toolkit

        Returns:
            Toolkit 实例
        """
        return self.toolkit
