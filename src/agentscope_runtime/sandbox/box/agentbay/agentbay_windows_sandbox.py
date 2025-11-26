# -*- coding: utf-8 -*-
"""
AgentBay Windows sandbox implementation.
"""
from typing import Any, Dict, Optional

from ...enums import SandboxType
from ...registry import SandboxRegistry
from .agentbay_sandbox_base import AgentbaySandboxBase


@SandboxRegistry.register(
    "agentbay-windows",
    sandbox_type="agentbay_windows",
    security_level="high",
    timeout=300,
    description="AgentBay Windows Sandbox Environment",
)
class AgentbayWindowsSandbox(AgentbaySandboxBase):
    """
    AgentBay Windows sandbox implementation.

    Supports Windows-specific operations:
    - Command execution
    - File operations
    - Desktop automation
    - Application management
    - Screenshot capture
    """

    def __init__(
        self,
        sandbox_id: Optional[str] = None,
        timeout: int = 3000,
        base_url: Optional[str] = None,
        bearer_token: Optional[str] = None,
        api_key: Optional[str] = None,
        image_id: str = "windows_latest",
        labels: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        """Initialize the AgentBay Windows sandbox."""
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
        """Get tool mapping for Windows sandbox."""
        return {
            "run_shell_command": self._execute_command,
            "read_file": self._read_file,
            "write_file": self._write_file,
            "list_directory": self._list_directory,
            "create_directory": self._create_directory,
            "move_file": self._move_file,
            "delete_file": self._delete_file,
            "screenshot": self._take_screenshot,
            "start_app": self._start_app,
            "stop_app": self._stop_app,
            "input_text": self._input_text,
            "window_maximize": self._window_maximize,
            "window_minimize": self._window_minimize,
        }

    def _execute_command(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a shell command in AgentBay."""
        command = arguments.get("command", "")
        result = session.command.execute_command(command)

        return {
            "success": result.success,
            "output": result.output,
            "error": result.error if hasattr(result, "error") else None,
            "exit_code": (
                result.exit_code if hasattr(result, "exit_code") else 0
            ),
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

    def _create_directory(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a directory in AgentBay."""
        path = arguments.get("path", "")
        result = session.file_system.create_directory(path)

        return {
            "success": result.success,
            "error": result.error if hasattr(result, "error") else None,
        }

    def _move_file(self, session, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Move a file in AgentBay."""
        source = arguments.get("source", "")
        destination = arguments.get("destination", "")
        result = session.file_system.move_file(source, destination)

        return {
            "success": result.success,
            "error": result.error if hasattr(result, "error") else None,
        }

    def _delete_file(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Delete a file in AgentBay."""
        path = arguments.get("path", "")
        result = session.file_system.delete_file(path)

        return {
            "success": result.success,
            "error": result.error if hasattr(result, "error") else None,
        }

    def _take_screenshot(
        self,
        session,
        arguments: Dict[str, Any],  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        """Take a screenshot in AgentBay."""
        result = session.computer.screenshot()

        return {
            "success": result.success,
            "screenshot_url": result.data if hasattr(result, "data") else None,
            "error": result.error if hasattr(result, "error") else None,
        }

    def _start_app(self, session, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Start a Windows application."""
        app_name = arguments.get("app_name", "")
        result = session.computer.start_app(app_name)
        return {
            "success": result.success,
            "error": result.error if hasattr(result, "error") else None,
        }

    def _stop_app(self, session, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Stop a Windows application."""
        app_name = arguments.get("app_name", "")
        result = session.computer.stop_app(app_name)
        return {
            "success": result.success,
            "error": result.error if hasattr(result, "error") else None,
        }

    def _input_text(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Input text in Windows."""
        text = arguments.get("text", "")
        result = session.computer.input_text(text)
        return {
            "success": result.success,
            "error": result.error if hasattr(result, "error") else None,
        }

    def _window_maximize(
        self,
        session,
        arguments: Dict[str, Any],  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        """Maximize a window."""
        result = session.computer.window.maximize()
        return {
            "success": result.success,
            "error": result.error if hasattr(result, "error") else None,
        }

    def _window_minimize(
        self,
        session,
        arguments: Dict[str, Any],  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        """Minimize a window."""
        result = session.computer.window.minimize()
        return {
            "success": result.success,
            "error": result.error if hasattr(result, "error") else None,
        }

    def list_tools(self, tool_type: Optional[str] = None) -> Dict[str, Any]:
        """List available tools in the Windows sandbox."""
        file_tools = [
            "read_file",
            "write_file",
            "list_directory",
            "create_directory",
            "move_file",
            "delete_file",
        ]
        command_tools = ["run_shell_command"]
        desktop_tools = [
            "start_app",
            "stop_app",
            "input_text",
            "window_maximize",
            "window_minimize",
        ]
        system_tools = ["screenshot"]

        tools_by_type = {
            "file": file_tools,
            "command": command_tools,
            "desktop": desktop_tools,
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

        all_tools = file_tools + command_tools + desktop_tools + system_tools
        return {
            "tools": all_tools,
            "tools_by_type": tools_by_type,
            "sandbox_id": self._sandbox_id,
            "total_count": len(all_tools),
        }
