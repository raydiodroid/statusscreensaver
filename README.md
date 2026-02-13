# StatusScreenSaver 控制系统

一个支持远程控制和多设备同步的 Windows 屏幕保护程序系统。

## 功能特性

- **多种内容展示**: 支持图片、视频、时钟等多种展示类型
- **远程控制**: 通过 WebHook 触发切换、暂停等操作
- **多设备同步**: 多个屏幕同时切换到相同内容
- **混合运行模式**: 支持系统屏保模式 + 常驻应用模式
- **离线运行**: 支持无服务器离线模式

## 项目结构

```
StatusScreenSaver/
├── client/                    # 客户端代码
│   ├── tray_app/              # 常驻应用（本地管理端）
│   │   ├── main.py            # 入口文件
│   │   ├── config.yaml        # 配置文件
│   │   └── core/              # 核心模块
│   │
│   ├── screensaver_scr/       # .scr 屏保程序（实际执行端）
│   │   ├── main.py            # 入口文件
│   │   └── core/              # 核心模块
│   │
│   └── contents/              # 本地内容文件
│       ├── images/
│       └── videos/
│
├── server/                    # 公网服务器
│   ├── main.py                # FastAPI 入口
│   ├── auth.py                # 认证模块
│   ├── device_manager.py      # 设备管理器
│   └── websocket_manager.py   # WebSocket 管理
│
├── scripts/                   # 脚本
│   ├── build.bat              # 打包脚本
│   ├── install.bat            # 安装脚本
│   └── start_*.bat            # 启动脚本
│
└── StatusScreenSaver_Overall.md  # 技术方案文档
```

## 快速开始

### 1. 安装依赖

```bash
# 服务端
cd server
pip install -r requirements.txt

# 客户端
cd client/tray_app
pip install -r requirements.txt

cd ../screensaver_scr
pip install -r requirements.txt
```

### 2. 启动服务端

```bash
cd server
python main.py
```

服务端将在 `http://localhost:9876` 启动，API 文档位于 `http://localhost:9876/docs`。

### 3. 启动常驻应用

```bash
cd client/tray_app
python main.py
```

常驻应用将在系统托盘显示图标。

### 4. 测试屏保程序

```bash
cd client/screensaver_scr
python main.py /s
```

## 打包与部署

### 打包

```bash
cd scripts
build.bat
```

### 安装系统屏保

```bash
cd scripts
install.bat
```

### 卸载

```bash
cd scripts
uninstall.bat
```

## 配置说明

编辑 `client/tray_app/config.yaml`：

```yaml
# 服务器配置
server:
  url: "ws://your-server:8000/ws"
  offline_mode: false

# 设备信息
device:
  name: "会议室A"
  location: "三楼大厅"

# 内容列表
contents:
  - type: image
    path: "../contents/images/poster1.jpg"
    duration: 20
  - type: video
    path: "../contents/videos/promo.mp4"
    duration: null
  - type: clock
    duration: 10
    mode: "datetime"
```

## API 使用

### 获取设备列表

```bash
curl -H "X-API-Key: sk_default_key_change_me" http://localhost:9876/devices
```

### 广播切换指令

```bash
curl -X POST http://localhost:9876/broadcast \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_default_key_change_me" \
  -d '{"command": {"action": "next"}}'
```

### 向指定设备发送指令

```bash
curl -X POST http://localhost:9876/device/{device_id}/command \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_default_key_change_me" \
  -d '{"action": "switch", "index": 1}'
```

## 视频格式支持

推荐格式：
- MP4 (H.264 视频编码 + AAC 音频)
- WMV
- AVI

其他格式需转码。

## 许可证

MIT License
