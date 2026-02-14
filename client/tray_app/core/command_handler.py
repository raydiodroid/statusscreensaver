"""
指令处理器模块
"""

import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class CommandHandler:
    """指令处理器"""
    
    def __init__(self, playlist, ipc_server, state_manager):
        self.playlist = playlist
        self.ipc_server = ipc_server
        self.state_manager = state_manager
    
    def handle(self, command: dict):
        """处理指令"""
        action = command.get("action")
        logger.info(f"收到指令: {action}")
        
        if action == "switch":
            index = command.get("index", 0)
            self.playlist.switch_to(index)
            self.ipc_server.push_switch_content(index)
            
        elif action == "next":
            self.playlist.next()
            self.ipc_server.push_switch_content(self.playlist.current_index)
            
        elif action == "prev":
            self.playlist.prev()
            self.ipc_server.push_switch_content(self.playlist.current_index)
            
        elif action == "reload":
            # 重新加载配置
            import yaml
            try:
                with open("config.yaml", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                self.playlist.reload(config)
            except Exception as e:
                logger.error(f"重新加载配置失败: {e}")
            
        elif action == "set_content":
            # 动态设置内容
            content = command.get("content")
            if content:
                self.ipc_server.push_content_update(content)
                
        elif action == "download":
            # 下载内容
            content_url = command.get("url")
            filename = command.get("filename")
            logger.info(f"收到下载指令: {content_url}")
            # TODO: 实现下载逻辑
            
        else:
            logger.warning(f"未知指令: {action}")
