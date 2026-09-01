---
name: piv-create-pr
description: 推送当前特性分支并开一个 pull request，准备评审。在 ticket 的实现已提交到独立分支后使用——自动检测 base 分支、推送、用清晰的正文开 PR（摘要 · 改了什么 · 验证状态），并返回 URL 交给评审者。
argument-hint: "[--base <branch>]（默认：自动检测）"
---

# 创建 PR：开 Pull Request，交接评审

这是 PIV 循环的**发布（ship）**步骤：实现已提交在特性分支上；现在开 PR，让它接受评审（先由 `piv-review-pr` 门禁自动评审，再由人评审）。

## 阶段 0 — 检测 base 分支

不要硬编码 `main`，按下面的顺序解析：
1. 如果 `$ARGUMENTS` 包含 `--base <branch>`，使用它。
2. 否则：`git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'`
3. 回退：`git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}'`
4. 最后手段：`main`。存为 `{base}`。

## 阶段 1 — 验证 git 状态

```bash
git branch --show-current
git status --short
git log origin/{base}..HEAD --oneline
```

| 状态 | 动作 |
|-------|--------|
| 在 `{base}` 上 | 停下："先创建一个特性分支（ticket 应该放在自己的分支上）。" |
| 有未提交更改 | 停下："开 PR 前先提交（或 stash）。" |
| 没有领先 `{base}` 的提交 | 停下："没有可 PR 的东西。" |
| 该分支已有 PR（`gh pr list --head $(git branch --show-current) --json url`） | 停下并打印 URL。 |
| 干净、有领先提交、无 PR | 继续 |

## 阶段 2 — 为正文收集上下文

- **项目约定：** 如果 `AGENTS.md` 或 `CLAUDE.md` 存在，阅读它的 `## pr` 章节——它的规则优先于下面的默认模板（章节、语气、必须说明什么）。那里存放项目的特定约定；本技能保持通用。
- 提交：`git log origin/{base}..HEAD --pretty=format:"- %s"`
- 文件：`git diff --stat origin/{base}..HEAD`
- **实现报告**（如果 `piv-implement` 写过——`docs/ai/reports/<…>-report.md`）：提取其中的摘要、验证结果和**记录过的偏离**（这些应写进 PR 正文——它们告诉评审者哪些改动是有意为之）。
- 链接的 ticket / issue：在提交/分支名中寻找 `ACC-…`、`#123`、`Fixes #…`。
- PR 模板：如果 `.github/PULL_REQUEST_TEMPLATE.md` 存在，填它；否则用下面的默认模板。

## 阶段 3 — 推送并开 PR

```bash
git push -u origin HEAD
```

```bash
gh pr create --base "{base}" --title "{type}: {简洁描述}" --body "$(cat <<'EOF'
## 摘要
{1-2 句：这个 ticket 交付了什么}

## 改了什么
{提交摘要}

## 验证
- 测试 / 类型检查 / lint：{来自实现报告或新运行结果的通过/失败}
- 手动检查：{演练了什么，或 "待评审"}

## 给评审者的备注
{与计划的有意偏离（有意的决策），或 "无"}

## 链接
{ticket / issue 引用，或 "无"}

_准备评审。_
EOF
)"
```

（`{type}` = 来自工作的 feat/fix/refactor/…。如果工作还没准备好接受真正评审，用 `--draft`。）

## 输出

```bash
gh pr view --json number,url,title,baseRefName,headRefName
```

报告 PR 编号 + URL、base ← head 分支，以及 **"准备评审 → 运行 `piv-review-pr <编号>`，然后由人批准。"** 这是交接点：AI 助手的循环止于一个打开的 PR；评审和合并是后续的门禁。

## 备注

- 理念上工具无关：本技能用 GitHub（`gh`）示范；同样的动作在 GitLab 上是"开 merge request"，或在你团队所在平台"标记为准备评审"。没有远程的单人开发？跳过 PR——直接在 `{base}` 上提交，继续前先自己评审自己的 diff。
- 为并行铺路：每个 ticket 一个分支 → 每个 ticket 一个 PR，这正是 worktree 能干净并行（同时运行独立 ticket）的原因。
