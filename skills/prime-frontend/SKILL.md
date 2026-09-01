---
name: prime-frontend
description: 让 AI 助手聚焦理解代码库的前端部分——组件、路由、状态管理和样式——而不加载无关的后端代码。适合在会话开始时、工作范围限定在 UI 或客户端功能时使用。可选：先通过 Jira 工单和 Confluence 页面拉取外部任务上下文。
argument-hint: "[jira-issue-keys] [confluence-page-ids]"
---

# Prime 前端：加载前端上下文

## 目标

通过分析前端代码库的结构、组件和约定，建立有针对性的理解。只加载前端上下文，可以让复杂全栈代码库的上下文窗口保持轻量。如果提供了外部任务引用，请先加载它们，让分析紧扣实际任务。

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

### 第 1 步：定位前端

列出所有受版本控制的文件，以找到前端根目录：

!`git ls-files`

常见前端根目录：`frontend/`、`client/`、`web/`、`src/`（项目仅前端时）、`app/`（Next.js）。继续之前先确认正确的根目录。

### 第 2 步：阅读前端文档

- 阅读 CLAUDE.md 或类似的全局规则文件（了解项目级约定）
- 阅读前端根目录内的 README 文件
- 如果存在项目声明的参考资料（`.claude/references/frontend-component-best-practices.md`、`.qoder/rules/` 等），阅读它——其中包含项目特定的组件约定

### 第 3 步：识别关键前端文件

根据项目结构，阅读：

- 主入口文件（`main.tsx`、`index.tsx`、`app/layout.tsx`、`pages/_app.tsx` 等）
- 路由配置（`router.tsx`、`routes.ts`、Next.js 的 `app/` 目录）
- 全局状态设置（store、context providers）
- 共享组件库根目录（`components/`、`ui/`）
- 核心配置（`package.json`、`tsconfig.json`、`vite.config.ts`、`next.config.ts`）
- 一两个有代表性的功能组件，以便内化既有模式

前端根目录之外的文件可以跳过，除非它们定义了前端依赖的共享类型或契约。

### 第 4 步：了解当前前端状态

检查近期与前端相关的活动：

!`git log -10 --oneline`

!`git status`

留意前端目录中任何未完成的改动。

## 输出报告

输出一份简洁的摘要，包含以下部分：

### 外部任务上下文（如已加载）
- Jira 工单：工单号、标题、一句话目标、验收标准
- Confluence 页面：页面标题及其规定的内容

### 前端概述
- 框架和主要库（React、Vue、Next.js、Tailwind 等）
- 观察到的组件模式（原子设计、按功能分目录等）
- 状态管理方式

### 目录地图
- 前端根目录和关键子目录，每个附一句话说明其用途

### 约定
- 命名约定、文件就近放置规则
- 样式方案
- 观察到的测试框架和约定

### 当前状态
- 当前分支、近期前端改动
- 需要立即关注的问题（缺少类型、已弃用的模式等）

**摘要应便于快速浏览——使用要点列表和清晰的标题。**
