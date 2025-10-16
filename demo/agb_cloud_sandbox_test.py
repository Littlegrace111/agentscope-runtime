# -*- coding: utf-8 -*-
"""
AGB 云沙箱测试脚本

测试新的云沙箱架构是否正常工作
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_agb_cloud_sandbox():
    """测试 AGB 云沙箱"""
    print("🧪 测试 AGB 云沙箱架构")
    print("=" * 50)
    
    # 检查环境变量
    if not os.getenv("AGB_API_KEY"):
        print("❌ 请设置 AGB_API_KEY 环境变量")
        return False
    
    try:
        # 导入新的云沙箱架构
        from agentscope_runtime.sandbox.factory import create_sandbox
        from agentscope_runtime.sandbox.enums import SandboxType
        from agentscope_runtime.sandbox.factory import is_cloud_sandbox, get_cloud_sandbox_types
        
        print("✅ 成功导入云沙箱模块")
        
        # 测试工厂函数
        print("\n--- 测试沙箱工厂 ---")
        print(f"AGB 是否为云沙箱: {is_cloud_sandbox(SandboxType.AGB)}")
        print(f"BASE 是否为云沙箱: {is_cloud_sandbox(SandboxType.BASE)}")
        print(f"云沙箱类型: {get_cloud_sandbox_types()}")
        
        # 创建 AGB 云沙箱
        print("\n--- 创建 AGB 云沙箱 ---")
        agb_sandbox = create_sandbox(sandbox_type=SandboxType.AGB)
        print(f"✅ AGB 云沙箱创建成功: {type(agb_sandbox).__name__}")
        
        # 测试基本方法
        print("\n--- 测试基本方法 ---")
        print(f"沙箱 ID: {agb_sandbox.sandbox_id}")
        print(f"沙箱类型: {agb_sandbox.sandbox_type}")
        print(f"是否可用: {agb_sandbox.is_available()}")
        
        # 测试获取信息
        print("\n--- 测试获取信息 ---")
        info = agb_sandbox.get_info()
        print(f"沙箱信息: {info}")
        
        # 测试工具列表
        print("\n--- 测试工具列表 ---")
        tools = agb_sandbox.list_tools()
        print(f"可用工具数量: {len(tools.get('tools', []))}")
        for tool in tools.get('tools', [])[:3]:  # 只显示前3个工具
            print(f"  - {tool['name']}: {tool['description']}")
        
        # 测试代码执行（如果 AGB 可用）
        if agb_sandbox.is_available():
            print("\n--- 测试代码执行 ---")
            result = agb_sandbox.execute_code("print('Hello from AGB Cloud!')", "python")
            if result["success"]:
                print(f"✅ 代码执行成功: {result['output']}")
            else:
                print(f"❌ 代码执行失败: {result['error']}")
        else:
            print("\n⚠️  AGB 不可用，跳过代码执行测试")
        
        # 清理资源
        print("\n--- 清理资源 ---")
        agb_sandbox.cleanup()
        print("✅ 资源清理完成")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_factory_functions():
    """测试工厂函数"""
    print("\n🔧 测试工厂函数")
    print("=" * 30)
    
    try:
        from agentscope_runtime.sandbox.factory import (
            get_supported_sandbox_types,
            get_cloud_sandbox_types,
            get_container_sandbox_types
        )
        
        print(f"支持的沙箱类型: {get_supported_sandbox_types()}")
        print(f"云沙箱类型: {get_cloud_sandbox_types()}")
        print(f"容器沙箱类型: {get_container_sandbox_types()}")
        
        return True
        
    except Exception as e:
        print(f"❌ 工厂函数测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 AGB 云沙箱架构测试")
    print("=" * 60)
    
    # 测试工厂函数
    factory_test = test_factory_functions()
    
    # 测试 AGB 云沙箱
    sandbox_test = test_agb_cloud_sandbox()
    
    # 总结
    print("\n📊 测试结果总结")
    print("=" * 30)
    print(f"工厂函数测试: {'✅ 通过' if factory_test else '❌ 失败'}")
    print(f"云沙箱测试: {'✅ 通过' if sandbox_test else '❌ 失败'}")
    
    if factory_test and sandbox_test:
        print("\n🎉 所有测试通过！AGB 云沙箱架构工作正常")
    else:
        print("\n⚠️  部分测试失败，请检查配置")


if __name__ == "__main__":
    main()
