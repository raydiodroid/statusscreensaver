#!/bin/bash
# Docker 部署脚本

set -e

echo "=========================================="
echo "屏幕保护服务端 - Docker 部署"
echo "=========================================="

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "警告: docker-compose 未安装，使用 docker compose"
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo ""
echo "1. 构建镜像..."
$COMPOSE_CMD build

echo ""
echo "2. 启动服务..."
$COMPOSE_CMD up -d

echo ""
echo "3. 检查状态..."
sleep 3
$COMPOSE_CMD ps

echo ""
echo "=========================================="
echo "部署完成!"
echo "=========================================="
echo ""
echo "服务地址: http://$(hostname -I | awk '{print $1}'):8000"
echo "API 文档: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "常用命令:"
echo "  查看日志: $COMPOSE_CMD logs -f"
echo "  停止服务: $COMPOSE_CMD down"
echo "  重启服务: $COMPOSE_CMD restart"
echo ""
