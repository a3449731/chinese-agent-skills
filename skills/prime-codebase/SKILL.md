---
name: prime-codebase
description: 让 AI 助手快速建立对代码库的深度理解——分析项目结构、文档与关键文件。适合在开始处理代码库、会话启动时、或规划与实现之前需要快速掌握全局时使用。可选：先通过 Jira 工单和 Confluence 页面拉取外部任务上下文。
argument-hint: "[jira-issue-keys] [confluence-page-ids]"
---

# Prime：加载项目上下文

## 目标

通过分析项目结构、文档和关键文件，建立对代码库的全面理解。如果提供了外部任务引用，请先加载它们，让代码库分析紧扣实际任务。

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

### 第 1 步：分析项目结构

列出所有受版本控制的文件：
!`git ls-files`

查看目录结构（Linux 上执行）：
`tree -L 3 -I 'node_modules|__pycache__|.git|dist|build'`

### 第 2 步：阅读核心文档

- 阅读 CLAUDE.md 或类似的全局规则文件
- 阅读项目根目录及主要目录下的 README 文件
- 阅读架构相关文档

### 第 3 步：识别关键文件

根据项目结构，识别并阅读：
- 主要入口文件（main.py、index.ts、app.py 等）
- 核心配置文件（pyproject.toml、package.json、tsconfig.json）
- 关键的模型/数据结构定义
- 重要的服务层或控制器文件

### 第 4 步：了解当前状态

检查近期提交记录：
!`git log -10 --oneline`

查看当前分支和工作区状态：
!`git status`

## 输出报告

输出一份简洁的摘要，包含以下部分：

### 外部任务上下文（如已加载）
- Jira 工单：工单号、标题、一句话目标、验收标准
- Confluence 页面：页面标题及其规定的内容

### 项目概述
- 应用的目的和类型
- 主要技术与框架
- 当前版本/状态

### 架构
- 整体结构与组织方式
- 识别出的关键架构模式
- 重要目录及其职责

### 技术栈
- 语言及版本
- 框架和主要库
- 构建工具与包管理器
- 测试框架

### 核心原则
- 观察到的代码风格与约定
- 文档规范
- 测试方法

### 当前状态
- 当前分支
- 近期改动或开发重点
- 需要立即关注的观察项或风险

**摘要应便于快速浏览——使用要点列表和清晰的标题。**
