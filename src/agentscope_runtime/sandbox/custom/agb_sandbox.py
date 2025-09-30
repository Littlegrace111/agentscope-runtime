# -*- coding: utf-8 -*-
import os
from typing import Optional

from ..constant import IMAGE_TAG
from ..registry import SandboxRegistry
from ..enums import SandboxType
from ..box.sandbox import Sandbox

SANDBOXTYPE = "agb"


@SandboxRegistry.register(
    f"agentscope/runtime-sandbox-{SANDBOXTYPE}:{IMAGE_TAG}",
    sandbox_type=SANDBOXTYPE,
    security_level="medium",
    timeout=300,
    description="AGB-enabled sandbox",
    environment={
        # Inject AGB credentials into sandbox containers
        "AGB_API_KEY": os.getenv("AGB_API_KEY", ""),
        # You may add more AGB-related envs here if needed
    },
)
class AgbSandbox(Sandbox):
    def __init__(
        self,
        sandbox_id: Optional[str] = None,
        timeout: int = 3000,
        base_url: Optional[str] = None,
        bearer_token: Optional[str] = None,
    ):
        super().__init__(
            sandbox_id,
            timeout,
            base_url,
            bearer_token,
            SandboxType(SANDBOXTYPE),
        )
