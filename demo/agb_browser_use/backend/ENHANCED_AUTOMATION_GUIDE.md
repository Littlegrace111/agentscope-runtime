# 增强的 AGB 浏览器自动化指南

## 🎯 概述

基于 AGB (Agent Browser) 的强大能力，我们为 `AgentscopeBrowseruseAgent` 添加了 8 个增强的浏览器自动化工具，提供自然语言驱动的智能浏览器操作。

## 🚀 核心能力

### 1. 自然语言操作 (Act)

- **工具**: `agb_act`
- **能力**: 使用自然语言描述执行复杂浏览器操作
- **用例**: 表单填写、元素点击、页面滚动、多步骤操作

### 2. 智能页面分析 (Observe)

- **工具**: `agb_observe`
- **能力**: 分析页面结构，识别可交互元素
- **用例**: 元素定位、页面结构分析、交互元素发现

### 3. 结构化数据提取 (Extract)

- **工具**: `agb_extract`
- **能力**: 使用自然语言和模式定义提取结构化数据
- **用例**: 数据抓取、信息提取、内容分析

## 🛠️ 增强工具集

### 核心 AI 工具

#### `agb_act` - 自然语言操作执行

```python
# 执行复杂操作
result = agb_act(
    action="Fill the login form with email 'user@example.com' and password 'password123', then click submit",
    timeout_ms=15000,
    include_iframes=False
)
```

#### `agb_observe` - 智能页面分析

```python
# 分析页面元素
result = agb_observe(
    instruction="Find all clickable buttons and links on the page",
    return_actions=10,
    include_iframes=False
)
```

#### `agb_extract` - 结构化数据提取

```python
# 提取产品信息
result = agb_extract(
    instruction="Extract all product names, prices, and ratings",
    schema_name="ProductData",
    use_text_extract=True,
    selector=".product-item"
)
```

### 配置和高级工具

#### `agb_configure_browser` - 动态浏览器配置

```python
# 配置隐身模式和视口
result = agb_configure_browser(
    use_stealth=True,
    viewport_width=1920,
    viewport_height=1080,
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    screen_width=1920,
    screen_height=1080
)
```

#### `agb_smart_fill_form` - 智能表单填写

```python
# 智能填写表单
result = agb_smart_fill_form(
    form_data="Fill email with 'test@example.com', password with 'password123', and agree to terms",
    timeout_ms=10000
)
```

#### `agb_find_and_click` - 智能元素查找和点击

```python
# 智能查找和点击
result = agb_find_and_click(
    element_description="Find the blue submit button with text 'Submit'",
    timeout_ms=10000
)
```

#### `agb_wait_for_condition` - 智能等待条件

```python
# 等待特定条件
result = agb_wait_for_condition(
    condition="Wait for the success message to appear after form submission",
    timeout_ms=15000
)
```

#### `agb_navigate` - 增强的页面导航

```python
# 使用 AGB + Playwright 进行导航
result = agb_navigate(
    url="https://example.com",
    wait_for_load=True,
    timeout_ms=30000
)
```

**实际实现架构**:

```python
# 1. 获取 AGB CDP 端点
endpoint_url = agb_session.browser.get_endpoint_url()

# 2. 使用 async_playwright() 连接
async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp(endpoint_url)
    page = await browser.new_page()

    # 3. 导航到目标 URL
    await page.goto(url, wait_until="domcontentloaded")

    # 4. 等待页面加载
    await page.wait_for_load_state("networkidle")
```

#### `agb_get_browser_info` - 浏览器信息获取

```python
# 获取浏览器连接信息
result = agb_get_browser_info()
```

## 📋 使用场景

### 1. 电商数据抓取

```python
# 观察产品列表
observe_result = agb_observe("Find all product cards on the page")

# 提取产品信息
extract_result = agb_extract(
    instruction="Extract product name, price, and rating from each card",
    schema_name="ProductList"
)

# 自动翻页
act_result = agb_act("Click the 'Next Page' button to load more products")
```

### 2. 自动化测试

```python
# 执行测试步骤
act_result = agb_act("Navigate to login page and fill credentials")

# 等待结果
wait_result = agb_wait_for_condition("Wait for dashboard to load")

# 验证结果
observe_result = agb_observe("Check if welcome message is displayed")
```

### 3. 表单自动化

```python
# 智能填写表单
form_result = agb_smart_fill_form(
    "Fill registration form with name 'John Doe', email 'john@example.com', and phone '123-456-7890'"
)

# 提交并等待
submit_result = agb_act("Click submit button and wait for confirmation")
```

### 4. 网站监控

```python
# 监控页面变化
observe_result = agb_observe("Check for any new notifications or alerts")

# 提取关键信息
extract_result = agb_extract(
    instruction="Extract all status updates and timestamps",
    schema_name="StatusUpdates"
)
```

## 🔧 配置选项

### 浏览器配置

- **隐身模式**: 避免检测
- **视口设置**: 自定义浏览器窗口大小
- **用户代理**: 模拟不同设备和浏览器
- **屏幕分辨率**: 设置显示分辨率

### 操作参数

- **超时设置**: 为不同操作设置合适的超时时间
- **iframe 支持**: 处理嵌套框架内容
- **重试机制**: 自动重试失败的操作

## 🎯 最佳实践

### 1. 操作顺序

1. 先使用 `agb_observe` 分析页面
2. 使用 `agb_act` 执行操作
3. 使用 `agb_wait_for_condition` 等待结果
4. 使用 `agb_extract` 提取数据

### 2. 错误处理

```python
try:
    result = agb_act("Click the submit button")
    if not result.get("success"):
        # 重试或使用备用方案
        backup_result = agb_find_and_click("Find any submit button")
except Exception as e:
    print(f"操作失败: {e}")
```

### 3. 性能优化

- 使用合适的超时时间
- 避免不必要的 iframe 处理
- 批量执行相关操作

## 🚨 注意事项

### 当前实现状态

- 当前实现为**占位符版本**，展示工具接口和参数
- 实际执行需要与 AGB 页面对象集成
- 需要有效的 AGB API 密钥

### 集成要求

- 需要传递当前页面对象给 AGB 代理
- 需要定义 Pydantic 数据模式用于提取
- 需要处理异步操作和错误恢复

### 扩展建议

1. 实现真实的 AGB 代理调用
2. 添加数据模式定义
3. 集成页面对象管理
4. 添加错误恢复机制

## 📚 示例代码

查看 `enhanced_browser_automation_example.py` 获取完整的使用示例和演示代码。

## 🔗 相关文档

- [AGB 浏览器自动化文档](../../../docs/agb/browser-automation.md)
- [AgentScope 运行时文档](../../../README.md)
- [AGB API 参考](https://docs.agb.com/api-reference)
