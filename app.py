import asyncio
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ---------- 请求/响应模型 ----------
class CalculatorRequest(BaseModel):
    a: float
    b: float
    operator: str  # + - * /

class CalculatorResponse(BaseModel):
    result: float

class FileListResponse(BaseModel):
    files: list[str]

# ---------- MCP 客户端辅助函数 ----------
async def call_mcp_tool(tool_name: str, arguments: dict = None):
    """
    调用 MCP 工具并返回结果内容列表。
    注意：FastMCP 将 list 返回值拆分为多个 TextContent，此函数会收集所有 text。
    """
    # 使用与客户端相同的 Python 解释器（重要！）
    server_params = StdioServerParameters(
        command="python313",   # 如果你的 python313 不在 PATH，请改用绝对路径，例如 r"D:\Django\python313\python.exe"
        args=["mcp_server.py"],
        env=None
    )
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments or {})
            # 提取所有 text 内容（FastMCP 拆分列表时每个文件一个 TextContent）
            return [content.text for content in result.content if hasattr(content, 'text')]

# ---------- FastAPI 应用 ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时检查 MCP 服务是否可用
    print("🔌 检查 MCP 服务连接...")
    try:
        await call_mcp_tool("get_desktop_files")
        print("✅ MCP 服务正常")
    except Exception as e:
        print(f"❌ MCP 服务连接失败: {e}")
    yield

app = FastAPI(lifespan=lifespan)

# ---------- API 端点 ----------
@app.get("/desktop-files", response_model=FileListResponse)
async def get_desktop_files():
    """获取桌面文件列表"""
    try:
        contents = await call_mcp_tool("get_desktop_files")
        # contents 已经是文件名列表（每个文件一个字符串）
        return FileListResponse(files=contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calculator", response_model=CalculatorResponse)
async def calculate(req: CalculatorRequest):
    """执行计算"""
    try:
        contents = await call_mcp_tool("calculator", {
            "a": req.a,
            "b": req.b,
            "operator": req.operator
        })
        # 计算器返回一个数字，contents 是 ['结果值']
        result = float(contents[0])
        return CalculatorResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- 提供前端页面 ----------
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MCP 工具演示</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
        .card { border: 1px solid #ccc; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        button { background-color: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        pre { background: #f4f4f4; padding: 10px; border-radius: 4px; overflow-x: auto; }
        input, select { padding: 8px; margin: 5px; }
        .result { margin-top: 10px; font-weight: bold; }
        .error { color: red; }
        .file-item { margin: 4px 0; }
    </style>
</head>
<body>
    <h1>🛠️ MCP 工具演示</h1>

    <div class="card">
        <h2>📁 桌面文件列表</h2>
        <button id="listFilesBtn">刷新列表</button>
        <div id="fileListResult" style="margin-top: 10px;"></div>
    </div>

    <div class="card">
        <h2>🧮 计算器</h2>
        <input type="number" id="numA" placeholder="数字 A" value="10">
        <select id="operator">
            <option value="+">+</option>
            <option value="-">-</option>
            <option value="*">*</option>
            <option value="/">/</option>
        </select>
        <input type="number" id="numB" placeholder="数字 B" value="5">
        <button id="calcBtn">计算</button>
        <div id="calcResult" class="result"></div>
    </div>

    <script>
        const API_BASE = '';

        document.getElementById('listFilesBtn').addEventListener('click', async () => {
            const container = document.getElementById('fileListResult');
            container.innerHTML = '加载中...';
            try {
                const resp = await fetch('/desktop-files');
                if (!resp.ok) throw new Error(await resp.text());
                const data = await resp.json();
                if (data.files.length === 0) {
                    container.innerHTML = '<p>桌面文件夹为空</p>';
                } else {
                    const ul = document.createElement('ul');
                    data.files.forEach(file => {
                        const li = document.createElement('li');
                        li.textContent = file;
                        ul.appendChild(li);
                    });
                    container.innerHTML = '';
                    container.appendChild(ul);
                }
            } catch (err) {
                container.innerHTML = `<p class="error">错误: ${err.message}</p>`;
            }
        });

        document.getElementById('calcBtn').addEventListener('click', async () => {
            const a = parseFloat(document.getElementById('numA').value);
            const b = parseFloat(document.getElementById('numB').value);
            const op = document.getElementById('operator').value;
            const resultDiv = document.getElementById('calcResult');
            resultDiv.textContent = '计算中...';
            try {
                const resp = await fetch('/calculator', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ a, b, operator: op })
                });
                if (!resp.ok) throw new Error(await resp.text());
                const data = await resp.json();
                resultDiv.textContent = `结果: ${data.result}`;
            } catch (err) {
                resultDiv.textContent = `错误: ${err.message}`;
                resultDiv.classList.add('error');
            }
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    return HTMLResponse(HTML_PAGE)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)