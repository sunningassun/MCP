@echo off
title MCP Bridge Service
echo Starting MCP Bridge...
start /B python313 bridge_service.py > bridge.log 2>&1
timeout /t 2 /nobreak >nul
start "" "%~dp0static\index.html"
echo Bridge service is running at http://127.0.0.1:8000
echo Press any key to stop the service and close...
pause >nul
taskkill /F /IM python313.exe 2>nul
echo Service stopped.