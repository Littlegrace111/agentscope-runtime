# import json
# from agentscope_runtime.sandbox.tools.base import run_ipython_cell

# # 模型上下文协议（MCP）兼容的工具调用结果
# result = run_ipython_cell(code="print('Setup successful!')")
# print(json.dumps(result, indent=4, ensure_ascii=False))

import json
from agentscope_runtime.sandbox.tools.base import (
    run_ipython_cell,
    run_shell_command,
)

# print(run_ipython_cell(code="print('hello world')"))
# print(run_shell_command(command="whoami"))
from agentscope_runtime.sandbox import BaseSandbox

with BaseSandbox() as sandbox:
    # 确保函数的沙箱类型与沙箱实例类型匹配
    assert run_ipython_cell.sandbox_type == sandbox.sandbox_type

    # 将沙箱绑定到工具函数
    func1 = run_ipython_cell.bind(sandbox=sandbox)
    func2 = run_shell_command.bind(sandbox=sandbox)

    # 在沙箱内执行函数
    print(func1(code="repo = 'agentscope-runtime'"))
    print(func1(code="print(repo)"))
    print(func2(command="whoami"))

from agentscope_runtime.sandbox.tools.mcp_tool import MCPConfigConverter

# 将 MCP 服务器转换为工具
# mcp_tools = MCPConfigConverter(
#     server_configs={
#         "mcpServers": {
#             "time": {
#                 "command": "uvx",
#                 "args": [
#                     "mcp-server-time",
#                     "--local-timezone=America/New_York",
#                 ],
#             },
#         },
#     },
# ).to_builtin_tools()

# print(mcp_tools)


from agentscope_runtime.sandbox.tools.function_tool import (
    FunctionTool,
    function_tool,
)


class MathCalculator:
    def calculate_power(self, base: int, exponent: int) -> int:
        """计算一个数的幂。"""
        print(f"Calculating {base}^{exponent}...")
        return base**exponent


calculator = MathCalculator()


@function_tool(
    name="calculate_power",
    description="计算底数的幂次方",
)
def another_calculate_power(base: int, exponent: int) -> int:
    """计算底数的幂次方。"""
    print(f"计算 {base}^{exponent}...")
    return base**exponent


tool_0 = FunctionTool(calculator.calculate_power)
tool_1 = another_calculate_power
print(tool_0, tool_1)

# 每个工具都有一个定义的schema，它指定了输入参数的预期结构和类型
print(json.dumps(run_ipython_cell.schema, indent=4, ensure_ascii=False))

# 简单的函数式调用
result = run_ipython_cell(code="print('hello world')")
result = tool_0(base=2, exponent=3)
# 创建新实例，原始工具保持不变
bound_tool = run_ipython_cell.bind(sandbox=sandbox)