# AGB Cloud 沙箱集成指南

## 概述

AGB Cloud 沙箱是 AgentScope Runtime 的一个自定义沙箱类型，它通过 AGB Cloud API 直接访问云端沙箱环境。AGB 本身是云服务，无需本地 Docker 容器，通过 API Key 即可使用云端代码执行、文件操作、命令执行和浏览器自动化能力。

## 功能特性

### 🚀 核心功能

- **多语言代码执行**: 支持 Python、JavaScript、Java、R
- **文件系统操作**: 完整的文件读写、目录管理功能
- **命令执行**: Shell 命令执行和系统操作
- **浏览器自动化**: AI 驱动的自然语言浏览器操作
- **云端隔离**: 安全的云端执行环境

### 🔧 技术特性

- **统一接口**: 与 AgentScope Runtime 沙箱系统完全集成
- **工具集成**: 提供丰富的工具集供智能体使用
- **云服务架构**: 直接通过 API 访问云端沙箱，无需本地容器
- **轻量级集成**: 仅需 API Key 即可使用所有功能

## 安装和配置

### 1. 环境要求

```bash
# Python 3.11+
python --version

# 安装 AGB Cloud SDK
pip install agbcloud-sdk

# 安装 Playwright (用于浏览器自动化)
pip install playwright
python -m playwright install chromium
```

### 2. 环境变量配置

创建 `.env` 文件：

```bash
# AGB Cloud API 密钥
AGB_API_KEY=your_agb_api_key_here

# AGB 镜像配置
AGB_DEFAULT_IMAGE_ID=agb-code-space-1
AGB_BROWSER_IMAGE_ID=agb-browser-use-1

# 可选：DashScope API 密钥（用于智能体）
DASHSCOPE_API_KEY=your_dashscope_api_key_here
```

### 3. 验证安装

```python
from agentscope_runtime.sandbox import Sandbox
from agentscope_runtime.sandbox.enums import SandboxType

# 创建 AGB 沙箱
agb_sandbox = Sandbox(sandbox_type=SandboxType.AGB)

# 检查是否可用
if agb_sandbox.is_agb_available():
    print("✅ AGB 沙箱可用")
else:
    print("❌ AGB 沙箱不可用，请检查配置")
```

## 使用方法

### 1. 直接使用 AGB 沙箱

```python
from agentscope_runtime.sandbox.factory import create_sandbox
from agentscope_runtime.sandbox.enums import SandboxType

# 创建 AGB 云沙箱
agb_sandbox = create_sandbox(sandbox_type=SandboxType.AGB)

# 代码执行
result = agb_sandbox.execute_code("print('Hello AGB!')", "python")
print(result["output"])

# 文件操作
agb_sandbox.write_file("/tmp/test.txt", "Hello World!")
content = agb_sandbox.read_file("/tmp/test.txt")
print(content["content"])

# 命令执行
result = agb_sandbox.execute_command("ls -la /tmp")
print(result["output"])

# 清理资源
agb_sandbox.cleanup()
```

### 2. 与智能体集成

```python
from agentscope_runtime.engine import Runner
from agentscope_runtime.engine.agents.llm_agent import LLMAgent
from agentscope_runtime.engine.llms import QwenLLM
from agentscope_runtime.sandbox.tools.agb_tools import get_agb_tools

# 创建智能体
model = QwenLLM(model_name="qwen-turbo", api_key="your_api_key")
agent = LLMAgent(
    model=model,
    name="AGB_Agent",
    tools=get_agb_tools()  # 获取所有 AGB 工具
)

# 使用 Runner
async with Runner(agent=agent) as runner:
    # 智能体可以使用 AGB 工具进行各种操作
    response = await runner.query("请使用 AGB 执行 Python 代码计算斐波那契数列")
```

### 3. 浏览器自动化

```python
# 初始化浏览器
browser_result = agb_sandbox.initialize_browser()
if browser_result["success"]:
    endpoint_url = browser_result["endpoint_url"]
    print(f"浏览器 CDP 端点: {endpoint_url}")

    # 使用 Playwright 连接
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(endpoint_url)
        page = await browser.new_page()
        await page.goto("https://example.com")
        title = await page.title()
        print(f"页面标题: {title}")
        await browser.close()
```

## 工具集

### 基础工具

1. **agb_execute_code**: 代码执行工具
2. **agb_file_operation**: 文件操作工具
3. **agb_execute_command**: 命令执行工具
4. **agb_browser_automation**: 浏览器自动化工具

### 高级工具

1. **agb_advanced_code**: 高级代码执行（多语言、批量操作）
2. **agb_data_processing**: 数据处理管道

### 使用工具

```python
from agentscope_runtime.sandbox.tools.agb_tools import (
    agb_execute_code,
    agb_file_operation,
    agb_execute_command,
    agb_browser_automation
)

# 获取特定类别的工具
from agentscope_runtime.sandbox.tools.agb_tools import get_agb_tools_by_category

code_tools = get_agb_tools_by_category("code")
file_tools = get_agb_tools_by_category("file")
browser_tools = get_agb_tools_by_category("browser")
```

## 架构设计

### 沙箱架构

