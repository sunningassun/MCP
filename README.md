# MCP 文件系统工具 + 前端演示

本项目演示了如何使用 MCP (Model Context Protocol) 构建一个文件系统工具和一个计算器工具，并通过一个轻量级桥接服务提供 HTTP API，最终由前端页面进行可视化调用。

- **后端 MCP 服务**：提供 `get_desktop_files`（桌面文件列表）和 `calculator`（基础数学运算）两个工具。
- **桥接服务**：基于 FastAPI，将 MCP 工具的调用转换为 RESTful API，并直接处理文件浏览（避免 MCP 序列化问题）。
- **前端页面**：独立的 HTML 文件，提供文件浏览器（支持任意路径）和计算器界面。

## 环境要求

- Python 3.11 或更高版本（推荐 3.13）
- 操作系统：Windows（路径示例为 Windows，macOS/Linux 可自行调整桌面路径）
- 已安装 `pip` 包管理器

## 安装步骤

### 1. 克隆或下载项目

将以下文件放在同一个目录中（例如 `D:\work\py\MCP`）：

project/
├── mcp_server.py          # MCP 服务
├── bridge_service.py      # FastAPI 桥接服务
├── start.bat              # Windows 一键启动脚本
├── static/                # 前端静态文件目录
│   └── index.html         # 前端页面
└── README.md              # 本文件
```

### 2. 安装 Python 依赖

打开终端（cmd 或 PowerShell），进入项目目录，执行：

```bash
pip install mcp fastapi uvicorn pydantic
```

> 注意：`mcp` 包可能名称为 `mcp` 或 `fastmcp`，请根据实际情况调整。如果安装失败，可尝试：
> ```bash
> pip install fastmcp fastapi uvicorn
> ```

### 3. 调整桌面路径（重要）

如果你的桌面路径不是 `D:\基本\桌面`，请修改以下文件中的默认路径：

- `mcp_server.py` 中的 `DESKTOP_PATH` 变量
- `bridge_service.py` 中的 `DEFAULT_DESKTOP` 变量

例如使用系统当前用户的桌面：

```python
import os
DEFAULT_DESKTOP = os.path.expanduser("~/Desktop")
```

或在 Windows 上通过 Shell API 获取更可靠：

```python
import ctypes.wintypes
buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
ctypes.windll.shell32.SHGetFolderPathW(None, 0x0000, None, 0, buf)
DEFAULT_DESKTOP = buf.value
```

## 使用方法

### 一键启动（Windows）

双击 `start.bat` 文件，脚本会：
- 在后台启动桥接服务（`http://127.0.0.1:8000`）
- 自动打开默认浏览器，显示 `static/index.html` 页面
- 按任意键停止服务并关闭 Python 进程

### 手动启动（调试模式）

1. **启动桥接服务**（不要关闭终端）：
   ```bash
   python bridge_service.py
   ```
   控制台会显示 `Uvicorn running on http://127.0.0.1:8000`

2. **打开前端页面**：
   用浏览器打开 `static/index.html` 文件（或直接双击）。

### 使用前端界面

![show](D:\work\py\MCP\show.png)

#### 文件浏览器
- 输入任意文件夹路径（例如 `D:\work`、`C:\Users`），点击“浏览”即可列出该目录下的文件和子文件夹。
- 留空路径则显示默认桌面路径（已在 `bridge_service.py` 中配置）。
- 支持中文文件名和特殊字符。

#### 计算器
- 输入两个数字，选择运算符（+、-、*、/），点击“计算结果”即可得到运算结果。
- 除零错误会给出提示。

## 常见问题

### 1. 桌面文件列表无法显示，提示“路径不存在”

**原因**：默认桌面路径与你的实际桌面路径不一致。

**解决**：修改 `bridge_service.py` 中的 `DEFAULT_DESKTOP` 变量为正确的绝对路径。或者在前端页面的路径输入框中手动输入你的桌面路径（如 `D:\基本\桌面`）后再点击浏览。

### 2. 计算器返回错误“无效运算符”

**原因**：前端传递的运算符不是 `+`、`-`、`*`、`/` 之一。

**解决**：检查前端下拉框是否被修改；正常情况下不会出现此问题。

### 3. 桥接服务启动失败，提示“No module named 'mcp'”

**原因**：未安装 MCP Python 库。

**解决**：执行 `pip install mcp` 或 `pip install fastmcp`。如果仍有问题，请确认 Python 环境是否正确。

### 4. 前端页面无法连接桥接服务（控制台显示 CORS 错误或连接失败）

**原因**：桥接服务未启动，或前端 `API_BASE` 地址配置错误。

**解决**：
- 确认桥接服务已启动（访问 `http://127.0.0.1:8000/desktop-files` 应返回 JSON 数据）。
- 检查 `index.html` 中的 `API_BASE` 是否设置为 `http://127.0.0.1:8000`。
- 如果使用 `file://` 协议打开 HTML，浏览器可能限制跨域请求，但本桥接服务已开启 CORS，应该可以正常工作。

### 5. 在 macOS/Linux 上如何使用？

- 将 `mcp_server.py` 和 `bridge_service.py` 中的桌面路径改为 `os.path.expanduser("~/Desktop")`。
- 启动脚本可以使用 shell 脚本（`start.sh`）替代 `start.bat`。
- 确保 Python 命令为 `python3` 而非 `python313`。

示例 `start.sh`：
```bash
#!/bin/bash
python3 bridge_service.py &
sleep 2
open static/index.html   # macOS
# xdg-open static/index.html  # Linux
read -p "Press enter to stop..."
pkill -f "bridge_service.py"
```

## 项目结构说明

| 文件                | 作用                                                         |
| ------------------- | ------------------------------------------------------------ |
| `mcp_server.py`     | MCP 服务端，定义 `get_desktop_files` 和 `calculator` 工具，通过 stdio 传输。 |
| `bridge_service.py` | FastAPI 应用，提供 `/desktop-files`（直接读磁盘）和 `/calculate`（调用 MCP 计算器）两个接口，并开启 CORS。 |
| `static/index.html` | 前端界面，使用 Fetch API 调用桥接服务，实现文件浏览和计算。  |
| `start.bat`         | Windows 一键启动脚本，后台运行桥接服务并打开浏览器。         |

## 扩展建议

- 若希望文件浏览也通过 MCP 工具实现，可以修改 `mcp_server.py` 中的 `get_desktop_files` 接受 `path` 参数，并在桥接服务中转发调用，但需要注意 MCP 序列化问题（目前直接读磁盘更稳定）。
- 可将桥接服务部署到服务器上，并将前端页面托管到 Web 服务器，实现远程访问。
- 增加用户认证、日志记录等生产环境所需功能。

## 许可证

MIT License

---

如有任何问题，欢迎提交 Issue 或自行根据错误日志调试。