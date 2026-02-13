@echo off
chcp 65001 >nul
echo ========================================
echo StatusScreenSaver 客户端打包脚本
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    pause
    exit /b 1
)

:: 检查 PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 安装 PyInstaller...
    pip install pyinstaller
)

:: 设置工作目录
set PROJECT_DIR=%~dp0..
set DIST_DIR=%PROJECT_DIR%\dist
set CLIENT_DIR=%PROJECT_DIR%\client

:: 清理旧的构建文件
echo 清理旧的构建文件...
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
mkdir "%DIST_DIR%"

:: 安装依赖
echo.
echo ========================================
echo 安装依赖...
echo ========================================
pip install PyQt6>=6.5.0
pip install PyQt6-QtMultimedia>=6.5.0
pip install websockets>=11.0
pip install PyYAML>=6.0
pip install pywin32>=305

:: ========================================
echo.
echo ========================================
echo 打包常驻应用 (Tray App)...
echo ========================================
cd /d "%CLIENT_DIR%\tray_app"

pyinstaller --onefile --windowed ^
    --name "StatusScreenSaverTray" ^
    --icon "assets\tray_icon.ico" ^
    --add-data "config.yaml;." ^
    --distpath "%DIST_DIR%" ^
    --workpath "%TEMP%\build_tray" ^
    --specpath "%TEMP%" ^
    main.py

if errorlevel 1 (
    echo 错误: 常驻应用打包失败
    pause
    exit /b 1
)

:: 复制配置文件
echo 复制配置文件...
copy /y "config.yaml" "%DIST_DIR%\config.yaml"

:: ========================================
echo.
echo ========================================
echo 打包屏保程序 (.scr)...
echo ========================================
cd /d "%CLIENT_DIR%\screensaver_scr"

pyinstaller --onefile --windowed ^
    --name "statusscreensaver" ^
    --distpath "%DIST_DIR%" ^
    --workpath "%TEMP%\build_scr" ^
    --specpath "%TEMP%" ^
    main.py

if errorlevel 1 (
    echo 错误: 屏保程序打包失败
    pause
    exit /b 1
)

:: 重命名为 .scr
echo 重命名为 .scr 文件...
cd /d "%DIST_DIR%"
if exist statusscreensaver.exe (
    move /y statusscreensaver.exe statusscreensaver.scr
    echo 已生成: statusscreensaver.scr
)

:: 创建内容目录
echo 创建内容目录...
mkdir "%DIST_DIR%\contents\images" 2>nul
mkdir "%DIST_DIR%\contents\videos" 2>nul

:: 创建示例配置
echo 创建默认配置...
(
echo # 将图片文件放入 images 目录
echo # 将视频文件放入 videos 目录
echo.
echo # 支持的图片格式: jpg, png, bmp, gif
echo # 支持的视频格式: mp4^(h.264^), wmv, avi
) > "%DIST_DIR%\contents\README.txt"

:: ========================================
echo.
echo ========================================
echo 打包完成!
echo ========================================
echo.
echo 输出目录: %DIST_DIR%
echo.
echo 生成的文件:
echo   - StatusScreenSaverTray.exe  (常驻应用)
echo   - statusscreensaver.scr      (系统屏保)
echo   - config.yaml                (配置文件)
echo   - contents\                  (内容目录)
echo.
echo 使用说明:
echo 1. 编辑 config.yaml 配置服务器地址
echo 2. 将图片/视频放入 contents 目录
echo 3. 运行 StatusScreenSaverTray.exe
echo 4. 右键 statusscreensaver.scr 选择"安装"
echo.
pause
