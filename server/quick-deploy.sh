#!/bin/bash
# 一键部署脚本 - 在服务器上运行
# 用法: curl -fsSL https://your-domain/deploy.sh | bash
# 或: wget -qO- https://your-domain/deploy.sh | bash

set -e

REPO_URL="https://git.woa.com/jiaruizhang/StatusScreenSaver.git"
PROJECT_DIR="StatusScreenSaver"
PORT=9876

echo "=========================================="
echo "屏幕保护服务端 - 一键部署"
echo "=========================================="

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "安装 Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "安装 Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 确定-compose 命令
if command -v docker-compose &> /dev/null; then
    COMPOSE="docker-compose"
else
    COMPOSE="docker compose"
fi

# 克隆或更新代码
if [ -d "$PROJECT_DIR" ]; then
    echo "更新代码..."
    cd $PROJECT_DIR/server
    git pull
else
    echo "克隆仓库..."
    git clone $REPO_URL $PROJECT_DIR
    cd $PROJECT_DIR/server
fi

# 部署
echo "构建并启动服务..."
$COMPOSE down 2>/dev/null || true
$COMPOSE up -d --build

# 等待启动
echo "等待服务启动..."
sleep 5

# 检查状态
if curl -s "http://localhost:$PORT/" > /dev/null; then
    echo ""
    echo "=========================================="
    echo "✅ 部署成功!"
    echo "=========================================="
    echo ""
    echo "服务地址: http://$(hostname -I | awk '{print $1}'):$PORT"
    echo "API 文档: http://$(hostname -I | awk '{print $1}'):$PORT/docs"
    echo ""
    echo "常用命令:"
    echo "  查看日志: $COMPOSE logs -f"
    echo "  重启服务: $COMPOSE restart"
    echo "  停止服务: $COMPOSE down"
    echo ""
else
    echo ""
    echo "❌ 部署可能失败，请检查日志:"
    echo "  $COMPOSE logs"
fi
