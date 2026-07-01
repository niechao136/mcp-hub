# 1. 使用 Python 镜像
FROM python:3.11-slim-bookworm

# 2. 环境变量优化
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_INSTALL_DIR="/usr/local/bin" \
    PATH="/usr/local/bin:${PATH}"

# 3. 安装必备编译工具（这是关键！）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gcc \
    g++ \
    make \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. 安装 uv（使用官方脚本）
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /app

# 5. 复制依赖文件
COPY pyproject.toml uv.lock ./

# 6. 使用挂载缓存加速重复构建（可选，但强烈推荐）
#    同时指定 --python-platform 避免编译，--parallelism 限制并发
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev \
    --python-platform x86_64-unknown-linux-gnu \
    --parallelism 4

# 7. 将虚拟环境的 bin 加入 PATH
ENV PATH="/app/.venv/bin:$PATH"

# 8. 复制源码（放在依赖安装之后，充分复用缓存）
COPY src ./src

# 9. 启动命令
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]