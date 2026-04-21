import json
import ast
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession

app = FastAPI(title="MCP Bridge")

# 允许跨域（以便 file:// 协议的 HTML 能访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MCP 客户端配置（仅用于计算器） ====================
SERVER_PARAMS = StdioServerParameters(
    command="python313",      # 根据你的 Python 命令调整
    args=["mcp_server.py"]
)

def parse_mcp_text(text: str):
    """解析 MCP 返回的文本，支持 JSON 和 Python 字面量"""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            return ast.literal_eval(text)
        except (ValueError, SyntaxError):
            return text

async def call_mcp_tool(tool_name: str, arguments: dict):
    """调用 MCP 工具（仅用于计算器）"""
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments=arguments)
            if result.content and len(result.content) > 0:
                text = result.content[0].text
                return parse_mcp_text(text)
            return None

# ==================== 文件浏览端点（直接读取磁盘） ====================
DEFAULT_DESKTOP = r"D:\基本\桌面"   # 你已验证正确的路径

@app.get("/desktop-files")
async def get_desktop_files(path: str = Query(None, description="要列出的文件夹路径")):
    """列出指定路径下的文件和文件夹"""
    target_path = path if path else DEFAULT_DESKTOP
    try:
        if not os.path.exists(target_path):
            raise HTTPException(status_code=404, detail=f"路径不存在: {target_path}")
        if not os.path.isdir(target_path):
            raise HTTPException(status_code=400, detail=f"不是目录: {target_path}")
        items = os.listdir(target_path)
        return {"success": True, "data": items, "current_path": target_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 计算器端点 ====================
class CalcRequest(BaseModel):
    a: float
    b: float
    operator: str

@app.post("/calculate")
async def calculate(req: CalcRequest):
    try:
        result = await call_mcp_tool("calculator", {
            "a": req.a,
            "b": req.b,
            "operator": req.operator
        })
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 启动服务 ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)