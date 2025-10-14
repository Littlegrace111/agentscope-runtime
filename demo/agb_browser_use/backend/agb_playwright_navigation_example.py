# -*- coding: utf-8 -*-
"""
AGB + Playwright 导航实现示例
展示如何正确使用 AGB 和 async_playwright() 进行浏览器导航
"""

import asyncio
import os
from playwright.async_api import async_playwright
from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser import BrowserOption, BrowserViewport

async def agb_navigate_with_playwright(agb_session, url: str, wait_for_load: bool = True, timeout_ms: int = 30000):
    """
    使用 AGB + Playwright 进行页面导航的实际实现
    
    Args:
        agb_session: AGB 会话对象
        url: 要导航的 URL
        wait_for_load: 是否等待页面完全加载
        timeout_ms: 超时时间（毫秒）
    
    Returns:
        dict: 导航结果
    """
    try:
        # 1. 获取 AGB 会话的 CDP 端点
        endpoint_url = agb_session.browser.get_endpoint_url()
        print(f"🔗 连接到 AGB CDP 端点: {endpoint_url}")
        
        # 2. 使用 async_playwright() 连接 CDP
        async with async_playwright() as p:
            # 连接到 AGB 的浏览器实例
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            print("✅ 成功连接到 AGB 浏览器")
            
            # 3. 创建新页面
            page = await browser.new_page()
            print("📄 创建新页面")
            
            # 4. 设置页面选项（可选）
            if wait_for_load:
                # 设置页面加载超时
                page.set_default_timeout(timeout_ms)
            
            # 5. 导航到目标 URL
            print(f"🌐 导航到: {url}")
            response = await page.goto(url, wait_until="domcontentloaded" if wait_for_load else "commit")
            
            # 6. 获取页面信息
            title = await page.title()
            current_url = page.url
            
            # 7. 等待页面完全加载（如果需要）
            if wait_for_load:
                print("⏳ 等待页面完全加载...")
                await page.wait_for_load_state("networkidle", timeout=timeout_ms)
            
            result = {
                "success": True,
                "message": f"成功导航到 {url}",
                "url": current_url,
                "title": title,
                "status": response.status if response else None,
                "features_used": [
                    "AGB stealth mode",
                    "CDP connection via async_playwright()",
                    "Enhanced fingerprinting protection",
                    "Custom browser configuration"
                ]
            }
            
            print(f"✅ 导航完成: {title}")
            return result
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"导航失败: {e}"
        }

async def demonstrate_agb_navigation():
    """演示 AGB 导航的完整流程"""
    
    # 初始化 AGB
    agb = AGB()  # 使用环境变量中的 AGB_API_KEY
    
    try:
        # 创建 AGB 会话
        print("🚀 创建 AGB 会话...")
        params = CreateSessionParams(image_id="agb-browser-use-1")
        result = agb.create(params)
        
        if not result.success:
            raise RuntimeError(f"创建 AGB 会话失败: {result.error_message}")
        
        session = result.session
        print("✅ AGB 会话创建成功")
        
        # 配置浏览器选项
        print("⚙️ 配置浏览器选项...")
        option = BrowserOption(
            use_stealth=True,
            viewport=BrowserViewport(width=1366, height=768),
        )
        
        # 初始化浏览器
        success = session.browser.initialize(option)
        if not success:
            raise RuntimeError("浏览器初始化失败")
        
        print("✅ 浏览器初始化成功")
        
        # 使用 Playwright 进行导航
        navigation_result = await agb_navigate_with_playwright(
            agb_session=session,
            url="https://example.com",
            wait_for_load=True,
            timeout_ms=30000
        )
        
        print(f"📊 导航结果: {navigation_result}")
        
        # 可以继续执行其他操作...
        # 例如：截图、提取数据、执行操作等
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
    
    finally:
        # 清理资源
        try:
            if 'session' in locals():
                agb.delete(session)
                print("🧹 AGB 会话已清理")
        except Exception as e:
            print(f"⚠️ 清理资源时出现错误: {e}")

def show_agb_navigation_architecture():
    """展示 AGB 导航架构"""
    
    print("🏗️ AGB 浏览器导航架构")
    print("=" * 40)
    
    architecture = {
        "1. AGB 会话管理": {
            "创建会话": "agb.create(CreateSessionParams())",
            "配置浏览器": "BrowserOption(use_stealth=True, viewport=...)",
            "初始化浏览器": "session.browser.initialize(option)"
        },
        "2. CDP 连接": {
            "获取端点": "session.browser.get_endpoint_url()",
            "Playwright 连接": "p.chromium.connect_over_cdp(endpoint_url)",
            "创建页面": "browser.new_page()"
        },
        "3. 页面导航": {
            "基础导航": "page.goto(url)",
            "等待加载": "page.wait_for_load_state()",
            "获取信息": "page.title(), page.url"
        },
        "4. 增强功能": {
            "隐身模式": "AGB 内置反检测",
            "指纹保护": "自定义浏览器指纹",
            "代理支持": "内置代理池"
        }
    }
    
    for section, details in architecture.items():
        print(f"\n{section}:")
        for key, value in details.items():
            print(f"  • {key}: {value}")

def show_implementation_comparison():
    """展示实现对比"""
    
    print("\n🔄 实现方式对比")
    print("=" * 30)
    
    comparison = {
        "传统 Playwright": {
            "优点": ["直接控制", "轻量级", "快速启动"],
            "缺点": ["容易被检测", "指纹识别", "IP 限制"],
            "适用场景": "简单自动化、测试"
        },
        "AGB + Playwright": {
            "优点": ["反检测", "指纹保护", "代理支持", "云端管理"],
            "缺点": ["需要网络", "成本较高", "依赖服务"],
            "适用场景": "生产环境、大规模自动化"
        }
    }
    
    for approach, details in comparison.items():
        print(f"\n{approach}:")
        for key, value in details.items():
            if isinstance(value, list):
                print(f"  {key}: {', '.join(value)}")
            else:
                print(f"  {key}: {value}")

if __name__ == "__main__":
    print("🎯 AGB + Playwright 导航实现演示")
    print("=" * 40)
    
    # 显示架构信息
    show_agb_navigation_architecture()
    
    # 显示实现对比
    show_implementation_comparison()
    
    # 运行演示（需要有效的 AGB_API_KEY）
    print("\n🚀 开始运行演示...")
    print("注意: 需要设置 AGB_API_KEY 环境变量")
    
    # 取消注释以运行实际演示
    # asyncio.run(demonstrate_agb_navigation())
