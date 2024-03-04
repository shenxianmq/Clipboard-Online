# 使用官方 Python 镜像作为基础镜像
# FROM shenxianmq/autosymlink_env:latest
FROM python:3.11-slim-bookworm


# 设置环境变量
ENV PYTHONUNBUFFERED 1

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 到工作目录
COPY requirements.txt /app/

# 安装依赖并删除 requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt