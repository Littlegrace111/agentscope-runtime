# -*- coding: utf-8 -*-
import os

from agentscope.agent import ReActAgent
from agentscope.model import DashScopeChatModel

from prompts import SYSTEM_PROMPT

# AGB Cloud
from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser import BrowserOption, BrowserViewport

if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv(".env")

from agentscope_runtime.engine.services.redis_session_history_service import (
    RedisSessionHistoryService,
)

from agentscope_runtime.engine import Runner
from agentscope_runtime.engine.agents.agentscope_agent import AgentScopeAgent
from agentscope_runtime.engine.schemas.agent_schemas import (
    RunStatus,
    AgentRequest,
)
from agentscope_runtime.engine.services.context_manager import (
    ContextManager,
)
from agentscope_runtime.engine.services.environment_manager import (
    EnvironmentManager,
)
from agentscope_runtime.engine.services import SandboxService
from agentscope_runtime.engine.services.memory_service import (
    InMemoryMemoryService,
)
from agentscope_runtime.engine.services.session_history_service import (
    InMemorySessionHistoryService,
)
from agentscope_runtime.sandbox.tools.browser import (
    run_shell_command,
    run_ipython_cell,
    browser_close,
    browser_resize,
    browser_console_messages,
    browser_handle_dialog,
    browser_file_upload,
    browser_press_key,
    browser_navigate,
    browser_navigate_back,
    browser_navigate_forward,
    browser_network_requests,
    browser_pdf_save,
    browser_take_screenshot,
    browser_snapshot,
    browser_click,
    browser_drag,
    browser_hover,
    browser_type,
    browser_select_option,
    browser_tab_list,
    browser_tab_new,
    browser_tab_select,
    browser_tab_close,
    browser_wait_for,
)
from agentscope_runtime.sandbox.tools.function_tool import (
    FunctionTool,
    function_tool,
)


if os.path.exists(".env"):
    from dotenv import load_dotenv

    load_dotenv(".env")

SESSION_ID = "session_001"  # Using a fixed ID for simplicity


class AgentscopeBrowseruseAgent:
    def __init__(self, session_id=SESSION_ID, config=None):
        self.tools = [
            run_shell_command,
            run_ipython_cell,
            browser_close,
            browser_resize,
            browser_console_messages,
            browser_handle_dialog,
            browser_file_upload,
            browser_press_key,
            browser_navigate,
            browser_navigate_back,
            browser_navigate_forward,
            browser_network_requests,
            browser_pdf_save,
            browser_take_screenshot,
            browser_snapshot,
            browser_click,
            browser_drag,
            browser_hover,
            browser_type,
            browser_select_option,
            browser_tab_list,
            browser_tab_new,
            browser_tab_select,
            browser_tab_close,
            browser_wait_for,
        ]
        self.config = config
        self.session_id = session_id
        self.user_id = session_id  # use session_id as
        # user_id for simplification
        if self.config["backend"]["agent-type"] == "agentscope":
            self.agent = AgentScopeAgent(
                name="Friday",
                model=DashScopeChatModel(
                    self.config["backend"]["llm-name"],
                    api_key=os.getenv("DASHSCOPE_API_KEY"),
                ),
                agent_config={
                    "sys_prompt": SYSTEM_PROMPT,
                },
                tools=self.tools,
                agent_builder=ReActAgent,
            )
        elif self.config["backend"]["agent-type"] == "agno":
            # add in the future
            raise NotImplementedError(
                'Agent type "agno" is not yet implemented',
            )
        else:
            raise ValueError("Invalid agent type")
        self.ws = ""
        self.runner = None
        self.is_closed = False

    async def connect(self):
        session_history_service = None
        if self.config["backend"]["session-type"] == "redis":
            session_history_service = RedisSessionHistoryService(
                redis_url=self.config["backend"]["session-redis"]["url"],
            )
            await session_history_service.start()
        elif self.config["backend"]["session-type"] == "memory":
            session_history_service = InMemorySessionHistoryService()
            await session_history_service.start()
        else:
            # no session service
            pass

        if session_history_service:
            await session_history_service.create_session(
                user_id=self.user_id,
                session_id=self.session_id,
            )

        mem_service = None
        if self.config["backend"]["memory-type"] == "redis":
            mem_service = RedisSessionHistoryService(
                redis_url=self.config["backend"]["memory-redis"]["url"],
            )
            await mem_service.start()
        elif self.config["backend"]["memory-type"] == "memory":
            mem_service = InMemoryMemoryService()
            await mem_service.start()
        else:
            # no memory service
            pass

        # initialize context/environment managers
        self.context_manager = ContextManager(
            memory_service=mem_service,
            session_history_service=session_history_service,
        )
        self.environment_manager = EnvironmentManager()

        # Initialize AGB session and browser instead of sandbox browser
        agb = AGB()  # uses AGB_API_KEY from env
        params = CreateSessionParams(image_id=self.config["backend"].get("agb-image-id", "agb-browser-use-1"))
        result = agb.create(params)
        if not result.success:
            raise RuntimeError(f"Failed to create AGB session: {result.error_message}")
        session = result.session

        # Configure and initialize browser
        option = BrowserOption(
            use_stealth=True,
            viewport=BrowserViewport(width=1366, height=768),
        )
        success = session.browser.initialize(option)
        if not success:
            agb.delete(session)
            raise RuntimeError("Failed to initialize AGB browser")

        # Save for later cleanup; set CDP endpoint
        self._agb = agb
        self._agb_session = session
        self.ws = session.browser.get_endpoint_url()
        # Also expose resource_url for iframe rendering
        try:
            info = session.get_info() if hasattr(session, "get_info") else None
            self.resource_url = getattr(session, "resource_url", None) or (
                info.get("resource_url") if isinstance(info, dict) else None
            )
        except Exception:
            self.resource_url = None

        # -------- AGB Tools (Scheme A): expose minimal tool for model usage --------
        @function_tool(
            name="agb_get_browser_info",
            description="Get current AGB browser connection info (CDP endpoint and resource_url).",
        )
        def agb_get_browser_info() -> dict:
            return {
                "endpoint": self.ws or "",
                "resource_url": self.resource_url or "",
            }

        # Attach AGB tool to agent
        self.tools.append(agb_get_browser_info)
        if hasattr(self, "agent") and hasattr(self.agent, "tools"):
            try:
                self.agent.tools = self.tools
            except Exception:
                pass
        # -------------------------------------------------------------------------

        runner = Runner(
            agent=self.agent,
            context_manager=self.context_manager,
            environment_manager=self.environment_manager,
        )
        self.runner = runner
        self.is_closed = False

    async def chat(self, chat_messages):
        convert_messages = []
        for chat_message in chat_messages:
            convert_messages.append(
                {
                    "role": chat_message["role"],
                    "content": [
                        {
                            "type": "text",
                            "text": chat_message["content"],
                        },
                    ],
                },
            )
        request = AgentRequest(
            input=convert_messages,
            session_id=self.session_id,
        )
        request.tools = []
        async for message in self.runner.stream_query(
            user_id=self.user_id,
            request=request,
        ):
            if (
                message.object == "message"
                and RunStatus.Completed == message.status
            ):
                yield message.content

    async def close(self):
        if self.is_closed:
            return
        # Cleanup AGB session if exists
        try:
            if hasattr(self, "_agb") and hasattr(self, "_agb_session") and self._agb_session:
                self._agb.delete(self._agb_session)
        except Exception:
            pass
        self.ws = ""
        self.is_closed = True
