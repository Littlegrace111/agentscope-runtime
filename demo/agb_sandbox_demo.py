# -*- coding: utf-8 -*-
"""
AGB Cloud 沙箱使用示例

演示如何使用 AGB Cloud 沙箱进行：
- 代码执行
- 文件操作
- 命令执行
- 浏览器自动化
"""

import os
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from agentscope_runtime.sandbox.factory import create_sandbox
from agentscope_runtime.sandbox.enums import SandboxType
from agentscope_runtime.sandbox.tools.agb_tools import get_agb_tools
from agentscope_runtime.engine import Runner
from agentscope_runtime.engine.agents.llm_agent import LLMAgent
from agentscope_runtime.engine.llms import QwenLLM
from agentscope_runtime.engine.services.context_manager import ContextManager


def demo_agb_sandbox_direct():
    """直接使用 AGB 沙箱的示例"""
    print("=== AGB 沙箱直接使用示例 ===")
    
    # 创建 AGB 云沙箱
    agb_sandbox = create_sandbox(sandbox_type=SandboxType.AGB)
    
    try:
        # 检查 AGB 是否可用
        if not agb_sandbox.is_available():
            print("❌ AGB 不可用，请检查 AGB_API_KEY 环境变量")
            print("💡 调试信息:")
            print(f"  - AGB 客户端: {'✅ 已初始化' if agb_sandbox._agb_client else '❌ 未初始化'}")
            print(f"  - AGB 会话: {'✅ 已创建' if agb_sandbox._agb_session else '❌ 未创建'}")
            print(f"  - API Key: {'✅ 已设置' if os.getenv('AGB_API_KEY') else '❌ 未设置'}")
            return
        
        print("✅ AGB 沙箱创建成功")
        
        # 获取 AGB 会话
        session = agb_sandbox.get_agb_session()
        if not session:
            print("❌ 无法获取 AGB 会话")
            return
        
        print("✅ AGB 会话获取成功")
        
        # 示例 1: 代码执行
        print("\n--- 代码执行示例 ---")
        python_code = """
import math
import datetime

# 计算圆周率
pi = math.pi
print(f"圆周率: {pi}")

# 当前时间
now = datetime.datetime.now()
print(f"当前时间: {now}")

# 简单计算
result = sum(range(1, 101))
print(f"1到100的和: {result}")
"""
        
        result = agb_sandbox.execute_code(python_code, "python")
        if result["success"]:
            print("✅ Python 代码执行成功:")
            print(result["output"])
        else:
            print(f"❌ Python 代码执行失败: {result['error']}")
        
        # 示例 2: 文件操作
        print("\n--- 文件操作示例 ---")
        
        # 写入文件
        test_content = "Hello from AGB Cloud!\nThis is a test file."
        write_result = agb_sandbox.write_file("/tmp/agb_test.txt", test_content)
        if write_result["success"]:
            print("✅ 文件写入成功")
            
            # 读取文件
            read_result = agb_sandbox.read_file("/tmp/agb_test.txt")
            if read_result["success"]:
                print("✅ 文件读取成功:")
                print(read_result["content"])
            else:
                print(f"❌ 文件读取失败: {read_result['error']}")
        else:
            print(f"❌ 文件写入失败: {write_result['error']}")
        
        # 示例 3: 命令执行
        print("\n--- 命令执行示例 ---")
        command_result = agb_sandbox.execute_command("ls -la /tmp/ | head -10")
        if command_result["success"]:
            print("✅ 命令执行成功:")
            print(command_result["output"])
        else:
            print(f"❌ 命令执行失败: {command_result['error']}")
        
        # 示例 4: 目录操作
        print("\n--- 目录操作示例 ---")
        
        # 创建目录
        create_dir_result = agb_sandbox.create_directory("/tmp/agb_demo")
        if create_dir_result["success"]:
            print("✅ 目录创建成功")
            
            # 列出目录
            list_result = agb_sandbox.list_directory("/tmp/agb_demo")
            if list_result["success"]:
                print("✅ 目录列表获取成功:")
                for entry in list_result["entries"]:
                    print(f"  - {entry['name']} ({entry['type']})")
            else:
                print(f"❌ 目录列表获取失败: {list_result['error']}")
        else:
            print(f"❌ 目录创建失败: {create_dir_result['error']}")
        
    except Exception as e:
        print(f"❌ 示例执行出错: {e}")
    
    finally:
        # 清理资源
        agb_sandbox.cleanup()
        print("\n✅ AGB 沙箱资源已清理")


