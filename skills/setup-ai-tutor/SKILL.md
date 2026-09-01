---
name: setup-ai-tutor
description: 在本地搭建并启动 AI Tutor 项目（环境文件、依赖、数据库、迁移和开发服务器）。在新机器上首次启动 AI Tutor，或全新克隆后使用。这是示例项目专用技能；当你把 AI 层装进自己的项目时，请适配它。
---

# 在本地搭建 AI Tutor

运行以下命令在本地搭建并启动 AI Tutor。

## 输入

无需输入。从仓库根目录运行。

## 流程

### 1. 创建环境文件
```bash
cp .env.example .env
```
从示例模板创建你的本地环境配置。

### 2. 安装依赖
```bash
uv sync
```
安装 pyproject.toml 中定义的所有 Python 包。

### 3. 启动数据库
```bash
docker-compose up -d db
```
在 Docker 容器中启动 PostgreSQL。

### 4. 运行数据库迁移
```bash
uv run alembic upgrade head
```
应用所有待处理的数据库迁移。

### 5. 启动开发服务器
```bash
uv run uvicorn app.main:app --reload --port 8123
```
在 8123 端口启动带热重载的 FastAPI 服务器。

### 6. 验证搭建

检查一切是否正常工作：

```bash
# 测试 API 健康检查
curl -s http://localhost:8123/health

# 测试数据库连接
curl -s http://localhost:8123/health/db
```

两者都应返回 `{"status":"healthy"}` 响应。

## 输出

一个正在运行的本地 AI Tutor 实例。

### 访问入口

- Swagger UI：http://localhost:8123/docs
- 健康检查：http://localhost:8123/health
- 数据库：localhost（Docker 容器）

## 清理

停止服务：
```bash
# 停止开发服务器：Ctrl+C
# 停止数据库：docker-compose down
```

## 备注

- 端口号和确切的 `docker-compose` 服务名可能不同——运行前对照 `docker-compose.yml`、`.env.example` 和项目 README 检查项目特定值。
