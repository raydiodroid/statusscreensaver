@echo off
chcp 65001 >nul
echo ========================================
echo 屏幕保护程序 - 打包脚本
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

:: 检查 PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 安装 PyInstaller...
    pip install pyinstaller
)

:: 安装依赖
echo 安装常驻应用依赖...
cd client\tray_app
pip install -r requirements.txt

echo.
echo 安装屏保程序依赖...
cd ..\screensaver_scr
pip install -r requirements.txt

:: 打包常驻应用
echo.
echo ========================================
echo 打包常驻应用...
echo ========================================
cd ..\tray_app
pyinstaller --onefile --windowed --name "ScreenSaverTray" --distpath "../../dist" main.py

:: 打包屏保程序
echo.
echo ========================================
echo 打包屏保程序...
echo ========================================
cd ..\screensaver_scr
pyinstaller --onefile --windowed --name "screensaver" --distpath "../../dist" main.py

:: 重命名为 .scr
echo.
echo 重命名屏保程序为 .scr 文件...
cd ..\..\dist
if exist screensaver.exe (
    move /y screensaver.exe screensaver.scr
    echo 已生成: screensaver.scr
)

echo.
echo ========================================
echo 打包完成!
echo ========================================
echo.
echo 生成的文件位于 dist 目录:
echo   - ScreenSaverTray.exe (常驻应用)
echo   - screensaver.scr     (系统屏保)
echo.
echo 使用说明:
echo 1. 运行 ScreenSaverTray.exe 启动常驻应用
echo 2. 右键 screensaver.scr 选择"安装"或手动复制到系统目录
echo.
pause
