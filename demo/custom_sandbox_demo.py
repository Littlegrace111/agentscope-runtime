from agentscope_runtime.sandbox.box.sandbox import Sandbox
from agentscope_runtime.sandbox.enums import SandboxType

with Sandbox(
    base_url="https://mcp.agb.cloud/sse?APIKEY=ako-62241dbe-8011-4ca9-8c45-4c48fac49d9f&IMAGEID=agb-code-space-1",
    bearer_token="",
    sandbox_type=SandboxType("custom_sandbox"),
) as box:
    print(box.list_tools())
    print(box.call_tool("run_shell_command", {"command": "whoami"}))