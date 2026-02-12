@echo off
chcp 65001 >nul
echo ========================================
echo 启动服务端
echo ========================================
echo.

cd server

:: 检查依赖
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 安装服务端依赖...
    pip install -r requirements.txt
)

echo.
echo 启动服务端 (端口: 8000)...
echo API 文档: http://localhost:8000/docs
echo.
python main.py
