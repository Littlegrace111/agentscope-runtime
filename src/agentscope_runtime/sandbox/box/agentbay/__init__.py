# -*- coding: utf-8 -*-
from .agentbay_browser_sandbox import AgentbayBrowserSandbox
from .agentbay_code_sandbox import AgentbayCodeSandbox
from .agentbay_linux_sandbox import AgentbayLinuxSandbox
from .agentbay_mobile_sandbox import AgentbayMobileSandbox
from .agentbay_sandbox_base import AgentbaySandboxBase
from .agentbay_windows_sandbox import AgentbayWindowsSandbox

# For backward compatibility
AgentbaySandbox = AgentbayLinuxSandbox

__all__ = [
    "AgentbaySandboxBase",
    "AgentbayLinuxSandbox",
    "AgentbayWindowsSandbox",
    "AgentbayBrowserSandbox",
    "AgentbayCodeSandbox",
    "AgentbayMobileSandbox",
    "AgentbaySandbox",  # Backward compatibility
]
