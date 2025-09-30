import os
from contextlib import asynccontextmanager
from agentscope_runtime.engine import Runner
from agentscope_runtime.engine.agents.llm_agent import LLMAgent
from agentscope_runtime.engine.llms import QwenLLM
from agentscope_runtime.engine.schemas.agent_schemas import (
    MessageType,
    RunStatus,
    AgentRequest,
)
from agentscope_runtime.engine.services.context_manager import (
    ContextManager,
)

print("✅ 依赖导入成功")


from agentscope.agent import ReActAgent
from agentscope.model import OpenAIChatModel
from agentscope_runtime.engine.agents.agentscope_agent import AgentScopeAgent


# 创建LLM实例
model = QwenLLM(
    model_name="qwen-turbo",
    api_key=os.getenv("DASHSCOPE_API_KEY")
)

# 创建LLM智能体
llm_agent = LLMAgent(
    model=model,
    name="llm_agent",
    description="A simple LLM agent for text generation",
)

print("✅ LLM智能体创建成功")

agent = AgentScopeAgent(
    name="Friday",
    model=OpenAIChatModel(
        "gpt-4",
        api_key=os.getenv("OPENAI_API_KEY"),
    ),
    agent_config={
        "sys_prompt": "You're a helpful assistant named {name}.",
    },
    agent_builder=ReActAgent,
)

print("✅ AgentScope agent created successfully")


@asynccontextmanager
async def create_runner():
    async with Runner(
        agent=llm_agent,
        context_manager=ContextManager(),
    ) as runner:
        print("✅ Runner创建成功")
        yield runner

async def interact_with_agent(runner):
    # Create a request
    request = AgentRequest(
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "法国的首都是什么？",
                    },
                ],
            },
        ],
    )

    # 流式获取响应
    print("🤖 智能体正在处理您的请求...")
    all_result = ""
    async for message in runner.stream_query(request=request):
        # Check if this is a completed message
        if (
            message.object == "message"
            and MessageType.MESSAGE == message.type
            and RunStatus.Completed == message.status
        ):
            all_result = message.content[0].text

    print(f"📝智能体回复: {all_result}")
    return all_result


async def test_interaction():
    async with create_runner() as runner:
        await interact_with_agent(runner)


from agentscope_runtime.engine.deployers import LocalDeployManager

async def deploy_agent(runner):
    # 创建部署管理器
    deploy_manager = LocalDeployManager(
        host="localhost",
        port=8090,
    )

    # 将智能体部署为流式服务
    deploy_result = await runner.deploy(
        deploy_manager=deploy_manager,
        endpoint_path="/process",
        stream=True,  # Enable streaming responses
    )
    print(f"🚀智能体部署在: {deploy_result}")
    print(f"🌐服务URL: {deploy_manager.service_url}")
    print(f"💚 健康检查: {deploy_manager.service_url}/health")

    return deploy_manager

async def run_deployment():
    async with create_runner() as runner:
        deploy_manager = await deploy_agent(runner)

    # Keep the service running (in production, you'd handle this differently)
    print("🏃 Service is running...")

    return deploy_manager

# Deploy the agent
# To deploy from main, use: asyncio.run(run_deployment())
   

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_deployment())