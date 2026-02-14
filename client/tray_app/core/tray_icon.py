"""
系统托盘图标模块
"""

import logging
from pathlib import Path
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import pyqtSignal, QObject

logger = logging.getLogger(__name__)


class TrayIcon(QObject):
    """系统托盘图标"""
    
    # 信号
    show_fullscreen = pyqtSignal()
    exit_app = pyqtSignal()
    next_content = pyqtSignal()
    prev_content = pyqtSignal()
    reload_config = pyqtSignal()
    manage_content = pyqtSignal()  # 内容管理信号
    open_settings = pyqtSignal()   # 设置信号
    
    def __init__(self, config, playlist, ipc_server):
        super().__init__()
        self.config = config
        self.playlist = playlist
        self.ipc_server = ipc_server
        
        self._create_tray_icon()
        self._create_menu()
    
    def _create_tray_icon(self):
        """创建托盘图标"""
        # 尝试加载图标文件
        icon_path = Path(__file__).parent.parent / "assets" / "tray_icon.png"
        
        if icon_path.exists():
            self.icon = QIcon(str(icon_path))
        else:
            # 尝试从资源目录加载（PyInstaller 打包后）
            import sys
            if getattr(sys, 'frozen', False):
                bundle_path = Path(sys._MEIPASS) / "assets" / "tray_icon.png"
                if bundle_path.exists():
                    self.icon = QIcon(str(bundle_path))
                else:
                    self.icon = self._create_default_icon()
            else:
                self.icon = self._create_default_icon()
        
        self.tray = QSystemTrayIcon(self.icon)
        self.tray.setToolTip("StatusScreenSaver")
    
    def _create_default_icon(self):
        """创建默认图标"""
        from PySide6.QtGui import QPixmap
        from PySide6.QtCore import Qt
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.blue)
        return QIcon(pixmap)
    
    def _create_menu(self):
        """创建右键菜单"""
        self.menu = QMenu()
        
        # 显示全屏
        show_action = QAction("🖥️ 显示全屏", self.menu)
        show_action.triggered.connect(lambda: self.show_fullscreen.emit())
        self.menu.addAction(show_action)
        
        self.menu.addSeparator()
        
        # 下一个/上一个
        next_action = QAction("⏭️ 下一个内容", self.menu)
        next_action.triggered.connect(self._on_next)
        self.menu.addAction(next_action)
        
        prev_action = QAction("⏮️ 上一个内容", self.menu)
        prev_action.triggered.connect(self._on_prev)
        self.menu.addAction(prev_action)
        
        self.menu.addSeparator()
        
        # 内容管理
        manage_action = QAction("📁 内容管理...", self.menu)
        manage_action.triggered.connect(lambda: self.manage_content.emit())
        self.menu.addAction(manage_action)
        
        # 设置
        settings_action = QAction("⚙️ 设置...", self.menu)
        settings_action.triggered.connect(lambda: self.open_settings.emit())
        self.menu.addAction(settings_action)
        
        # 重新加载配置
        reload_action = QAction("🔄 重新加载配置", self.menu)
        reload_action.triggered.connect(lambda: self.reload_config.emit())
        self.menu.addAction(reload_action)
        
        self.menu.addSeparator()
        
        # 退出
        exit_action = QAction("❌ 退出", self.menu)
        exit_action.triggered.connect(lambda: self.exit_app.emit())
        self.menu.addAction(exit_action)
        
        self.tray.setContextMenu(self.menu)
        
        # 双击显示全屏
        self.tray.activated.connect(self._on_activated)
    
    def _on_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_fullscreen.emit()
    
    def _on_next(self):
        """下一个内容"""
        self.playlist.next()
        self.ipc_server.push_switch_content(self.playlist.current_index)
    
    def _on_prev(self):
        """上一个内容"""
        self.playlist.prev()
        self.ipc_server.push_switch_content(self.playlist.current_index)
    
    def show(self):
        """显示托盘图标"""
        self.tray.show()
        logger.info("托盘图标已显示")
    
    def hide(self):
        """隐藏托盘图标"""
        self.tray.hide()
    
    def show_message(self, title: str, message: str):
        """显示消息"""
        self.tray.showMessage(title, message)
