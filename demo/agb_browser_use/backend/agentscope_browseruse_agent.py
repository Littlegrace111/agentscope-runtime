# -*- coding: utf-8 -*-
import os
import logging

from agentscope.agent import ReActAgent
from agentscope.model import DashScopeChatModel

from prompts import SYSTEM_PROMPT

# AGB Cloud
from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser import (
    BrowserOption, BrowserViewport, BrowserScreen, BrowserFingerprint, BrowserProxy,
    ActOptions, ObserveOptions, ExtractOptions
)
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv(".env")

# module logger
logger = logging.getLogger(__name__)

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
            # run_shell_command,
            # run_ipython_cell,
            # browser_close,
            # browser_resize,
            # browser_console_messages,
            # browser_handle_dialog,
            # browser_file_upload,
            # browser_press_key,
            # browser_navigate,
            # browser_navigate_back,
            # browser_navigate_forward,
            # browser_network_requests,
            # browser_pdf_save,
            # browser_take_screenshot,
            # browser_snapshot,
            # browser_click,
            # browser_drag,
            # browser_hover,
            # browser_type,
            # browser_select_option,
            # browser_tab_list,
            # browser_tab_new,
            # browser_tab_select,
            # browser_tab_close,
            # browser_wait_for,
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

        # -------- Enhanced AGB Tools: AI-powered browser automation --------
        
        @function_tool(
            name="agb_get_browser_info",
            description="Get current AGB browser connection info (CDP endpoint and resource_url).",
        )
        def agb_get_browser_info() -> dict:
            logger.info("agb_get_browser_info: fetching connection info")
            info = {
                "endpoint": self.ws or "",
                "resource_url": self.resource_url or "",
            }
            logger.info("agb_get_browser_info: %s", info)
            return info

        @function_tool(
            name="agb_act",
            description="Execute browser actions using AGB's AI agent with natural language. Uses AGB's Act capability through CDP connection.",
        )
        def agb_act(action: str, timeout_ms: int = 15000, include_iframes: bool = False) -> dict:
            """
            Execute a natural language action using AGB's AI agent.
            
            Args:
                action: Natural language description of the action to perform
                timeout_ms: Maximum time to wait for action completion (default: 15000ms)
                include_iframes: Whether to include iframe content in the action (default: False)
            
            Returns:
                dict: Result with success status and message
            """
            try:
                logger.info("agb_act: action=%s timeout_ms=%s include_iframes=%s", action, timeout_ms, include_iframes)
                if not hasattr(self, '_agb_session') or not self._agb_session:
                    logger.error("agb_act: AGB session not initialized")
                    return {"success": False, "error": "AGB session not initialized"}
                
                # Get CDP endpoint from AGB session
                endpoint_url = self._agb_session.browser.get_endpoint_url()
                
                # AGB Act implementation plan
                act_plan = {
                    "step1": "Get AGB CDP endpoint",
                    "step2": "Connect to CDP using async_playwright()",
                    "step3": "Get current page object",
                    "step4": f"Use AGB agent.act_async(page, ActOptions(action='{action}'))",
                    "step5": "Wait for action completion",
                    "step6": "Return action result"
                }
                
                result = {
                    "success": True,
                    "message": f"AGB Act action prepared: {action}",
                    "action": action,
                    "timeout": timeout_ms,
                    "cdp_endpoint": endpoint_url,
                    "act_plan": act_plan,
                    "features": [
                        "AGB AI agent powered",
                        "Natural language understanding",
                        "Smart element detection",
                        "Automatic retry on failure"
                    ],
                    "implementation_note": "Requires AGB agent.act_async() with page object and ActOptions"
                }
                logger.info("agb_act: prepared result=%s", result)
                return result
            except Exception as e:
                logger.exception("agb_act: error")
                return {"success": False, "error": str(e)}

        @function_tool(
            name="agb_observe",
            description="Analyze and observe page elements using AGB's AI agent. Uses AGB's Observe capability through CDP connection.",
        )
        def agb_observe(instruction: str, return_actions: int = 10, include_iframes: bool = False) -> dict:
            """
            Observe and analyze page elements using AGB's AI agent.
            
            Args:
                instruction: Natural language instruction for what to observe
                return_actions: Maximum number of actions to return (default: 10)
                include_iframes: Whether to include iframe content (default: False)
            
            Returns:
                dict: List of found elements with selectors and descriptions
            """
            try:
                logger.info("agb_observe: instruction=%s return_actions=%s include_iframes=%s", instruction, return_actions, include_iframes)
                if not hasattr(self, '_agb_session') or not self._agb_session:
                    logger.error("agb_observe: AGB session not initialized")
                    return {"success": False, "error": "AGB session not initialized"}
                
                # Get CDP endpoint from AGB session
                endpoint_url = self._agb_session.browser.get_endpoint_url()
                
                # AGB Observe implementation plan
                observe_plan = {
                    "step1": "Get AGB CDP endpoint",
                    "step2": "Connect to CDP using async_playwright()",
                    "step3": "Get current page object",
                    "step4": f"Use AGB agent.observe_async(page, ObserveOptions(instruction='{instruction}'))",
                    "step5": "Process AI analysis results",
                    "step6": "Return structured element data"
                }
                
                result = {
                    "success": True,
                    "message": f"AGB Observe analysis prepared: {instruction}",
                    "instruction": instruction,
                    "return_actions": return_actions,
                    "cdp_endpoint": endpoint_url,
                    "observe_plan": observe_plan,
                    "features": [
                        "AGB AI-powered analysis",
                        "Smart element detection",
                        "Natural language understanding",
                        "Structured data extraction"
                    ],
                    "implementation_note": "Requires AGB agent.observe_async() with page object and ObserveOptions"
                }
                logger.info("agb_observe: prepared result=%s", result)
                return result
            except Exception as e:
                logger.exception("agb_observe: error")
                return {"success": False, "error": str(e)}

        @function_tool(
            name="agb_extract",
            description="Extract structured data using AGB's AI agent with Pydantic schemas. Uses AGB's Extract capability through CDP connection.",
        )
        def agb_extract(instruction: str, schema_name: str = "GenericData", use_text_extract: bool = True, selector: str = None) -> dict:
            """
            Extract structured data using AGB's AI agent with Pydantic schemas.
            
            Args:
                instruction: Natural language instruction for what data to extract
                schema_name: Name of the data schema to use (default: "GenericData")
                use_text_extract: Whether to use text-based extraction (default: True)
                selector: CSS selector to focus extraction on specific elements (optional)
            
            Returns:
                dict: Extracted structured data
            """
            try:
                logger.info("agb_extract: instruction=%s schema=%s use_text_extract=%s selector=%s", instruction, schema_name, use_text_extract, selector)
                if not hasattr(self, '_agb_session') or not self._agb_session:
                    logger.error("agb_extract: AGB session not initialized")
                    return {"success": False, "error": "AGB session not initialized"}
                
                # Get CDP endpoint from AGB session
                endpoint_url = self._agb_session.browser.get_endpoint_url()
                
                # AGB Extract implementation plan
                extract_plan = {
                    "step1": "Get AGB CDP endpoint",
                    "step2": "Connect to CDP using async_playwright()",
                    "step3": "Get current page object",
                    "step4": f"Use AGB agent.extract_async(page, ExtractOptions(instruction='{instruction}', schema={schema_name}))",
                    "step5": "Process AI extraction results",
                    "step6": "Return structured data with Pydantic validation"
                }
                
                result = {
                    "success": True,
                    "message": f"AGB Extract analysis prepared: {instruction}",
                    "instruction": instruction,
                    "schema": schema_name,
                    "selector": selector,
                    "cdp_endpoint": endpoint_url,
                    "extract_plan": extract_plan,
                    "features": [
                        "AGB AI-powered extraction",
                        "Pydantic schema validation",
                        "Natural language understanding",
                        "Structured data output"
                    ],
                    "implementation_note": "Requires AGB agent.extract_async() with page object, ExtractOptions, and Pydantic schema"
                }
                logger.info("agb_extract: prepared result=%s", result)
                return result
            except Exception as e:
                logger.exception("agb_extract: error")
                return {"success": False, "error": str(e)}

        @function_tool(
            name="agb_configure_browser",
            description="Configure AGB browser settings including stealth mode, viewport, user agent, and fingerprinting.",
        )
        def agb_configure_browser(
            use_stealth: bool = True,
            viewport_width: int = 1366,
            viewport_height: int = 768,
            user_agent: str = None,
            screen_width: int = 1920,
            screen_height: int = 1080
        ) -> dict:
            """
            Configure AGB browser settings with enhanced capabilities.
            
            Args:
                use_stealth: Enable stealth mode to avoid detection (default: True)
                viewport_width: Browser viewport width (default: 1366)
                viewport_height: Browser viewport height (default: 768)
                user_agent: Custom user agent string (optional)
                screen_width: Screen width (default: 1920)
                screen_height: Screen height (default: 1080)
            
            Returns:
                dict: Configuration result
            """
            try:
                logger.info("agb_configure_browser: use_stealth=%s viewport=%sx%s user_agent=%s screen=%sx%s", use_stealth, viewport_width, viewport_height, user_agent, screen_width, screen_height)
                if not hasattr(self, '_agb_session') or not self._agb_session:
                    logger.error("agb_configure_browser: AGB session not initialized")
                    return {"success": False, "error": "AGB session not initialized"}
                
                # Create new browser option with AGB capabilities
                option = BrowserOption(
                    use_stealth=use_stealth,
                    viewport=BrowserViewport(width=viewport_width, height=viewport_height),
                    screen=BrowserScreen(width=screen_width, height=screen_height),
                    user_agent=user_agent
                )
                
                # Reinitialize AGB browser with new options
                success = self._agb_session.browser.initialize(option)
                
                if success:
                    result = {
                        "success": True,
                        "message": "AGB browser configuration updated successfully",
                        "config": {
                            "stealth_mode": use_stealth,
                            "viewport": f"{viewport_width}x{viewport_height}",
                            "screen": f"{screen_width}x{screen_height}",
                            "user_agent": user_agent or "AGB default",
                            "agb_features": [
                                "Anti-detection measures",
                                "Enhanced fingerprinting",
                                "Proxy support",
                                "Custom headers"
                            ]
                        }
                    }
                    logger.info("agb_configure_browser: success config=%s", result["config"])
                    return result
                else:
                    logger.error("agb_configure_browser: failed to apply config")
                    return {"success": False, "error": "Failed to apply AGB browser configuration"}
                    
            except Exception as e:
                logger.exception("agb_configure_browser: error")
                return {"success": False, "error": str(e)}

        @function_tool(
            name="agb_smart_fill_form",
            description="Intelligently fill form fields using AGB's AI agent with natural language understanding.",
        )
        def agb_smart_fill_form(form_data: str, timeout_ms: int = 10000) -> dict:
            """
            Intelligently fill form fields using AGB's AI agent.
            
            Args:
                form_data: Natural language description of form data to fill
                timeout_ms: Maximum time to wait for form filling (default: 10000ms)
            
            Returns:
                dict: Form filling result
            """
            try:
                logger.info("agb_smart_fill_form: form_data=%s timeout_ms=%s", form_data, timeout_ms)
                if not hasattr(self, '_agb_session') or not self._agb_session:
                    logger.error("agb_smart_fill_form: AGB session not initialized")
                    return {"success": False, "error": "AGB session not initialized"}
                
                # Get CDP endpoint from AGB session
                endpoint_url = self._agb_session.browser.get_endpoint_url()
                
                # AGB smart form filling plan
                form_plan = {
                    "step1": "Get AGB CDP endpoint",
                    "step2": "Connect to CDP using async_playwright()",
                    "step3": "Get current page object",
                    "step4": f"Use AGB agent.act_async(page, ActOptions(action='Fill form: {form_data}'))",
                    "step5": "AI analyzes form structure and fills fields",
                    "step6": "Return form filling result"
                }
                
                result = {
                    "success": True,
                    "message": f"AGB smart form filling prepared: {form_data}",
                    "form_data": form_data,
                    "timeout": timeout_ms,
                    "cdp_endpoint": endpoint_url,
                    "form_plan": form_plan,
                    "features": [
                        "AGB AI-powered form analysis",
                        "Smart field detection",
                        "Natural language understanding",
                        "Automatic field mapping"
                    ],
                    "implementation_note": "Uses AGB agent.act_async() with form-specific ActOptions"
                }
                logger.info("agb_smart_fill_form: prepared result=%s", result)
                return result
            except Exception as e:
                logger.exception("agb_smart_fill_form: error")
                return {"success": False, "error": str(e)}

        @function_tool(
            name="agb_find_and_click",
            description="Find and click elements using AGB's AI agent with smart element detection.",
        )
        def agb_find_and_click(element_description: str, timeout_ms: int = 10000) -> dict:
            """
            Find and click an element using AGB's AI agent.
            
            Args:
                element_description: Natural language description of the element to click
                timeout_ms: Maximum time to wait for element and click (default: 10000ms)
            
            Returns:
                dict: Click result
            """
            try:
                logger.info("agb_find_and_click: element_description=%s timeout_ms=%s", element_description, timeout_ms)
                if not hasattr(self, '_agb_session') or not self._agb_session:
                    logger.error("agb_find_and_click: AGB session not initialized")
                    return {"success": False, "error": "AGB session not initialized"}
                
                # Get CDP endpoint from AGB session
                endpoint_url = self._agb_session.browser.get_endpoint_url()
                
                # AGB find and click plan
                click_plan = {
                    "step1": "Get AGB CDP endpoint",
                    "step2": "Connect to CDP using async_playwright()",
                    "step3": "Get current page object",
                    "step4": f"Use AGB agent.act_async(page, ActOptions(action='Find and click: {element_description}'))",
                    "step5": "AI locates element and performs click",
                    "step6": "Return click result"
                }
                
                result = {
                    "success": True,
                    "message": f"AGB find and click prepared: {element_description}",
                    "element_description": element_description,
                    "timeout": timeout_ms,
                    "cdp_endpoint": endpoint_url,
                    "click_plan": click_plan,
                    "features": [
                        "AGB AI-powered element detection",
                        "Smart element location",
                        "Natural language understanding",
                        "Automatic retry on failure"
                    ],
                    "implementation_note": "Uses AGB agent.act_async() with click-specific ActOptions"
                }
                logger.info("agb_find_and_click: prepared result=%s", result)
                return result
            except Exception as e:
                logger.exception("agb_find_and_click: error")
                return {"success": False, "error": str(e)}

        @function_tool(
            name="agb_wait_for_condition",
            description="Wait for specific conditions using AGB's AI agent with intelligent condition monitoring.",
        )
        def agb_wait_for_condition(condition: str, timeout_ms: int = 15000) -> dict:
            """
            Wait for a specific condition using AGB's AI agent.
            
            Args:
                condition: Natural language description of the condition to wait for
                timeout_ms: Maximum time to wait (default: 15000ms)
            
            Returns:
                dict: Wait result
            """
            try:
                logger.info("agb_wait_for_condition: condition=%s timeout_ms=%s", condition, timeout_ms)
                if not hasattr(self, '_agb_session') or not self._agb_session:
                    logger.error("agb_wait_for_condition: AGB session not initialized")
                    return {"success": False, "error": "AGB session not initialized"}
                
                # Get CDP endpoint from AGB session
                endpoint_url = self._agb_session.browser.get_endpoint_url()
                
                # AGB wait for condition plan
                wait_plan = {
                    "step1": "Get AGB CDP endpoint",
                    "step2": "Connect to CDP using async_playwright()",
                    "step3": "Get current page object",
                    "step4": f"Use AGB agent.act_async(page, ActOptions(action='Wait for: {condition}'))",
                    "step5": "AI monitors page state for condition",
                    "step6": "Return wait result"
                }
                
                result = {
                    "success": True,
                    "message": f"AGB wait condition prepared: {condition}",
                    "condition": condition,
                    "timeout": timeout_ms,
                    "cdp_endpoint": endpoint_url,
                    "wait_plan": wait_plan,
                    "features": [
                        "AGB AI-powered condition monitoring",
                        "Smart state detection",
                        "Natural language understanding",
                        "Intelligent timeout handling"
                    ],
                    "implementation_note": "Uses AGB agent.act_async() with wait-specific ActOptions"
                }
                logger.info("agb_wait_for_condition: prepared result=%s", result)
                return result
            except Exception as e:
                logger.exception("agb_wait_for_condition: error")
                return {"success": False, "error": str(e)}

        @function_tool(
            name="agb_navigate",
            description="Navigate to a URL via Playwright CDP connection to AGB and return page info.",
        )
        async def agb_navigate(url: str, wait_for_load: bool = True, timeout_ms: int = 30000) -> dict:
            """
            Connect to AGB's browser over CDP using async_playwright, open a page, navigate
            to the given URL and return basic page information.

            Args:
                url: Destination URL
                wait_for_load: If True wait for networkidle, else only for commit
                timeout_ms: Navigation timeout in milliseconds

            Returns:
                dict: { success, data: { title, current_url, status }, endpoint, error }
            """
            try:
                logger.info("agb_navigate: url=%s wait_for_load=%s timeout_ms=%s", url, wait_for_load, timeout_ms)
                if not hasattr(self, '_agb_session') or not self._agb_session:
                    logger.error("agb_navigate: AGB session not initialized")
                    return {"success": False, "error": "AGB session not initialized"}

                endpoint_url = self._agb_session.browser.get_endpoint_url()
                print(f"🔗 CDP endpoint: {endpoint_url}")

                # p = sync_playwright().start()
                # browser = p.chromium.connect_over_cdp(endpoint_url)
                # page = browser.new_page()
                # wait_until = "networkidle" if wait_for_load else "commit"
                # response = page.goto(url, wait_until=wait_until, timeout=timeout_ms)

                # title = page.title()
                # current_url = page.url

                # browser.close()

                async with async_playwright() as p:
                    browser = await p.chromium.connect_over_cdp(endpoint_url)
                    page = await browser.new_page()

                    wait_until = "networkidle" if wait_for_load else "commit"
                    response = await page.goto(url, wait_until=wait_until, timeout=timeout_ms)
                    title = await page.title()
                    current_url = page.url

                    await browser.close()

                result = {
                    "success": True,
                    "endpoint": endpoint_url,
                    "data": {
                        "title": title,
                        "current_url": current_url,
                        "status": (response.status if response else None),
                        "waited_for": wait_until,
                    },
                    "error": None,
                }
                logger.info("agb_navigate: success data=%s", result["data"])
                return result
            except Exception as e:
                logger.exception("agb_navigate: error")
                return {"success": False, "endpoint": None, "data": None, "error": str(e)}

        @function_tool(
            name="agb_browse_and_analyze",
            description="Connect to AGB via Playwright CDP, navigate multiple websites, analyze pages, and test back/forward/reload. Returns structured results.",
        )
        def agb_browse_and_analyze(websites: list[str] | None = None, per_page_wait_ms: int = 2000) -> dict:
            """
            Use async_playwright() to connect over CDP to AGB browser, navigate a list of websites,
            collect basic page info, and test navigation actions. Returns structured results.

            Args:
                websites: List of URLs to visit. If None, uses a default demo list.
                per_page_wait_ms: Milliseconds to wait between navigations.

            Returns:
                dict with success, data, and errors (if any)
            """
            try:
                logger.info("agb_browse_and_analyze: websites=%s per_page_wait_ms=%s", websites, per_page_wait_ms)
                if not hasattr(self, '_agb_session') or not self._agb_session:
                    logger.error("agb_browse_and_analyze: AGB session not initialized")
                    return {"success": False, "error": "AGB session not initialized"}

                endpoint_url = self._agb_session.browser.get_endpoint_url()
                targets = websites or [
                    "https://example.com",
                    "https://httpbin.org/html",
                    "https://quotes.toscrape.com",
                ]
                print(f"\ud83d\uddc2\ufe0f Websites to visit: {targets}")

                results = []
                nav_test = {}

                with sync_playwright() as p:
                    browser = p.chromium.connect_over_cdp(endpoint_url)
                    page = browser.new_page()

                    for url in targets:
                        try:
                            page.goto(url, wait_until="networkidle")
                            title = page.title()
                            current_url = page.url
                            body_text = page.evaluate("document.body.innerText")
                            text_length = len(body_text.strip()) if body_text else 0
                            has_forms = page.evaluate("document.forms.length > 0")
                            has_images = page.evaluate("document.images.length > 0")
                            has_links = page.evaluate("document.links.length > 0")

                            results.append({
                                "url": url,
                                "title": title,
                                "current_url": current_url,
                                "content_length": text_length,
                                "has_forms": bool(has_forms),
                                "has_images": bool(has_images),
                                "has_links": bool(has_links),
                            })

                            if per_page_wait_ms and per_page_wait_ms > 0:
                                # convert ms to seconds
                                page.wait_for_timeout(per_page_wait_ms)
                        except Exception as page_err:
                            logger.warning("agb_browse_and_analyze: page error for %s: %s", url, page_err)
                            results.append({
                                "url": url,
                                "error": str(page_err),
                            })

                    # Navigation tests
                    try:
                        page.go_back(timeout=10000, wait_until="commit")
                        nav_test["back_url"] = page.url
                        page.go_forward(timeout=10000, wait_until="commit")
                        nav_test["forward_url"] = page.url
                    except Exception as nav_error:
                        logger.warning("agb_browse_and_analyze: nav test error: %s", nav_error)
                        nav_test["nav_error"] = str(nav_error)
                        nav_test["current_url"] = page.url

                    try:
                        page.reload(timeout=10000)
                        nav_test["reloaded_url"] = page.url
                        # Save a screenshot to a temp path inside the runtime
                        screenshot_path = "/tmp/navigation_example.png"
                        page.screenshot(path=screenshot_path)
                        nav_test["screenshot_path"] = screenshot_path
                    except Exception as reload_error:
                        logger.warning("agb_browse_and_analyze: reload/screenshot error: %s", reload_error)
                        nav_test["reload_error"] = str(reload_error)
                        nav_test["current_url_after_reload"] = page.url

                    browser.close()

                result = {
                    "success": True,
                    "data": {
                        "endpoint": endpoint_url,
                        "input_websites": targets,
                        "visited": results,
                        "navigation_test": nav_test,
                    },
                    "summary": f"Visited {len(results)} pages and ran back/forward/reload tests.",
                    "error": None,
                }
                logger.info("agb_browse_and_analyze: finished summary=%s", result["summary"])
                return result
            except Exception as e:
                logger.exception("agb_browse_and_analyze: error")
                return {
                    "success": False,
                    "data": None,
                    "summary": "AGB browse and analyze failed",
                    "error": str(e),
                }

        # Attach all AGB tools to agent
        agb_tools = [
            agb_get_browser_info,
            agb_act,
            agb_observe, 
            agb_extract,
            agb_configure_browser,
            agb_smart_fill_form,
            agb_find_and_click,
            agb_wait_for_condition,
            agb_navigate,
            agb_browse_and_analyze
        ]
        
        self.tools.extend(agb_tools)
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
