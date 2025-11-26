# AgentBay SDK 学习指南

> 基于 `llms.txt` 文档整理的 AgentBay SDK 核心概念与使用指南

## 📚 目录

1. [核心概念](#核心概念)
2. [快速开始](#快速开始)
3. [主要功能模块](#主要功能模块)
4. [API 使用示例](#api-使用示例)
5. [最佳实践](#最佳实践)
6. [常见问题](#常见问题)

---

## 核心概念

### 1. AgentBay 是什么？

AgentBay 是一个**专为 AI Agents 构建的云沙箱平台**，提供按需虚拟环境：

- 🌐 **云原生远程计算机**：支持不同操作系统（Windows、Linux、Android）
- ⚡ **即时创建和销毁**：虚拟环境可以瞬间创建和释放
- 🎯 **专为自动化设计**：适用于自动化、测试和开发任务

### 2. AgentBay 类 - 云服务网关

`AgentBay` 类是 SDK 中与云服务交互的主要接口：

```python
from agentbay import AgentBay

# 创建 AgentBay 客户端实例
agent_bay = AgentBay(api_key=os.getenv("AGENTBAY_API_KEY"))
```

**核心功能：**

- **Session 管理器**：创建、删除和管理云会话
- **API 客户端**：处理与 AgentBay 云服务的所有通信
- **认证处理器**：自动管理 API 密钥和安全

**基本使用模式：**

```python
# 1. 初始化客户端
agent_bay = AgentBay()

# 2. 创建会话（默认使用 linux_latest）
session = agent_bay.create().session

# 3. 使用会话执行任务
# ... 你的自动化任务 ...

# 4. 清理资源
agent_bay.delete(session)
```

### 3. Session（会话）

**Session** 是连接到云环境的连接，就像在云端租用一台计算机：

**关键特性：**

- ⏱️ **临时性**：按需创建，用完销毁
- 🔒 **隔离性**：每个会话完全独立
- 💰 **按需计费**：按会话活跃时间计费

**Session 生命周期：**

```
创建会话 → 使用会话 → (暂停会话) → (恢复会话) → 删除会话
    ↓          ↓           ↓            ↓           ↓
分配资源   执行操作    暂停资源    恢复资源    释放资源
```

**基本使用：**

```python
# 创建会话
session = agent_bay.create().session

# 使用会话执行任务
result = session.command.execute_command("echo 'Hello World'")

# 清理资源
agent_bay.delete(session)
```

**暂停和恢复：**

```python
# 暂停会话（降低资源使用和成本）
result = session.pause()
if result.success:
    print(f"会话已暂停: {result.request_id}")

# 恢复会话
result = session.resume()
if result.success:
    print(f"会话已恢复: {result.request_id}")
```

### 4. Image Types（镜像类型）

创建会话时必须选择**镜像类型**，决定环境类型和可用功能：

| Image ID         | 环境类型     | 适用场景                              |
| ---------------- | ------------ | ------------------------------------- |
| `linux_latest`   | Computer Use | 通用计算、服务器任务（默认）          |
| `windows_latest` | Computer Use | Windows 任务、.NET 开发、Windows 应用 |
| `browser_latest` | Browser Use  | 网页抓取、浏览器自动化、网站测试      |
| `code_latest`    | CodeSpace    | 编码、开发工具、编程任务              |
| `mobile_latest`  | Mobile Use   | 移动应用测试、Android 自动化          |

**选择示例：**

```python
from agentbay.session_params import CreateSessionParams

# Windows 环境示例
params = CreateSessionParams(image_id="windows_latest")
session = agent_bay.create(params).session
session.computer.start_app("notepad.exe")

# 浏览器环境示例
params = CreateSessionParams(image_id="browser_latest")
session = agent_bay.create(params).session
session.browser.initialize(BrowserOption())

# CodeSpace 环境示例
params = CreateSessionParams(image_id="code_latest")
session = agent_bay.create(params).session
result = session.code.run_code("print('Hello')", "python")
```

### 5. 数据持久化

**临时数据（默认）：**

- 所有会话数据默认是临时的
- 会话结束时所有数据都会丢失
- 适用于：处理任务、临时文件、缓存

```python
# 这些数据在会话结束时会被删除
session.file_system.write_file("/tmp/temp_data.txt", "这会消失")
```

**持久化数据（Context）：**

- 跨会话保存的数据
- 必须显式配置
- 适用于：项目文件、配置、重要结果

```python
from agentbay import ContextSync

# 创建持久化存储
context = agent_bay.context.get("my-project", create=True).context
context_sync = ContextSync.new(context.id, "/persistent")

# 创建带持久化数据的会话
params = CreateSessionParams(context_syncs=[context_sync])
session = agent_bay.create(params).session

# 这些数据会跨会话保存
session.file_system.write_file("/persistent/important.txt", "这会持久保存")
```

---

## 快速开始

### 安装和配置

```bash
# 安装 SDK
pip install wuying-agentbay-sdk

# 设置 API Key
export AGENTBAY_API_KEY=your_api_key_here
```

### 30 秒快速验证

```python
import os
from agentbay import AgentBay

api_key = os.getenv("AGENTBAY_API_KEY")
agent_bay = AgentBay(api_key=api_key)

result = agent_bay.create()
if result.success:
    session = result.session
    cmd_result = session.command.execute_command("echo 'Hello from the cloud!'")
    print(f"✅ 云端响应: {cmd_result.output.strip()}")
    agent_bay.delete(session)
else:
    print(f"❌ 失败: {result.error_message}")
```

### 完整示例：云端数据处理

```python
import os
from agentbay import AgentBay

agent_bay = AgentBay(api_key=os.getenv("AGENTBAY_API_KEY"))
result = agent_bay.create()
session = result.session

try:
    # 1. 创建 Python 脚本
    script_content = '''
import json

data = {
    "students": [
        {"name": "Alice", "scores": [85, 92, 88]},
        {"name": "Bob", "scores": [78, 85, 80]},
    ]
}

results = []
for student in data["students"]:
    avg = sum(student["scores"]) / len(student["scores"])
    results.append({
        "name": student["name"],
        "average": round(avg, 2),
        "grade": "A" if avg >= 90 else "B" if avg >= 80 else "C"
    })

print(json.dumps(results, indent=2))
'''

    # 2. 上传脚本到云端
    session.file_system.write_file("/tmp/process_data.py", script_content)
    print("✅ 脚本已上传到云端")

    # 3. 在云端环境执行脚本
    result = session.command.execute_command("python3 /tmp/process_data.py")
    print(f"\n📊 处理结果:\n{result.output}")

finally:
    agent_bay.delete(session)
    print("\n✅ 会话已清理")
```

---

## 主要功能模块

### 1. Session 管理

```python
# 创建会话
params = CreateSessionParams(image_id="linux_latest")
result = agent_bay.create(params)
session = result.session

# 获取会话信息
info = session.get_info()

# 暂停/恢复会话
session.pause()
session.resume()

# 删除会话
agent_bay.delete(session)
```

### 2. 命令执行

```python
# 执行 Shell 命令
result = session.command.execute_command("ls -la")
print(result.output)
print(result.exit_code)

# 执行 Python 代码
result = session.code.run_code("print('Hello')", "python")
print(result.result)
```

### 3. 文件操作

```python
# 写入文件
session.file_system.write_file("/tmp/test.txt", "Hello World")

# 读取文件
result = session.file_system.read_file("/tmp/test.txt")
print(result.content)

# 列出目录
result = session.file_system.list_directory("/tmp")
print(result.files)

# 创建目录
session.file_system.create_directory("/tmp/my_dir")

# 移动文件
session.file_system.move_file("/tmp/old.txt", "/tmp/new.txt")

# 删除文件
session.file_system.delete_file("/tmp/test.txt")
```

### 4. 浏览器自动化

```python
from agentbay.browser.browser import BrowserOption
from playwright.async_api import async_playwright

# 创建浏览器会话
params = CreateSessionParams(image_id="browser_latest")
session = agent_bay.create(params).session

# 初始化浏览器
option = BrowserOption(
    user_agent="Mozilla/5.0...",
    viewport=BrowserViewport(width=1366, height=768)
)
await session.browser.initialize_async(option)

# 获取 CDP 端点
endpoint_url = session.browser.get_endpoint_url()

# 使用 Playwright 连接
async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp(endpoint_url)
    page = await browser.contexts[0].new_page()
    await page.goto("https://www.aliyun.com")
    print(await page.title())
    await browser.close()

session.delete()
```

### 5. PageUseAgent（AI 驱动的浏览器自动化）

```python
from agentbay.browser.browser_agent import BrowserAgent, ActOptions, ExtractOptions
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(..., description="产品名称")
    price: str | None = Field(None, description="价格")

# 初始化浏览器
session = agent_bay.create(CreateSessionParams(image_id="browser_latest")).session
await session.browser.initialize_async(BrowserOption())

agent: BrowserAgent = session.browser.agent

# 导航
await agent.navigate_async("https://example.com")

# 自然语言操作
await agent.act_async(ActOptions(action="点击搜索框并输入'iPhone'"))

# 提取结构化数据
ok, data = await agent.extract_async(
    ExtractOptions(
        instruction="提取所有产品名称和价格",
        schema=Product,
        use_text_extract=True
    )
)

# 关闭
await agent.close_async()
```

### 6. 桌面自动化（Computer Use）

```python
# Windows 环境
params = CreateSessionParams(image_id="windows_latest")
session = agent_bay.create(params).session

# 启动应用
session.computer.start_app("notepad.exe")

# 输入文本
session.computer.input_text("Hello from Windows!")

# 截图
result = session.computer.screenshot()
print(result.data)  # 截图 URL

# 窗口管理
session.computer.window.maximize()
session.computer.window.minimize()
```

### 7. 移动端自动化（Mobile Use）

```python
from agentbay.mobile import KeyCode

params = CreateSessionParams(image_id="mobile_latest")
session = agent_bay.create(params).session

# 发送按键
session.mobile.send_key(KeyCode.HOME)

# 点击
session.mobile.click(x=100, y=200)

# 滑动
session.mobile.swipe(start_x=100, start_y=200, end_x=300, end_y=400)

# 输入文本
session.mobile.input_text("Hello Mobile")
```

### 8. AI Agent 模块

```python
# 使用 AI Agent 执行自然语言任务
result = session.agent.execute_task(
    "创建一个 Excel 文件，包含学生成绩数据"
)

# Agent 支持的任务类型：
# - Office 自动化：Word/Excel/PowerPoint
# - 文件操作：创建/删除/移动/复制文件和文件夹
# - 信息收集：从互联网收集信息
# - 文本编辑：使用记事本编辑文本文件
```

---

## API 使用示例

### 结果对象结构

所有 API 调用都返回结果对象：

```python
result = session.command.execute_command("ls")

# 结果对象包含：
print(result.success)      # True/False - 操作是否成功
print(result.output)       # 实际数据（命令输出）
print(result.request_id)   # 请求 ID（用于故障排除）
print(result.error_message)  # 错误信息（如果失败）
```

### 错误处理

```python
result = session.code.run_code("print('hello')", "python")
if not result.success:
    print(f"代码执行失败！Request ID: {result.request_id}")
    print(f"错误信息: {result.error_message}")
    # 可以将 Request ID 提供给支持团队以便快速解决问题
```

### 异步操作

```python
import asyncio

async def main():
    agent_bay = AgentBay(api_key=os.getenv("AGENTBAY_API_KEY"))
    result = agent_bay.create()
    session = result.session

    # 异步初始化浏览器
    await session.browser.initialize_async(BrowserOption())

    # 异步执行 Agent 操作
    await session.browser.agent.act_async(ActOptions(action="点击按钮"))

    session.delete()

asyncio.run(main())
```

---

## 最佳实践

### 1. 资源管理

```python
# ✅ 推荐：使用 try-finally 确保清理
session = agent_bay.create().session
try:
    # 执行任务
    result = session.command.execute_command("ls")
finally:
    agent_bay.delete(session)  # 确保清理

# ✅ 推荐：使用上下文管理器（如果支持）
with agent_bay.create() as session:
    result = session.command.execute_command("ls")
```

### 2. 数据持久化

```python
# ✅ 重要数据使用 Context
context = agent_bay.context.get("my-project", create=True).context
context_sync = ContextSync.new(context.id, "/persistent")

params = CreateSessionParams(context_syncs=[context_sync])
session = agent_bay.create(params).session

# 保存到持久化目录
session.file_system.write_file("/persistent/important.txt", "数据")
```

### 3. 会话复用

```python
# ✅ 对于长时间任务，考虑暂停而不是删除
session.pause()  # 暂停以节省成本
# ... 稍后 ...
session.resume()  # 恢复继续工作
```

### 4. 错误处理

```python
# ✅ 始终检查结果
result = agent_bay.create()
if not result.success:
    logger.error(f"创建会话失败: {result.error_message}")
    return

session = result.session

# ✅ 记录 Request ID 用于调试
if not result.success:
    logger.error(f"操作失败 - Request ID: {result.request_id}")
```

### 5. 生产环境建议

```python
# ⚠️ 生产环境不要使用 xxxx_latest 镜像
# ✅ 使用自定义镜像确保稳定性
params = CreateSessionParams(
    image_id="my-custom-image-v1.0.0"  # 固定版本
)
```

---

## 常见问题

### Q1: 如何获取 API Key？

A: 访问 [AgentBay Console](https://agentbay.console.aliyun.com/service-management) 获取 API Key。

### Q2: 会话会自动删除吗？

A: 是的，如果未手动删除，会话会在超时后自动释放。但建议始终手动删除以释放资源。

### Q3: 数据会持久保存吗？

A: 默认情况下，所有数据都是临时的。需要使用 Context 来实现数据持久化。

### Q4: 支持哪些编程语言？

A: Python、TypeScript、Golang 都支持。

### Q5: 如何调试问题？

A: 检查 API 返回的 `request_id`，可以提供给支持团队用于快速定位问题。

### Q6: PageUseAgent 和 Playwright 有什么区别？

A: PageUseAgent 使用自然语言描述任务，由 AI 自动执行；Playwright 需要手动编写选择器和操作代码。两者可以结合使用。

---

## 相关资源

- 📖 [完整文档](README.md)
- 🚀 [快速开始指南](quickstart/README.md)
- 🔧 [功能指南](guides/README.md)
- 💻 [代码示例](../examples/agentbay_sandbox/)
- 🐛 [GitHub Issues](https://github.com/aliyun/wuying-agentbay-sdk/issues)

---

## 学习路径建议

### 初学者路径

1. ✅ 理解核心概念（Session、Image Types、数据持久化）
2. ✅ 完成快速开始示例
3. ✅ 尝试命令执行和文件操作
4. ✅ 探索特定环境（Browser/Computer/Mobile）

### 进阶路径

1. ✅ 掌握浏览器自动化（Playwright + PageUseAgent）
2. ✅ 学习数据持久化（Context）
3. ✅ 探索高级功能（VPC Sessions、Custom Images）
4. ✅ 集成到 AgentScope 工作流

---

**最后更新**: 基于 `llms.txt` 文档整理
**版本**: AgentBay SDK v1.0+
