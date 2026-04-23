import os
import sys
from mcp.server.fastmcp import FastMCP

print("🚀 MCP 服务启动中...", file=sys.stderr)
mcp = FastMCP("FileSystem")

@mcp.tool()
def get_desktop_files() -> list:
    desktop = r"D:\基本\桌面"
    try:
        if not os.path.exists(desktop):
            return ["桌面路径不存在"]
        files = os.listdir(desktop)

        if len(files) == 0:
            return ["当前桌面文件夹为空"]
        return files
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return [f"读取异常：{str(e)}"]

@mcp.tool()
def calculator(a: float, b: float, operator: str) -> float:
    """执行基础数学运算（支持+-*/）"""
    if operator == '+':
        return a + b
    elif operator == '-':
        return a - b
    elif operator == '*':
        return a * b
    elif operator == '/':
        if b == 0:
            raise ValueError("除数不能为零")
        return a / b
    else:
        raise ValueError(f"无效运算符: {operator}")

if __name__ == "__main__":
    print("✅ MCP 服务准备就绪，等待连接...", file=sys.stderr)
    mcp.run(transport='stdio')