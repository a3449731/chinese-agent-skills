---
name: plan-create-stories
description: 把一份 PRD 分解成结构良好、工程师可直接使用的 ticket——Jira issues 或 GitHub issues。在 PRD 已存在之后使用，把它的阶段和用户故事变成一个结构化的 backlog。适用于新代码库（MVP 范围）或现有代码库（epic 范围）。
argument-hint: <prd-path> --platform <jira|github> [--project KEY] [--epic KEY] [--milestone NAME]
---

# 创建 Stories：PRD → Ticket Backlog

## 概述

把一份完成的 PRD 变成一个小而结构良好的 ticket backlog。PRD 中的每个实现阶段（Implementation Phase）变成一组 ticket；每个用户故事（User Story）变成一个或多个带明确验收标准的 ticket。

本技能刻意做到平台无关——**`--platform` 标志**决定 backlog 落在 Jira 还是 GitHub Issues。该标志之前的所有环节（读 PRD、分解、写验收标准）完全相同。

## 参数

| 参数 | 必填 | 含义 |
|----------|----------|----------|
| `<prd-path>` | 是 | `plan-create-prd` 产出的 PRD 的路径 |
| `--platform` | 是 | `jira` 或 `github` — ticket 创建在哪里 |
| `--project` | 仅 jira | Jira 项目 key（例如 `HELP`） |
| `--epic` | 仅 jira | 作为 ticket 父级的 Jira epic key（例如 `HELP-1`） |
| `--milestone` | 仅 github | 可选：要附加 issues 的 GitHub milestone |

如果缺少 `--platform`，**停下来询问**——不要猜测。

## 工作流

### 1. 阅读并分解 PRD
- 完整阅读 `<prd-path>`。
- 走查 **Implementation Phases（实现阶段）** 章节。每个阶段是一个 ticket 组。
- 走查 **User Stories（用户故事）** 章节。每个故事映射到一个 ticket（如果它隐藏了超过约一天的工作量，就拆分）。
- 为每个 ticket 起草：
  - **标题** — 祈使句、具体（`Add token refresh endpoint`，而不是 `Auth`）。
  - **描述** — 做什么和为什么，回链到 PRD 阶段。
  - **验收标准** — 评审者可以核对的清单。
  - **阶段标签** — 它属于哪个 PRD 阶段。
- 保持 ticket 小。一个无法在一屏内描述的 ticket，就是两个 ticket。

### 2. 创建任何东西之前先确认计划
先打印提议的 ticket 清单（标题 + 阶段分组）和目标平台。这是检查点——创建真实 ticket 不是一键可逆的。

### 3. 创建 ticket — 按 `--platform` 分支

**`--platform jira`:**
- 使用 Atlassian MCP 服务器。
- 在 `--project` 中的 `--epic` 下创建每个 ticket。
- 映射：PRD 阶段 → 标签或 epic；验收标准 → 描述。
- 记录每个创建的 issue key。

**`--platform github`:**
- 使用 `gh` CLI：`gh issue create --title "..." --body "..." [--label phase-N] [--milestone "..."]`。
- 把验收标准作为 markdown 清单放进 issue body。
- 按 PRD 阶段应用 `phase-N` 标签（如果标签不存在，用 `gh label create` 创建）。
- 记录每个创建的 issue 编号/URL。

### 4. 报告
- 一张表：ticket 标题 → 阶段 → 创建的 key/编号/URL。
- 生成 backlog 所依据的 PRD 路径。
- 下一步：每个阶段现在都可以作为 PIV 循环运行。

## 质量检查

- ✅ 每个 ticket 都能追溯到一个 PRD 阶段或用户故事
- ✅ 每个 ticket 都有可验证的验收标准
- ✅ Ticket 小（≤ 约 1 天工作量）
- ✅ 使用了正确的平台，且每次创建都成功
- ✅ 保留了阶段分组（标签/epic），backlog 保持可导航

## 备注

- 全新项目 vs 存量项目只改变 PRD 的*范围*（MVP vs 下一个 epic），不改变本技能——`plan-create-stories` 两种场景下运行方式相同。
- 未经步骤 2 的确认绝不创建 ticket。
- 如果某个阶段过于含糊无法分解，停下来标记它——那是 PRD 的缺口，不是写 ticket 的问题。
