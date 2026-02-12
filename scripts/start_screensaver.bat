@echo off
chcp 65001 >nul
echo ========================================
echo 启动屏保程序 (测试模式)
echo ========================================
echo.

cd client\screensaver_scr

:: 检查依赖
pip show PyQt6 >nul 2>&1
if errorlevel 1 (
    echo 安装客户端依赖...
    pip install -r requirements.txt
)

echo.
echo 启动屏保程序 (按任意键退出)...
python main.py /s
