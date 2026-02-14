#!/usr/bin/env python3
"""
屏幕保护程序 - 常驻应用（本地管理端）
"""

import sys
import yaml
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core.tray_icon import TrayIcon
from core.websocket_client import WebSocketClient
from core.playlist import PlaylistManager
from core.ipc_server import IPCServer
from core.state_manager import StateManager
from core.command_handler import CommandHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('statusscreensaver_tray.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    """加载配置文件"""
    # 尝试多个路径
    paths = [
        Path(config_path),
        Path(__file__).parent / config_path,
    ]
    
    for path in paths:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f)
    
    raise FileNotFoundError(f"配置文件不存在: {config_path}")


def save_config(config: dict, config_path: str = "config.yaml"):
    """保存配置文件"""
    paths = [
        Path(config_path),
        Path(__file__).parent / config_path,
    ]
    
    for path in paths:
        if path.exists():
            with open(path, encoding="utf-8", mode="w") as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
            logger.info(f"配置已保存: {path}")
            return
    
    # 如果文件不存在，保存到当前目录
    with open(config_path, encoding="utf-8", mode="w") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    logger.info(f"配置已保存: {config_path}")


def main():
    # 加载配置
    config = load_config()
    logger.info("配置加载完成")
    
    # 创建 Qt 应用
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出应用
    
    # 创建状态管理器
    state_manager = StateManager(config.get("state", {}))
    state_manager.load()
    logger.info("状态管理器已初始化")
    
    # 创建播放列表管理器
    playlist = PlaylistManager(config)
    current_index = state_manager.get("current_index", 0)
    playlist.current_index = current_index
    
    # 创建 IPC 服务端
    ipc_server = IPCServer(config.get("ipc", {}))
    ipc_server.start()
    logger.info("IPC 服务端已启动")
    
    # 注册 IPC 请求处理器
    def handle_ipc_request(request):
        req_type = request.get("type")
        
        if req_type == "get_content":
            return {
                "type": "content",
                "data": playlist.get_current_content()
            }
        elif req_type == "get_playlist":
            return {
                "type": "playlist",
                "data": playlist.get_all_contents()
            }
        elif req_type == "report_status":
            state_manager.update("last_status", request.get("data"))
            return {"type": "ack"}
        
        return {"type": "error", "message": "Unknown request"}
    
    ipc_server.on_request = handle_ipc_request
    
    # 创建 WebSocket 客户端
    ws_client = None
    server_cfg = config.get("server", {})
    
    if server_cfg.get("url") and not server_cfg.get("offline_mode"):
        ws_client = WebSocketClient(
            server_url=server_cfg["url"],
            token=state_manager.get("token"),
            device_id=state_manager.get("device_id"),
            device_name=config["device"]["name"],
            device_location=config["device"].get("location"),
            heartbeat_interval=server_cfg.get("heartbeat_interval", 30),
            reconnect_interval=server_cfg.get("reconnect_interval", 5)
        )
        
        # 创建指令处理器
        command_handler = CommandHandler(playlist, ipc_server, state_manager)
        ws_client.on_command = command_handler.handle
        
        # 连接状态回调
        def on_connected(device_id, token):
            logger.info(f"已连接到服务器，设备ID: {device_id}")
            state_manager.update("device_id", device_id)
            state_manager.update("token", token)
            state_manager.save()
        
        def on_disconnected():
            logger.warning("与服务器断开连接")
        
        ws_client.on_connected = on_connected
        ws_client.on_disconnected = on_disconnected
        
        # 启动 WebSocket 客户端
        ws_client.start()
        logger.info("WebSocket 客户端已启动")
    
    # 创建系统托盘图标
    tray_icon = TrayIcon(config, playlist, ipc_server)
    tray_icon.show()
    logger.info("系统托盘图标已创建")
    
    # 显示全屏屏保
    def on_show_fullscreen():
        import subprocess
        import os
        try:
            # 获取屏保程序路径
            if getattr(sys, 'frozen', False):
                # 打包后，屏保在同一目录
                exe_dir = Path(sys.executable).parent
            else:
                # 开发模式，在 dist 目录
                exe_dir = Path(__file__).parent.parent.parent / "dist"
            
            scr_path = exe_dir / "statusscreensaver.scr"
            if not scr_path.exists():
                scr_path = exe_dir / "statusscreensaver.exe"
            
            if scr_path.exists():
                subprocess.Popen([str(scr_path), "/s"], cwd=str(exe_dir))
                logger.info(f"已启动屏保: {scr_path}")
            else:
                tray_icon.show_message("错误", "未找到屏保程序")
                logger.error(f"屏保程序不存在: {scr_path}")
        except Exception as e:
            logger.error(f"启动屏保失败: {e}")
            tray_icon.show_message("启动失败", str(e))
    
    tray_icon.show_fullscreen.connect(on_show_fullscreen)
    
    # 退出应用
    def on_exit():
        logger.info("用户请求退出")
        QApplication.quit()
    
    tray_icon.exit_app.connect(on_exit)
    
    # 重新加载配置
    def on_reload_config():
        nonlocal config
        try:
            config = load_config()
            playlist.reload(config)
            tray_icon.show_message("配置重载", "配置已重新加载")
            logger.info("配置已重新加载")
        except Exception as e:
            logger.error(f"重载配置失败: {e}")
            tray_icon.show_message("配置重载失败", str(e))
    
    tray_icon.reload_config.connect(on_reload_config)
    
    # 内容管理对话框
    def on_manage_content():
        from core.content_dialog import ContentManagerDialog
        dialog = ContentManagerDialog(config)
        if dialog.exec():
            # 内容已更新
            new_contents = dialog.get_contents()
            config["contents"] = new_contents
            playlist.reload(config)
            # 保存配置
            save_config(config)
            tray_icon.show_message("内容管理", f"已更新 {len(new_contents)} 个内容")
    
    tray_icon.manage_content.connect(on_manage_content)
    
    # 设置对话框
    def on_open_settings():
        from core.config_dialog import ConfigDialog
        dialog = ConfigDialog(config, save_callback=save_config)
        if dialog.exec():
            # 配置已更新，重新加载
            playlist.reload(config)
            logger.info("配置已更新")
    
    tray_icon.open_settings.connect(on_open_settings)
    
    # 内容切换回调 - 同步到 IPC
    def on_content_change(content, index):
        state_manager.update("current_index", index)
        ipc_server.push_switch_content(index)
    
    playlist.on_content_change = on_content_change
    
    # 自动保存状态定时器
    save_timer = None
    if config.get("state", {}).get("auto_save", True):
        save_timer = QTimer()
        save_timer.timeout.connect(state_manager.save)
        save_timer.start(config["state"].get("auto_save_interval", 60) * 1000)
    
    # 运行应用
    exit_code = app.exec()
    
    # 清理
    ipc_server.stop()
    if ws_client:
        ws_client.stop()
    state_manager.save()
    
    logger.info(f"程序退出，代码: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