```
┌─────────────────────────────────────┐
│           AgentScope Runtime        │
├─────────────────────────────────────┤
│            Sandbox Manager          │
├─────────────────────────────────────┤
│              AGB Sandbox            │
│  ┌─────────────────────────────────┐ │
│  │         AGB Client              │ │
│  │  ┌─────────────────────────────┐ │ │
│  │  │      AGB Session            │ │ │
│  │  │  ┌─────────────────────────┐ │ │ │
│  │  │  │    Code Execution       │ │ │ │
│  │  │  │    File Operations      │ │ │ │
│  │  │  │    Command Execution    │ │ │ │
│  │  │  │    Browser Automation   │ │ │ │
│  │  │  └─────────────────────────┘ │ │ │
│  │  └─────────────────────────────┘ │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### 工具集成

```
┌─────────────────────────────────────┐
│              Agent                  │
├─────────────────────────────────────┤
│            AGB Tools                │
│  ┌─────────────────────────────────┐ │
│  │    SandboxTool (Base)           │ │
│  │  ┌─────────────────────────────┐ │ │
│  │  │    AgbCodeExecutionTool     │ │ │
│  │  │    AgbFileOperationTool     │ │ │
│  │  │    AgbCommandExecutionTool  │ │ │
│  │  │    AgbBrowserTool           │ │ │
│  │  └─────────────────────────────┘ │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## 部署配置

### 云服务部署

AGB 是云服务，无需本地部署。只需要：

1. **获取 AGB API Key**: 在 [AGB Console](https://agb.cloud/console) 注册并获取 API Key
2. **设置环境变量**: 配置 `AGB_API_KEY` 环境变量
3. **直接使用**: 通过 AgentScope Runtime 直接调用 AGB 云服务

```bash
# 设置环境变量
export AGB_API_KEY=your_agb_api_key
export AGB_DEFAULT_IMAGE_ID=agb-code-space-1
export AGB_BROWSER_IMAGE_ID=agb-browser-use-1

# 直接使用，无需部署
python your_script.py
```

### 生产环境配置

```python
# 在应用启动时设置环境变量
import os
os.environ["AGB_API_KEY"] = "your_production_api_key"
os.environ["AGB_DEFAULT_IMAGE_ID"] = "agb-code-space-1"
os.environ["AGB_BROWSER_IMAGE_ID"] = "agb-browser-use-1"

# 创建 AGB 沙箱
from agentscope_runtime.sandbox.factory import create_sandbox
from agentscope_runtime.sandbox.enums import SandboxType

agb_sandbox = create_sandbox(sandbox_type=SandboxType.AGB)
```

## 最佳实践

### 1. 资源管理

```python
# ✅ 正确：使用 try-finally 确保资源清理
agb_sandbox = Sandbox(sandbox_type=SandboxType.AGB)
try:
    # 使用沙箱
    result = agb_sandbox.execute_code("print('Hello')", "python")
finally:
    agb_sandbox.cleanup()

# ❌ 错误：忘记清理资源
agb_sandbox = Sandbox(sandbox_type=SandboxType.AGB)
result = agb_sandbox.execute_code("print('Hello')", "python")
# 忘记调用 cleanup()
```

### 2. 错误处理

```python
# ✅ 正确：检查操作结果
result = agb_sandbox.execute_code(code, "python")
if result["success"]:
    print(f"执行成功: {result['output']}")
else:
    print(f"执行失败: {result['error']}")

# ❌ 错误：假设操作总是成功
result = agb_sandbox.execute_code(code, "python")
print(result["output"])  # 可能为 None
```

### 3. 会话复用

```python
# ✅ 正确：复用会话进行多个操作
session = agb_sandbox.get_agb_session()
if session:
    # 执行多个操作
    result1 = agb_sandbox.execute_code("import math", "python")
    result2 = agb_sandbox.execute_code("print(math.pi)", "python")
    result3 = agb_sandbox.execute_code("print(math.e)", "python")
```

### 4. 超时配置

```python
# ✅ 正确：根据操作类型设置合适的超时
# 快速操作
result = agb_sandbox.execute_code("print('Hello')", "python", timeout_s=10)

# 长时间运行的操作
result = agb_sandbox.execute_code(long_running_code, "python", timeout_s=600)

# 命令执行
result = agb_sandbox.execute_command("find / -name '*.log'", timeout_ms=30000)
```

## 故障排除

### 常见问题

1. **AGB_API_KEY 未设置**

   ```
   Error: AGB_API_KEY not found in environment variables
   ```

   解决：确保设置了正确的 AGB API 密钥

2. **AGB SDK 未安装**

   ```
   Error: AGB SDK not installed
   ```

   解决：运行 `pip install agbcloud-sdk`

3. **会话创建失败**

   ```
   Error: Failed to create AGB session
   ```

   解决：检查 API 密钥和网络连接

4. **浏览器初始化失败**
   ```
   Error: Failed to initialize browser
   ```
   解决：确保使用了正确的浏览器镜像 ID

### 调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 启用详细日志
agb_sandbox = Sandbox(sandbox_type=SandboxType.AGB)
```

## 示例代码

完整的使用示例请参考：

- `demo/agb_sandbox_demo.py` - 基础使用示例
- `demo/agb_integration_demo.py` - 集成示例

## 相关文档

- [AGB Cloud SDK 文档](https://docs.agb.cloud/)
- [AgentScope Runtime 文档](../README.md)
- [沙箱系统文档](../sandbox.md)

## 支持

如有问题，请：

1. 查看本文档的故障排除部分
2. 检查 AGB Cloud 官方文档
3. 提交 Issue 到项目仓库
