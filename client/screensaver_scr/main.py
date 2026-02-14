#!/usr/bin/env python3
"""
屏幕保护程序 - .scr 屏保（实际执行端）

启动参数：
  /s  - 正常屏保模式（全屏显示）
  /c  - 配置模式（显示设置对话框）
  /p  - 预览模式（在指定窗口中预览）
"""

import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication, QWidget, QMessageBox
from PySide6.QtCore import Qt

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core.window import ScreenSaverWindow
from core.ipc_client import IPCClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('statusscreensaver_scr.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def main():
    # 解析命令行参数
    if len(sys.argv) < 2:
        # 默认全屏模式
        mode = "/s"
    else:
        mode = sys.argv[1].lower()
    
    # 创建 Qt 应用
    app = QApplication(sys.argv)
    
    if mode == "/s":
        # 正常屏保模式
        run_screensaver(app)
    elif mode == "/c":
        # 配置模式
        run_config()
    elif mode == "/p":
        # 预览模式
        run_preview(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        # 默认全屏模式
        run_screensaver(app)


def run_screensaver(app):
    """运行屏保模式"""
    # 创建 IPC 客户端
    ipc_client = IPCClient({"pipe_name": "statusscreensaver_ipc"})
    
    if ipc_client.connect():
        logger.info("已连接到常驻应用")
        
        # 获取播放列表
        playlist_response = ipc_client.request("get_playlist")
        if playlist_response and playlist_response.get("type") == "playlist":
            playlist = playlist_response.get("data", [])
            logger.info(f"获取到播放列表，共 {len(playlist)} 个内容")
        else:
            playlist = []
            logger.warning("无法获取播放列表")
        
        # 获取当前内容
        content_response = ipc_client.request("get_content")
        
        # 创建全屏窗口
        window = ScreenSaverWindow(ipc_client)
        window.set_playlist(playlist)
        window.showFullScreen()
        
        # 显示初始内容
        if content_response and content_response.get("type") == "content":
            content = content_response.get("data")
            if content:
                window.show_content(content)
            elif playlist:
                window.switch_to(0)
            else:
                logger.warning("无可用内容")
        elif playlist:
            window.switch_to(0)
        else:
            logger.warning("无可用内容，请先添加播放列表")
        
        # 运行应用
        exit_code = app.exec()
        
        # 清理
        ipc_client.disconnect()
        sys.exit(exit_code)
    
    else:
        logger.error("无法连接到常驻应用，显示独立窗口")
        window = StandaloneWindow()
        window.showFullScreen()
        sys.exit(app.exec())


def run_config():
    """运行配置模式"""
    QMessageBox.information(
        None,
        "屏幕保护程序设置",
        "请通过系统托盘图标进行设置。\n\n"
        "如果托盘图标未显示，请先启动常驻应用。"
    )
    sys.exit(0)


def run_preview(hwnd):
    """运行预览模式"""
    # 简化实现，预览模式通常不需要
    pass


class StandaloneWindow(QWidget):
    """独立运行窗口（无常驻应用时）"""
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet("background-color: black;")
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
    
    def mousePressEvent(self, event):
        self.close()


if __name__ == "__main__":
    main()
