# -*- coding: utf-8 -*-
"""
AgentBay Linux sandbox implementation.
"""
from typing import Any, Dict, Optional

from ...enums import SandboxType
from ...registry import SandboxRegistry
from .agentbay_sandbox_base import AgentbaySandboxBase


@SandboxRegistry.register(
    "agentbay-linux",
    sandbox_type="agentbay_linux",
    security_level="high",
    timeout=300,
    description="AgentBay Linux Sandbox Environment",
)
class AgentbayLinuxSandbox(AgentbaySandboxBase):
    """
    AgentBay Linux sandbox implementation.

    Supports Linux-specific operations:
    - Command execution
    - File operations
    - Directory management
    """

    def __init__(
        self,
        sandbox_id: Optional[str] = None,
        timeout: int = 3000,
        base_url: Optional[str] = None,
        bearer_token: Optional[str] = None,
        api_key: Optional[str] = None,
        image_id: str = "linux_latest",
        labels: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        """Initialize the AgentBay Linux sandbox."""
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
        """Get tool mapping for Linux sandbox."""
        return {
            "run_shell_command": self._execute_command,
            "run_ipython_cell": self._execute_code,
            "read_file": self._read_file,
            "write_file": self._write_file,
            "list_directory": self._list_directory,
            "create_directory": self._create_directory,
            "move_file": self._move_file,
            "delete_file": self._delete_file,
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

    def _execute_code(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute Python code in AgentBay."""
        code = arguments.get("code", "")
        result = session.code.run_code(code, "python")

        return {
            "success": result.success,
            "output": result.result,
            "error": result.error if hasattr(result, "error") else None,
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

    def list_tools(self, tool_type: Optional[str] = None) -> Dict[str, Any]:
        """List available tools in the Linux sandbox."""
        file_tools = [
            "read_file",
            "write_file",
            "list_directory",
            "create_directory",
            "move_file",
            "delete_file",
        ]
        command_tools = ["run_shell_command", "run_ipython_cell"]

        tools_by_type = {
            "file": file_tools,
            "command": command_tools,
        }

        if tool_type:
            tools = tools_by_type.get(tool_type, [])
            return {
                "tools": tools,
                "tool_type": tool_type,
                "sandbox_id": self._sandbox_id,
                "total_count": len(tools),
            }

        all_tools = file_tools + command_tools
        return {
            "tools": all_tools,
            "tools_by_type": tools_by_type,
            "sandbox_id": self._sandbox_id,
            "total_count": len(all_tools),
        }
