---
name: piv-review-pr
description: 完整的 pull request 评审——获取 PR、运行项目验证、用全新视角评审 diff（派发 code-reviewer 子代理）、按严重度对问题分类、把评审发布到 GitHub（approve / request-changes / comment）并保存报告。这是人工批准之前对打开的 PR 运行的自动化门禁。在 piv-create-pr 之后使用。
argument-hint: "<pr-number | pr-url | branch> [--approve | --request-changes]"
---

# 评审 PR：人工之前的自动化门禁

**输入**：$ARGUMENTS

这个技能的要点是**全新视角（fresh eyes）**：在干净的上下文中评审 PR——*不是*写代码时的上下文——并能把深度分析交给 **`code-reviewer` 子代理**。这正是评审能抓住那些被作者自己的上下文合理化掉的缺陷的原因。它把结论发布到 PR 上，然后由**人**做最终决定。

## 阶段 1 — 获取 PR

把输入解析成 PR 编号（数字、URL，或通过 `gh pr list --head <branch> --json number -q '.[0].number'` 从分支解析）。然后：

```bash
gh pr view {N} --json number,title,body,author,headRefName,baseRefName,state,additions,deletions,changedFiles,files
gh pr diff {N}
gh pr checkout {N}
```

状态守卫：`MERGED`/`CLOSED` → 停下（"没有可评审的内容"）；`DRAFT` → 只给出评审方向，不要 approve/block。

## 阶段 2 — 加载上下文（这样你对照正确的标尺评审）

- **`CLAUDE.md`**/**`AGENTS.md`** + 项目声明的参考资料（`.claude/references/`、`.qoder/rules/` 等）——项目的标准就是评审的量规。
- **实现报告**（如果 `piv-implement` 写过——`docs/ai/reports/*{branch}*`）+ 它的计划：阅读**记录过的偏离**。一条记录过的偏离是*有意的决策*，**不是**问题——只标记*未记录*的分歧。（没有报告？正常评审并注明其缺失。）
- PR 自己的意图（标题/正文）：它声称解决什么问题。

## 阶段 3 — 运行验证

运行项目的真实套件（**`piv-validate`** 技能，或计划中的验证命令）——测试、类型检查、lint、构建。记录通过/失败与计数。套件变红本身就是一条发现。

## 阶段 4 — 评审 diff（派发 code-reviewer 子代理）

如果项目有 **`code-reviewer`** 子代理（Qoder 下用 create-subagent 创建；Claude Code 下为 `.claude/agents/code-reviewer.md`），把深度检查交给它；否则用 Agent 工具的 CodeReview 子代理，或在本会话中用干净上下文评审——它对照项目标准评审，**只报告高置信度问题**。*完整*阅读每个更改过的文件（不只是 diff）以获取上下文。覆盖：正确性 · 类型安全 · 模式/标准符合性 · 安全 · 性能 · 测试存在性 · 可维护性。

**按严重度对每个问题分类：**

| 严重度 | 含义 |
|----------|----------|
| **Critical（关键）** | 阻塞性——安全、数据丢失、崩溃 |
| **High（高）** | 合并前应修——类型安全漏洞、缺少错误处理、逻辑错误 |
| **Medium（中）** | 模式不一致、缺少边界情况、*未记录*的偏离 |
| **Low（低）** | 建议、小的打磨 |

也要肯定做得好的地方——评审是建设性的，不只是缺陷清单。

## 阶段 5 — 决定

- **Approve（批准）** — 无 critical/high 问题、验证通过、符合意图。
- **Request changes（要求修改）** — 有 high 问题，或可修复的验证失败，或未记录的模式违规。
- **Block（阻止）**（强烈 request-changes）— 关键安全/数据问题，或根本方法错误。
- 尊重显式的 `--approve` / `--request-changes` 标志，但绝不带着未解决的 critical 问题 approve。

## 阶段 6 — 发布到 GitHub + 保存报告

把报告写到 `docs/ai/code-reviews/pr-{N}-review.md`（摘要 · 按严重度分类的问题，带 `file:line` + 修复 · 验证表 · 做得好的地方 · 建议）。然后发布它：

```bash
# approve（批准）
gh pr review {N} --approve --body-file docs/ai/code-reviews/pr-{N}-review.md
# request changes（要求修改）
gh pr review {N} --request-changes --body-file docs/ai/code-reviews/pr-{N}-review.md
# 或仅评论（draft PRs / 咨询性）
gh pr comment {N} --body-file docs/ai/code-reviews/pr-{N}-review.md
```

## 输出 + 交接

打印：PR 编号/URL · 按严重度的问题计数 · 验证结果 · 建议。然后交接：**"已发布在 PR 上。现在由人评审代码 + 这份评审并合并。"** 如果有问题，自然的下一步是对报告运行 **`piv-fix-review-findings`**，然后重新运行验证。

## 备注

- **全新视角就是全部意义**——在干净上下文中运行它（或让 `code-reviewer` 子代理充当干净上下文）。不要用写代码的那个会话评审；它会为代码找理由，而不是审视它。
- 这是*自动化*门禁；它不替代人——它给人一份经过验证、分级过的 PR 来批准。更进一步意味着多个评审子代理、把评审者调优到你的技术栈，以及背后的验证金字塔。
