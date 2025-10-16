# -*- coding: utf-8 -*-
"""
沙箱工厂

提供统一的沙箱创建接口，支持传统容器沙箱和云沙箱
"""

from typing import Optional, Union
from .enums import SandboxType
from .box.sandbox import Sandbox
from .custom.agb_sandbox import AgbSandbox


def create_sandbox(
    sandbox_type: Union[SandboxType, str],
    sandbox_id: Optional[str] = None,
    timeout: int = 3000,
    base_url: Optional[str] = None,
    bearer_token: Optional[str] = None,
    **kwargs
) -> Union[Sandbox, AgbSandbox]:
    """
    创建沙箱实例
    
    Args:
        sandbox_type: 沙箱类型
        sandbox_id: 沙箱 ID
        timeout: 超时时间
        base_url: 远程沙箱 URL
        bearer_token: 认证令牌
        **kwargs: 其他参数
    
    Returns:
        沙箱实例
    """
    sandbox_type = SandboxType(sandbox_type)
    
    # 云沙箱类型
    if sandbox_type == SandboxType.AGB:
        return AgbSandbox(
            sandbox_id=sandbox_id,
            timeout=timeout,
            agb_image_id=kwargs.get("agb_image_id")
        )
    
    # 传统容器沙箱
    else:
        return Sandbox(
            sandbox_id=sandbox_id,
            timeout=timeout,
            base_url=base_url,
            bearer_token=bearer_token,
            sandbox_type=sandbox_type
        )


def is_cloud_sandbox(sandbox_type: Union[SandboxType, str]) -> bool:
    """
    检查是否为云沙箱类型
    
    Args:
        sandbox_type: 沙箱类型
    
    Returns:
        是否为云沙箱
    """
    sandbox_type = SandboxType(sandbox_type)
    return sandbox_type == SandboxType.AGB


def get_supported_sandbox_types() -> list:
    """
    获取支持的沙箱类型列表
    
    Returns:
        支持的沙箱类型列表
    """
    return [
        SandboxType.DUMMY,
        SandboxType.BASE,
        SandboxType.BROWSER,
        SandboxType.FILESYSTEM,
        SandboxType.APPWORLD,
        SandboxType.BFCL,
        SandboxType.WEBSHOP,
        SandboxType.AGB,
    ]


def get_cloud_sandbox_types() -> list:
    """
    获取云沙箱类型列表
    
    Returns:
        云沙箱类型列表
    """
    return [
        SandboxType.AGB,
    ]


def get_container_sandbox_types() -> list:
    """
    获取容器沙箱类型列表
    
    Returns:
        容器沙箱类型列表
    """
    return [
        SandboxType.DUMMY,
        SandboxType.BASE,
        SandboxType.BROWSER,
        SandboxType.FILESYSTEM,
        SandboxType.APPWORLD,
        SandboxType.BFCL,
        SandboxType.WEBSHOP,
    ]
