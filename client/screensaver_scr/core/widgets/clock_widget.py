"""
时钟组件
"""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

logger = logging.getLogger(__name__)


class ClockWidget(QWidget):
    """时钟显示组件"""
    
    def __init__(self):
        super().__init__()
        
        self.mode = "time_only"  # time_only / datetime
        self.timezone = None
        self.format_24h = True
        
        self._setup_ui()
        self._start_timer()
    
    def _setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
            QLabel {
                color: white;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 日期标签
        self.date_label = QLabel()
        self.date_label.setFont(QFont("Microsoft YaHei", 24))
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.hide()
        
        # 时间标签
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Consolas", 120))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.layout.addWidget(self.date_label)
        self.layout.addWidget(self.time_label)
    
    def configure(self, config: dict):
        """配置时钟"""
        self.mode = config.get("mode", "time_only")
        self.timezone = config.get("timezone")
        self.format_24h = config.get("format_24h", True)
        
        # 根据模式调整布局
        if self.mode == "datetime":
            self.date_label.show()
        else:
            self.date_label.hide()
        
        self._update_time()
    
    def _start_timer(self):
        self._update_time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)  # 每秒更新
    
    def _update_time(self):
        """更新时间显示"""
        # 获取时间
        now = datetime.now()
        if self.timezone:
            try:
                tz = ZoneInfo(self.timezone)
                now = datetime.now(tz)
            except Exception as e:
                logger.warning(f"无效的时区: {self.timezone}, {e}")
        
        # 格式化时间
        if self.format_24h:
            time_str = now.strftime("%H:%M:%S")
        else:
            time_str = now.strftime("%I:%M:%S %p")
        
        self.time_label.setText(time_str)
        
        # 格式化日期
        if self.mode == "datetime":
            date_str = now.strftime("%Y年%m月%d日 %A")
            self.date_label.setText(date_str)
