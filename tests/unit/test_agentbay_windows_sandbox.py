# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name, protected-access, unused-argument
"""
Unit tests for AgentbayWindowsSandbox implementation.
"""
from unittest.mock import MagicMock, patch

import pytest

from agentscope_runtime.sandbox.box.agentbay.agentbay_windows_sandbox import (
    AgentbayWindowsSandbox,
)
from agentscope_runtime.sandbox.enums import SandboxType


@pytest.fixture
def mock_agentbay_client():
    """Create a mock AgentBay client."""
    client = MagicMock()
    return client


@pytest.fixture
def mock_session():
    """Create a mock AgentBay session."""
    session = MagicMock()

    # Mock command execution
    command_result = MagicMock()
    command_result.success = True
    command_result.output = "test output"
    command_result.exit_code = 0
    session.command.execute_command.return_value = command_result

    # Mock file system operations
    file_result = MagicMock()
    file_result.success = True
    file_result.content = "file content"
    session.file_system.read_file.return_value = file_result
    session.file_system.write_file.return_value = file_result
    session.file_system.list_directory.return_value = file_result
    session.file_system.create_directory.return_value = file_result
    session.file_system.move_file.return_value = file_result
    session.file_system.delete_file.return_value = file_result
    file_result.files = ["file1.txt", "file2.txt"]

    # Mock computer operations
    screenshot_result = MagicMock()
    screenshot_result.success = True
    screenshot_result.data = "screenshot_url"
    session.computer.screenshot.return_value = screenshot_result

    app_result = MagicMock()
    app_result.success = True
    session.computer.start_app.return_value = app_result
    session.computer.stop_app.return_value = app_result
    session.computer.input_text.return_value = app_result

    window_result = MagicMock()
    window_result.success = True
    session.computer.window.maximize.return_value = window_result
    session.computer.window.minimize.return_value = window_result

    return session


@pytest.fixture
def mock_create_session_result():
    """Create a mock create session result."""
    result = MagicMock()
    result.success = True
    result.session = MagicMock()
    result.session.session_id = "test-session-123"
    return result


@pytest.fixture
def windows_sandbox(mock_agentbay_client, mock_create_session_result):
    """Create an AgentbayWindowsSandbox with mocked dependencies."""
    base_path = "agentscope_runtime.sandbox.box.agentbay.agentbay_sandbox_base"
    with patch(f"{base_path}.AgentBay") as mock_agentbay_class:
        mock_agentbay_class.return_value = mock_agentbay_client
        mock_agentbay_client.create.return_value = mock_create_session_result

        with patch(f"{base_path}.CreateSessionParams"):
            sandbox = AgentbayWindowsSandbox(
                api_key="test-api-key",
                image_id="windows_latest",
            )
            yield sandbox


