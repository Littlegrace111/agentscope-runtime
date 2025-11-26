# Curl Scripts for Sandbox Management

本目录包含用于创建沙箱和获取 resource_url 的 curl 脚本。

## 脚本说明

### 1. `create_and_get_resource_url.sh` (完整版)

功能完整的脚本，包含：

- 详细的错误处理
- 彩色输出
- 支持使用 `jq` 或原生 shell 工具解析 JSON
- 完整的错误信息显示

**使用方法**:

```bash
# 使用默认的 linux 沙箱
./create_and_get_resource_url.sh

# 指定沙箱类型
./create_and_get_resource_url.sh linux
./create_and_get_resource_url.sh windows
./create_and_get_resource_url.sh browser
./create_and_get_resource_url.sh mobile

# 指定 API 服务器地址
API_BASE_URL=http://localhost:8000 ./create_and_get_resource_url.sh linux
```

### 2. `create_and_get_resource_url_simple.sh` (简化版)

简化版本，需要 `jq` 工具，代码更简洁。

**使用方法**:

```bash
# 使用默认的 linux 沙箱
./create_and_get_resource_url_simple.sh

# 指定沙箱类型
./create_and_get_resource_url_simple.sh browser
```

## 前置要求

### 完整版脚本

- `curl` (必需)
- `jq` (可选，但推荐安装以获得更好的 JSON 解析)

### 简化版脚本

- `curl` (必需)
- `jq` (必需)

### 安装 jq

**macOS**:

```bash
brew install jq
```

**Linux (Ubuntu/Debian)**:

```bash
sudo apt-get install jq
```

**Linux (CentOS/RHEL)**:

```bash
sudo yum install jq
```

## 使用示例

### 示例 1: 创建 Linux 沙箱并获取 URL

```bash
$ ./create_and_get_resource_url.sh linux

=== Creating linux sandbox ===
Step 1: Creating sandbox...
✓ Sandbox created successfully
  Sandbox ID: s-abc123xyz

=== Getting resource_url for sandbox s-abc123xyz ===
Step 2: Fetching resource_url...
✓ Resource URL retrieved successfully

=== Result ===
Sandbox ID: s-abc123xyz
Sandbox Type: linux
Resource URL:
https://wy.aliyuncs.com/app/InnoArchClub/mcp_container/mcp.html?authcode=...

You can open this URL in your browser to access the sandbox GUI
```

### 示例 2: 使用环境变量指定 API 地址

```bash
API_BASE_URL=http://192.168.1.100:8000 ./create_and_get_resource_url.sh browser
```

## 手动 curl 命令

如果不想使用脚本，也可以手动执行以下命令：

```bash
# 1. 创建沙箱
curl -X POST "http://localhost:8000/api/sandboxes?sandbox_type=linux"

# 响应示例:
# {"success":true,"sandbox_id":"s-xxxxx","sandbox_type":"linux","image_id":"linux_latest"}

# 2. 提取 sandbox_id (假设为 s-xxxxx)，然后获取 resource_url
curl "http://localhost:8000/api/sandboxes/s-xxxxx/resource_url"

# 响应示例:
# {"success":true,"resource_url":"https://...","sandbox_id":"s-xxxxx",...}
```

## 故障排除

### 问题 1: 脚本报错 "jq: command not found"

**解决方案**: 安装 `jq` 工具，或使用完整版脚本（支持不使用 jq 的降级方案）

### 问题 2: 连接失败

**检查项**:

- API 服务器是否正在运行
- `API_BASE_URL` 是否正确
- 防火墙设置

### 问题 3: 沙箱创建失败

**可能原因**:

- AgentBay API Key 未配置或无效
- 网络连接问题
- AgentBay 服务不可用

**调试方法**:

```bash
# 查看详细响应
curl -v -X POST "http://localhost:8000/api/sandboxes?sandbox_type=linux"
```

## 相关文档

- [API 文档](./API_DOCUMENTATION.md)
- [README](./README.md)
