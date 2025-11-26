# -*- coding: utf-8 -*-
"""
Prompt Builder for Multi-Sandbox Agent

This module provides functions to build system prompts for the
multi-sandbox agent.
"""
from typing import Any, Dict


def create_system_prompt(all_tools: Dict[str, Dict[str, Any]]) -> str:
    """
    Create system prompt for the multi-sandbox agent.

    Args:
        all_tools: Dictionary containing tools information from all sandboxes.
                  Format: {sandbox_type: {"tools": [...], ...}}

    Returns:
        System prompt string
    """
    tools_summary = []

    for sandbox_type, tools_info in all_tools.items():
        if "error" not in tools_info:
            tools = tools_info.get("tools", [])
            tools_summary.append(
                f"- **{sandbox_type.upper()}** sandbox: "
                f"{', '.join(tools[:5])}"
                + (f" and {len(tools) - 5} more" if len(tools) > 5 else ""),
            )

    tools_list = "\n".join(tools_summary)

    prompt = f"""You are an AI assistant with access to 4 GUI sandbox
environments:
1. **Linux** sandbox - Linux desktop environment for command execution
   and file operations
2. **Windows** sandbox - Windows desktop environment for application
   management and desktop automation
3. **Browser** sandbox - Browser automation environment for web
   navigation and interaction
4. **Mobile** sandbox - Android mobile device environment for mobile
   UI automation

Available tools are prefixed with the sandbox type (e.g.,
`linux_run_shell_command`, `browser_navigate`).

**Important**: Sandboxes are created on-demand when you use their tools.
You don't need to worry about initialization - just use the appropriate
tool and the sandbox will be created automatically if needed.

When users ask you to do something:
1. Understand the task and determine which sandbox(es) are needed
2. Use the appropriate tools with the correct sandbox prefix
3. The sandbox will be automatically created when you first use its
   tools
4. You can use multiple sandboxes in sequence or parallel if needed
5. Always explain what you're doing and provide helpful responses

Available tools by sandbox:
{tools_list}

Remember:
- Tool names follow the pattern: `{{sandbox_type}}_{{tool_name}}`
- Choose the right sandbox based on the task (Linux for commands,
  Browser for web, etc.)
- Sandboxes are created automatically when needed - just use the tools
- You can coordinate multiple sandboxes to complete complex tasks
- Always provide clear feedback about what you're doing
"""
    return prompt
