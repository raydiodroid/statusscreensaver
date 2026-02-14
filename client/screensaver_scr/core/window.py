"""
全屏窗口模块
"""

import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Qt, QTimer

from .widgets import ImageWidget, VideoWidget, ClockWidget, ErrorWidget

logger = logging.getLogger(__name__)


class ScreenSaverWindow(QWidget):
    """屏幕保护全屏窗口"""
    
    def __init__(self, ipc_client=None):
        super().__init__()
        self.ipc_client = ipc_client
        self.current_content = None
        self.playlist = []
        self.current_index = 0
        
        self._setup_ui()
        self._create_widgets()
        self._setup_ipc_listener()
    
    def _setup_ui(self):
        """设置窗口属性"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet("background-color: #000000;")
        
        # 布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 内容堆栈
        self.content_stack = QStackedWidget()
        self.layout.addWidget(self.content_stack)
    
    def _create_widgets(self):
        """创建内容组件"""
        self.image_widget = ImageWidget()
        self.video_widget = VideoWidget()
        self.clock_widget = ClockWidget()
        self.error_widget = ErrorWidget()
        
        # 视频播放完成回调
        self.video_widget.on_finished = self._on_video_finished
        
        self.content_stack.addWidget(self.image_widget)   # index 0
        self.content_stack.addWidget(self.video_widget)   # index 1
        self.content_stack.addWidget(self.clock_widget)   # index 2
        self.content_stack.addWidget(self.error_widget)   # index 3
    
    def _setup_ipc_listener(self):
        """设置 IPC 消息监听"""
        if self.ipc_client:
            # 定时检查 IPC 消息
            self.ipc_timer = QTimer(self)
            self.ipc_timer.timeout.connect(self._check_ipc_messages)
            self.ipc_timer.start(100)  # 每100ms检查一次
    
    def _check_ipc_messages(self):
        """检查 IPC 推送消息"""
        if not self.ipc_client:
            return
        
        message = self.ipc_client.get_message()
        if message:
            self._handle_ipc_message(message)
    
    def _handle_ipc_message(self, message: dict):
        """处理 IPC 消息"""
        msg_type = message.get("type")
        
        if msg_type == "switch_content":
            index = message.get("index", 0)
            self.switch_to(index)
        
        elif msg_type == "content_update":
            content = message.get("content")
            if content:
                self.show_content(content)
    
    def set_playlist(self, playlist: list):
        """设置播放列表"""
        self.playlist = playlist
    
    def show_content(self, content: dict):
        """显示内容"""
        self.current_content = content
        content_type = content.get("type")
        
        try:
            if content_type == "image":
                self.video_widget.stop()
                if self.image_widget.load_image(content["path"]):
                    self.content_stack.setCurrentIndex(0)
                else:
                    self.show_error("图片加载失败", content["path"])
                
            elif content_type == "video":
                if self.video_widget.play(content["path"], loop=True):
                    self.content_stack.setCurrentIndex(1)
                else:
                    self.show_error("视频播放失败", content["path"])
                
            elif content_type == "clock":
                self.video_widget.stop()
                self.clock_widget.configure(content)
                self.content_stack.setCurrentIndex(2)
            
            logger.info(f"显示内容: {content_type}")
            
        except Exception as e:
            logger.error(f"内容显示失败: {e}")
            self.show_error("内容显示错误", str(e))
    
    def show_error(self, error_type: str, detail: str):
        """显示错误提示"""
        self.video_widget.stop()
        self.error_widget.set_message(detail, error_type)
        self.content_stack.setCurrentIndex(3)
    
    def switch_to(self, index: int):
        """切换到指定索引"""
        if 0 <= index < len(self.playlist):
            self.current_index = index
            self.show_content(self.playlist[index])
    
    def next_content(self):
        """下一个内容"""
        if self.playlist:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.show_content(self.playlist[self.current_index])
    
    def prev_content(self):
        """上一个内容"""
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)
            self.show_content(self.playlist[self.current_index])
    
    def _on_video_finished(self):
        """视频播放完成"""
        # 如果不循环播放，切换到下一个
        pass
    
    def keyPressEvent(self, event):
        """按键事件"""
        # 任意键退出
        self.close()
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        self.close()
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.video_widget.stop()
        super().closeEvent(event)