async def demo_agb_with_agent():
    """使用 AGB 沙箱和智能体的示例"""
    print("\n=== AGB 沙箱 + 智能体示例 ===")
    
    # 检查环境变量
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("❌ 请设置 DASHSCOPE_API_KEY 环境变量")
        return
    
    if not os.getenv("AGB_API_KEY"):
        print("❌ 请设置 AGB_API_KEY 环境变量")
        return
    
    try:
        # 创建 AGB 云沙箱
        agb_sandbox = create_sandbox(sandbox_type=SandboxType.AGB)
        
        # 获取 AGB 工具
        agb_tools = get_agb_tools()
        print(f"✅ 获取到 {len(agb_tools)} 个 AGB 工具")
        
        # 创建 LLM 模型
        model = QwenLLM(
            model_name="qwen-turbo",
            api_key=os.getenv("DASHSCOPE_API_KEY")
        )
        
        # 创建智能体
        agent = LLMAgent(
            model=model,
            name="AGB_Agent",
            description="使用 AGB Cloud 进行代码执行、文件操作和浏览器自动化的智能体",
            tools=agb_tools
        )
        
        # 创建上下文管理器
        context_manager = ContextManager()
        
        # 使用 Runner 运行智能体
        async with Runner(agent=agent, context_manager=context_manager) as runner:
            # 测试查询
            test_queries = [
                "请使用 AGB Cloud 执行 Python 代码计算斐波那契数列的前10项",
                "请使用 AGB Cloud 创建一个文件并写入一些内容",
                "请使用 AGB Cloud 执行命令查看当前目录的文件列表"
            ]
            
            for i, query in enumerate(test_queries, 1):
                print(f"\n--- 测试查询 {i} ---")
                print(f"查询: {query}")
                
                from agentscope_runtime.engine.schemas.agent_schemas import AgentRequest
                
                request = AgentRequest(
                    input=[{
                        "role": "user",
                        "content": [{
                            "type": "text",
                            "text": query
                        }]
                    }]
                )
                
                try:
                    async for message in runner.stream_query(request=request):
                        if hasattr(message, 'content') and message.content:
                            content = message.content[0]
                            if hasattr(content, 'text'):
                                print(f"智能体回复: {content.text}")
                            else:
                                print(f"智能体回复: {content}")
                except Exception as e:
                    print(f"❌ 查询执行失败: {e}")
        
    except Exception as e:
        print(f"❌ 智能体示例执行出错: {e}")
    
    finally:
        # 清理资源
        if 'agb_sandbox' in locals():
            agb_sandbox.cleanup()
        print("\n✅ 智能体示例资源已清理")


def demo_agb_browser():
    """AGB 浏览器自动化示例"""
    print("\n=== AGB 浏览器自动化示例 ===")
    
    try:
        # 创建 AGB 云沙箱
        agb_sandbox = create_sandbox(sandbox_type=SandboxType.AGB)
        
        if not agb_sandbox.is_available():
            print("❌ AGB 不可用")
            print("💡 调试信息:")
            print(f"  - AGB 客户端: {'✅ 已初始化' if agb_sandbox._agb_client else '❌ 未初始化'}")
            print(f"  - AGB 会话: {'✅ 已创建' if agb_sandbox._agb_session else '❌ 未创建'}")
            return
        
        # 初始化浏览器
        print("正在初始化浏览器...")
        browser_result = agb_sandbox.initialize_browser()
        
        if browser_result["success"]:
            print("✅ 浏览器初始化成功")
            print(f"CDP 端点: {browser_result['endpoint_url']}")
            
            # 这里可以进一步使用 Playwright 进行浏览器操作
            # 由于需要额外的 Playwright 集成，这里只显示端点信息
            print("💡 提示: 可以使用 Playwright 连接到上述 CDP 端点进行浏览器自动化")
            
        else:
            print(f"❌ 浏览器初始化失败: {browser_result['error']}")
    
    except Exception as e:
        print(f"❌ 浏览器示例执行出错: {e}")
    
    finally:
        if 'agb_sandbox' in locals():
            agb_sandbox.cleanup()
        print("✅ 浏览器示例资源已清理")


def main():
    """主函数"""
    print("🚀 AGB Cloud 沙箱演示程序")
    print("=" * 50)
    
    # 检查环境变量
    if not os.getenv("AGB_API_KEY"):
        print("❌ 请设置 AGB_API_KEY 环境变量")
        print("💡 提示: 在 .env 文件中添加 AGB_API_KEY=your_api_key")
        return
    
    # 运行示例
    demo_agb_sandbox_direct()
    
    # 运行智能体示例（需要 DASHSCOPE_API_KEY）
    if os.getenv("DASHSCOPE_API_KEY"):
        asyncio.run(demo_agb_with_agent())
    else:
        print("\n💡 提示: 设置 DASHSCOPE_API_KEY 可以运行智能体示例")
    
    # 运行浏览器示例
    # demo_agb_browser()
    
    print("\n🎉 所有示例执行完成！")


if __name__ == "__main__":
    main()
