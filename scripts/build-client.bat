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
if exist "%PROJECT_DIR%\build" rmdir /s /q "%PROJECT_DIR%\build"
mkdir "%DIST_DIR%"

:: 安装依赖
echo.
echo ========================================
echo 安装依赖...
echo ========================================
pip install "PySide6>=6.5.0"
pip install "websockets>=11.0"
pip install "PyYAML>=6.0"
pip install "pywin32>=305"

:: ========================================
echo.
echo ========================================
echo 打包常驻应用 (Tray App)...
echo ========================================
cd /d "%CLIENT_DIR%\tray_app"

:: 创建临时默认配置
echo 创建默认配置...
(
echo # StatusScreenSaver 配置文件
echo.
echo server:
echo   url: ""
echo   token: null
echo   reconnect_interval: 5
echo   heartbeat_interval: 30
echo   offline_mode: true
echo.
echo device:
echo   name: "未命名设备"
echo   location: ""
echo   id: null
echo.
echo playlist:
echo   auto_play: true
echo   interval: 30
echo   shuffle: false
echo.
echo contents: []
echo.
echo download:
echo   enabled: false
echo   content_server: ""
echo   check_interval: 300
echo   download_dir: "contents/downloaded"
echo.
echo ipc:
echo   pipe_name: "statusscreensaver_ipc"
echo   max_clients: 5
echo.
echo ui:
echo   background_color: "#000000"
echo   error_display_time: 5
echo.
echo state:
echo   file: "state.json"
echo   auto_save: true
echo   auto_save_interval: 60
) > config.yaml

pyinstaller --onefile --windowed ^
    --name "StatusScreenSaverTray" ^
    --add-data "%CLIENT_DIR%\tray_app\config.yaml;." ^
    --add-data "%CLIENT_DIR%\tray_app\assets;assets" ^
    --distpath "%DIST_DIR%" ^
    --workpath "%PROJECT_DIR%\build\tray" ^
    --specpath "%PROJECT_DIR%\build" ^
    main.py

if errorlevel 1 (
    echo 错误: 常驻应用打包失败
    pause
    exit /b 1
)

:: 复制配置文件模板
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
    --workpath "%PROJECT_DIR%\build\scr" ^
    --specpath "%PROJECT_DIR%\build" ^
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

:: 创建使用说明
echo 创建使用说明...
(
echo # StatusScreenSaver 使用说明
echo.
echo ## 快速开始
echo.
echo 1. 运行 StatusScreenSaverTray.exe
echo 2. 右键托盘图标 -^> 内容管理
echo 3. 添加图片、视频或时钟
echo 4. 右键 statusscreensaver.scr 选择"安装"
echo.
echo ## 配置服务器（可选）
echo.
echo 编辑 config.yaml，设置服务器地址：
echo   server:
echo     url: "ws://服务器IP:端口/ws"
echo     offline_mode: false
echo.
echo ## 支持的格式
echo.
echo 图片: jpg, png, bmp, gif
echo 视频: mp4 ^(h.264^), wmv, avi
echo.
) > README.txt

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
echo   - README.txt                 (使用说明)
echo.
echo 使用说明:
echo 1. 运行 StatusScreenSaverTray.exe
echo 2. 右键托盘图标 -^> 内容管理
echo 3. 添加图片/视频/时钟
echo 4. 如需远程控制，编辑 config.yaml 配置服务器
echo.
pause
