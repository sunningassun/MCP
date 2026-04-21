import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("FileSystem")

@mcp.tool()
def get_desktop_files() -> list:
    '''获取当前用户的桌面文件列表'''
    return os.listdir(os.path.expanduser(r"D:\基本\桌面"))

@mcp.tool()
def calculator(a: float, b: float, operator: str) -> float:
    """执行基础数学运算（支持+-*/）
    Args:
        operator: 运算符，必须是'+','-','*','/'之一
    """
    if operator == '+':
        return a + b
    elif operator == '-':
        return a - b
    elif operator == '*':
        return a * b
    elif operator == '/':
        if b == 0:
            raise ValueError("除数不能为0")
        return a / b
    else:
        raise ValueError("无效运算符")

if __name__ == "__main__":
    mcp.run(transport='stdio')
