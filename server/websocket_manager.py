"""
WebSocket 连接管理器
"""

from typing import Dict, Optional
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
    
    def connect(self, device_id: str, websocket: WebSocket):
        """添加连接"""
        self.connections[device_id] = websocket
        logger.info(f"WebSocket 连接: {device_id}")
    
    def disconnect(self, device_id: str):
        """断开连接"""
        if device_id in self.connections:
            del self.connections[device_id]
            logger.info(f"WebSocket 断开: {device_id}")
    
    def get(self, device_id: str) -> Optional[WebSocket]:
        """获取连接"""
        return self.connections.get(device_id)
    
    def is_connected(self, device_id: str) -> bool:
        """检查是否连接"""
        return device_id in self.connections
    
    def get_all_ids(self) -> list:
        """获取所有已连接设备ID"""
        return list(self.connections.keys())
    
    def count(self) -> int:
        """获取连接数"""
        return len(self.connections)
