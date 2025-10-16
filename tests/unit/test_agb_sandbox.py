# -*- coding: utf-8 -*-
"""
AGB 沙箱单元测试

测试 AGB 沙箱的基本功能
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock

from agentscope_runtime.sandbox.custom.agb_sandbox import AgbSandbox, AgbSessionInfo
from agentscope_runtime.sandbox.enums import SandboxType


class TestAgbSandbox:
    """AGB 沙箱测试类"""
    
    def setup_method(self):
        """测试前准备"""
        # 模拟环境变量
        self.original_env = os.environ.copy()
        os.environ["AGB_API_KEY"] = "test_api_key"
        os.environ["AGB_DEFAULT_IMAGE_ID"] = "agb-code-space-1"
        os.environ["AGB_BROWSER_IMAGE_ID"] = "agb-browser-use-1"
    
    def teardown_method(self):
        """测试后清理"""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    @patch('agentscope_runtime.sandbox.custom.agb_sandbox.AGB')
    def test_agb_sandbox_initialization(self, mock_agb_class):
        """测试 AGB 沙箱初始化"""
        # 模拟 AGB 客户端
        mock_agb_client = Mock()
        mock_agb_class.return_value = mock_agb_client
        
        # 创建沙箱
        sandbox = AgbSandbox()
        
        # 验证初始化
        assert sandbox._agb_client == mock_agb_client
        assert sandbox._agb_image_id == "agb-code-space-1"
        assert sandbox.sandbox_type == SandboxType.AGB
        mock_agb_class.assert_called_once_with(api_key="test_api_key")
    
    @patch('agentscope_runtime.sandbox.custom.agb_sandbox.AGB')
    def test_agb_sandbox_without_api_key(self, mock_agb_class):
        """测试没有 API 密钥时的初始化"""
        # 移除 API 密钥
        del os.environ["AGB_API_KEY"]
        
        # 创建沙箱
        sandbox = AgbSandbox()
        
        # 验证客户端未初始化
        assert sandbox._agb_client is None
        mock_agb_class.assert_not_called()
    
    @patch('agentscope_runtime.sandbox.custom.agb_sandbox.AGB')
    def test_create_agb_session(self, mock_agb_class):
        """测试创建 AGB 会话"""
        # 模拟 AGB 客户端和会话
        mock_agb_client = Mock()
        mock_session = Mock()
        mock_session.id = "test_session_id"
        
        mock_create_result = Mock()
        mock_create_result.success = True
        mock_create_result.session = mock_session
        mock_agb_client.create.return_value = mock_create_result
        
        mock_agb_class.return_value = mock_agb_client
        
        # 创建沙箱
        sandbox = AgbSandbox()
        
        # 创建会话
        result = sandbox._create_agb_session("test-image-id")
        
        # 验证结果
        assert result is True
        assert sandbox._agb_session == mock_session
        assert sandbox._agb_session_info is not None
        assert sandbox._agb_session_info.session_id == "test_session_id"
        assert sandbox._agb_session_info.image_id == "test-image-id"
        assert sandbox._agb_session_info.status == "active"
    
    @patch('agentscope_runtime.sandbox.custom.agb_sandbox.AGB')
    def test_create_agb_session_failure(self, mock_agb_class):
        """测试创建 AGB 会话失败"""
        # 模拟 AGB 客户端
        mock_agb_client = Mock()
        mock_create_result = Mock()
        mock_create_result.success = False
        mock_create_result.error_message = "Session creation failed"
        mock_agb_client.create.return_value = mock_create_result
        
        mock_agb_class.return_value = mock_agb_client
        
        # 创建沙箱
        sandbox = AgbSandbox()
        
        # 创建会话
        result = sandbox._create_agb_session("test-image-id")
        
        # 验证结果
        assert result is False
        assert sandbox._agb_session is None
        assert sandbox._agb_session_info is None
    
    @patch('agentscope_runtime.sandbox.custom.agb_sandbox.AGB')
    def test_execute_code(self, mock_agb_class):
        """测试代码执行"""
        # 模拟 AGB 客户端和会话
        mock_agb_client = Mock()
        mock_session = Mock()
        mock_code_result = Mock()
        mock_code_result.success = True
        mock_code_result.result = "Hello World"
        mock_code_result.error_message = None
        mock_session.code.run_code.return_value = mock_code_result
        
        mock_create_result = Mock()
        mock_create_result.success = True
        mock_create_result.session = mock_session
        mock_agb_client.create.return_value = mock_create_result
        
        mock_agb_class.return_value = mock_agb_client
        
        # 创建沙箱
        sandbox = AgbSandbox()
        
        # 执行代码
        result = sandbox.execute_code("print('Hello World')", "python")
        
        # 验证结果
        assert result["success"] is True
        assert result["output"] == "Hello World"
        assert result["language"] == "python"
        assert result["error"] is None
        mock_session.code.run_code.assert_called_once_with(
            "print('Hello World')", "python", timeout_s=300
        )
    
    @patch('agentscope_runtime.sandbox.custom.agb_sandbox.AGB')
    def test_execute_code_failure(self, mock_agb_class):
        """测试代码执行失败"""
        # 模拟 AGB 客户端和会话
        mock_agb_client = Mock()
        mock_session = Mock()
        mock_code_result = Mock()
        mock_code_result.success = False
        mock_code_result.result = None
        mock_code_result.error_message = "Syntax error"
        mock_session.code.run_code.return_value = mock_code_result
        
        mock_create_result = Mock()
        mock_create_result.success = True
        mock_create_result.session = mock_session
        mock_agb_client.create.return_value = mock_create_result
        
        mock_agb_class.return_value = mock_agb_client
        
        # 创建沙箱
        sandbox = AgbSandbox()
        
        # 执行代码
        result = sandbox.execute_code("invalid python code", "python")
        
        # 验证结果
        assert result["success"] is False
        assert result["output"] is None
        assert result["error"] == "Syntax error"
    
    @patch('agentscope_runtime.sandbox.custom.agb_sandbox.AGB')
    def test_file_operations(self, mock_agb_class):
        """测试文件操作"""
        # 模拟 AGB 客户端和会话
        mock_agb_client = Mock()
        mock_session = Mock()
        
        # 模拟文件系统操作
        mock_write_result = Mock()
        mock_write_result.success = True
        mock_write_result.error_message = None
        
        mock_read_result = Mock()
        mock_read_result.success = True
        mock_read_result.content = "Hello World"
        mock_read_result.error_message = None
        
        mock_session.file_system.write_file.return_value = mock_write_result
        mock_session.file_system.read_file.return_value = mock_read_result
        
        mock_create_result = Mock()
        mock_create_result.success = True
        mock_create_result.session = mock_session
        mock_agb_client.create.return_value = mock_create_result
        
        mock_agb_class.return_value = mock_agb_client
        
        # 创建沙箱
        sandbox = AgbSandbox()
        
        # 写入文件
        write_result = sandbox.write_file("/tmp/test.txt", "Hello World")
        assert write_result["success"] is True
        
        # 读取文件
        read_result = sandbox.read_file("/tmp/test.txt")
        assert read_result["success"] is True
        assert read_result["content"] == "Hello World"
    
    @patch('agentscope_runtime.sandbox.custom.agb_sandbox.AGB')
    def test_command_execution(self, mock_agb_class):
        """测试命令执行"""
        # 模拟 AGB 客户端和会话
        mock_agb_client = Mock()
        mock_session = Mock()
        
        mock_command_result = Mock()
        mock_command_result.success = True
        mock_command_result.output = "file1.txt\nfile2.txt"
        mock_command_result.error_message = None
        mock_command_result.request_id = "req_123"
        mock_session.command.execute_command.return_value = mock_command_result
        
        mock_create_result = Mock()
        mock_create_result.success = True
        mock_create_result.session = mock_session
        mock_agb_client.create.return_value = mock_create_result
        
        mock_agb_class.return_value = mock_agb_client
        
        # 创建沙箱
        sandbox = AgbSandbox()
        
        # 执行命令
        result = sandbox.execute_command("ls -la")
        
        # 验证结果
        assert result["success"] is True
        assert result["output"] == "file1.txt\nfile2.txt"
        assert result["request_id"] == "req_123"
        assert result["error"] is None
    
    @patch('agentscope_runtime.sandbox.custom.agb_sandbox.AGB')
    def test_cleanup(self, mock_agb_class):
        """测试资源清理"""
        # 模拟 AGB 客户端和会话
        mock_agb_client = Mock()
        mock_session = Mock()
        mock_session.id = "test_session_id"
        
        mock_create_result = Mock()
        mock_create_result.success = True
        mock_create_result.session = mock_session
        mock_agb_client.create.return_value = mock_create_result
        
        mock_agb_class.return_value = mock_agb_client
        
        # 创建沙箱
        sandbox = AgbSandbox()
        
        # 创建会话
        sandbox._create_agb_session()
        
        # 清理资源
        sandbox.cleanup()
        
        # 验证清理
        assert sandbox._agb_session is None
        assert sandbox._agb_session_info is None
        mock_agb_client.delete.assert_called_once_with(mock_session)
    
    def test_agb_session_info(self):
        """测试 AGB 会话信息类"""
        session_info = AgbSessionInfo(
            session_id="test_id",
            image_id="test_image",
            status="active",
            endpoint_url="ws://test:8080",
            resource_url="http://test:8080"
        )
        
        assert session_info.session_id == "test_id"
        assert session_info.image_id == "test_image"
        assert session_info.status == "active"
        assert session_info.endpoint_url == "ws://test:8080"
        assert session_info.resource_url == "http://test:8080"


if __name__ == "__main__":
    pytest.main([__file__])
