# -*- coding: utf-8 -*-
"""
Enhanced Browser Automation Example
展示如何使用增强的 AGB 浏览器自动化能力
"""

import asyncio
import json
from agentscope_browseruse_agent import AgentscopeBrowseruseAgent

# 示例配置
config = {
    "backend": {
        "agent-type": "agentscope",
        "llm-name": "qwen-plus",
        "session-type": "memory",
        "memory-type": "memory",
        "agb-image-id": "agb-browser-use-1"
    }
}

async def demonstrate_enhanced_automation():
    """演示增强的浏览器自动化能力"""
    
    # 初始化增强的浏览器代理
    agent = AgentscopeBrowseruseAgent(session_id="demo_session", config=config)
    
    try:
        # 连接并初始化
        await agent.connect()
        print("✅ AGB 浏览器会话已初始化")
        
        # 1. 获取浏览器信息
        print("\n🔍 获取浏览器信息...")
        browser_info = agent.tools[-8]()  # agb_get_browser_info
        print(f"浏览器端点: {browser_info.get('endpoint', 'N/A')}")
        print(f"资源URL: {browser_info.get('resource_url', 'N/A')}")
        
        # 2. 配置浏览器设置
        print("\n⚙️ 配置浏览器设置...")
        config_result = agent.tools[-7](  # agb_configure_browser
            use_stealth=True,
            viewport_width=1920,
            viewport_height=1080,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        print(f"配置结果: {config_result}")
        
        # 3. 使用增强的导航工具
        print("\n🌐 使用增强的导航工具...")
        navigate_result = agent.tools[-1](  # agb_navigate
            url="https://example.com",
            wait_for_load=True,
            timeout_ms=30000
        )
        print(f"导航结果: {navigate_result}")
        
        # 4. 执行 AGB AI 操作
        print("\n🎯 执行 AGB AI 操作...")
        act_result = agent.tools[-6](  # agb_act
            action="Take a screenshot of the current page",
            timeout_ms=20000,
            include_iframes=False
        )
        print(f"AGB Act 结果: {act_result}")
        
        # 5. AGB 智能页面分析
        print("\n👀 AGB 智能页面分析...")
        observe_result = agent.tools[-5](  # agb_observe
            instruction="Find all clickable buttons and links on the page",
            return_actions=5,
            include_iframes=False
        )
        print(f"AGB Observe 结果: {observe_result}")
        
        # 6. AGB 结构化数据提取
        print("\n📊 AGB 结构化数据提取...")
        extract_result = agent.tools[-4](  # agb_extract
            instruction="Extract all headings and their text content",
            schema_name="PageHeadings",
            use_text_extract=True,
            selector="h1, h2, h3"
        )
        print(f"AGB Extract 结果: {extract_result}")
        
        # 7. AGB 智能表单填写
        print("\n📝 AGB 智能表单填写...")
        form_result = agent.tools[-3](  # agb_smart_fill_form
            form_data="Fill email field with 'test@example.com' and password with 'password123'",
            timeout_ms=15000
        )
        print(f"AGB 表单填写结果: {form_result}")
        
        # 8. AGB 智能元素查找和点击
        print("\n🖱️ AGB 智能元素查找和点击...")
        click_result = agent.tools[-2](  # agb_find_and_click
            element_description="Find and click the submit button",
            timeout_ms=10000
        )
        print(f"AGB 点击结果: {click_result}")
        
        # 9. AGB 智能等待条件
        print("\n⏳ AGB 智能等待条件...")
        wait_result = agent.tools[-1](  # agb_wait_for_condition
            condition="Wait for the success message to appear",
            timeout_ms=15000
        )
        print(f"AGB 等待结果: {wait_result}")
        
        print("\n🎉 增强浏览器自动化演示完成！")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
    
    finally:
        # 清理资源
        await agent.close()
        print("🧹 资源清理完成")

def demonstrate_tool_capabilities():
    """演示工具能力概览"""
    
    print("🚀 增强的 AGB 浏览器自动化工具集")
    print("=" * 50)
    
    tools_info = [
        {
            "name": "agb_get_browser_info",
            "description": "获取 AGB 浏览器连接信息",
            "use_case": "检查 AGB 会话状态和 CDP 端点"
        },
        {
            "name": "agb_act", 
            "description": "AGB AI 代理自然语言操作",
            "use_case": "通过 AGB agent.act_async() 执行复杂交互"
        },
        {
            "name": "agb_observe",
            "description": "AGB AI 代理智能页面分析",
            "use_case": "通过 AGB agent.observe_async() 分析页面结构"
        },
        {
            "name": "agb_extract",
            "description": "AGB AI 代理结构化数据提取",
            "use_case": "通过 AGB agent.extract_async() 提取数据"
        },
        {
            "name": "agb_configure_browser",
            "description": "AGB 浏览器增强配置",
            "use_case": "配置隐身模式、指纹保护、代理支持"
        },
        {
            "name": "agb_smart_fill_form",
            "description": "AGB AI 代理智能表单填写",
            "use_case": "通过 AGB AI 分析表单结构并自动填写"
        },
        {
            "name": "agb_find_and_click",
            "description": "AGB AI 代理智能元素查找和点击",
            "use_case": "通过 AGB AI 智能定位和点击元素"
        },
        {
            "name": "agb_wait_for_condition",
            "description": "AGB AI 代理智能等待条件",
            "use_case": "通过 AGB AI 智能监控页面状态变化"
        },
        {
            "name": "agb_navigate",
            "description": "AGB + Playwright 增强导航",
            "use_case": "通过 CDP 连接实现反检测导航"
        }
    ]
    
    for i, tool in enumerate(tools_info, 1):
        print(f"{i}. {tool['name']}")
        print(f"   功能: {tool['description']}")
        print(f"   用例: {tool['use_case']}")
        print()

def show_usage_examples():
    """展示使用示例"""
    
    print("📚 使用示例")
    print("=" * 30)
    
    examples = [
        {
            "scenario": "电商网站数据抓取",
            "tools": ["agb_observe", "agb_extract", "agb_act"],
            "description": "观察产品列表，提取价格和名称，自动翻页"
        },
        {
            "scenario": "自动化测试",
            "tools": ["agb_act", "agb_wait_for_condition", "agb_find_and_click"],
            "description": "执行测试用例，等待结果，验证功能"
        },
        {
            "scenario": "表单自动化",
            "tools": ["agb_smart_fill_form", "agb_observe", "agb_act"],
            "description": "智能填写表单，观察验证结果，提交数据"
        },
        {
            "scenario": "网站监控",
            "tools": ["agb_observe", "agb_wait_for_condition", "agb_extract"],
            "description": "监控页面变化，提取关键信息，生成报告"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['scenario']}")
        print(f"   工具: {', '.join(example['tools'])}")
        print(f"   描述: {example['description']}")
        print()

if __name__ == "__main__":
    print("🎯 AGB 增强浏览器自动化演示")
    print("=" * 40)
    
    # 显示工具能力
    demonstrate_tool_capabilities()
    
    # 显示使用示例
    show_usage_examples()
    
    # 运行演示（需要有效的 AGB API 密钥）
    print("🚀 开始运行演示...")
    print("注意: 需要设置 AGB_API_KEY 环境变量")
    
    # 取消注释以运行实际演示
    # asyncio.run(demonstrate_enhanced_automation())
