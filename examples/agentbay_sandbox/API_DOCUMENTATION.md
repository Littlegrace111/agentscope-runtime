# Multi-Sandbox Agent API 文档

## 概述

Multi-Sandbox Agent API 提供了与多沙箱智能体交互的 RESTful API 和 WebSocket 接口。智能体可以访问 4 个 GUI 沙箱环境（Linux、Windows、Browser、Mobile）来完成自动化任务。

**Base URL**: `http://localhost:8000`

**API 版本**: 1.0.0

---

## 认证

当前版本不需要认证，但需要确保环境变量中配置了以下 API Keys：

- `DASHSCOPE_API_KEY`: DashScope API Key（用于 LLM）
- `AGENTBAY_API_KEY`: AgentBay API Key（用于沙箱服务）

---

## 健康检查

### GET /

根端点，返回 API 基本信息。

**请求示例**:

```bash
curl http://localhost:8000/
```

**响应示例**:

```json
{
  "message": "Multi-Sandbox Agent API",
  "status": "running"
}
```

---

### GET /health

检查服务健康状态和 Agent 初始化状态。

**请求示例**:

```bash
curl http://localhost:8000/health
```

**响应示例**:

```json
{
  "status": "healthy",
  "agent_initialized": true
}
```

**响应字段**:

- `status` (string): 服务状态，通常为 "healthy"
- `agent_initialized` (boolean): Agent 服务是否已初始化

---

## 对话接口

### POST /api/chat

发送消息给智能体并获取回复（非流式）。

**请求**:

- **Method**: `POST`
- **Content-Type**: `application/json`

**请求体**:

```json
{
  "message": "在 Linux 沙箱中列出当前目录的文件",
  "session_id": "default",
  "user_id": "user"
}
```

**请求字段**:

- `message` (string, 必需): 用户消息
- `session_id` (string, 可选): 会话 ID，默认为 "default"
- `user_id` (string, 可选): 用户 ID，默认为 "user"

**响应示例**:

```json
{
  "response": "我已经在 Linux 沙箱中执行了 ls 命令...",
  "session_id": "default"
}
```

**响应字段**:

- `response` (string): 智能体的回复
- `session_id` (string): 会话 ID

**错误响应**:

- `503`: Agent Service 未初始化
- `500`: 服务器内部错误

---

### GET /api/chat/stream

使用 Server-Sent Events (SSE) 进行流式对话。

**请求**:

- **Method**: `GET`
- **Query Parameters**:
  - `message` (string, 必需): 用户消息
  - `session_id` (string, 可选): 会话 ID，默认为 "default"

**请求示例**:

```bash
curl -N "http://localhost:8000/api/chat/stream?message=在Linux沙箱中执行ls命令"
```

**响应格式**: `text/event-stream`

**响应示例**:

```
data: 我已经
data: 在 Linux
data: 沙箱中
data: 执行了
data: ls 命令
data: [DONE]
```

**说明**:

- 每个数据块以 `data: ` 开头，后跟内容
- 流式响应以 `data: [DONE]` 结束
- 如果发生错误，会返回 `data: Error: <error_message>`

**错误响应**:

- `503`: Agent Service 未初始化

---

### WebSocket /ws/chat

WebSocket 端点，用于实时双向对话。

