# -*- coding: utf-8 -*-
"""
AgentBay Mobile sandbox implementation.
"""
from typing import Any, Dict, Optional

from agentbay.mobile import KeyCode  # type: ignore

from ...enums import SandboxType
from ...registry import SandboxRegistry
from .agentbay_sandbox_base import AgentbaySandboxBase


@SandboxRegistry.register(
    "agentbay-mobile",
    sandbox_type="agentbay_mobile",
    security_level="high",
    timeout=300,
    description="AgentBay Mobile Sandbox Environment",
)
class AgentbayMobileSandbox(AgentbaySandboxBase):
    """
    AgentBay Mobile sandbox implementation.

    Supports mobile automation operations:
    - Mobile UI interaction (click, swipe, input)
    - Key events
    - Application management
    - ADB connection
    - File operations
    """

    def __init__(
        self,
        sandbox_id: Optional[str] = None,
        timeout: int = 3000,
        base_url: Optional[str] = None,
        bearer_token: Optional[str] = None,
        api_key: Optional[str] = None,
        image_id: str = "mobile_latest",
        labels: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        """Initialize the AgentBay Mobile sandbox."""
        super().__init__(
            sandbox_id=sandbox_id,
            timeout=timeout,
            base_url=base_url,
            bearer_token=bearer_token,
            sandbox_type=SandboxType.AGENTBAY,
            api_key=api_key,
            image_id=image_id,
            labels=labels,
            **kwargs,
        )

    def _get_tool_mapping(self) -> Dict[str, Any]:
        """Get tool mapping for Mobile sandbox."""
        return {
            "read_file": self._read_file,
            "write_file": self._write_file,
            "list_directory": self._list_directory,
            "mobile_click": self._mobile_click,
            "mobile_swipe": self._mobile_swipe,
            "mobile_input_text": self._mobile_input_text,
            "mobile_send_key": self._mobile_send_key,
            "mobile_start_app": self._mobile_start_app,
            "mobile_stop_app": self._mobile_stop_app,
            "mobile_screenshot": self._mobile_screenshot,
        }

    def _read_file(self, session, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Read a file from AgentBay."""
        path = arguments.get("path", "")
        result = session.file_system.read_file(path)

        return {
            "success": result.success,
            "content": result.content if hasattr(result, "content") else None,
            "error": result.error if hasattr(result, "error") else None,
        }

    def _write_file(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Write a file to AgentBay."""
        path = arguments.get("path", "")
        content = arguments.get("content", "")
        result = session.file_system.write_file(path, content)

        return {
            "success": result.success,
            "error": result.error if hasattr(result, "error") else None,
        }

    def _list_directory(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """List directory contents in AgentBay."""
        path = arguments.get("path", ".")
        result = session.file_system.list_directory(path)

        return {
            "success": result.success,
            "files": result.files if hasattr(result, "files") else [],
            "error": result.error if hasattr(result, "error") else None,
        }

    def _mobile_click(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Click on mobile screen."""
        x = arguments.get("x", 0)
        y = arguments.get("y", 0)
        result = session.mobile.click(x=x, y=y)
        return {
            "success": result.success,
            "error": result.error if hasattr(result, "error") else None,
        }

    def _mobile_swipe(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Swipe on mobile screen."""
        start_x = arguments.get("start_x", 0)
        start_y = arguments.get("start_y", 0)
        end_x = arguments.get("end_x", 0)
        end_y = arguments.get("end_y", 0)
        result = session.mobile.swipe(
            start_x=start_x,
            start_y=start_y,
            end_x=end_x,
            end_y=end_y,
        )
        return {
            "success": result.success,
            "error": result.error if hasattr(result, "error") else None,
        }

    def _mobile_input_text(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Input text on mobile."""
        text = arguments.get("text", "")
        result = session.mobile.input_text(text)
        return {
            "success": result.success,
            "error": result.error if hasattr(result, "error") else None,
        }

    def _mobile_send_key(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Send key event on mobile."""
        key_name = arguments.get("key", "HOME")
        key_code = getattr(KeyCode, key_name.upper(), KeyCode.HOME)
        result = session.mobile.send_key(key_code)
        return {
            "success": result.success,
            "error": result.error if hasattr(result, "error") else None,
        }

    def _mobile_screenshot(
        self,
        session,
        arguments: Dict[str, Any],  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        """Take mobile screenshot."""
        result = session.mobile.screenshot()
        return {
            "success": result.success,
            "screenshot_url": result.data if hasattr(result, "data") else None,
            "error": result.error if hasattr(result, "error") else None,
        }

    def _mobile_start_app(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Start mobile app."""
        app_name = arguments.get("app_name", "")
        result = session.mobile.start_app(app_name)
        return {
            "success": result.success,
            "error": result.error if hasattr(result, "error") else None,
        }

    def _mobile_stop_app(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Stop mobile app."""
        app_name = arguments.get("app_name", "")
        result = session.mobile.stop_app(app_name)
        return {
            "success": result.success,
            "error": result.error if hasattr(result, "error") else None,
        }

    def list_tools(self, tool_type: Optional[str] = None) -> Dict[str, Any]:
        """List available tools in the Mobile sandbox."""
        file_tools = ["read_file", "write_file", "list_directory"]
        ui_tools = [
            "mobile_click",
            "mobile_swipe",
            "mobile_input_text",
            "mobile_send_key",
        ]
        app_tools = ["mobile_start_app", "mobile_stop_app"]
        system_tools = ["mobile_screenshot"]

        tools_by_type = {
            "file": file_tools,
            "ui": ui_tools,
            "app": app_tools,
            "system": system_tools,
        }

        if tool_type:
            tools = tools_by_type.get(tool_type, [])
            return {
                "tools": tools,
                "tool_type": tool_type,
                "sandbox_id": self._sandbox_id,
                "total_count": len(tools),
            }

        all_tools = file_tools + ui_tools + app_tools + system_tools
        return {
            "tools": all_tools,
            "tools_by_type": tools_by_type,
            "sandbox_id": self._sandbox_id,
            "total_count": len(all_tools),
        }
