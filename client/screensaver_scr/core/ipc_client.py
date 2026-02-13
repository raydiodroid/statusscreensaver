"""
IPC 客户端模块
"""

import json
import threading
import time
import logging
import queue

logger = logging.getLogger(__name__)

try:
    import win32file
    import pywintypes
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    logger.warning("pywin32 未安装，IPC 功能将不可用")


class IPCClient:
    """IPC 客户端"""
    
    def __init__(self, config: dict):
        self.pipe_name = config.get("pipe_name", "statusscreensaver_ipc")
        self.connected = False
        self.pipe = None
        self._running = False
        self._listener = None
        
        # 推送消息队列
        self.message_queue = queue.Queue()
        
        # 回调
        self.on_switch_content = None
        self.on_content_update = None
        self.on_pause = None
        self.on_resume = None
    
    def connect(self) -> bool:
        """连接到服务端"""
        if not HAS_WIN32:
            logger.error("无法连接 IPC：pywin32 未安装")
            return False
        
        pipe_path = f"\\\\.\\pipe\\{self.pipe_name}"
        
        try:
            self.pipe = win32file.CreateFile(
                pipe_path,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0, None,
                win32file.OPEN_EXISTING,
                0, None
            )
            
            # 设置消息模式
            win32file.SetNamedPipeHandleState(
                self.pipe,
                win32file.PIPE_READMODE_MESSAGE,
                None, None
            )
            
            self.connected = True
            self._running = True
            
            # 启动监听线程
            self._listener = threading.Thread(target=self._listen, daemon=True)
            self._listener.start()
            
            logger.info("已连接到 IPC 服务端")
            return True
            
        except pywintypes.error as e:
            logger.error(f"连接 IPC 服务端失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        self._running = False
        self.connected = False
        if self.pipe:
            try:
                win32file.CloseHandle(self.pipe)
            except:
                pass
        logger.info("已断开 IPC 连接")
    
    def request(self, request_type: str, data: dict = None) -> dict:
        """发送请求并等待响应"""
        if not self.connected:
            return None
        
        message = {"type": request_type}
        if data:
            message.update(data)
        
        try:
            # 发送请求
            win32file.WriteFile(self.pipe, json.dumps(message).encode('utf-8'))
            
            # 接收响应
            result, response = win32file.ReadFile(self.pipe, 65536)
            return json.loads(response.decode('utf-8'))
            
        except Exception as e:
            logger.error(f"IPC 请求失败: {e}")
            return None
    
    def _listen(self):
        """监听推送消息"""
        while self._running and self.connected:
            try:
                # 尝试读取推送消息（非阻塞）
                time.sleep(0.1)
                
                # 定期发送心跳请求来获取可能的推送消息
                # 这是一个简化的实现，实际的推送需要服务端支持
            except Exception:
                break
    
    def get_message(self, timeout: float = 0.1) -> dict:
        """获取推送消息"""
        try:
            return self.message_queue.get(timeout=timeout)
        except queue.Empty:
            return None
