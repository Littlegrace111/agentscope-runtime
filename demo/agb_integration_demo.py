# demo/agbcloud_integration_demo.py
import os
from dotenv import load_dotenv
from agentscope_runtime.sandbox.tools.function_tool import function_tool
from agentscope_runtime.engine import Runner
from agentscope_runtime.engine.agents.llm_agent import LLMAgent
from agentscope_runtime.engine.llms import QwenLLM
from agentscope_runtime.engine.services.context_manager import ContextManager

# 加载 .env 文件
load_dotenv()

# 正确的 AGB Cloud SDK 用法
try:
    from agb import AGB
    from agb.session_params import CreateSessionParams
    AGB_CLOUD_AVAILABLE = True
except ImportError:
    AGB_CLOUD_AVAILABLE = False
    print("⚠️ agbcloud-sdk 未安装，请运行: pip install agbcloud-sdk")

# 创建 AGB Cloud 客户端
if AGB_CLOUD_AVAILABLE:
    try:
        # Initialize the AGB client
        api_key = os.environ.get("AGB_API_KEY", "")
        agb = AGB(api_key=api_key)
    except ValueError as e:
        print(f"⚠️ AGB API Key 未设置: {e}")
        print("请在 .env 文件中设置: AGB_API_KEY=your_api_key")
        AGB_CLOUD_AVAILABLE = False

def agb_code_execution_impl(code: str, language: str = "python") -> str:
    """使用 AGB Cloud SDK 执行代码的实际实现"""
    if not AGB_CLOUD_AVAILABLE:
        return "错误: agbcloud-sdk 未安装或 AGB_API_KEY 未设置"
    
    try:
        # 创建会话参数
        params = CreateSessionParams(image_id="agb-code-space-1")
        result = agb.create(params)
        
        if result.success:
            session = result.session
            # 执行代码
            code_result = session.code.run_code(code, language)
            # 清理会话
            agb.delete(session)
            return f"AGB Cloud 执行结果: {code_result.result}"
        else:
            return f"AGB Cloud 会话创建失败: {result.error_message}"
    except Exception as e:
        return f"AGB Cloud 执行失败: {str(e)}"

@function_tool(
    name="agb_code_execution",
    description="使用 AGB Cloud SDK 执行代码"
)
def agb_code_execution(code: str, language: str = "python") -> str:
    """使用 AGB Cloud SDK 执行代码"""
    return agb_code_execution_impl(code, language)

# 创建智能体并集成工具
model = QwenLLM(
    model_name="qwen-turbo",
    api_key=os.getenv("DASHSCOPE_API_KEY")
)

llm_agent = LLMAgent(
    model=model,
    name="agb_agent",
    description="集成 AGB Cloud SDK 的智能体",
    tools=[agb_code_execution]  # 添加自定义工具
)

# 使用智能体
async def test_agb_integration():
    # 直接测试 AGB Cloud 功能
    print("=== 直接调用 AGB Cloud ===")
    result = agb_code_execution_impl("print('Hello from AGB Cloud!')", "python")
    print(f"AGB Cloud 结果: {result}")
    
    # 通过智能体调用
    print("\n=== 通过智能体调用 AGB Cloud ===")
    async with Runner(agent=llm_agent, context_manager=ContextManager()) as runner:
        from agentscope_runtime.engine.schemas.agent_schemas import AgentRequest
        
        request = AgentRequest(
            input=[{
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": "请使用 AGB Cloud 执行代码: print('Hello from AGB Cloud via Agent!')"
                }]
            }]
        )
        
        async for message in runner.stream_query(request=request):
            if hasattr(message, 'content') and message.content:
                print(f"智能体回复: {message.content[0].text if hasattr(message.content[0], 'text') else message.content[0]}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_agb_integration())