**连接**:

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/chat");
```

**发送消息**:

```json
{
  "message": "在 Linux 沙箱中列出当前目录的文件"
}
```

**接收消息**:

- **流式块**:

  ```json
  {
    "type": "chunk",
    "content": "我已经"
  }
  ```

- **完成信号**:

  ```json
  {
    "type": "done"
  }
  ```

- **错误**:
  ```json
  {
    "error": "Error message"
  }
  ```

**说明**:

- 连接建立后，可以持续发送消息
- 每个消息会触发一次完整的回复流
- 回复以多个 `chunk` 消息发送，最后发送 `done` 信号

---

## 沙箱管理接口

### GET /api/sandboxes

获取所有沙箱的信息和状态。

**请求示例**:

```bash
curl http://localhost:8000/api/sandboxes
```

**响应示例**:

```json
{
  "sandboxes": {
    "s-xxxxx": {
      "sandbox_id": "s-xxxxx",
      "sandbox_type": "linux",
      "image_id": "linux_latest",
      "status": "active",
      "tools_count": 8
    },
    "linux": {
      "sandbox_id": null,
      "sandbox_type": "linux",
      "image_id": "linux_latest",
      "status": "not_initialized",
      "tools_count": 0
    },
    "windows": {
      "sandbox_id": null,
      "sandbox_type": "windows",
      "image_id": "windows_latest",
      "status": "not_initialized",
      "tools_count": 0
    }
  }
}
```

**响应字段**:

- `sandboxes` (object): 沙箱信息字典
  - 键为 `sandbox_id`（如果沙箱已创建）或 `sandbox_type`（如果沙箱未初始化）
  - 值包含：
    - `sandbox_id` (string | null): 沙箱 ID，未初始化时为 null
    - `sandbox_type` (string): 沙箱类型（"linux", "windows", "browser", "mobile"）
    - `image_id` (string): 沙箱镜像 ID
    - `status` (string): 沙箱状态（"active" 或 "not_initialized"）
    - `tools_count` (number): 可用工具数量

**说明**:

- 已创建的沙箱使用 `sandbox_id` 作为键
- 未初始化的沙箱使用 `sandbox_type` 作为键
- `sandbox_id` 在沙箱创建后由 AgentBay 返回，格式通常为 `s-xxxxx`

**错误响应**:

- `503`: Agent Service 未初始化
- `500`: 服务器内部错误

---

### POST /api/sandboxes

创建指定类型的沙箱并返回 sandbox_id。

**请求**:

- **Method**: `POST`
- **Query Parameters**:
  - `sandbox_type` (string, 必需): 沙箱类型，可选值：`linux`、`windows`、`browser`、`mobile`

**请求示例**:

```bash
curl -X POST "http://localhost:8000/api/sandboxes?sandbox_type=linux"
```

**响应示例**:

```json
{
  "success": true,
  "sandbox_id": "s-xxxxx",
  "sandbox_type": "linux",
  "image_id": "linux_latest"
}
```

**响应字段**:

- `success` (boolean): 是否成功
- `sandbox_id` (string): 创建的沙箱 ID，格式通常为 `s-xxxxx`
- `sandbox_type` (string): 沙箱类型
- `image_id` (string): 沙箱镜像 ID
- `error` (string, 可选): 错误信息（当 success 为 false 时）

**说明**:

- 如果该类型的沙箱已经存在，会返回已存在的沙箱 ID
- `sandbox_id` 是后续调用其他接口（如获取截图、resource_url 等）所需的标识符
- 创建沙箱可能需要一些时间（通常 10-30 秒）

**错误响应**:

- `400`: 无效的沙箱类型
- `500`: 创建沙箱失败
- `503`: Agent Service 未初始化

**使用流程示例**:

```bash
# 1. 创建 Linux 沙箱
response = requests.post("http://localhost:8000/api/sandboxes?sandbox_type=linux")
sandbox_data = response.json()
sandbox_id = sandbox_data["sandbox_id"]

