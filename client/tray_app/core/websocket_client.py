"""
WebSocket 客户端模块
"""

import asyncio
import json
import threading
import time
import logging
from typing import Callable, Optional
import websockets
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger(__name__)


class WebSocketClient:
    """WebSocket 客户端"""
    
    def __init__(
        self,
        server_url: str,
        token: str = None,
        device_id: str = None,
        device_name: str = "Unknown",
        device_location: str = None,
        heartbeat_interval: float = 30.0,
        reconnect_interval: float = 5.0
    ):
        self.server_url = server_url
        self.token = token
        self.device_id = device_id
        self.device_name = device_name
        self.device_location = device_location
        self.heartbeat_interval = heartbeat_interval
        self.reconnect_interval = reconnect_interval
        
        # 连接状态
        self.connected = False
        self.running = False
        
        # 回调函数
        self.on_command: Optional[Callable] = None
        self.on_connected: Optional[Callable] = None
        self.on_disconnected: Optional[Callable] = None
        
        # WebSocket 连接
        self._ws = None
        self._loop = None
        self._thread = None
    
    def start(self):
        """启动客户端"""
        if self.running:
            return
        
        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("WebSocket 客户端线程已启动")
    
    def stop(self):
        """停止客户端"""
        self.running = False
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._disconnect(), self._loop)
        logger.info("WebSocket 客户端已停止")
    
    def _run_loop(self):
        """主循环（在独立线程中运行）"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        while self.running:
            try:
                self._loop.run_until_complete(self._connect_and_run())
            except Exception as e:
                logger.error(f"连接错误: {e}")
            
            if self.running:
                logger.info(f"{self.reconnect_interval}秒后重连...")
                time.sleep(self.reconnect_interval)
    
    async def _connect_and_run(self):
        """建立连接并运行"""
        try:
            async with websockets.connect(
                self.server_url,
                ping_interval=None,  # 我们自己管理心跳
                close_timeout=5
            ) as ws:
                self._ws = ws
                self.connected = True
                
                # 发送注册消息
                await self._register()
                
                # 连接成功回调
                if self.on_connected:
                    self.on_connected(self.device_id, self.token)
                
                logger.info(f"已连接到服务器: {self.server_url}")
                
                # 启动心跳任务
                heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                
                # 接收消息循环
                try:
                    async for message in ws:
                        await self._handle_message(message)
                except ConnectionClosed:
                    pass
                finally:
                    heartbeat_task.cancel()
                    
        except Exception as e:
            logger.error(f"连接失败: {e}")
        finally:
            self.connected = False
            self._ws = None
            
            if self.on_disconnected:
                self.on_disconnected()
    
    async def _register(self):
        """向服务器注册设备"""
        register_msg = {
            "type": "register",
            "name": self.device_name,
            "location": self.device_location
        }
        await self._ws.send(json.dumps(register_msg))
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        while self.connected and self.running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                if self._ws:
                    await self._ws.send(json.dumps({"type": "ping"}))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"心跳发送失败: {e}")
                break
    
    async def _handle_message(self, message: str):
        """处理收到的消息"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "register_ack":
                # 注册确认
                self.device_id = data.get("device_id")
                self.token = data.get("token")
                logger.info(f"设备注册成功: {self.device_id}")
                
            elif msg_type == "pong":
                # 心跳响应
                pass
                
            elif msg_type == "command":
                # 执行指令
                if self.on_command:
                    self.on_command(data.get("command"))
                    
            else:
                logger.warning(f"未知消息类型: {msg_type}")
                
        except json.JSONDecodeError:
            logger.error(f"无效的JSON消息: {message}")
    
    async def _disconnect(self):
        """断开连接"""
        if self._ws:
            await self._ws.close()
    
    def send_status(self, status: dict):
        """发送状态更新"""
        if self._ws and self.connected and self._loop:
            msg = {
                "type": "status",
                "device_id": self.device_id,
                "data": status
            }
            asyncio.run_coroutine_threadsafe(
                self._ws.send(json.dumps(msg)),
                self._loop
            )
