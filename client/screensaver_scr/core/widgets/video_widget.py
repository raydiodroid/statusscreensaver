"""
视频组件
"""

import logging
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

logger = logging.getLogger(__name__)


class VideoWidget(QWidget):
    """视频播放组件"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._current_path = None
        self._is_playing = False
        self.on_finished = None  # 播放完成回调
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: black;")
        
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setAudioOutput(self.audio_output)
        
        # 连接信号
        self.media_player.mediaStatusChanged.connect(self._on_media_status_changed)
        self.media_player.errorOccurred.connect(self._on_error)
        
        layout.addWidget(self.video_widget)
    
    def play(self, path: str, loop: bool = True) -> bool:
        """播放视频"""
        self._current_path = path
        
        # 检查文件是否存在
        if not Path(path).exists():
            logger.error(f"视频文件不存在: {path}")
            return False
        
        try:
            self.media_player.setSource(QUrl.fromLocalFile(path))
            self.media_player.play()
            self._is_playing = True
            self._loop = loop
            logger.info(f"开始播放视频: {path}")
            return True
        except Exception as e:
            logger.error(f"播放视频失败: {e}")
            return False
    
    def stop(self):
        """停止播放"""
        self.media_player.stop()
        self._is_playing = False
    
    def pause(self):
        """暂停播放"""
        self.media_player.pause()
    
    def resume(self):
        """恢复播放"""
        self.media_player.play()
    
    def set_volume(self, volume: float):
        """设置音量 (0.0 - 1.0)"""
        self.audio_output.setVolume(volume)
    
    def _on_media_status_changed(self, status):
        """媒体状态变化"""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self._loop:
                self.media_player.setPosition(0)
                self.media_player.play()
            elif self.on_finished:
                self.on_finished()
    
    def _on_error(self, error):
        """播放错误"""
        error_string = self.media_player.errorString()
        logger.error(f"视频播放错误: {error_string}")
