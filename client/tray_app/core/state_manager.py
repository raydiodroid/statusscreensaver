"""
状态持久化模块
"""

import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class StateManager:
    """状态管理器"""
    
    def __init__(self, config: dict):
        self.state_file = Path(config.get("file", "state.json"))
        self.state = {
            "device_id": None,
            "token": None,
            "current_index": 0,
            "last_content": None,
            "last_status": None,
            "last_update": None
        }
    
    def load(self):
        """从文件加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.state.update(loaded)
                logger.info("状态已从文件加载")
            except Exception as e:
                logger.error(f"加载状态失败: {e}")
    
    def save(self):
        """保存状态到文件"""
        try:
            self.state["last_update"] = datetime.now().isoformat()
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            logger.debug("状态已保存")
        except Exception as e:
            logger.error(f"保存状态失败: {e}")
    
    def update(self, key: str, value):
        """更新状态"""
        self.state[key] = value
    
    def get(self, key: str, default=None):
        """获取状态"""
        return self.state.get(key, default)
    
    def reset(self):
        """重置状态"""
        self.state = {
            "device_id": None,
            "token": None,
            "current_index": 0,
            "last_content": None,
            "last_status": None,
            "last_update": datetime.now().isoformat()
        }
