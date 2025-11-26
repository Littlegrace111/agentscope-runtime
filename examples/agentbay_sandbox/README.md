# Multi-Sandbox Agent 实现说明

本文档说明如何运行和使用多沙箱智能体系统。

## 项目结构

```
examples/agentbay_sandbox/
├── backend/                    # 后端服务
│   ├── __init__.py
│   ├── multi_sandbox_manager.py    # 多沙箱管理器
│   ├── tool_registry.py            # 工具注册器
│   ├── agent_service.py            # 智能体服务
│   └── api_server.py               # FastAPI 服务器
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── MessageList.jsx
│   │   │   ├── InputBox.jsx
│   │   │   ├── SandboxViewer.jsx
│   │   │   └── SandboxManager.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── requirements.txt            # Python 依赖
└── .env.example               # 环境变量示例
```

## 环境配置

### 1. 安装 uv

`uv` 是一个快速的 Python 包管理器。安装方法：

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 pip
pip install uv
```

### 2. 创建 `.env` 文件

在 `examples/agentbay_sandbox/` 目录下创建 `.env` 文件：

```bash
cd examples/agentbay_sandbox
cp .env.example .env
# 然后编辑 .env 文件，填入你的 API Keys
```

`.env` 文件内容：

```bash
DASHSCOPE_API_KEY=your_dashscope_api_key
AGENTBAY_API_KEY=your_agentbay_api_key
```

### 3. 安装 Python 依赖

使用 `uv` 管理依赖：

```bash
# 进入项目目录
cd examples/agentbay_sandbox

# 使用安装脚本（推荐，会自动安装 agentscope-runtime 和所有依赖）
./install_deps.sh

# 如果需要安装开发依赖
./install_deps.sh --dev
```

**注意**：

- `install_deps.sh` 脚本会自动：
  1. 从项目根目录安装 `agentscope-runtime`（可编辑模式，使用源码）
  2. 安装 `pyproject.toml` 中定义的所有依赖
- `agentscope-runtime` 使用当前工程的源码，脚本会自动处理
- `wuying-agentbay-sdk` 不需要单独安装，因为工程已经集成了 AgentBay 沙箱类
- 使用 `uv run` 时，会自动使用项目虚拟环境（`.venv`），无需手动激活

**手动安装方式**（如果脚本无法使用）：

```bash
# 1. 安装 agentscope-runtime（从项目根目录）
cd /path/to/agentscope-runtime-outer
uv pip install -e .

# 2. 安装其他依赖（在 agentbay_sandbox 目录）
cd examples/agentbay_sandbox
uv pip install -r requirements.txt
```

### 4. 安装前端依赖

```bash
cd frontend
npm install
```

## 运行系统

### 方式一：一键启动（推荐）

使用合并脚本同时启动后端和前端：

```bash
cd examples/agentbay_sandbox
./start.sh
```

这个脚本会：

- 同时启动后端（端口 8000）和前端（端口 5173）
- 显示服务状态和访问地址
- 支持 Ctrl+C 优雅关闭两个服务

### 方式二：分别启动

如果需要分别启动服务：

#### 1. 启动后端服务

```bash
cd examples/agentbay_sandbox
./start_backend.sh
```

或者：

```bash
cd examples/agentbay_sandbox
uv run python -m backend.api_server
```

后端服务将在 `http://localhost:8000` 启动。

#### 2. 启动前端服务

在另一个终端：

```bash
cd examples/agentbay_sandbox
./start_frontend.sh
```

或者：

```bash
cd examples/agentbay_sandbox/frontend
npm run dev
```

前端应用将在 `http://localhost:5173` 启动。

## API 接口

### 对话接口

- `POST /api/chat` - 发送消息给智能体
- `GET /api/chat/stream` - 流式对话（SSE）
- `WebSocket /ws/chat` - WebSocket 实时对话

### 沙箱管理接口

- `GET /api/sandboxes` - 获取所有沙箱信息
- `GET /api/sandboxes/{sandbox_type}/screenshot` - 获取沙箱截图
- `GET /api/sandboxes/{sandbox_type}/tools` - 获取沙箱工具列表
- `GET /api/tools` - 获取所有工具

## 使用示例

### 1. 通过前端界面使用

1. 打开浏览器访问 `http://localhost:5173`
2. 在左侧聊天界面输入消息，例如：
   - "List files in the Linux sandbox"
   - "Take a screenshot of the Windows sandbox"
   - "Navigate to https://www.example.com in the browser sandbox"
3. 右侧会显示当前选中沙箱的 GUI 画面
4. 可以通过沙箱管理器切换查看不同沙箱

### 2. 通过 API 使用

```python
import requests

# 发送消息
response = requests.post(
    "http://localhost:8000/api/chat",
    json={"message": "List files in Linux sandbox", "session_id": "test"}
)
print(response.json())

# 获取沙箱信息
response = requests.get("http://localhost:8000/api/sandboxes")
print(response.json())

# 获取截图
response = requests.get("http://localhost:8000/api/sandboxes/linux/screenshot")
print(response.json())
```

## 功能特性

### 多沙箱支持

系统支持 4 个 GUI 沙箱：

- **Linux** - Linux 桌面环境
- **Windows** - Windows 桌面环境
- **Browser** - 浏览器自动化环境
- **Mobile** - Android 移动设备环境

### 工具自动发现

系统会自动：

1. 初始化所有沙箱
2. 调用每个沙箱的 `list_tools()` 获取工具列表
3. 将所有工具注册到 AgentScope Toolkit
4. 工具命名规则：`{sandbox_type}_{tool_name}`

### 实时 GUI 画面

- 前端自动刷新沙箱截图（每 3 秒）
- 工具调用后自动刷新画面
- 支持手动刷新
- 支持切换查看不同沙箱

### 流式对话

- 支持 WebSocket 实时流式输出
- 支持 SSE 流式输出
- 前端实时显示智能体回复

## 故障排查

### 后端无法启动

1. 检查 API Key 是否正确配置在 `.env` 文件中
2. 检查端口 8000 是否被占用
3. 查看后端日志了解详细错误信息

### 前端无法连接后端

1. 检查后端服务是否正常运行
2. 检查 `vite.config.js` 中的代理配置
3. 检查浏览器控制台的错误信息

### 沙箱初始化失败

1. 检查 AgentBay API Key 是否有效
2. 检查网络连接
3. 查看后端日志了解详细错误信息

## 开发说明

### 添加新工具

工具会自动从沙箱的 `list_tools()` 方法获取，无需手动注册。

### 修改系统提示词

编辑 `backend/agent_service.py` 中的 `_create_system_prompt()` 方法。

### 自定义前端样式

修改 `frontend/src/` 目录下的 CSS 文件。

## 注意事项

1. 确保 AgentBay API Key 有足够的配额
2. 沙箱初始化可能需要一些时间（每个沙箱约 10-30 秒）
3. 截图刷新频率建议不要太高，避免性能问题
4. 生产环境应限制 CORS 配置和 API 访问
