"""
错误提示组件
"""

import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

logger = logging.getLogger(__name__)


class ErrorWidget(QWidget):
    """错误提示组件"""
    
    def __init__(self, display_time: int = 5):
        super().__init__()
        self.display_time = display_time  # 显示时长（秒）
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(20)
        
        # 错误图标
        self.icon_label = QLabel("⚠️")
        self.icon_label.setFont(QFont("Segoe UI Emoji", 64))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("color: #FF6B6B;")
        
        # 错误类型
        self.type_label = QLabel("内容无法显示")
        self.type_label.setFont(QFont("Microsoft YaHei", 28))
        self.type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.type_label.setStyleSheet("color: white;")
        
        # 错误详情
        self.detail_label = QLabel("")
        self.detail_label.setFont(QFont("Microsoft YaHei", 16))
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_label.setStyleSheet("color: #AAAAAA;")
        self.detail_label.setWordWrap(True)
        
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.type_label)
        self.layout.addWidget(self.detail_label)
    
    def set_message(self, message: str, error_type: str = "内容无法显示"):
        """设置错误消息"""
        self.type_label.setText(error_type)
        self.detail_label.setText(message)
    
    def show_temporary(self, callback=None):
        """临时显示，到期后执行回调"""
        if callback:
            QTimer.singleShot(self.display_time * 1000, callback)
