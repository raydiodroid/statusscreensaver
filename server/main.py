"""
屏幕保护控制服务器 - 主入口
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import json
import logging

from auth import AuthManager
from device_manager import DeviceManager
from websocket_manager import WebSocketManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ============ FastAPI 应用 ============
app = FastAPI(
    title="StatusScreenSaver Control Server",
    description="屏幕保护程序控制服务器 API",
    version="2.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ 认证 ============
auth_manager = AuthManager()
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Depends(api_key_header)):
    """验证 API Key"""
    if not auth_manager.validate_api_key(api_key):
        raise HTTPException(401, "Invalid API Key")
    return api_key

# ============ 数据模型 ============
class DeviceInfo(BaseModel):
    id: str
    name: str
    location: Optional[str] = None
    connected: bool = False
    last_seen: Optional[str] = None
    current_content: Optional[dict] = None

class Command(BaseModel):
    action: str
    index: Optional[int] = None
    content: Optional[dict] = None

class BroadcastRequest(BaseModel):
    command: Command
    device_ids: Optional[List[str]] = None

class TokenRefreshRequest(BaseModel):
    device_id: str
    current_token: str

# ============ 全局状态 ============
device_manager = DeviceManager()
ws_manager = WebSocketManager()

# ============ WebSocket 端点 ============
@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """WebSocket 连接端点"""
    await websocket.accept()
    device_id = None
    
    try:
        # 首条消息必须是注册
        message = await websocket.receive_text()
        data = json.loads(message)
        
        if data.get("type") != "register":
            await websocket.close(code=4002, reason="Registration required")
            return
        
        # 验证 Token（如果有）
        if token:
            validated_id = auth_manager.validate_token(token)
            if not validated_id:
                await websocket.close(code=4001, reason="Invalid token")
                return
        
        # 注册设备
        name = data.get("name", "Unknown")
        location = data.get("location")
        device_id, new_token = device_manager.register(name, location)
        
        ws_manager.connect(device_id, websocket)
        
        # 发送注册确认
        await websocket.send(json.dumps({
            "type": "register_ack",
            "device_id": device_id,
            "token": new_token,
            "token_expires": (datetime.now() + timedelta(hours=24)).isoformat()
        }))
        
        logger.info(f"设备注册: {device_id} ({name})")
        
        # 消息循环
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "ping":
                device_manager.update_last_seen(device_id)
                await websocket.send(json.dumps({"type": "pong"}))
                
            elif msg_type == "status":
                device_manager.update_status(device_id, data.get("data"))
                
            elif msg_type == "pong":
                device_manager.update_last_seen(device_id)
                
    except WebSocketDisconnect:
        if device_id:
            ws_manager.disconnect(device_id)
            device_manager.set_offline(device_id)
            logger.info(f"设备断开: {device_id}")
    except Exception as e:
        logger.error(f"WebSocket 错误: {e}")
        if device_id:
            ws_manager.disconnect(device_id)
            device_manager.set_offline(device_id)

# ============ 认证 API ============
@app.post("/auth/refresh")
async def refresh_token(request: TokenRefreshRequest):
    """刷新 Token"""
    device = device_manager.get(request.device_id)
    if not device:
        raise HTTPException(404, "Device not found")
    
    new_token = auth_manager.refresh_token(request.current_token, request.device_id)
    if not new_token:
        raise HTTPException(401, "Token refresh failed")
    
    return {
        "token": new_token,
        "expires": (datetime.now() + timedelta(hours=24)).isoformat()
    }

# ============ HTTP API ============
@app.get("/")
def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "connected_devices": ws_manager.count()
    }

@app.get("/devices")
def list_devices(api_key: str = Depends(verify_api_key)):
    """获取所有设备列表"""
    return device_manager.list_devices()

@app.post("/device/{device_id}/command")
async def send_command(device_id: str, command: Command, api_key: str = Depends(verify_api_key)):
    """向指定设备发送指令"""
    if not device_manager.exists(device_id):
        raise HTTPException(404, f"设备不存在: {device_id}")
    
    cmd_dict = command.model_dump()
    
    if ws_manager.is_connected(device_id):
        ws = ws_manager.get(device_id)
        await ws.send(json.dumps({
            "type": "command",
            "command": cmd_dict
        }))
        return {"status": "sent", "device_id": device_id}
    else:
        return {"status": "offline", "device_id": device_id}

@app.post("/broadcast")
async def broadcast_command(request: BroadcastRequest, api_key: str = Depends(verify_api_key)):
    """广播指令到多个设备"""
    cmd_dict = request.command.model_dump()
    target_ids = request.device_ids or ws_manager.get_all_ids()
    
    results = {"sent": [], "offline": [], "not_found": []}
    
    for device_id in target_ids:
        if not device_manager.exists(device_id):
            results["not_found"].append(device_id)
            continue
        
        if ws_manager.is_connected(device_id):
            ws = ws_manager.get(device_id)
            await ws.send(json.dumps({
                "type": "command",
                "command": cmd_dict
            }))
            results["sent"].append(device_id)
        else:
            results["offline"].append(device_id)
    
    return {
        "status": "broadcasted",
        "command": cmd_dict,
        "results": results
    }

@app.delete("/device/{device_id}")
def remove_device(device_id: str, api_key: str = Depends(verify_api_key)):
    """移除设备"""
    device_manager.remove(device_id)
    ws_manager.disconnect(device_id)
    return {"status": "removed", "device_id": device_id}

# ============ 启动入口 ============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9876,
        reload=True,
        log_level="info"
    )
