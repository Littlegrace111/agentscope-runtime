# -*- coding: utf-8 -*-
"""
AGB Cloud 工具集

提供基于 AGB Cloud SDK 的工具，包括：
- 代码执行工具
- 文件操作工具
- 命令执行工具
- 浏览器自动化工具
"""

import logging
from typing import Dict, Any, Optional, List
from ..tools.sandbox_tool import SandboxTool
from ..enums import SandboxType

logger = logging.getLogger(__name__)


class AgbCodeExecutionTool(SandboxTool):
    """AGB 代码执行工具"""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="agb_execute_code",
            sandbox_type=SandboxType.AGB,
            **kwargs
        )
    
    def _call_agb_method(self, method: str, **kwargs) -> Dict[str, Any]:
        """调用 AGB 方法的统一接口"""
        if not self.sandbox or not hasattr(self.sandbox, 'execute_code'):
            return {"success": False, "error": "AGB sandbox not available"}
        
        try:
            if method == "execute_code":
                return self.sandbox.execute_code(
                    code=kwargs.get("code", ""),
                    language=kwargs.get("language", "python"),
                    timeout_s=kwargs.get("timeout_s", 300)
                )
            else:
                return {"success": False, "error": f"Unknown method: {method}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


class AgbFileOperationTool(SandboxTool):
    """AGB 文件操作工具"""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="agb_file_operation",
            sandbox_type=SandboxType.AGB,
            **kwargs
        )
    
    def _call_agb_method(self, method: str, **kwargs) -> Dict[str, Any]:
        """调用 AGB 文件操作方法"""
        if not self.sandbox or not hasattr(self.sandbox, 'read_file'):
            return {"success": False, "error": "AGB sandbox not available"}
        
        try:
            if method == "read_file":
                return self.sandbox.read_file(kwargs.get("filepath", ""))
            elif method == "write_file":
                return self.sandbox.write_file(
                    filepath=kwargs.get("filepath", ""),
                    content=kwargs.get("content", "")
                )
            elif method == "list_directory":
                return self.sandbox.list_directory(kwargs.get("directory", ""))
            elif method == "create_directory":
                return self.sandbox.create_directory(kwargs.get("directory", ""))
            else:
                return {"success": False, "error": f"Unknown file operation: {method}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


class AgbCommandExecutionTool(SandboxTool):
    """AGB 命令执行工具"""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="agb_execute_command",
            sandbox_type=SandboxType.AGB,
            **kwargs
        )
    
    def _call_agb_method(self, method: str, **kwargs) -> Dict[str, Any]:
        """调用 AGB 命令执行方法"""
        if not self.sandbox or not hasattr(self.sandbox, 'execute_command'):
            return {"success": False, "error": "AGB sandbox not available"}
        
        try:
            if method == "execute_command":
                return self.sandbox.execute_command(
                    command=kwargs.get("command", ""),
                    timeout_ms=kwargs.get("timeout_ms", 5000)
                )
            else:
                return {"success": False, "error": f"Unknown method: {method}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


class AgbBrowserTool(SandboxTool):
    """AGB 浏览器自动化工具"""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="agb_browser_automation",
            sandbox_type=SandboxType.AGB,
            **kwargs
        )
    
    def _call_agb_method(self, method: str, **kwargs) -> Dict[str, Any]:
        """调用 AGB 浏览器方法"""
        if not self.sandbox or not hasattr(self.sandbox, 'initialize_browser'):
            return {"success": False, "error": "AGB sandbox not available"}
        
        try:
            if method == "initialize_browser":
                return self.sandbox.initialize_browser(
                    image_id=kwargs.get("image_id")
                )
            elif method == "get_browser_endpoint":
                endpoint = self.sandbox.get_browser_endpoint()
                return {
                    "success": endpoint is not None,
                    "endpoint_url": endpoint,
                    "error": None if endpoint else "Browser not initialized"
                }
            else:
                return {"success": False, "error": f"Unknown browser method: {method}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# 预定义的 AGB 工具实例
agb_execute_code = AgbCodeExecutionTool()
agb_file_operation = AgbFileOperationTool()
agb_execute_command = AgbCommandExecutionTool()
agb_browser_automation = AgbBrowserTool()


# 工具函数，用于创建特定功能的工具
def create_agb_code_tool(name: str = "agb_code_execution", **kwargs) -> AgbCodeExecutionTool:
    """创建 AGB 代码执行工具"""
    return AgbCodeExecutionTool(name=name, **kwargs)


def create_agb_file_tool(name: str = "agb_file_operations", **kwargs) -> AgbFileOperationTool:
    """创建 AGB 文件操作工具"""
    return AgbFileOperationTool(name=name, **kwargs)


def create_agb_command_tool(name: str = "agb_command_execution", **kwargs) -> AgbCommandExecutionTool:
    """创建 AGB 命令执行工具"""
    return AgbCommandExecutionTool(name=name, **kwargs)


def create_agb_browser_tool(name: str = "agb_browser_automation", **kwargs) -> AgbBrowserTool:
    """创建 AGB 浏览器自动化工具"""
    return AgbBrowserTool(name=name, **kwargs)


# 高级 AGB 工具
class AgbAdvancedCodeTool(SandboxTool):
    """高级 AGB 代码执行工具，支持多语言和复杂操作"""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="agb_advanced_code",
            sandbox_type=SandboxType.AGB,
            **kwargs
        )
    
    def _call_agb_method(self, method: str, **kwargs) -> Dict[str, Any]:
        """调用高级 AGB 代码方法"""
        if not self.sandbox or not hasattr(self.sandbox, 'execute_code'):
            return {"success": False, "error": "AGB sandbox not available"}
        
        try:
            if method == "execute_python":
                return self.sandbox.execute_code(
                    code=kwargs.get("code", ""),
                    language="python",
                    timeout_s=kwargs.get("timeout_s", 300)
                )
            elif method == "execute_javascript":
                return self.sandbox.execute_code(
                    code=kwargs.get("code", ""),
                    language="javascript",
                    timeout_s=kwargs.get("timeout_s", 300)
                )
            elif method == "execute_java":
                return self.sandbox.execute_code(
                    code=kwargs.get("code", ""),
                    language="java",
                    timeout_s=kwargs.get("timeout_s", 300)
                )
            elif method == "execute_r":
                return self.sandbox.execute_code(
                    code=kwargs.get("code", ""),
                    language="r",
                    timeout_s=kwargs.get("timeout_s", 300)
                )
            elif method == "batch_execute":
                # 批量执行代码
                codes = kwargs.get("codes", [])
                results = []
                for code_info in codes:
                    result = self.sandbox.execute_code(
                        code=code_info.get("code", ""),
                        language=code_info.get("language", "python"),
                        timeout_s=code_info.get("timeout_s", 300)
                    )
                    results.append({
                        "code": code_info.get("code", "")[:100] + "..." if len(code_info.get("code", "")) > 100 else code_info.get("code", ""),
                        "language": code_info.get("language", "python"),
                        "result": result
                    })
                return {"success": True, "results": results}
            else:
                return {"success": False, "error": f"Unknown advanced method: {method}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


class AgbDataProcessingTool(SandboxTool):
    """AGB 数据处理工具，结合代码执行和文件操作"""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="agb_data_processing",
            sandbox_type=SandboxType.AGB,
            **kwargs
        )
    
    def _call_agb_method(self, method: str, **kwargs) -> Dict[str, Any]:
        """调用 AGB 数据处理方法"""
        if not self.sandbox:
            return {"success": False, "error": "AGB sandbox not available"}
        
        try:
            if method == "process_csv":
                # CSV 数据处理
                input_file = kwargs.get("input_file", "")
                output_file = kwargs.get("output_file", "")
                processing_code = kwargs.get("processing_code", "")
                
                # 读取输入文件
                read_result = self.sandbox.read_file(input_file)
                if not read_result["success"]:
                    return read_result
                
                # 执行处理代码
                code_result = self.sandbox.execute_code(
                    code=processing_code,
                    language="python",
                    timeout_s=kwargs.get("timeout_s", 300)
                )
                if not code_result["success"]:
                    return code_result
                
                # 写入输出文件（如果需要）
                if output_file:
                    write_result = self.sandbox.write_file(
                        filepath=output_file,
                        content=code_result.get("output", "")
                    )
                    if not write_result["success"]:
                        return write_result
                
                return {
                    "success": True,
                    "input_file": input_file,
                    "output_file": output_file,
                    "processing_result": code_result.get("output", "")
                }
            
            elif method == "analyze_data":
                # 数据分析
                data_file = kwargs.get("data_file", "")
                analysis_type = kwargs.get("analysis_type", "basic")
                
                if analysis_type == "basic":
                    analysis_code = f"""
import pandas as pd
import json

# Read data
df = pd.read_csv('{data_file}')
print("Data shape:", df.shape)
print("\\nColumn names:", list(df.columns))
print("\\nData types:")
print(df.dtypes)
print("\\nBasic statistics:")
print(df.describe())
print("\\nMissing values:")
print(df.isnull().sum())
"""
                elif analysis_type == "advanced":
                    analysis_code = f"""
import pandas as pd
import numpy as np
import json

# Read data
df = pd.read_csv('{data_file}')

# Advanced analysis
analysis = {{
    "shape": df.shape,
    "columns": list(df.columns),
    "dtypes": df.dtypes.to_dict(),
    "missing_values": df.isnull().sum().to_dict(),
    "numeric_summary": df.describe().to_dict(),
    "categorical_summary": {{col: df[col].value_counts().to_dict() for col in df.select_dtypes(include=['object']).columns}}
}}

print(json.dumps(analysis, indent=2, default=str))
"""
                else:
                    return {"success": False, "error": f"Unknown analysis type: {analysis_type}"}
                
                return self.sandbox.execute_code(
                    code=analysis_code,
                    language="python",
                    timeout_s=kwargs.get("timeout_s", 300)
                )
            
            else:
                return {"success": False, "error": f"Unknown data processing method: {method}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# 创建高级工具实例
agb_advanced_code = AgbAdvancedCodeTool()
agb_data_processing = AgbDataProcessingTool()


# 导出所有 AGB 工具
AGB_TOOLS = [
    agb_execute_code,
    agb_file_operation,
    agb_execute_command,
    agb_browser_automation,
    agb_advanced_code,
    agb_data_processing,
]


def get_agb_tools() -> List[SandboxTool]:
    """获取所有 AGB 工具"""
    return AGB_TOOLS.copy()


def get_agb_tools_by_category(category: str) -> List[SandboxTool]:
    """根据类别获取 AGB 工具"""
    category_map = {
        "code": [agb_execute_code, agb_advanced_code],
        "file": [agb_file_operation],
        "command": [agb_execute_command],
        "browser": [agb_browser_automation],
        "data": [agb_data_processing],
    }
    return category_map.get(category, [])
