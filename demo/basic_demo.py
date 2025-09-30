import asyncio
import os
from agentscope_runtime.engine import Runner
from agentscope_runtime.engine.agents.llm_agent import LLMAgent
from agentscope_runtime.engine.llms import QwenLLM
from agentscope_runtime.engine.schemas.agent_schemas import AgentRequest
from agentscope_runtime.engine.services.context_manager import ContextManager


async def main():
    # Set up the language model and agent
    model = QwenLLM(
        model_name="qwen-turbo",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
    )
    llm_agent = LLMAgent(model=model, name="llm_agent")

    async with ContextManager() as context_manager:
        runner = Runner(agent=llm_agent, context_manager=context_manager)

        # Create a request and stream the response
        request = AgentRequest(
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What is the capital of France?",
                        },
                    ],
                },
            ],
        )

        async for message in runner.stream_query(request=request):
            if hasattr(message, "text"):
                print(f"Streamed Answer: {message.text}")


asyncio.run(main())