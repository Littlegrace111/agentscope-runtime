# -*- coding: utf-8 -*-
"""
AgentBay Browser sandbox implementation.
"""
import asyncio
import logging
import time
from typing import Any, Dict, Optional

from agentbay.browser.browser import BrowserOption  # type: ignore
from agentbay.browser.browser_agent import ActOptions  # type: ignore
from agentbay.browser.browser_agent import ExtractOptions, ObserveOptions

from ...enums import SandboxType
from ...registry import SandboxRegistry
from .agentbay_sandbox_base import AgentbaySandboxBase

logger = logging.getLogger(__name__)


@SandboxRegistry.register(
    "agentbay-browser",
    sandbox_type="agentbay_browser",
    security_level="high",
    timeout=300,
    description="AgentBay Browser Sandbox Environment",
)
class AgentbayBrowserSandbox(AgentbaySandboxBase):
    """
    AgentBay Browser sandbox implementation.

    Supports browser automation operations:
    - Browser navigation
    - Page interaction (click, input)
    - PageUseAgent (AI-powered automation)
    - File operations
    """

    def __init__(
        self,
        sandbox_id: Optional[str] = None,
        timeout: int = 3000,
        base_url: Optional[str] = None,
        bearer_token: Optional[str] = None,
        api_key: Optional[str] = None,
        image_id: str = "browser_latest",
        labels: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        """Initialize the AgentBay Browser sandbox."""
        super().__init__(
            sandbox_id=sandbox_id,
            timeout=timeout,
            base_url=base_url,
            bearer_token=bearer_token,
            sandbox_type=SandboxType.AGENTBAY,
            api_key=api_key,
            image_id=image_id,
            labels=labels,
            **kwargs,
        )

    def _get_tool_mapping(self) -> Dict[str, Any]:
        """Get tool mapping for Browser sandbox."""
        return {
            "read_file": self._read_file,
            "write_file": self._write_file,
            "list_directory": self._list_directory,
            "browser_navigate": self._browser_navigate,
            "browser_click": self._browser_click,
            "browser_input": self._browser_input,
            "browser_agent_navigate": self._browser_agent_navigate,
            "browser_agent_act": self._browser_agent_act,
            "browser_agent_extract": self._browser_agent_extract,
            "browser_agent_observe": self._browser_agent_observe,
            "browser_screenshot": self._browser_screenshot,
        }

    def _read_file(self, session, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Read a file from AgentBay."""
        path = arguments.get("path", "")
        result = session.file_system.read_file(path)

        return {
            "success": result.success,
            "content": result.content if hasattr(result, "content") else None,
            "error": result.error if hasattr(result, "error") else None,
        }

    def _write_file(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Write a file to AgentBay."""
        path = arguments.get("path", "")
        content = arguments.get("content", "")
        result = session.file_system.write_file(path, content)

        return {
            "success": result.success,
            "error": result.error if hasattr(result, "error") else None,
        }

    def _list_directory(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """List directory contents in AgentBay."""
        path = arguments.get("path", ".")
        result = session.file_system.list_directory(path)

        return {
            "success": result.success,
            "files": result.files if hasattr(result, "files") else [],
            "error": result.error if hasattr(result, "error") else None,
        }

    def _ensure_browser_initialized(self, session) -> bool:
        """Ensure browser is initialized before use."""
        try:
            # Check if browser is already initialized using is_initialized()
            if hasattr(session.browser, "is_initialized"):
                if session.browser.is_initialized():
                    return True
            elif hasattr(session.browser, "agent"):
                # Fallback: try to access agent to check if it's available
                try:
                    _ = session.browser.agent
                    return True
                except (AttributeError, RuntimeError):
                    pass

            # Initialize browser if not already initialized
            browser_option = BrowserOption()
            # Use asyncio to run async initialization in sync context
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if loop.is_running():
                # If loop is running, we can't use it synchronously
                # Try sync initialization if available
                if hasattr(session.browser, "initialize"):
                    result = session.browser.initialize(browser_option)
                    if result:
                        # Wait a bit for browser to be ready
                        time.sleep(1)
                        return True
                return False

            # Run async initialization
            result = loop.run_until_complete(
                session.browser.initialize_async(browser_option),
            )
            if result:
                # Wait a bit for browser to be ready
                time.sleep(1)
            return result
        except (RuntimeError, ValueError, AttributeError, TypeError) as e:
            # Log the error for debugging
            logger.error("Error ensuring browser initialized: %s", e)
            return False

    def _browser_navigate(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Navigate browser in AgentBay."""
        url = arguments.get("url", "")

        # Early validation
        if not self._ensure_browser_initialized(session):
            return {
                "success": False,
                "error": "Failed to initialize browser",
            }

        browser = getattr(session, "browser", None)
        if not browser:
            return {
                "success": False,
                "error": "Browser session not available",
            }

        # Get navigation result
        result = self._get_navigation_result(browser, url)
        if result is None:
            return {
                "success": False,
                "error": "Browser navigation tool not available",
            }

        # Process result
        return self._process_navigation_result(result)

    def _get_navigation_result(self, browser, url: str) -> Any:
        """Get navigation result from browser."""
        if hasattr(browser, "browser_navigate"):
            return browser.browser_navigate(url)
        if hasattr(browser, "call_tool"):
            return browser.call_tool(
                "browser_navigate",
                {"url": url},
            )
        return None

    def _process_navigation_result(self, result: Any) -> Dict[str, Any]:
        """Process navigation result and return standardized response."""
        try:
            if isinstance(result, dict):
                success = result.get("success", True)
                if success:
                    return {
                        "success": True,
                        "message": result.get("message", "Navigation success"),
                    }
                return {
                    "success": False,
                    "error": result.get("error", "Navigation failed"),
                }

            return {
                "success": True,
                "message": str(result),
            }
        except (RuntimeError, ValueError, TypeError, AttributeError) as e:
            return {
                "success": False,
                "error": f"Error navigating browser: {str(e)}",
            }

    def _browser_click(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Click element in browser using act method."""
        selector = arguments.get("selector", "")
        try:
            # Ensure browser is initialized
            if not self._ensure_browser_initialized(session):
                return {
                    "success": False,
                    "error": "Failed to initialize browser",
                }

            agent = session.browser.agent
            # BrowserAgent doesn't have click method, use act instead
            action = f"Click on the element with selector: {selector}"
            # Try async method first, fallback to sync
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    result = agent.act(ActOptions(action=action))
                else:
                    result = loop.run_until_complete(
                        agent.act_async(
                            action_input=ActOptions(action=action),
                        ),
                    )
            except (RuntimeError, AttributeError):
                result = agent.act(ActOptions(action=action))

            return {
                "success": (
                    result.success if hasattr(result, "success") else True
                ),
                "message": (
                    result.message
                    if hasattr(result, "message")
                    else str(result)
                ),
                "error": (result.error if hasattr(result, "error") else None),
            }
        except (RuntimeError, ValueError, TypeError, AttributeError) as e:
            return {
                "success": False,
                "error": f"Error clicking element: {str(e)}",
            }

    def _browser_input(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Input text in browser using act method."""
        selector = arguments.get("selector", "")
        text = arguments.get("text", "")
        try:
            # Ensure browser is initialized
            if not self._ensure_browser_initialized(session):
                return {
                    "success": False,
                    "error": "Failed to initialize browser",
                }

            agent = session.browser.agent
            # BrowserAgent doesn't have input_text method, use act instead
            action = (
                f"Type '{text}' into the element with selector: {selector}"
            )
            # Try async method first, fallback to sync
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    result = agent.act(ActOptions(action=action))
                else:
                    result = loop.run_until_complete(
                        agent.act_async(
                            action_input=ActOptions(action=action),
                        ),
                    )
            except (RuntimeError, AttributeError):
                result = agent.act(ActOptions(action=action))

            return {
                "success": (
                    result.success if hasattr(result, "success") else True
                ),
                "message": (
                    result.message
                    if hasattr(result, "message")
                    else str(result)
                ),
                "error": (result.error if hasattr(result, "error") else None),
            }
        except (RuntimeError, ValueError, TypeError, AttributeError) as e:
            return {
                "success": False,
                "error": f"Error inputting text: {str(e)}",
            }

    def _browser_agent_navigate(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Navigate using BrowserAgent."""
        url = arguments.get("url", "")
        try:
            # Ensure browser is initialized
            if not self._ensure_browser_initialized(session):
                return {
                    "success": False,
                    "error": "Failed to initialize browser",
                }

            agent = session.browser.agent
            # Try async method first, fallback to sync
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Can't use async in running loop, try sync
                    if hasattr(agent, "navigate"):
                        result = agent.navigate(url)
                    else:
                        return {
                            "success": False,
                            "error": "BrowserAgent.navigate not available",
                        }
                else:
                    # Use async method
                    result = loop.run_until_complete(agent.navigate_async(url))
            except (RuntimeError, AttributeError):
                # Fallback to sync method
                if hasattr(agent, "navigate"):
                    result = agent.navigate(url)
                else:
                    return {
                        "success": False,
                        "error": "BrowserAgent.navigate not available",
                    }

            return {
                "success": True,
                "message": result if isinstance(result, str) else str(result),
            }
        except (RuntimeError, ValueError, TypeError, AttributeError) as e:
            return {
                "success": False,
                "error": f"Error navigating browser: {str(e)}",
            }

    def _browser_agent_act(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Perform action using BrowserAgent."""
        action = arguments.get("action", "")
        result = session.browser.agent.act(ActOptions(action=action))
        return {
            "success": result.success if hasattr(result, "success") else True,
            "message": (
                result.message if hasattr(result, "message") else str(result)
            ),
            "error": result.error if hasattr(result, "error") else None,
        }

    def _browser_agent_extract(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Extract data using BrowserAgent."""
        # This is a simplified version - full implementation would need schema
        instruction = arguments.get("instruction", "")
        result = session.browser.agent.extract(
            ExtractOptions(instruction=instruction, schema=None),
        )
        return {
            "success": result[0] if isinstance(result, tuple) else True,
            "data": result[1] if isinstance(result, tuple) else result,
        }

    def _browser_agent_observe(
        self,
        session,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Observe page using BrowserAgent."""
        instruction = arguments.get("instruction", "")
        result = session.browser.agent.observe(
            ObserveOptions(instruction=instruction),
        )
        return {
            "success": result[0] if isinstance(result, tuple) else True,
            "results": result[1] if isinstance(result, tuple) else result,
        }

    def _browser_screenshot(
        self,
        session,
        arguments: Dict[str, Any],  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        """Take browser screenshot."""
        result = session.browser.agent.screenshot()
        return {
            "success": True,
            "screenshot": result,
        }

    def list_tools(self, tool_type: Optional[str] = None) -> Dict[str, Any]:
        """List available tools in the Browser sandbox."""
        file_tools = ["read_file", "write_file", "list_directory"]
        browser_tools = [
            "browser_navigate",
            "browser_click",
            "browser_input",
        ]
        agent_tools = [
            "browser_agent_navigate",
            "browser_agent_act",
            "browser_agent_extract",
            "browser_agent_observe",
            "browser_screenshot",
        ]

        tools_by_type = {
            "file": file_tools,
            "browser": browser_tools,
            "agent": agent_tools,
        }

        if tool_type:
            tools = tools_by_type.get(tool_type, [])
            return {
                "tools": tools,
                "tool_type": tool_type,
                "sandbox_id": self._sandbox_id,
                "total_count": len(tools),
            }

        all_tools = file_tools + browser_tools + agent_tools
        return {
            "tools": all_tools,
            "tools_by_type": tools_by_type,
            "sandbox_id": self._sandbox_id,
            "total_count": len(all_tools),
        }
