# MCP 工具演示项目

一个基于 **MCP (Model Context Protocol)** 的文件和计算器服务，提供 Web 图形界面。

## 📖 项目介绍

本项目实现了一个 MCP 服务端，提供两个实用工具：
- **获取桌面文件列表**：列出指定目录（如桌面）下的所有文件和文件夹。
- **计算器**：支持加、减、乘、除四则运算。

同时提供一个 Web 客户端：基于 FastAPI + 现代浏览器，提供美观的图形界面。

## 🛠️ 技术栈

- Python 3.13+
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- FastAPI + Uvicorn（Web 后端）
- HTML/CSS/JavaScript（前端界面）

## 📁 项目结构

```
MCP/
├── mcp_server.py      # MCP 服务端（核心工具）
├── app.py             # Web 后端 + 前端界面
└── README.md          # 项目说明
```

## 🔧 环境要求

- Python 3.13 或更高版本
- 操作系统：Windows / Linux / macOS（路径配置需相应调整）

## 📦 安装步骤

### 1. 克隆或下载项目代码

将上述文件保存到同一目录，例如 `D:\work\py\MCP`。

### 2. 安装 Python 依赖

打开终端，进入项目目录，执行：

```bash
python -m pip install mcp fastapi uvicorn
```

### 3. 配置服务端路径

编辑 `mcp_server.py`，修改桌面目录路径（第 9 行）：

```python
desktop = r"D:\基本\桌面"   # 改为你真实的桌面路径
```

- **Windows 示例**：`C:\Users\你的用户名\Desktop`
- **Linux/macOS 示例**：`/home/用户名/Desktop`

也可以改为其他任何你想浏览的文件夹。

## 🚀 运行方法

### Web 图形界面

```bash
python app.py
```

启动后，终端会显示：

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

打开浏览器访问 `http://127.0.0.1:8000`，即可看到图形界面。

## 🖥️ 使用说明

### Web 界面

打开浏览器后，页面包含两个功能卡片：

#### 📁 桌面文件列表
- 点击 **刷新列表** 按钮，下方会以列表形式显示所有文件/文件夹。
- 若文件夹为空或路径错误，会给出相应提示。

#### 🧮 计算器
- 输入数字 A、选择运算符（+ - * /）、输入数字 B。
- 点击 **计算** 按钮，立即显示结果。
- 除数为零时会提示错误。

## ⚙️ 常见问题及解决

### 1. Web 后端启动后，点击“刷新列表”报错 `MCP 服务连接失败`

**可能原因**：
- `app.py` 中调用的 Python 命令与你的环境不匹配。  
- `mcp_server.py` 路径不正确或代码有语法错误。

**解决**：
- 修改 `app.py` 中 `call_mcp_tool` 函数内的 `command` 参数，使用绝对路径或正确的命令名。
- 手动运行 `python mcp_server.py` 检查是否有报错。

### 2. 桌面路径不存在或找不到文件

**原因**：`mcp_server.py` 中配置的路径不正确。  
**解决**：确认路径存在，并注意 Windows 路径中的反斜杠应使用原始字符串（`r"..."`）或双反斜杠。

### 3. Web 界面无法访问

**原因**：后端未成功启动或端口被占用。  
**解决**：
- 检查终端是否有报错信息。
- 更换端口：修改 `app.py` 最后一行 `port=8000` 为其他端口（如 `8080`）。
- 确保防火墙未阻止该端口。

## 📝 开发与扩展

### 添加新工具

1. 在 `mcp_server.py` 中使用 `@mcp.tool()` 装饰器定义新函数。
2. 函数文档字符串会自动成为工具描述。
3. 无需修改客户端代码，MCP 协议会自动发现新工具。

示例：添加一个获取系统时间的工具

```python
from datetime import datetime

@mcp.tool()
def get_current_time() -> str:
    """返回当前日期和时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

重启服务后，客户端即可调用。

### 修改 Web 前端样式

编辑 `app.py` 中的 `HTML_PAGE` 变量，修改 CSS 或 HTML 结构。保存后刷新浏览器即可生效。

## 🤝 贡献

欢迎提交 Issue 或 Pull Request 来改进本项目。
