# ---------- 阶段 1: 仅安装依赖(独立缓存层) ----------
FROM node:20-alpine AS deps
WORKDIR /app

# 部分原生依赖(如 sharp)在 alpine 上需要这个兼容库
RUN apk add --no-cache libc6-compat

# 只拷贝依赖清单，源码变动不会使这一层失效
COPY package.json package-lock.json ./
# 用 npm ci 而不是 npm install：更快、更严格按 lock 文件安装，构建可复现
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# ---------- 阶段 2: 构建 ----------
FROM node:20-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

ARG NEXT_PUBLIC_API_URL=/api
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_TELEMETRY_DISABLED=1

# next.config.js 中需要 output: 'standalone'
RUN npm run build

# ---------- 阶段 3: 运行时(极简) ----------
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

# 非 root 用户运行，更安全
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# standalone 输出自带一个精简版 server.js 和最小化的 node_modules
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000

# standalone 模式下不再用 npm start，直接跑 server.js，启动更快、依赖更少
CMD ["node", "server.js"]