"""
播放列表管理模块
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class PlaylistManager:
    """播放列表管理器"""
    
    def __init__(self, config: dict):
        playlist_cfg = config.get("playlist", {})
        self.auto_play = playlist_cfg.get("auto_play", True)
        self.interval = playlist_cfg.get("interval", 30) * 1000  # 转为毫秒
        self.shuffle = playlist_cfg.get("shuffle", False)
        
        self.contents: List[Dict] = config.get("contents", [])
        self.current_index = 0
        self.is_playing = False
        
        # 回调
        self.on_content_change = None  # 内容切换回调
    
    def get_current_content(self) -> Optional[Dict]:
        """获取当前内容"""
        if self.contents and 0 <= self.current_index < len(self.contents):
            return self.contents[self.current_index]
        return None
    
    def get_all_contents(self) -> List[Dict]:
        """获取所有内容"""
        return self.contents
    
    def next(self):
        """下一个内容"""
        if not self.contents:
            return
        
        self.current_index = (self.current_index + 1) % len(self.contents)
        self._notify_change()
    
    def prev(self):
        """上一个内容"""
        if not self.contents:
            return
        
        self.current_index = (self.current_index - 1) % len(self.contents)
        self._notify_change()
    
    def switch_to(self, index: int):
        """切换到指定索引"""
        if 0 <= index < len(self.contents):
            self.current_index = index
            self._notify_change()
    
    def get_current_duration(self) -> float:
        """获取当前内容的显示时长（秒）"""
        content = self.get_current_content()
        if content:
            duration = content.get("duration")
            if duration is not None:
                return duration
            # 对于视频，返回 None 表示播完为止
            if content.get("type") == "video":
                return None
        return self.interval / 1000
    
    def _notify_change(self):
        """通知内容切换"""
        if self.on_content_change:
            self.on_content_change(self.get_current_content(), self.current_index)
    
    def reload(self, config: dict):
        """重新加载配置"""
        self.contents = config.get("contents", [])
        self.current_index = 0
        logger.info(f"播放列表已重新加载，共 {len(self.contents)} 个内容")
