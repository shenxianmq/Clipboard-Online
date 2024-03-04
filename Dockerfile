# 使用官方 Python 镜像作为基础镜像
# FROM shenxianmq/autosymlink_env:latest
FROM python:3.11-slim-bookworm


# 设置环境变量
ENV PYTHONUNBUFFERED 1

# 在创建容器时指定的用户和组 ID
ARG USER_ID=1000
ARG GROUP_ID=1000

# 创建一个非root用户，指定用户和组 ID
RUN groupadd -r -g $GROUP_ID clipboardOnline && useradd -r -g clipboardOnline -u $USER_ID clipboardOnline


# 从当前目录复制所有文件到工作目录
COPY . /app

# 设置工作目录
WORKDIR /app


RUN chmod 777 -R /app

# 在构建过程中为脚本赋予执行权限
RUN chmod +x /app/start.sh

# 定义容器启动命令
ENTRYPOINT ["/app/start.sh"]
