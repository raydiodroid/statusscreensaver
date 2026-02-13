# 客户端打包说明

## 快速打包

```powershell
# 运行打包脚本
scripts\build-client.bat
```

打包完成后，在 `dist` 目录会生成：

```
dist/
├── StatusScreenSaverTray.exe  # 常驻应用
├── statusscreensaver.scr      # 系统屏保
├── config.yaml                # 配置文件
└── contents/                  # 内容目录
    ├── images/
    └── videos/
```

## 部署到客户端设备

### 步骤 1：配置服务器

编辑 `config.yaml`：

```yaml
server:
  url: "ws://你的服务器IP:29876/ws"
  offline_mode: false

device:
  name: "会议室A"
  location: "三楼大厅"
```

### 步骤 2：添加内容

将图片和视频放入 `contents` 目录：

```
contents/
├── images/
│   ├── poster1.jpg
│   └── poster2.jpg
└── videos/
    └── promo.mp4
```

### 步骤 3：运行

1. **运行常驻应用**
   - 双击 `StatusScreenSaverTray.exe`
   - 系统托盘会出现图标

2. **安装系统屏保**
   - 右键 `statusscreensaver.scr`
   - 选择"安装"或"测试"

## 开机自启

将 `StatusScreenSaverTray.exe` 的快捷方式放入 Windows 启动目录：

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
```

## 手动打包

如果需要手动打包：

```powershell
# 安装 PyInstaller
pip install pyinstaller

# 打包常驻应用
cd client\tray_app
pyinstaller --onefile --windowed --name "StatusScreenSaverTray" main.py

# 打包屏保
cd ..\screensaver_scr
pyinstaller --onefile --windowed --name "statusscreensaver" main.py
# 重命名为 .scr
move dist\statusscreensaver.exe dist\statusscreensaver.scr
```

## 注意事项

- **视频格式**: 支持 MP4 (H.264)、WMV、AVI
- **图片格式**: 支持 JPG、PNG、BMP、GIF
- **网络**: 确保客户端能访问服务器端口
- **防火墙**: 可能需要允许程序通过防火墙
