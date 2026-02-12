@echo off
chcp 65001 >nul
echo ========================================
echo 启动常驻应用
echo ========================================
echo.

cd client\tray_app

:: 检查依赖
pip show PyQt6 >nul 2>&1
if errorlevel 1 (
    echo 安装客户端依赖...
    pip install -r requirements.txt
)

echo.
echo 启动常驻应用...
python main.py
