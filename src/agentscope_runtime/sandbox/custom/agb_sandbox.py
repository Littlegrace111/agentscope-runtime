# -*- coding: utf-8 -*-
import os
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from ..enums import SandboxType
from ..cloud_sandbox import CloudSandbox

logger = logging.getLogger(__name__)

SANDBOXTYPE = "agb"


@dataclass
class AgbSessionInfo:
    """AGB 会话信息"""
    session_id: str
    image_id: str
    status: str
    endpoint_url: Optional[str] = None
    resource_url: Optional[str] = None


class AgbSandbox(CloudSandbox):
    """
    AGB Cloud 沙箱实现
    
    AGB 是云服务，通过 API Key 直接访问云端沙箱环境，无需本地容器。
    支持功能：
    - 代码执行（Python, JavaScript, Java, R）
    - 文件系统操作
    - 命令执行
    - 浏览器自动化（AI 驱动）
    """
    
    def __init__(
        self,
        sandbox_id: Optional[str] = None,
        timeout: int = 3000,
        agb_image_id: Optional[str] = None,
    ):
        # AGB 相关属性（在调用父类构造函数之前初始化）
        self._agb_client = None
        self._agb_session = None
        self._agb_session_info: Optional[AgbSessionInfo] = None
        self._agb_image_id = agb_image_id or os.getenv("AGB_DEFAULT_IMAGE_ID", "agb-code-space-1")
        
        # 调用父类构造函数
        super().__init__(
            sandbox_id=sandbox_id,
            timeout=timeout,
            sandbox_type=SandboxType(SANDBOXTYPE)
        )
    
    def _initialize_cloud_service(self):
        """初始化云服务连接"""
        self._initialize_agb_client()
        # 初始化时立即创建会话
        if self._agb_client:
            self._create_agb_session()
    
    def _initialize_agb_client(self):
        """初始化 AGB 客户端"""
        try:
            from agb import AGB
            
            api_key = os.getenv("AGB_API_KEY")
            if not api_key:
                logger.warning("AGB_API_KEY not found in environment variables")
                return
            
            self._agb_client = AGB(api_key=api_key)
            logger.info("AGB client initialized successfully")
            
        except ImportError:
            logger.error("AGB SDK not installed. Please install with: pip install agbcloud-sdk")
        except Exception as e:
            logger.error(f"Failed to initialize AGB client: {e}")
    
    def _create_agb_session(self, image_id: Optional[str] = None) -> bool:
        """创建 AGB 会话"""
        if not self._agb_client:
            logger.error("AGB client not initialized")
            return False
        
        try:
            from agb.session_params import CreateSessionParams
            
            target_image_id = image_id or self._agb_image_id
            params = CreateSessionParams(
                image_id=target_image_id
            )
            
            result = self._agb_client.create(params)
            if result.success:
                self._agb_session = result.session
                self._agb_session_info = AgbSessionInfo(
                    session_id=getattr(self._agb_session, 'id', 'unknown'),
                    image_id=target_image_id,
                    status="active"
                )
                logger.info(f"AGB session created successfully with image: {target_image_id}")
                return True
            else:
                logger.error(f"Failed to create AGB session: {result.error_message}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating AGB session: {e}")
            return False
    
    def _delete_agb_session(self):
        """删除 AGB 会话"""
        if self._agb_client and self._agb_session:
            try:
                self._agb_client.delete(self._agb_session)
                logger.info("AGB session deleted successfully")
            except Exception as e:
                logger.error(f"Error deleting AGB session: {e}")
            finally:
                self._agb_session = None
                self._agb_session_info = None
    
    def get_agb_session(self) -> Optional[Any]:
        """获取 AGB 会话对象"""
        if not self._agb_session:
            if not self._create_agb_session():
                return None
        return self._agb_session
    
    def get_agb_session_info(self) -> Optional[AgbSessionInfo]:
        """获取 AGB 会话信息"""
        return self._agb_session_info
    
    def is_available(self) -> bool:
        """检查云服务是否可用"""
        return self._agb_client is not None and self.get_agb_session() is not None
    
    def is_agb_available(self) -> bool:
        """检查 AGB 是否可用（兼容性方法）"""
        return self.is_available()
    
    def execute_code(self, code: str, language: str = "python", timeout_s: int = 300) -> Dict[str, Any]:
        """执行代码"""
        session = self.get_agb_session()
        if not session:
            return {"success": False, "error": "AGB session not available"}
        
        try:
            result = session.code.run_code(code, language, timeout_s=timeout_s)
            return {
                "success": result.success,
                "output": result.result if result.success else None,
                "error": result.error_message if not result.success else None,
                "language": language
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_command(self, command: str, timeout_ms: int = 5000) -> Dict[str, Any]:
        """执行命令"""
        session = self.get_agb_session()
        if not session:
            return {"success": False, "error": "AGB session not available"}
        
        try:
            result = session.command.execute_command(command, timeout_ms=timeout_ms)
            return {
                "success": result.success,
                "output": result.output if result.success else None,
                "error": result.error_message if not result.success else None,
                "request_id": getattr(result, 'request_id', None)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def read_file(self, filepath: str) -> Dict[str, Any]:
        """读取文件"""
        session = self.get_agb_session()
        if not session:
            return {"success": False, "error": "AGB session not available"}
        
        try:
            result = session.file_system.read_file(filepath)
            return {
                "success": result.success,
                "content": result.content if result.success else None,
                "error": result.error_message if not result.success else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """写入文件"""
        session = self.get_agb_session()
        if not session:
            return {"success": False, "error": "AGB session not available"}
        
        try:
            result = session.file_system.write_file(filepath, content)
            return {
                "success": result.success,
                "error": result.error_message if not result.success else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_directory(self, directory: str) -> Dict[str, Any]:
        """列出目录内容"""
        session = self.get_agb_session()
        if not session:
            return {"success": False, "error": "AGB session not available"}
        
        try:
            result = session.file_system.list_directory(directory)
            return {
                "success": result.success,
                "entries": result.entries if result.success else None,
                "error": result.error_message if not result.success else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_directory(self, directory: str) -> Dict[str, Any]:
        """创建目录"""
        session = self.get_agb_session()
        if not session:
            return {"success": False, "error": "AGB session not available"}
        
        try:
            result = session.file_system.create_directory(directory)
            return {
                "success": result.success,
                "error": result.error_message if not result.success else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def initialize_browser(self, image_id: Optional[str] = None) -> Dict[str, Any]:
        """初始化浏览器（需要浏览器镜像）"""
        browser_image_id = image_id or os.getenv("AGB_BROWSER_IMAGE_ID", "agb-browser-use-1")
        
        # 如果当前会话不是浏览器镜像，创建新的浏览器会话
        if self._agb_session_info and self._agb_session_info.image_id != browser_image_id:
            self._delete_agb_session()
        
        if not self._agb_session:
            if not self._create_agb_session(browser_image_id):
                return {"success": False, "error": "Failed to create browser session"}
        
        session = self._agb_session
        try:
            from agb.modules.browser import BrowserOption
            
            # 配置浏览器选项
            option = BrowserOption(
                use_stealth=True,
                viewport={"width": 1366, "height": 768}
            )
            
            success = session.browser.initialize(option)
            if success:
                endpoint_url = session.browser.get_endpoint_url()
                self._agb_session_info.endpoint_url = endpoint_url
                
                return {
                    "success": True,
                    "endpoint_url": endpoint_url,
                    "message": "Browser initialized successfully"
                }
            else:
                return {"success": False, "error": "Failed to initialize browser"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_browser_endpoint(self) -> Optional[str]:
        """获取浏览器 CDP 端点"""
        if self._agb_session_info and self._agb_session_info.endpoint_url:
            return self._agb_session_info.endpoint_url
        
        # 尝试初始化浏览器
        result = self.initialize_browser()
        if result["success"]:
            return result["endpoint_url"]
        
        return None
    
    def list_tools(self, tool_type: Optional[str] = None) -> Dict[str, Any]:
        """列出可用工具"""
        from ..tools.agb_tools import AGB_TOOLS
        
        tools = []
        for tool in AGB_TOOLS:
            tool_info = {
                "name": tool.name,
                "description": tool.description,
                "category": getattr(tool, 'category', 'general')
            }
            
            # 如果指定了工具类型，进行过滤
            if tool_type is None or tool_info["category"] == tool_type:
                tools.append(tool_info)
        
        return {"tools": tools}
    
    def call_tool(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """调用工具"""
        if arguments is None:
            arguments = {}
        
        # 根据工具名称调用相应的 AGB 方法
        if name == "agb_execute_code":
            return self.execute_code(
                code=arguments.get("code", ""),
                language=arguments.get("language", "python"),
                timeout_s=arguments.get("timeout_s", 300)
            )
        elif name == "agb_execute_command":
            return self.execute_command(
                command=arguments.get("command", ""),
                timeout_ms=arguments.get("timeout_ms", 5000)
            )
        elif name == "agb_read_file":
            return self.read_file(arguments.get("filepath", ""))
        elif name == "agb_write_file":
            return self.write_file(
                filepath=arguments.get("filepath", ""),
                content=arguments.get("content", "")
            )
        elif name == "agb_list_directory":
            return self.list_directory(arguments.get("directory", ""))
        elif name == "agb_create_directory":
            return self.create_directory(arguments.get("directory", ""))
        elif name == "agb_initialize_browser":
            return self.initialize_browser(arguments.get("image_id"))
        else:
            raise NotImplementedError(f"Tool '{name}' not implemented")
    
    def cleanup(self):
        """清理资源"""
        self._delete_agb_session()
    
    def __del__(self):
        """析构函数，确保资源被清理"""
        self.cleanup()
