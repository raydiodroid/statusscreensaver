"""
图片组件
"""

import logging
from pathlib import Path
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

logger = logging.getLogger(__name__)


class ImageWidget(QLabel):
    """图片显示组件"""
    
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: transparent;")
        self._current_pixmap = None
        self._current_path = None
    
    def load_image(self, path: str) -> bool:
        """加载并显示图片"""
        self._current_path = path
        
        # 检查文件是否存在
        if not Path(path).exists():
            logger.error(f"图片文件不存在: {path}")
            return False
        
        self._current_pixmap = QPixmap(path)
        if self._current_pixmap.isNull():
            logger.error(f"无法加载图片: {path}")
            return False
        
        # 自适应窗口大小
        self._update_scaled_pixmap()
        return True
    
    def _update_scaled_pixmap(self):
        """更新缩放后的图片"""
        if self._current_pixmap and not self._current_pixmap.isNull():
            scaled = self._current_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled)
    
    def resizeEvent(self, event):
        """窗口大小改变时重新缩放图片"""
        super().resizeEvent(event)
        self._update_scaled_pixmap()
    
    def clear_image(self):
        """清除图片"""
        self.clear()
        self._current_pixmap = None
        self._current_path = None
