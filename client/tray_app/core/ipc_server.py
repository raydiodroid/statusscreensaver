"""
IPC 服务端模块 - 使用命名管道与 .scr 屏保通信
"""

import json
import threading
import logging
import queue

logger = logging.getLogger(__name__)

try:
    import win32pipe
    import win32file
    import pywintypes
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    logger.warning("pywin32 未安装，IPC 功能将不可用")


class IPCServer:
    """IPC 服务端"""
    
    def __init__(self, config: dict):
        self.pipe_name = config.get("pipe_name", "statusscreensaver_ipc")
        self.max_clients = config.get("max_clients", 5)
        self.running = False
        self.clients = {}
        self.client_counter = 0
        self.on_request = None
        
        # 推送消息队列
        self.push_queue = queue.Queue()
        
        self._thread = None
        self._push_thread = None
    
    def start(self):
        """启动 IPC 服务"""
        if not HAS_WIN32:
            logger.error("无法启动 IPC 服务：pywin32 未安装")
            return
        
        self.running = True
        self._thread = threading.Thread(target=self._run_server, daemon=True)
        self._thread.start()
        
        # 启动推送线程
        self._push_thread = threading.Thread(target=self._push_loop, daemon=True)
        self._push_thread.start()
        
        logger.info(f"IPC 服务端已启动: {self.pipe_name}")
    
    def stop(self):
        """停止 IPC 服务"""
        self.running = False
        logger.info("IPC 服务端已停止")
    
    def _run_server(self):
        """运行服务主循环"""
        while self.running:
            try:
                self._handle_client()
            except Exception as e:
                logger.error(f"IPC 服务错误: {e}")
    
    def _handle_client(self):
        """处理客户端连接"""
        pipe_path = f"\\\\.\\pipe\\{self.pipe_name}"
        pipe = None
        client_id = None
        
        try:
            # 创建命名管道
            pipe = win32pipe.CreateNamedPipe(
                pipe_path,
                win32pipe.PIPE_ACCESS_DUPLEX,
                win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                self.max_clients,
                65536, 65536,
                0, None
            )
            
            # 等待客户端连接（阻塞模式）
            win32pipe.ConnectNamedPipe(pipe, None)
            
            self.client_counter += 1
            client_id = f"client_{self.client_counter}"
            self.clients[client_id] = pipe
            
            logger.info(f"IPC 客户端已连接: {client_id}")
            
            # 处理消息
            while self.running:
                try:
                    # 读取消息
                    result, data = win32file.ReadFile(pipe, 65536)
                    message = data.decode('utf-8')
                    
                    # 处理请求
                    response = self._process_message(message)
                    
                    # 发送响应
                    win32file.WriteFile(pipe, response.encode('utf-8'))
                    
                except pywintypes.error as e:
                    if e.winerror == 109:  # 管道已关闭
                        break
                    if e.winerror == 232:  # 管道正在关闭
                        break
                    logger.error(f"IPC 读取错误: {e}")
                    break
                    
        except pywintypes.error as e:
            if e.winerror == 535:  # 管道正在等待连接（非阻塞模式）
                pass
            else:
                logger.error(f"IPC 客户端处理错误: {e}")
        except Exception as e:
            logger.error(f"IPC 客户端处理错误: {e}")
        finally:
            if client_id and client_id in self.clients:
                del self.clients[client_id]
            if pipe:
                try:
                    win32file.CloseHandle(pipe)
                except:
                    pass
            if client_id:
                logger.info(f"IPC 客户端已断开: {client_id}")
    
    def _process_message(self, message: str) -> str:
        """处理消息"""
        try:
            request = json.loads(message)
            
            if self.on_request:
                response = self.on_request(request)
            else:
                response = {"type": "error", "message": "No handler"}
            
            return json.dumps(response)
            
        except json.JSONDecodeError:
            return json.dumps({"type": "error", "message": "Invalid JSON"})
    
    def _push_loop(self):
        """推送消息循环"""
        while self.running:
            try:
                # 获取待推送的消息
                message = self.push_queue.get(timeout=1)
                self._broadcast_internal(message)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"IPC 推送错误: {e}")
    
    def _broadcast_internal(self, message: dict):
        """内部广播实现"""
        message_str = json.dumps(message)
        
        for client_id, pipe in list(self.clients.items()):
            try:
                win32file.WriteFile(pipe, message_str.encode('utf-8'))
            except Exception as e:
                logger.error(f"IPC 推送失败 ({client_id}): {e}")
    
    def broadcast(self, message: dict):
        """向所有连接的客户端推送消息"""
        self.push_queue.put(message)
    
    def push_switch_content(self, index: int):
        """推送内容切换消息"""
        self.broadcast({
            "type": "switch_content",
            "index": index
        })
    
    def push_content_update(self, content: dict):
        """推送内容更新消息"""
        self.broadcast({
            "type": "content_update",
            "content": content
        })
