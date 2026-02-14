"""
设备管理器 - 支持持久化
"""

import json
import secrets
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class DeviceManager:
    """设备管理器"""
    
    def __init__(self, storage_file: str = "devices.json"):
        self.storage_file = Path(storage_file)
        self.devices: Dict[str, dict] = {}
        self._load()
    
    def _load(self):
        """从文件加载设备数据"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.devices = data.get("devices", {})
                logger.info(f"已加载 {len(self.devices)} 个设备")
            except Exception as e:
                logger.error(f"加载设备数据失败: {e}")
                self.devices = {}
        else:
            logger.info(f"设备数据文件不存在，将创建新文件: {self.storage_file}")
    
    def _save(self):
        """保存设备数据到文件"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "devices": self.devices,
                    "updated_at": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
            logger.debug(f"设备数据已保存到 {self.storage_file}")
        except Exception as e:
            logger.error(f"保存设备数据失败: {e}")
            raise
    
    def register(self, name: str, location: str = None, token: str = None) -> tuple:
        """注册设备，返回 (device_id, token)"""
        # 查找是否已存在同名设备
        for device_id, device in self.devices.items():
            if device["name"] == name:
                # 恢复已有设备
                device["connected"] = True
                device["last_seen"] = datetime.now().isoformat()
                self._save()
                return device_id, device.get("token")
        
        # 创建新设备
        device_id = str(secrets.token_hex(4))  # 8位ID
        token = token or secrets.token_hex(16)
        
        self.devices[device_id] = {
            "id": device_id,
            "name": name,
            "location": location,
            "connected": True,
            "last_seen": datetime.now().isoformat(),
            "current_content": None,
            "token": token,
            "created_at": datetime.now().isoformat()
        }
        
        self._save()
        return device_id, token
    
    def set_offline(self, device_id: str):
        """设置设备离线"""
        if device_id in self.devices:
            self.devices[device_id]["connected"] = False
            self._save()
    
    def update_last_seen(self, device_id: str):
        """更新最后在线时间"""
        if device_id in self.devices:
            self.devices[device_id]["last_seen"] = datetime.now().isoformat()
    
    def update_status(self, device_id: str, status: dict):
        """更新设备状态"""
        if device_id in self.devices:
            self.devices[device_id].update(status)
            self.devices[device_id]["last_seen"] = datetime.now().isoformat()
    
    def get(self, device_id: str) -> Optional[dict]:
        """获取设备信息"""
        return self.devices.get(device_id)
    
    def exists(self, device_id: str) -> bool:
        """检查设备是否存在"""
        return device_id in self.devices
    
    def list_devices(self) -> List[dict]:
        """获取所有设备列表"""
        return list(self.devices.values())
    
    def remove(self, device_id: str):
        """移除设备"""
        if device_id in self.devices:
            del self.devices[device_id]
            self._save()
