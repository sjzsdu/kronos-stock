#!/bin/bash

# 设置变量
COMPOSE_FILE="./docker-compose.yml"
IMAGE_NAME="sjzsdu/kronos-china-stock-prediction"
NETWORK_NAME="traefik-public"

# 下载模型（如果不存在）
echo "Checking and downloading models..."
python3 download_models.py

# 移动模型到 models 目录
if [ -d "kronos-mini" ]; then
    mv kronos-mini ./models/ 2>/dev/null || cp -r kronos-mini ./models/
fi
if [ -d "kronos-small" ]; then
    mv kronos-small ./models/ 2>/dev/null || cp -r kronos-small ./models/
fi
if [ -d "kronos-base" ]; then
    mv kronos-base ./models/ 2>/dev/null || cp -r kronos-base ./models/
fi

# 获取本地已存在的镜像版本
CURRENT_VERSION=$(docker images ${IMAGE_NAME} --format '{{.Tag}}' | grep -v 'latest' | head -n 1)

# 如果传入了版本参数，使用参数版本并拉取
if [ "$1" != "" ]; then
    IMAGE_NAME="${IMAGE_NAME}:$1"
    echo "拉取指定版本镜像 $IMAGE_NAME..."
    docker pull "$IMAGE_NAME"
# 如果本地存在非latest版本，使用该版本
elif [ ! -z "$CURRENT_VERSION" ]; then
    IMAGE_NAME="${IMAGE_NAME}:${CURRENT_VERSION}"
    echo "使用本地已存在的版本: ${CURRENT_VERSION}"
# 如果本地有latest版本，直接使用
elif docker image inspect "${IMAGE_NAME}:latest" &> /dev/null; then
    IMAGE_NAME="${IMAGE_NAME}:latest"
    echo "使用本地已存在的latest版本"
# 如果本地没有任何版本，才去拉取latest
else
    IMAGE_NAME="${IMAGE_NAME}:latest"
    echo "本地无镜像，拉取latest版本..."
    docker pull "$IMAGE_NAME"
fi

# 检查镜像是否存在
if ! docker image inspect "$IMAGE_NAME" &> /dev/null; then
    echo "Error: 镜像 $IMAGE_NAME 不存在"
    exit 1
fi

# 检查docker-compose.yml文件是否存在
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "Error: $COMPOSE_FILE not found!"
    exit 1
fi

# 检查并创建 traefik-public 网络
if ! docker network inspect "$NETWORK_NAME" &> /dev/null; then
    echo "Creating $NETWORK_NAME network..."
    docker network create "$NETWORK_NAME"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create $NETWORK_NAME network"
        exit 1
    fi
else
    echo "$NETWORK_NAME network already exists"
fi

# 启动Docker Compose（添加 参数避免自动拉取镜像）
echo "Starting services with Docker Compose..."
docker-compose -f "$COMPOSE_FILE" up -d

# 检查服务是否成功启动
if [ $? -eq 0 ]; then
    echo "Services started successfully!"
    
    # 等待几秒钟让服务完全启动
    sleep 5
    
    # 打印容器日志
    echo "Printing container logs:"
    docker-compose -f "$COMPOSE_FILE" logs kronos-csweb
else
    echo "Error: Failed to start services"
    exit 1
fi

# 打印环境变量
echo "Printing environment variables inside the container:"
docker-compose -f "$COMPOSE_FILE" exec kronos-csweb env

# 检查应用是否正在运行
echo "Checking if the application is running:"
docker-compose -f "$COMPOSE_FILE" ps