class TestAgentbayWindowsSandbox:
    """Test cases for AgentbayWindowsSandbox class."""

    def test_init(self, windows_sandbox):
        """Test initialization."""
        assert windows_sandbox.api_key == "test-api-key"
        assert windows_sandbox.image_id == "windows_latest"
        assert windows_sandbox.sandbox_type == SandboxType.AGENTBAY

    def test_list_tools_all(self, windows_sandbox):
        """Test listing all tools - priority test."""
        result = windows_sandbox.list_tools()

        # Verify structure
        assert "tools" in result
        assert "tools_by_type" in result
        assert "total_count" in result
        assert "sandbox_id" in result

        # Verify total count
        assert result["total_count"] == 13

        # Verify all tools are present
        expected_tools = [
            "read_file",
            "write_file",
            "list_directory",
            "create_directory",
            "move_file",
            "delete_file",
            "run_shell_command",
            "screenshot",
            "start_app",
            "stop_app",
            "input_text",
            "window_maximize",
            "window_minimize",
        ]
        assert set(result["tools"]) == set(expected_tools)

        # Verify tools_by_type structure
        assert "file" in result["tools_by_type"]
        assert "command" in result["tools_by_type"]
        assert "desktop" in result["tools_by_type"]
        assert "system" in result["tools_by_type"]

        # Verify file tools
        file_tools = result["tools_by_type"]["file"]
        assert len(file_tools) == 6
        assert "read_file" in file_tools
        assert "write_file" in file_tools
        assert "list_directory" in file_tools
        assert "create_directory" in file_tools
        assert "move_file" in file_tools
        assert "delete_file" in file_tools

        # Verify command tools
        command_tools = result["tools_by_type"]["command"]
        assert len(command_tools) == 1
        assert "run_shell_command" in command_tools

        # Verify desktop tools
        desktop_tools = result["tools_by_type"]["desktop"]
        assert len(desktop_tools) == 5
        assert "start_app" in desktop_tools
        assert "stop_app" in desktop_tools
        assert "input_text" in desktop_tools
        assert "window_maximize" in desktop_tools
        assert "window_minimize" in desktop_tools

        # Verify system tools
        system_tools = result["tools_by_type"]["system"]
        assert len(system_tools) == 1
        assert "screenshot" in system_tools

    def test_list_tools_by_type_file(self, windows_sandbox):
        """Test listing file tools only."""
        result = windows_sandbox.list_tools(tool_type="file")

        assert result["tool_type"] == "file"
        assert result["total_count"] == 6
        assert "read_file" in result["tools"]
        assert "write_file" in result["tools"]
        assert "list_directory" in result["tools"]
        assert "create_directory" in result["tools"]
        assert "move_file" in result["tools"]
        assert "delete_file" in result["tools"]

    def test_list_tools_by_type_command(self, windows_sandbox):
        """Test listing command tools only."""
        result = windows_sandbox.list_tools(tool_type="command")

        assert result["tool_type"] == "command"
        assert result["total_count"] == 1
        assert "run_shell_command" in result["tools"]

    def test_list_tools_by_type_desktop(self, windows_sandbox):
        """Test listing desktop tools only."""
        result = windows_sandbox.list_tools(tool_type="desktop")

        assert result["tool_type"] == "desktop"
        assert result["total_count"] == 5
        assert "start_app" in result["tools"]
        assert "stop_app" in result["tools"]
        assert "input_text" in result["tools"]
        assert "window_maximize" in result["tools"]
        assert "window_minimize" in result["tools"]

    def test_list_tools_by_type_system(self, windows_sandbox):
        """Test listing system tools only."""
        result = windows_sandbox.list_tools(tool_type="system")

        assert result["tool_type"] == "system"
        assert result["total_count"] == 1
        assert "screenshot" in result["tools"]

    def test_get_tool_mapping(self, windows_sandbox):
        """Test tool mapping contains all expected tools."""
        tool_mapping = windows_sandbox._get_tool_mapping()

        # Verify all tools are mapped
        assert "run_shell_command" in tool_mapping
        assert "read_file" in tool_mapping
        assert "write_file" in tool_mapping
        assert "list_directory" in tool_mapping
        assert "create_directory" in tool_mapping
        assert "move_file" in tool_mapping
        assert "delete_file" in tool_mapping
        assert "screenshot" in tool_mapping
        assert "start_app" in tool_mapping
        assert "stop_app" in tool_mapping
        assert "input_text" in tool_mapping
        assert "window_maximize" in tool_mapping
        assert "window_minimize" in tool_mapping

        # Verify mapping count matches list_tools
        assert len(tool_mapping) == 13

    def test_desktop_operations(self, windows_sandbox, mock_session):
        """Test desktop automation operations."""
        # Test start_app
        result = windows_sandbox._start_app(
            mock_session,
            {"app_name": "notepad"},
        )
        assert result["success"] is True

        # Test stop_app
        result = windows_sandbox._stop_app(
            mock_session,
            {"app_name": "notepad"},
        )
        assert result["success"] is True

        # Test input_text
        result = windows_sandbox._input_text(
            mock_session,
            {"text": "Hello"},
        )
        assert result["success"] is True

        # Test window_maximize
        result = windows_sandbox._window_maximize(mock_session, {})
        assert result["success"] is True

        # Test window_minimize
        result = windows_sandbox._window_minimize(mock_session, {})
        assert result["success"] is True

    def test_screenshot(self, windows_sandbox, mock_session):
        """Test taking a screenshot."""
        result = windows_sandbox._take_screenshot(mock_session, {})
        assert result["success"] is True
        assert result["screenshot_url"] == "screenshot_url"
