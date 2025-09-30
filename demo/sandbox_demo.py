from agentscope_runtime.sandbox import BaseSandbox, FilesystemSandbox, BrowserSandbox

# 创建基础沙箱
# with BaseSandbox() as box:
#     print(box.list_tools())
#     print(box.run_ipython_cell(code="print('hi')"))
#     print(box.run_shell_command(command="echo hello"))

with BaseSandbox() as sandbox:
    mcp_server_configs = {
        "mcpServers": {
            "time": {
                "command": "uvx",
                "args": [
                    "mcp-server-time",
                    "--local-timezone=America/New_York",
                ],
            },
        },
    }

    # 将MCP服务器添加到沙箱
    sandbox.add_mcp_servers(server_configs=mcp_server_configs)

    # 列出所有可用工具（现在包括MCP工具）
    print(sandbox.list_tools())

    #使用MCP服务器提供的时间工具
    print(
        sandbox.call_tool(
            "get_current_time",
            arguments={
                "timezone": "America/New_York",
            },
        ),
    )

# 创建文件系统沙箱
# with FilesystemSandbox() as box:
#     print(box.list_tools())
#     print(box.create_directory("test"))
#     print(box.list_allowed_directories())


# 创建浏览器沙箱
# with BrowserSandbox() as box:
#     print(box.list_tools())
#     print(box.browser_navigate("https://www.example.com/"))
#     print(box.browser_snapshot())