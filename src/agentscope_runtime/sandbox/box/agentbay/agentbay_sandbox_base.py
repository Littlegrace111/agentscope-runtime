# -*- coding: utf-8 -*-
"""
AgentBay sandbox base class.

This module provides the base class for AgentBay cloud sandbox implementations.
All specialized AgentBay sandbox types inherit from this base class.
"""
import logging
import os
from typing import Any, Dict, Optional

from agentbay import AgentBay  # type: ignore
from agentbay.session_params import CreateSessionParams  # type: ignore

from ...enums import SandboxType
from ..cloud.cloud_sandbox import CloudSandbox

logger = logging.getLogger(__name__)


class AgentbaySandboxBase(CloudSandbox):
    """
    Base class for AgentBay cloud sandbox implementations.

    This base class provides common functionality for all AgentBay sandbox
    types, including session management, client initialization, and tool
    execution infrastructure.

    Features:
    - Cloud-native environment (no local containers)
    - Direct API communication with AgentBay
    - Session management and lifecycle control
    - Tool execution infrastructure

    Subclasses must implement:
    - _get_tool_mapping(): Return a dictionary mapping tool names to handler
      methods. Each sandbox type has different tools available, so subclasses
      should implement only the tools they support.
    - Tool handler methods: Implement the actual tool methods (e.g.,
      _execute_command, _read_file, etc.) that are referenced in the tool
      mapping. Each sandbox type should implement only the tools it supports.
    - list_tools(): Return the list of available tools for this sandbox type.
    - Image-specific initialization if needed.
    """

    def __init__(
        self,
        sandbox_id: Optional[str] = None,
        timeout: int = 3000,
        base_url: Optional[str] = None,
        bearer_token: Optional[str] = None,
        sandbox_type: SandboxType = SandboxType.AGENTBAY,
        api_key: Optional[str] = None,
        image_id: str = "linux_latest",
        labels: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        """
        Initialize the AgentBay sandbox.

        Args:
            sandbox_id: Optional sandbox ID for existing sessions
            timeout: Timeout for operations in seconds
            base_url: Base URL for AgentBay API (optional)
            bearer_token: Authentication token (deprecated, use api_key)
            sandbox_type: Type of sandbox (default: AGENTBAY)
            api_key: AgentBay API key (from environment or parameter)
            image_id: AgentBay image type (linux_latest, windows_latest, etc.)
            labels: Optional labels for session organization
            **kwargs: Additional configuration
        """
        # Get API key from parameter, environment, or bearer_token
        self.api_key = api_key or os.getenv("AGENTBAY_API_KEY") or bearer_token
        if not self.api_key:
            raise ValueError(
                "AgentBay API key is required. Set AGENTBAY_API_KEY "
                "environment variable or pass api_key parameter.",
            )

        # Store AgentBay-specific configuration
        self.image_id = image_id
        self.labels = labels or {}
        self.base_url = base_url

        super().__init__(
            sandbox_id=sandbox_id,
            timeout=timeout,
            base_url=base_url,
            bearer_token=self.api_key,
            sandbox_type=sandbox_type,
            **kwargs,
        )

    def _initialize_cloud_client(self):
        """
        Initialize the AgentBay client.

        Returns:
            AgentBay client instance
        """
        if AgentBay is None:
            raise ImportError(
                "AgentBay SDK is not installed. Please install it with: "
                "pip install wuying-agentbay-sdk",
            )

        try:
            # Initialize client with API key
            client = AgentBay(api_key=self.api_key)

            logger.info("AgentBay client initialized successfully")
            return client

        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize AgentBay client: {e}",
            ) from e

    def _create_cloud_sandbox(self) -> Optional[str]:
        """
        Create a new AgentBay session.

        Returns:
            Session ID if successful, None otherwise
        """
        if CreateSessionParams is None:
            raise ImportError(
                "AgentBay SDK is not installed. Please install it with: "
                "pip install wuying-agentbay-sdk",
            )

        try:
            # Create session parameters
            params = CreateSessionParams(
                image_id=self.image_id,
                labels=self.labels,
            )

            # Create session
            result = self.cloud_client.create(params)

            if result.success:
                session_id = result.session.session_id
                logger.info("AgentBay session created: %s", session_id)
                return session_id
            else:
                logger.error(
                    "Failed to create AgentBay session: %s",
                    result.error_message,
                )
                return None

        except (RuntimeError, ValueError, AttributeError, TypeError) as e:
            logger.error("Error creating AgentBay session: %s", e)
            return None

    def _delete_cloud_sandbox(self, sandbox_id: str) -> bool:
        """
        Delete an AgentBay session.

        Args:
            sandbox_id: ID of the session to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get session object first
            get_result = self.cloud_client.get(sandbox_id)
            if not get_result.success:
                logger.warning(
                    "Session %s not found or already deleted",
                    sandbox_id,
                )
                return True  # Consider it successful if already gone

            # Delete the session
            delete_result = self.cloud_client.delete(get_result.session)

            if delete_result.success:
                logger.info(
                    "AgentBay session %s deleted successfully",
                    sandbox_id,
                )
                return True
            else:
                logger.error(
                    "Failed to delete AgentBay session: %s",
                    delete_result.error_message,
                )
                return False

        except (RuntimeError, ValueError, AttributeError, TypeError) as e:
            logger.error(
                "Error deleting AgentBay session %s: %s",
                sandbox_id,
                e,
            )
            return False

    def _call_cloud_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Any:
        """
        Call a tool in the AgentBay environment.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments for the tool

        Returns:
            Tool execution result
        """
        try:
            # Get the session object
            get_result = self.cloud_client.get(self._sandbox_id)
            if not get_result.success:
                raise RuntimeError(f"Sandbox {self._sandbox_id} not found")

            session = get_result.session

            # Get tool mapping from subclass
            tool_mapping = self._get_tool_mapping()

            if tool_name in tool_mapping:
                return tool_mapping[tool_name](session, arguments)
            else:
                # Try to call as a generic method
                return self._generic_tool_call(session, tool_name, arguments)

        except (RuntimeError, ValueError, AttributeError, TypeError) as e:
            logger.error("Error calling tool %s: %s", tool_name, e)
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name,
                "arguments": arguments,
            }

    def _get_tool_mapping(self) -> Dict[str, Any]:
        """
        Get the tool mapping for this sandbox type.

        Subclasses must override this method to provide their specific
        tool mappings. Each sandbox type has different tools available,
        so subclasses should implement only the tools they support.

        Returns:
            Dictionary mapping tool names to handler methods
        """
        # Base implementation - subclasses must override
        return {}

    def _generic_tool_call(
        self,
        session,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generic tool call fallback."""
        try:
            # Try to find and call the method on the session
            if hasattr(session, tool_name):
                method = getattr(session, tool_name)
                result = method(**arguments)

                return {
                    "success": True,
                    "result": result,
                }
            else:
                return {
                    "success": False,
                    "error": (
                        f"Tool '{tool_name}' not found in AgentBay session"
                    ),
                }
        except (RuntimeError, ValueError, AttributeError, TypeError) as e:
            return {
                "success": False,
                "error": f"Error calling tool '{tool_name}': {str(e)}",
            }

    def _get_cloud_provider_name(self) -> str:
        """Get the name of the cloud provider."""
        return "AgentBay"

    def list_tools(self, tool_type: Optional[str] = None) -> Dict[str, Any]:
        """
        List available tools in the AgentBay sandbox.

        Subclasses should override this method to provide their specific
        tool lists.

        Args:
            tool_type: Optional filter for tool type (e.g., "file", "browser")

        Returns:
            Dictionary containing available tools organized by type
        """
        # Base implementation - subclasses should override
        return {
            "tools": [],
            "tools_by_type": {},
            "tool_type": tool_type,
            "sandbox_id": self._sandbox_id,
            "total_count": 0,
        }
