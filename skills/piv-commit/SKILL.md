---
name: piv-commit
description: 为所有未提交的更改创建一个新的 git 提交，使用原子性、带 conventional 标签的消息。当工作完成、准备提交时使用。
---

# 提交：创建新提交

为所有未提交的更改创建一个新提交。

## 流程

0. **阅读本项目的约定。** 如果 `AGENTS.md` 或 `CLAUDE.md` 存在，阅读它的 `## commit` 章节并遵循它——那些规则优先于下面的默认值。那里存放项目的特定约定；本技能保持通用。
1. 运行 `git status && git diff HEAD && git status --porcelain` 查看哪些文件未提交。
2. 添加未跟踪和已更改的文件。
3. 写一条原子性的提交消息，附上恰当、有描述性的摘要。
4. 添加一个体现本次工作的标签，如 `feat`、`fix`、`docs`、`refactor`、`test`、`chore` 等。

## 输出

一个包含所有未提交更改的单一提交，消息采用 conventional-commit 风格（`<标签>: <原子描述>`），准确反映所做的工作。

提交成功后，打印两段带清晰标签的摘要：

### 改了什么（What Changed）
一段短文（3–6 句）描述被提交的特性/修复/重构——它解决什么问题、哪些文件是关键触点。面向快速浏览 git log 的开发者而写。

### AI 层更改（AI Layer Changes）
仅当 AI 层文件被修改或添加时才包含此章节（AGENTS.md、CLAUDE.md、`.qoder/`、`~/.qoder-cn/skills/`（其他工具对应 `~/.claude/skills/`、`~/.codex/skills/`、`~/.cursor/skills/`）、`.claude/` 等）。

列出每个更改的 AI 层文件，附一行说明改了什么以及为什么。如果 AI 层没有任何更改，完全省略此章节。
