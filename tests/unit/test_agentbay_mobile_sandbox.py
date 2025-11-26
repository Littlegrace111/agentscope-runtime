# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name, protected-access, unused-argument
"""
Unit tests for AgentbayMobileSandbox implementation.
"""
from unittest.mock import MagicMock, patch

import pytest

from agentscope_runtime.sandbox.box.agentbay.agentbay_mobile_sandbox import (
    AgentbayMobileSandbox,
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

    # Mock file system operations
    file_result = MagicMock()
    file_result.success = True
    file_result.content = "file content"
    session.file_system.read_file.return_value = file_result
    session.file_system.write_file.return_value = file_result
    session.file_system.list_directory.return_value = file_result
    file_result.files = ["file1.txt", "file2.txt"]

    # Mock mobile operations
    mobile_result = MagicMock()
    mobile_result.success = True
    session.mobile.click.return_value = mobile_result
    session.mobile.swipe.return_value = mobile_result
    session.mobile.input_text.return_value = mobile_result
    session.mobile.send_key.return_value = mobile_result
    session.mobile.start_app.return_value = mobile_result
    session.mobile.stop_app.return_value = mobile_result

    screenshot_result = MagicMock()
    screenshot_result.success = True
    screenshot_result.data = "screenshot_url"
    session.mobile.screenshot.return_value = screenshot_result

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
def mobile_sandbox(mock_agentbay_client, mock_create_session_result):
    """Create an AgentbayMobileSandbox with mocked dependencies."""
    base_path = "agentscope_runtime.sandbox.box.agentbay.agentbay_sandbox_base"
    with patch(f"{base_path}.AgentBay") as mock_agentbay_class:
        mock_agentbay_class.return_value = mock_agentbay_client
        mock_agentbay_client.create.return_value = mock_create_session_result

        with patch(f"{base_path}.CreateSessionParams"):
            sandbox = AgentbayMobileSandbox(
                api_key="test-api-key",
                image_id="mobile_latest",
            )
            yield sandbox


class TestAgentbayMobileSandbox:
    """Test cases for AgentbayMobileSandbox class."""

    def test_init(self, mobile_sandbox):
        """Test initialization."""
        assert mobile_sandbox.api_key == "test-api-key"
        assert mobile_sandbox.image_id == "mobile_latest"
        assert mobile_sandbox.sandbox_type == SandboxType.AGENTBAY

    def test_list_tools_all(self, mobile_sandbox):
        """Test listing all tools - priority test."""
        result = mobile_sandbox.list_tools()

        # Verify structure
        assert "tools" in result
        assert "tools_by_type" in result
        assert "total_count" in result
        assert "sandbox_id" in result

        # Verify total count
        assert result["total_count"] == 10

        # Verify all tools are present
        expected_tools = [
            "read_file",
            "write_file",
            "list_directory",
            "mobile_click",
            "mobile_swipe",
            "mobile_input_text",
            "mobile_send_key",
            "mobile_start_app",
            "mobile_stop_app",
            "mobile_screenshot",
        ]
        assert set(result["tools"]) == set(expected_tools)

        # Verify tools_by_type structure
        assert "file" in result["tools_by_type"]
        assert "ui" in result["tools_by_type"]
        assert "app" in result["tools_by_type"]
        assert "system" in result["tools_by_type"]

        # Verify file tools
        file_tools = result["tools_by_type"]["file"]
        assert len(file_tools) == 3
        assert "read_file" in file_tools
        assert "write_file" in file_tools
        assert "list_directory" in file_tools

        # Verify UI tools
        ui_tools = result["tools_by_type"]["ui"]
        assert len(ui_tools) == 4
        assert "mobile_click" in ui_tools
        assert "mobile_swipe" in ui_tools
        assert "mobile_input_text" in ui_tools
        assert "mobile_send_key" in ui_tools

        # Verify app tools
        app_tools = result["tools_by_type"]["app"]
        assert len(app_tools) == 2
        assert "mobile_start_app" in app_tools
        assert "mobile_stop_app" in app_tools

        # Verify system tools
        system_tools = result["tools_by_type"]["system"]
        assert len(system_tools) == 1
        assert "mobile_screenshot" in system_tools

    def test_list_tools_by_type_file(self, mobile_sandbox):
        """Test listing file tools only."""
        result = mobile_sandbox.list_tools(tool_type="file")

        assert result["tool_type"] == "file"
        assert result["total_count"] == 3
        assert "read_file" in result["tools"]
        assert "write_file" in result["tools"]
        assert "list_directory" in result["tools"]
        assert "mobile_click" not in result["tools"]

    def test_list_tools_by_type_ui(self, mobile_sandbox):
        """Test listing UI tools only."""
        result = mobile_sandbox.list_tools(tool_type="ui")

        assert result["tool_type"] == "ui"
        assert result["total_count"] == 4
        assert "mobile_click" in result["tools"]
        assert "mobile_swipe" in result["tools"]
        assert "mobile_input_text" in result["tools"]
        assert "mobile_send_key" in result["tools"]

    def test_list_tools_by_type_app(self, mobile_sandbox):
        """Test listing app tools only."""
        result = mobile_sandbox.list_tools(tool_type="app")

        assert result["tool_type"] == "app"
        assert result["total_count"] == 2
        assert "mobile_start_app" in result["tools"]
        assert "mobile_stop_app" in result["tools"]

    def test_list_tools_by_type_system(self, mobile_sandbox):
        """Test listing system tools only."""
        result = mobile_sandbox.list_tools(tool_type="system")

        assert result["tool_type"] == "system"
        assert result["total_count"] == 1
        assert "mobile_screenshot" in result["tools"]

    def test_get_tool_mapping(self, mobile_sandbox):
        """Test tool mapping contains all expected tools."""
        tool_mapping = mobile_sandbox._get_tool_mapping()

        # Verify all tools are mapped
        assert "read_file" in tool_mapping
        assert "write_file" in tool_mapping
        assert "list_directory" in tool_mapping
        assert "mobile_click" in tool_mapping
        assert "mobile_swipe" in tool_mapping
        assert "mobile_input_text" in tool_mapping
        assert "mobile_send_key" in tool_mapping
        assert "mobile_start_app" in tool_mapping
        assert "mobile_stop_app" in tool_mapping
        assert "mobile_screenshot" in tool_mapping

        # Verify mapping count matches list_tools
        assert len(tool_mapping) == 10

    def test_mobile_ui_operations(self, mobile_sandbox, mock_session):
        """Test mobile UI operations."""
        # Test mobile_click
        result = mobile_sandbox._mobile_click(
            mock_session,
            {"x": 100, "y": 200},
        )
        assert result["success"] is True

        # Test mobile_swipe
        result = mobile_sandbox._mobile_swipe(
            mock_session,
            {
                "start_x": 100,
                "start_y": 200,
                "end_x": 300,
                "end_y": 400,
            },
        )
        assert result["success"] is True

        # Test mobile_input_text
        result = mobile_sandbox._mobile_input_text(
            mock_session,
            {"text": "Hello"},
        )
        assert result["success"] is True

        # Test mobile_send_key
        result = mobile_sandbox._mobile_send_key(
            mock_session,
            {"key": "HOME"},
        )
        assert result["success"] is True

    def test_mobile_app_operations(self, mobile_sandbox, mock_session):
        """Test mobile app operations."""
        # Test mobile_start_app
        result = mobile_sandbox._mobile_start_app(
            mock_session,
            {"app_name": "com.example.app"},
        )
        assert result["success"] is True

        # Test mobile_stop_app
        result = mobile_sandbox._mobile_stop_app(
            mock_session,
            {"app_name": "com.example.app"},
        )
        assert result["success"] is True

    def test_mobile_screenshot(self, mobile_sandbox, mock_session):
        """Test taking a mobile screenshot."""
        result = mobile_sandbox._mobile_screenshot(mock_session, {})
        assert result["success"] is True
        assert result["screenshot_url"] == "screenshot_url"
