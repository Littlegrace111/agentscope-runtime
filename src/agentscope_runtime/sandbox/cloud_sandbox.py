# -*- coding: utf-8 -*-
"""
云沙箱基类

为云服务沙箱（如 AGB）提供基础接口，不依赖本地容器管理
"""

import logging
from typing import Any, Optional, Dict
from abc import ABC, abstractmethod

from .enums import SandboxType

logger = logging.getLogger(__name__)


class CloudSandbox(ABC):
    """
    云沙箱基类
    
    为云服务沙箱提供统一的接口，不依赖本地容器管理
    """
    
    def __init__(
        self,
        sandbox_id: Optional[str] = None,
        timeout: int = 3000,
        sandbox_type: SandboxType = SandboxType.AGB,
    ):
        """
        初始化云沙箱
        
        Args:
            sandbox_id: 沙箱 ID（云服务中可能为会话 ID）
            timeout: 超时时间
            sandbox_type: 沙箱类型
        """
        self._sandbox_id = sandbox_id or f"cloud-session-{id(self)}"
        self.timeout = timeout
        self.sandbox_type = sandbox_type
        self._is_available = False
        
        # 初始化云服务
        self._initialize_cloud_service()
    
    @abstractmethod
    def _initialize_cloud_service(self):
        """初始化云服务连接"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查云服务是否可用"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """清理云服务资源"""
        pass
    
    @property
    def sandbox_id(self) -> str:
        """获取沙箱 ID"""
        return self._sandbox_id
    
    @sandbox_id.setter
    def sandbox_id(self, value: str) -> None:
        """设置沙箱 ID"""
        if not value:
            raise ValueError("Sandbox ID cannot be empty.")
        self._sandbox_id = value
    
    def get_info(self) -> Dict[str, Any]:
        """获取沙箱信息"""
        return {
            "sandbox_id": self._sandbox_id,
            "sandbox_type": self.sandbox_type.value,
            "is_available": self.is_available(),
            "timeout": self.timeout,
        }
    
    def list_tools(self, tool_type: Optional[str] = None) -> Dict[str, Any]:
        """列出可用工具"""
        # 子类应该实现具体的工具列表
        return {"tools": []}
    
    def call_tool(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """调用工具"""
        if arguments is None:
            arguments = {}
        
        # 子类应该实现具体的工具调用逻辑
        raise NotImplementedError(f"Tool '{name}' not implemented")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()
    
    def __del__(self):
        """析构函数，确保资源被清理"""
        try:
            self.cleanup()
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
