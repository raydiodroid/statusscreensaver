@echo off
chcp 65001 >nul
echo ========================================
echo 屏幕保护程序 - 安装脚本
echo ========================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if errorlevel 1 (
    echo 需要管理员权限，正在请求...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: 设置路径
set SRC_DIR=%~dp0..\dist
set SYSTEM_DIR=%SystemRoot%\System32

:: 安装屏保程序
echo 安装屏保程序到系统目录...
if exist "%SRC_DIR%\screensaver.scr" (
    copy /y "%SRC_DIR%\screensaver.scr" "%SYSTEM_DIR%\screensaver.scr"
    echo 已复制: %SYSTEM_DIR%\screensaver.scr
) else (
    echo 错误: 未找到 screensaver.scr
    echo 请先运行 build.bat 进行打包
    pause
    exit /b 1
)

:: 注册屏保
echo.
echo 注册屏保程序...
reg add "HKCU\Control Panel\Desktop" /v SCRNSAVE.EXE /t REG_SZ /d "%SYSTEM_DIR%\screensaver.scr" /f

echo.
echo ========================================
echo 安装完成!
echo ========================================
echo.
echo 现在可以在 Windows 设置中选择此屏保:
echo   设置 → 个性化 → 锁屏界面 → 屏幕保护程序设置
echo.
echo 注意: 请确保 ScreenSaverTray.exe 正在运行
echo.
pause
