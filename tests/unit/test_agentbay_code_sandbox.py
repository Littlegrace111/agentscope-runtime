# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name, protected-access, unused-argument
"""
Unit tests for AgentbayCodeSandbox implementation.
"""
from unittest.mock import MagicMock, patch

import pytest

from agentscope_runtime.sandbox.box.agentbay.agentbay_code_sandbox import (
    AgentbayCodeSandbox,
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

    # Mock code execution
    code_result = MagicMock()
    code_result.success = True
    code_result.result = "test result"
    session.code.run_code.return_value = code_result

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
def code_sandbox(mock_agentbay_client, mock_create_session_result):
    """Create an AgentbayCodeSandbox with mocked dependencies."""
    base_path = "agentscope_runtime.sandbox.box.agentbay.agentbay_sandbox_base"
    with patch(f"{base_path}.AgentBay") as mock_agentbay_class:
        mock_agentbay_class.return_value = mock_agentbay_client
        mock_agentbay_client.create.return_value = mock_create_session_result

        with patch(f"{base_path}.CreateSessionParams"):
            sandbox = AgentbayCodeSandbox(
                api_key="test-api-key",
                image_id="code_latest",
            )
            yield sandbox


class TestAgentbayCodeSandbox:
    """Test cases for AgentbayCodeSandbox class."""

    def test_init(self, code_sandbox):
        """Test initialization."""
        assert code_sandbox.api_key == "test-api-key"
        assert code_sandbox.image_id == "code_latest"
        assert code_sandbox.sandbox_type == SandboxType.AGENTBAY

    def test_list_tools_all(self, code_sandbox):
        """Test listing all tools - priority test."""
        result = code_sandbox.list_tools()

        # Verify structure
        assert "tools" in result
        assert "tools_by_type" in result
        assert "total_count" in result
        assert "sandbox_id" in result

        # Verify total count
        assert result["total_count"] == 9

        # Verify all tools are present
        expected_tools = [
            "read_file",
            "write_file",
            "list_directory",
            "create_directory",
            "move_file",
            "delete_file",
            "run_shell_command",
            "run_python_code",
            "run_javascript_code",
        ]
        assert set(result["tools"]) == set(expected_tools)

        # Verify tools_by_type structure
        assert "file" in result["tools_by_type"]
        assert "code" in result["tools_by_type"]

        # Verify file tools
        file_tools = result["tools_by_type"]["file"]
        assert len(file_tools) == 6
        assert "read_file" in file_tools
        assert "write_file" in file_tools
        assert "list_directory" in file_tools
        assert "create_directory" in file_tools
        assert "move_file" in file_tools
        assert "delete_file" in file_tools

        # Verify code tools
        code_tools = result["tools_by_type"]["code"]
        assert len(code_tools) == 3
        assert "run_shell_command" in code_tools
        assert "run_python_code" in code_tools
        assert "run_javascript_code" in code_tools

    def test_list_tools_by_type_file(self, code_sandbox):
        """Test listing file tools only."""
        result = code_sandbox.list_tools(tool_type="file")

        assert result["tool_type"] == "file"
        assert result["total_count"] == 6
        assert "read_file" in result["tools"]
        assert "write_file" in result["tools"]
        assert "list_directory" in result["tools"]
        assert "create_directory" in result["tools"]
        assert "move_file" in result["tools"]
        assert "delete_file" in result["tools"]
        assert "run_python_code" not in result["tools"]

    def test_list_tools_by_type_code(self, code_sandbox):
        """Test listing code tools only."""
        result = code_sandbox.list_tools(tool_type="code")

        assert result["tool_type"] == "code"
        assert result["total_count"] == 3
        assert "run_shell_command" in result["tools"]
        assert "run_python_code" in result["tools"]
        assert "run_javascript_code" in result["tools"]
        assert "read_file" not in result["tools"]

    def test_get_tool_mapping(self, code_sandbox):
        """Test tool mapping contains all expected tools."""
        tool_mapping = code_sandbox._get_tool_mapping()

        # Verify all tools are mapped
        assert "run_shell_command" in tool_mapping
        assert "run_python_code" in tool_mapping
        assert "run_javascript_code" in tool_mapping
        assert "read_file" in tool_mapping
        assert "write_file" in tool_mapping
        assert "list_directory" in tool_mapping
        assert "create_directory" in tool_mapping
        assert "move_file" in tool_mapping
        assert "delete_file" in tool_mapping

        # Verify mapping count matches list_tools
        assert len(tool_mapping) == 9

    def test_execute_python_code(self, code_sandbox, mock_session):
        """Test executing Python code."""
        result = code_sandbox._execute_python_code(
            mock_session,
            {"code": "print('hello')"},
        )
        assert result["success"] is True
        assert result["output"] == "test result"

    def test_execute_javascript_code(self, code_sandbox, mock_session):
        """Test executing JavaScript code."""
        result = code_sandbox._execute_javascript_code(
            mock_session,
            {"code": "console.log('hello')"},
        )
        assert result["success"] is True
        assert result["output"] == "test result"

    def test_execute_command(self, code_sandbox, mock_session):
        """Test executing a shell command."""
        result = code_sandbox._execute_command(
            mock_session,
            {"command": "echo hello"},
        )
        assert result["success"] is True
        assert result["output"] == "test output"
        assert result["exit_code"] == 0
