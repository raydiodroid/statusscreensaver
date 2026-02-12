@echo off
chcp 65001 >nul
echo ========================================
echo 屏幕保护程序 - 卸载脚本
echo ========================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if errorlevel 1 (
    echo 需要管理员权限，正在请求...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: 删除屏保文件
echo 删除屏保程序...
if exist "%SystemRoot%\System32\screensaver.scr" (
    del /f "%SystemRoot%\System32\screensaver.scr"
    echo 已删除屏保文件
)

:: 清除注册表
echo 清除注册表项...
reg delete "HKCU\Control Panel\Desktop" /v SCRNSAVE.EXE /f 2>nul

echo.
echo ========================================
echo 卸载完成!
echo ========================================
echo.
pause