# 2. 使用 sandbox_id 获取 resource_url
response = requests.get(f"http://localhost:8000/api/sandboxes/{sandbox_id}/resource_url")
resource_url_data = response.json()
print(f"Resource URL: {resource_url_data['resource_url']}")
```

---

### GET /api/sandboxes/{sandbox_id}/screenshot

获取指定沙箱的截图。

**路径参数**:

- `sandbox_id` (string, 必需): 沙箱 ID（在沙箱创建后返回，格式通常为 `s-xxxxx`）

**请求示例**:

```bash
curl http://localhost:8000/api/sandboxes/s-xxxxx/screenshot
```

**响应示例**:

```json
{
  "success": true,
  "screenshot": "base64_encoded_image_data",
  "screenshot_url": "https://...",
  "sandbox_id": "s-xxxxx",
  "sandbox_type": "linux"
}
```

**响应字段**:

- `success` (boolean): 是否成功
- `screenshot` (string, 可选): Base64 编码的截图数据
- `screenshot_url` (string, 可选): 截图 URL
- `sandbox_id` (string): 沙箱 ID
- `sandbox_type` (string): 沙箱类型
- `error` (string, 可选): 错误信息（当 success 为 false 时）

**说明**:

- `sandbox_id` 在沙箱创建后由 AgentBay 返回，可以通过 `/api/sandboxes` 接口获取
- 不同沙箱类型使用不同的截图工具：
  - `browser`: `browser_screenshot`
  - `linux` / `windows`: `screenshot`
  - `mobile`: `mobile_screenshot`

**错误响应**:

- `404`: 沙箱不存在或截图不可用
- `503`: Agent Service 未初始化
- `500`: 服务器内部错误

---

### GET /api/sandboxes/{sandbox_id}/resource_url

获取指定沙箱的 resource_url（用于在浏览器中直接访问沙箱环境）。

**路径参数**:

- `sandbox_id` (string, 必需): 沙箱 ID（在沙箱创建后返回，格式通常为 `s-xxxxx`）

**请求示例**:

```bash
curl http://localhost:8000/api/sandboxes/s-xxxxx/resource_url
```

**响应示例**:

```json
{
  "success": true,
  "resource_url": "https://wy.aliyuncs.com/app/InnoArchClub/mcp_container/mcp.html?authcode=...",
  "sandbox_id": "s-xxxxx",
  "resource_id": "p-xxxxx",
  "app_id": "mcp-server-linux",
  "resource_type": "AIAgent",
  "sandbox_type": "linux"
}
```

**响应字段**:

- `success` (boolean): 是否成功
- `resource_url` (string): 可以直接在浏览器中打开的 URL，用于访问沙箱的 GUI 界面
- `sandbox_id` (string): 沙箱会话 ID
- `resource_id` (string): 云端资源 ID
- `app_id` (string): 应用程序类型标识
- `resource_type` (string): 资源类型（通常为 "AIAgent"）
- `sandbox_type` (string): 沙箱类型
- `error` (string, 可选): 错误信息（当 success 为 false 时）

**说明**:

- `sandbox_id` 在沙箱创建后由 AgentBay 返回，可以通过 `/api/sandboxes` 接口获取
- `resource_url` 是一个可以直接在浏览器中打开的 URL，提供了对沙箱环境的实时视频流和完整的鼠标/键盘控制
- `resource_url` 在沙箱创建时就会生成，包含必要的认证信息

**错误响应**:

- `404`: 沙箱不存在或无法获取 resource_url
- `503`: Agent Service 未初始化
- `500`: 服务器内部错误

---

### GET /api/sandboxes/{sandbox_id}/tools

获取指定沙箱的可用工具列表。

**路径参数**:

- `sandbox_id` (string, 必需): 沙箱 ID（在沙箱创建后返回，格式通常为 `s-xxxxx`）

**请求示例**:

```bash
curl http://localhost:8000/api/sandboxes/s-xxxxx/tools
```

**响应示例**:

```json
{
  "sandbox_id": "s-xxxxx",
  "sandbox_type": "linux",
  "tools": {
    "linux_read_file": {
      "sandbox_type": "linux",
      "tool_name": "read_file",
      "description": "Execute read_file on linux sandbox..."
    },
    "linux_write_file": {
      "sandbox_type": "linux",
      "tool_name": "write_file",
      "description": "Execute write_file on linux sandbox..."
    }
  }
}
```

**响应字段**:

- `sandbox_id` (string): 沙箱 ID
- `sandbox_type` (string): 沙箱类型
- `tools` (object): 工具字典，键为完整工具名称（格式：`{sandbox_type}_{tool_name}`），值为工具信息
  - `sandbox_type` (string): 沙箱类型
  - `tool_name` (string): 工具名称
  - `description` (string): 工具描述

**说明**:

- `sandbox_id` 在沙箱创建后由 AgentBay 返回，可以通过 `/api/sandboxes` 接口获取

**错误响应**:

- `404`: 沙箱不存在
- `503`: Agent Service 未初始化
- `500`: 服务器内部错误

---

### GET /api/tools

获取所有已注册的工具列表。

**请求示例**:

```bash
curl http://localhost:8000/api/tools
```

**响应示例**:

```json
{
  "tools": {
    "linux_read_file": {
      "sandbox_type": "linux",
      "tool_name": "read_file",
      "description": "Execute read_file on linux sandbox..."
    },
    "linux_write_file": {
      "sandbox_type": "linux",
      "tool_name": "write_file",
      "description": "Execute write_file on linux sandbox..."
    },
    "browser_navigate": {
      "sandbox_type": "browser",
      "tool_name": "browser_navigate",
      "description": "Execute browser_navigate on browser sandbox..."
    }
  }
}
```

**响应字段**:

- `tools` (object): 所有工具字典，键为完整工具名称，值为工具信息

**错误响应**:

- `503`: Agent Service 未初始化
- `500`: 服务器内部错误

---

## 沙箱类型说明

系统支持以下 4 种 GUI 沙箱类型：

1. **linux** (`linux_latest`): Linux 桌面环境

   - 支持文件操作、Shell 命令执行等
   - 工具示例：`read_file`, `write_file`, `run_shell_command` 等

2. **windows** (`windows_latest`): Windows 桌面环境

   - 支持应用程序管理、桌面自动化等
   - 工具示例：`start_app`, `input_text`, `screenshot` 等

3. **browser** (`browser_latest`): 浏览器自动化环境

   - 支持网页导航、元素交互等
   - 工具示例：`browser_navigate`, `browser_click`, `browser_screenshot` 等

4. **mobile** (`mobile_latest`): Android 移动设备环境
   - 支持移动 UI 自动化
   - 工具示例：`mobile_tap`, `mobile_swipe`, `mobile_screenshot` 等

---

## 工具命名规则

所有工具名称遵循以下格式：

```
{sandbox_type}_{tool_name}
```

例如：

- `linux_run_shell_command`: Linux 沙箱的 Shell 命令执行工具
- `browser_navigate`: Browser 沙箱的网页导航工具
- `windows_start_app`: Windows 沙箱的应用程序启动工具
- `mobile_tap`: Mobile 沙箱的点击工具

---

## 错误码说明

| HTTP 状态码 | 说明                             |
| ----------- | -------------------------------- |
| 200         | 请求成功                         |
| 400         | 请求参数错误（如无效的沙箱类型） |
| 404         | 资源未找到（如截图不可用）       |
| 500         | 服务器内部错误                   |
| 503         | Agent Service 未初始化           |

---

## 使用示例

### Python 示例

```python
import requests

