"""
认证模块 - API Key 和 Token 管理
"""

import os
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional


class AuthManager:
    """认证管理器"""
    
    def __init__(self, jwt_secret: str = None):
        # API Keys（从环境变量读取）
        # 格式: SCREENSAVER_API_KEY=your-key-here 或多个用逗号分隔
        env_api_key = os.environ.get("SCREENSAVER_API_KEY", "")
        
        if env_api_key:
            # 支持多个 API Key，用逗号分隔
            self.api_keys = {key.strip(): f"key_{i}" for i, key in enumerate(env_api_key.split(","))}
        else:
            # 默认 API Key（生产环境应设置环境变量）
            self.api_keys = {
                "sk_default_key_change_me": "default",
            }
        
        # JWT 配置（可从环境变量读取）
        self.jwt_secret = jwt_secret or os.environ.get("SCREENSAVER_JWT_SECRET") or secrets.token_hex(32)
        self.jwt_algorithm = "HS256"
        self.token_expire_hours = int(os.environ.get("SCREENSAVER_TOKEN_EXPIRE_HOURS", "24"))
    
    # ========== API Key 管理 ==========
    
    def validate_api_key(self, api_key: str) -> bool:
        """验证 API Key"""
        return api_key in self.api_keys
    
    def generate_api_key(self, name: str) -> str:
        """生成新的 API Key"""
        key = f"sk_{secrets.token_hex(16)}"
        self.api_keys[key] = name
        return key
    
    # ========== Token 管理 ==========
    
    def generate_token(self, device_id: str) -> str:
        """生成 Token"""
        payload = {
            "device_id": device_id,
            "exp": datetime.utcnow() + timedelta(hours=self.token_expire_hours),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def validate_token(self, token: str) -> Optional[str]:
        """验证 Token，返回 device_id 或 None"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload.get("device_id")
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_token(self, current_token: str, device_id: str) -> Optional[str]:
        """刷新 Token"""
        try:
            payload = jwt.decode(
                current_token, 
                self.jwt_secret, 
                algorithms=[self.jwt_algorithm],
                options={"verify_exp": False}  # 允许过期 Token 刷新
            )
            
            if payload.get("device_id") != device_id:
                return None
            
            return self.generate_token(device_id)
            
        except jwt.InvalidTokenError:
            return None
