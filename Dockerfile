# 1. 使用 Python 镜像
FROM python:3.11-slim-bookworm

# 2. 设置环境变量，强制 uv 安装到固定位置
ENV UV_INSTALL_DIR="/usr/local/bin"
ENV PATH="/usr/local/bin:${PATH}"
# Python 环境变量优化
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. 安装必要工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 4. 直接安装 uv (它会自动装到 /usr/local/bin)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /app

# 5. 复制依赖文件
COPY pyproject.toml uv.lock ./

# 6. 正确的 sync 写法：
# --frozen 避免联网更新 lock，--no-dev 排除开发依赖（如 pytest/black 等）
RUN uv sync --frozen --no-dev

# 7. 关键：把容器内生成的虚拟环境路径，加入到环境变量的最前面
ENV PATH="/app/.venv/bin:$PATH"

# 8. 复制源码（把复制源码放在安装依赖后面，可以完美利用 Docker 缓存层）
COPY src ./src

# 9. 启动命令（因为上面已经把 .venv/bin 加到 PATH 了，直接呼叫 uvicorn 即可）
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]