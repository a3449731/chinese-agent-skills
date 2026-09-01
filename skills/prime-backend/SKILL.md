---
name: prime-backend
description: 让 AI 助手聚焦理解代码库的后端部分——API 路由、服务、数据模型和数据库层——而不加载无关的前端代码。适合在会话开始时、工作范围限定在 API 端点、业务逻辑或数据访问时使用。可选：先通过 Jira 工单和 Confluence 页面拉取外部任务上下文。
argument-hint: "[jira-issue-keys] [confluence-page-ids]"
---

# Prime 后端：加载后端上下文

## 目标

通过分析后端代码库的结构、路由、服务和数据层，建立有针对性的理解。只加载后端上下文，可以让复杂全栈代码库的上下文窗口保持轻量。如果提供了外部任务引用，请先加载它们，让分析紧扣实际任务。

## 流程

### 第 0 步：加载外部上下文（可选）

**本步必须在代码库分析之前执行。** 接受可选参数：`[jira-issue-keys] [confluence-page-ids]`。

- Jira 工单号可以是单个（`ACC-2`），也可以是以逗号分隔的多个（`ACC-2,ACC-3`）。
- Confluence 页面 ID 为数字形式。

**如果提供了 Jira 工单号：**

1. 调用 `mcp__atlassian__getAccessibleAtlassianResources` 获取 `cloudId`。
2. 对每个 Jira 工单号，用该 `cloudId`、工单号和 `responseContentFormat: "markdown"` 调用 `mcp__atlassian__getJiraIssue`。
3. 将返回的工单摘要、描述和验收标准作为后续所有工作的任务上下文。

**如果提供了 Confluence 页面 ID：**

1. 对每个页面 ID 调用 `mcp__atlassian__getConfluencePage`，参数为 `contentFormat: "markdown"`（复用上面的 `cloudId`；若此前未获取过，先通过 `mcp__atlassian__getAccessibleAtlassianResources` 获取）。
2. 将返回的页面内容作为补充上下文（规格、设计文档、需求）。

**如果未提供任何参数，或未配置 Atlassian MCP：** 完全跳过本步，直接进入第 1 步。

继续之前，简要总结已加载的外部上下文——它为后续的上下文加载定下基调。

### 第 1 步：定位后端

列出所有受版本控制的文件，以找到后端根目录：

!`git ls-files`

常见后端根目录：`backend/`、`server/`、`api/`、`app/`（FastAPI/Django）、`src/`（项目仅后端时）。继续之前先确认正确的根目录。

### 第 2 步：阅读后端文档

- 阅读 CLAUDE.md 或类似的全局规则文件（了解项目级约定）
- 阅读后端根目录内的 README 文件
- 如果存在项目声明的参考资料（`.claude/references/backend-api-best-practices.md`、`.qoder/rules/` 等），阅读它——其中包含项目特定的 API 约定

### 第 3 步：识别关键后端文件

根据项目结构，阅读：

- 主入口文件（`main.py`、`app.py`、`server.ts`、`index.ts` 等）
- 路由注册 / 路由索引（`routes/`、`api/`、`routers/`）
- 核心配置（`pyproject.toml`、`package.json`、`tsconfig.json`）
- 数据库配置和 ORM 设置（`database.py`、`db.ts`、`alembic.ini`）
- 核心数据模型或模式（`models/`、`schemas/`）
- 一两个有代表性的功能切片（路由 + 服务 + 模型），以便内化既有模式
- 中间件和依赖注入设置

后端根目录之外的文件可以跳过，除非它们定义了后端对外暴露的共享类型或契约。

### 第 4 步：了解当前后端状态

检查近期与后端相关的活动：

!`git log -10 --oneline`

!`git status`

留意任何未完成的迁移、待定的模式变更或进行中的 API 改动。

## 输出报告

输出一份简洁的摘要，包含以下部分：

### 外部任务上下文（如已加载）
- Jira 工单：工单号、标题、一句话目标、验收标准
- Confluence 页面：页面标题及其规定的内容

### 后端概述
- 框架和主要库（FastAPI、Django、Express、NestJS 等）
- 语言和运行时版本
- 数据库和 ORM（PostgreSQL + SQLAlchemy、MongoDB + Mongoose 等）

### 目录地图
- 后端根目录和关键子目录，每个附一句话说明其用途

### 架构模式
- 路由、服务和数据访问如何分层
- 观察到的依赖注入或中间件模式
- 错误处理方式

### 约定
- 命名约定、模块组织
- 迁移工具及当前迁移状态
- 观察到的测试框架和约定

### 当前状态
- 当前分支、近期后端改动
- 任何待定的迁移或模式变更
- 需要立即关注的问题（缺少校验、未处理的错误等）

**摘要应便于快速浏览——使用要点列表和清晰的标题。**
