# ============================================================================
# Antigravity Manager - Docker 多阶段构建
#
# 此 Dockerfile 构建独立的 Web 服务器模式，无需 GUI 依赖
# ============================================================================

# ============================================================================
# 阶段 1: 构建前端
# ============================================================================
FROM node:20-slim AS frontend-builder

WORKDIR /app

# 复制前端依赖文件
COPY package.json package-lock.json* pnpm-lock.yaml* ./

# 安装依赖 (优先使用 pnpm，否则使用 npm)
RUN if [ -f pnpm-lock.yaml ]; then \
        npm install -g pnpm && pnpm install --frozen-lockfile; \
    else \
        npm ci; \
    fi

# 复制前端源码
COPY src/ ./src/
COPY public/ ./public/
COPY index.html vite.config.ts tsconfig*.json tailwind.config.js postcss.config.cjs ./

# 构建前端
RUN npm run build

# ============================================================================
# 阶段 2: 构建 Rust 后端 (使用 Alpine + musl 静态编译)
# ============================================================================
FROM rust:alpine AS backend-builder

# 安装构建依赖
RUN apk add --no-cache \
    musl-dev \
    pkgconfig \
    openssl-dev \
    openssl-libs-static \
    perl \
    make

WORKDIR /build

# 复制 Cargo 配置文件
COPY src-tauri/Cargo.toml src-tauri/Cargo.lock ./src-tauri/

# 复制 Rust 源码
COPY src-tauri/src ./src-tauri/src

# 复制前端 locale 文件 (Rust 编译时 include_str! 需要)
COPY src/locales ./src/locales

# 构建独立 Web 服务器 (静态链接)
WORKDIR /build/src-tauri
ENV OPENSSL_STATIC=1
ENV OPENSSL_LIB_DIR=/usr/lib
ENV OPENSSL_INCLUDE_DIR=/usr/include
RUN cargo build --release --bin antigravity-server --no-default-features --features web-server

# ============================================================================
# 阶段 3: 运行时镜像 (使用 Alpine 最小化)
# ============================================================================
FROM alpine:latest AS runtime

LABEL maintainer="Antigravity Manager Docker"
LABEL description="Antigravity Manager Web Server Mode"

# 安装运行时依赖
RUN apk add --no-cache \
    ca-certificates \
    curl

WORKDIR /app

# 从构建阶段复制二进制文件
COPY --from=backend-builder /build/src-tauri/target/release/antigravity-server /app/antigravity-server

# 从前端构建阶段复制静态文件
COPY --from=frontend-builder /app/dist /app/dist

# 创建数据目录
RUN mkdir -p /data

# 设置环境变量
ENV RUST_LOG=info
ENV ANTIGRAVITY_DATA_DIR=/data

# 暴露端口
# 8765 - Web UI + 管理 API
# 8045 - 反代服务端口 (可配置)
EXPOSE 8765
EXPOSE 8045

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://127.0.0.1:8765/api/health || exit 1

# 启动服务
# --port 8765: Web UI + API 端口
# --host 0.0.0.0: 允许外部访问
# --static-dir /app/dist: 前端静态文件
# --data-dir /data: 数据持久化目录
ENTRYPOINT ["/app/antigravity-server"]
CMD ["--port", "8765", "--host", "0.0.0.0", "--static-dir", "/app/dist", "--data-dir", "/data"]