# 1. 检查服务状态
response = requests.get("http://localhost:8000/health")
print(response.json())

# 2. 发送消息给智能体
response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "message": "在 Linux 沙箱中列出当前目录的文件",
        "session_id": "test_session"
    }
)
print(response.json())

# 3. 获取所有沙箱信息
response = requests.get("http://localhost:8000/api/sandboxes")
print(response.json())

# 4. 获取所有沙箱信息，找到 sandbox_id
response = requests.get("http://localhost:8000/api/sandboxes")
sandboxes = response.json()["sandboxes"]
# 查找已创建的沙箱
for key, info in sandboxes.items():
    if info.get("sandbox_id"):
        sandbox_id = info["sandbox_id"]
        print(f"Found sandbox: {sandbox_id} ({info.get('sandbox_type')})")

# 5. 获取指定沙箱的截图（使用 sandbox_id）
if sandbox_id:
    response = requests.get(
        f"http://localhost:8000/api/sandboxes/{sandbox_id}/screenshot"
    )
    screenshot_data = response.json()
    if screenshot_data.get("success"):
        print(f"Screenshot URL: {screenshot_data.get('screenshot_url')}")

# 6. 获取指定沙箱的 resource_url（使用 sandbox_id）
if sandbox_id:
    response = requests.get(
        f"http://localhost:8000/api/sandboxes/{sandbox_id}/resource_url"
    )
    resource_url_data = response.json()
    if resource_url_data.get("success"):
        print(f"Resource URL: {resource_url_data.get('resource_url')}")
        print("可以在浏览器中打开此 URL 来访问沙箱环境")

# 6. 获取所有工具
response = requests.get("http://localhost:8000/api/tools")
tools = response.json()["tools"]
print(f"Total tools: {len(tools)}")
```

### JavaScript/TypeScript 示例

```javascript
// 1. 发送消息（非流式）
const response = await fetch("http://localhost:8000/api/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    message: "在 Linux 沙箱中列出当前目录的文件",
    session_id: "test_session",
  }),
});
const data = await response.json();
console.log(data.response);

// 2. 流式对话（SSE）
const eventSource = new EventSource(
  "http://localhost:8000/api/chat/stream?message=执行ls命令"
);
eventSource.onmessage = (event) => {
  if (event.data === "[DONE]") {
    eventSource.close();
  } else {
    console.log(event.data);
  }
};

// 3. WebSocket 对话
const ws = new WebSocket("ws://localhost:8000/ws/chat");
ws.onopen = () => {
  ws.send(JSON.stringify({ message: "执行ls命令" }));
};
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === "chunk") {
    console.log(data.content);
  } else if (data.type === "done") {
    console.log("Response complete");
  }
};
```

---

## 注意事项

1. **沙箱按需创建**: 沙箱不会在 Agent 启动时预先创建，而是在首次使用工具时按需创建。这减少了启动时间和资源消耗。

2. **工具自动发现**: 所有工具在 Agent 启动时自动注册，无需手动配置。工具列表可以通过 `/api/tools` 或 `/api/sandboxes/{sandbox_id}/tools` 获取。

3. **会话管理**: 当前版本使用简单的会话 ID 机制，未来可能会增强会话管理功能。

4. **CORS 配置**: 当前 CORS 设置为允许所有来源（`allow_origins=["*"]`），生产环境应限制为特定域名。

5. **错误处理**: 所有 API 端点都包含错误处理，会返回适当的 HTTP 状态码和错误信息。

---

## API 文档自动生成

FastAPI 自动生成了交互式 API 文档，可以通过以下地址访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

这些文档提供了完整的 API 说明、请求/响应示例和在线测试功能。
