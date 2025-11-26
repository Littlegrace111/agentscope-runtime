# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name, protected-access, unused-argument
"""
Unit tests for AgentbayBrowserSandbox implementation.
"""
from unittest.mock import MagicMock, patch

import pytest

from agentscope_runtime.sandbox.box.agentbay.agentbay_browser_sandbox import (
    AgentbayBrowserSandbox,
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

    # Mock browser operations
    browser_result = MagicMock()
    browser_result.success = True
    browser_result.message = "Success"
    session.browser.agent.navigate.return_value = browser_result
    session.browser.agent.click.return_value = browser_result
    session.browser.agent.input_text.return_value = browser_result
    session.browser.agent.screenshot.return_value = "screenshot_data"

    # Mock browser agent operations
    session.browser.agent.act.return_value = browser_result
    session.browser.agent.extract.return_value = (True, {"data": "extracted"})
    session.browser.agent.observe.return_value = (
        True,
        {"results": "observed"},
    )

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
def browser_sandbox(mock_agentbay_client, mock_create_session_result):
    """Create an AgentbayBrowserSandbox with mocked dependencies."""
    base_path = "agentscope_runtime.sandbox.box.agentbay.agentbay_sandbox_base"
    with patch(f"{base_path}.AgentBay") as mock_agentbay_class:
        mock_agentbay_class.return_value = mock_agentbay_client
        mock_agentbay_client.create.return_value = mock_create_session_result

        with patch(f"{base_path}.CreateSessionParams"):
            sandbox = AgentbayBrowserSandbox(
                api_key="test-api-key",
                image_id="browser_latest",
            )
            yield sandbox


class TestAgentbayBrowserSandbox:
    """Test cases for AgentbayBrowserSandbox class."""

    def test_init(self, browser_sandbox):
        """Test initialization."""
        assert browser_sandbox.api_key == "test-api-key"
        assert browser_sandbox.image_id == "browser_latest"
        assert browser_sandbox.sandbox_type == SandboxType.AGENTBAY

    def test_list_tools_all(self, browser_sandbox):
        """Test listing all tools - priority test."""
        result = browser_sandbox.list_tools()

        # Verify structure
        assert "tools" in result
        assert "tools_by_type" in result
        assert "total_count" in result
        assert "sandbox_id" in result

        # Verify total count
        assert result["total_count"] == 11

        # Verify all tools are present
        expected_tools = [
            "read_file",
            "write_file",
            "list_directory",
            "browser_navigate",
            "browser_click",
            "browser_input",
            "browser_agent_navigate",
            "browser_agent_act",
            "browser_agent_extract",
            "browser_agent_observe",
            "browser_screenshot",
        ]
        assert set(result["tools"]) == set(expected_tools)

        # Verify tools_by_type structure
        assert "file" in result["tools_by_type"]
        assert "browser" in result["tools_by_type"]
        assert "agent" in result["tools_by_type"]

        # Verify file tools
        file_tools = result["tools_by_type"]["file"]
        assert len(file_tools) == 3
        assert "read_file" in file_tools
        assert "write_file" in file_tools
        assert "list_directory" in file_tools

        # Verify browser tools
        browser_tools = result["tools_by_type"]["browser"]
        assert len(browser_tools) == 3
        assert "browser_navigate" in browser_tools
        assert "browser_click" in browser_tools
        assert "browser_input" in browser_tools

        # Verify agent tools
        agent_tools = result["tools_by_type"]["agent"]
        assert len(agent_tools) == 5
        assert "browser_agent_navigate" in agent_tools
        assert "browser_agent_act" in agent_tools
        assert "browser_agent_extract" in agent_tools
        assert "browser_agent_observe" in agent_tools
        assert "browser_screenshot" in agent_tools

    def test_list_tools_by_type_file(self, browser_sandbox):
        """Test listing file tools only."""
        result = browser_sandbox.list_tools(tool_type="file")

        assert result["tool_type"] == "file"
        assert result["total_count"] == 3
        assert "read_file" in result["tools"]
        assert "write_file" in result["tools"]
        assert "list_directory" in result["tools"]
        assert "browser_navigate" not in result["tools"]

    def test_list_tools_by_type_browser(self, browser_sandbox):
        """Test listing browser tools only."""
        result = browser_sandbox.list_tools(tool_type="browser")

        assert result["tool_type"] == "browser"
        assert result["total_count"] == 3
        assert "browser_navigate" in result["tools"]
        assert "browser_click" in result["tools"]
        assert "browser_input" in result["tools"]
        assert "browser_agent_navigate" not in result["tools"]

    def test_list_tools_by_type_agent(self, browser_sandbox):
        """Test listing agent tools only."""
        result = browser_sandbox.list_tools(tool_type="agent")

        assert result["tool_type"] == "agent"
        assert result["total_count"] == 5
        assert "browser_agent_navigate" in result["tools"]
        assert "browser_agent_act" in result["tools"]
        assert "browser_agent_extract" in result["tools"]
        assert "browser_agent_observe" in result["tools"]
        assert "browser_screenshot" in result["tools"]

    def test_get_tool_mapping(self, browser_sandbox):
        """Test tool mapping contains all expected tools."""
        tool_mapping = browser_sandbox._get_tool_mapping()

        # Verify all tools are mapped
        assert "read_file" in tool_mapping
        assert "write_file" in tool_mapping
        assert "list_directory" in tool_mapping
        assert "browser_navigate" in tool_mapping
        assert "browser_click" in tool_mapping
        assert "browser_input" in tool_mapping
        assert "browser_agent_navigate" in tool_mapping
        assert "browser_agent_act" in tool_mapping
        assert "browser_agent_extract" in tool_mapping
        assert "browser_agent_observe" in tool_mapping
        assert "browser_screenshot" in tool_mapping

        # Verify mapping count matches list_tools
        assert len(tool_mapping) == 11

    def test_browser_operations(self, browser_sandbox, mock_session):
        """Test browser operations."""
        # Test browser_navigate
        result = browser_sandbox._browser_navigate(
            mock_session,
            {"url": "https://example.com"},
        )
        assert result["success"] is True

        # Test browser_click
        result = browser_sandbox._browser_click(
            mock_session,
            {"selector": "#button"},
        )
        assert result["success"] is True

        # Test browser_input
        result = browser_sandbox._browser_input(
            mock_session,
            {"selector": "#input", "text": "test"},
        )
        assert result["success"] is True

    def test_browser_agent_operations(self, browser_sandbox, mock_session):
        """Test browser agent operations."""
        # Test browser_agent_navigate
        result = browser_sandbox._browser_agent_navigate(
            mock_session,
            {"url": "https://example.com"},
        )
        assert result["success"] is True

        # Test browser_agent_act
        result = browser_sandbox._browser_agent_act(
            mock_session,
            {"action": "click button"},
        )
        assert result["success"] is True

        # Test browser_agent_extract
        result = browser_sandbox._browser_agent_extract(
            mock_session,
            {"instruction": "extract data"},
        )
        assert result["success"] is True
        assert "data" in result

        # Test browser_agent_observe
        result = browser_sandbox._browser_agent_observe(
            mock_session,
            {"instruction": "observe page"},
        )
        assert result["success"] is True
        assert "results" in result

        # Test browser_screenshot
        result = browser_sandbox._browser_screenshot(mock_session, {})
        assert result["success"] is True
        assert "screenshot" in result
