# StatusScreenSaver 服务端部署指南

## 方案一：直接运行（开发/测试）

```bash
# 安装依赖
cd server
pip install -r requirements.txt

# 启动服务
python main.py

# 或使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

服务将在 `http://0.0.0.0:9876` 启动。

---

## 方案二：Systemd 服务（Linux 生产环境）

### 1. 创建服务文件

```bash
sudo nano /etc/systemd/system/screensaver-server.service
```

内容：

```ini
[Unit]
Description=StatusScreenSaver Control Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/statusscreensaver-server
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 9876
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

### 2. 部署代码

```bash
# 创建目录
sudo mkdir -p /opt/screensaver-server

# 复制代码
sudo cp server/* /opt/screensaver-server/

# 安装依赖
cd /opt/screensaver-server
sudo pip install -r requirements.txt
```

### 3. 启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable statusscreensaver-server
sudo systemctl start statusscreensaver-server

# 查看状态
sudo systemctl status statusscreensaver-server

# 查看日志
sudo journalctl -u statusscreensaver-server -f
```

---

## 方案三：Docker 部署

### 1. 创建 Dockerfile

在 `server/` 目录创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 构建镜像

```bash
cd server
docker build -t statusscreensaver .
```

### 3. 运行容器

```bash
# 基本运行
docker run -d -p 8000:8000 --name screensaver-server screensaver-server

# 挂载持久化数据
docker run -d -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  --name screensaver-server \
  screensaver-server
```

### 4. Docker Compose（推荐）

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  screensaver-server:
    build: .
    ports:
      - "9876:9876"
    volumes:
      - ./data:/app/data
    restart: always
    environment:
      - TZ=Asia/Shanghai
```

运行：

```bash
docker-compose up -d
```

---

## 方案四：Nginx 反向代理（生产环境推荐）

### 1. 安装 Nginx

```bash
sudo apt install nginx
```

### 2. 配置 SSL 证书

```bash
# 使用 Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. Nginx 配置

```nginx
# /etc/nginx/sites-available/screensaver
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # WebSocket 支持
    location /ws {
        proxy_pass http://127.0.0.1:9876;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # WebSocket 超时设置
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }

    # HTTP API
    location / {
        proxy_pass http://127.0.0.1:9876;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 4. 启用配置

```bash
sudo ln -s /etc/nginx/sites-available/screensaver /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 客户端配置

部署完成后，修改客户端配置：

```yaml
# client/tray_app/config.yaml
server:
  url: "wss://your-domain.com/ws"  # 注意使用 wss://
```

---

## 安全建议

### 1. 修改默认 API Key

编辑 `server/auth.py`：

```python
self.api_keys = {
    "sk_your_secure_api_key_here": "admin",
}
```

或通过环境变量：

```python
import os
API_KEY = os.environ.get("SCREENSAVER_API_KEY", "sk_default")
```

### 2. 防火墙配置

```bash
# 只开放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. 定期更新证书

```bash
sudo certbot renew --dry-run
```

---

## 监控与日志

### 查看日志

```bash
# Systemd 服务
sudo journalctl -u screensaver-server -f

# Docker
docker logs -f statusscreensaver
```

### 健康检查

```bash
curl https://your-domain.com/
```

---

## 快速部署脚本

创建 `deploy.sh`：

```bash
#!/bin/bash
set -e

echo "部署屏幕保护服务端..."

# 安装依赖
apt update
apt install -y python3-pip nginx certbot python3-certbot-nginx

# 部署代码
mkdir -p /opt/screensaver-server
cp -r server/* /opt/screensaver-server/
cd /opt/screensaver-server
pip3 install -r requirements.txt

# 配置 Systemd
cp screensaver-server.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable screensaver-server
systemctl start screensaver-server

echo "部署完成！"
echo "请配置 Nginx 和 SSL 证书。"
```
