# ---------- Stage 1: 构建依赖 ----------
FROM python:3.11-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# 直接从官方 uv 镜像复制二进制,比 curl 安装脚本更快更稳定
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# 编译工具只在这一层需要,不会进入最终镜像
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 第一步:只用 lock 文件安装依赖(不含项目源码本身)
# 这样只要 pyproject.toml/uv.lock 不变,这一层缓存永远命中
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# 第二步:拷贝源码,再补一次同步(把项目本身装进去)
# 源码改动不会让上面的依赖层失效
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ---------- Stage 2: 精简运行时镜像 ----------
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# 只拷贝虚拟环境和源码,不带编译工具链,镜像体积大幅缩小
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]