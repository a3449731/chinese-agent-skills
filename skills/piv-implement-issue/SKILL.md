---
name: piv-implement-issue
description: 根据 RCA 产物（由 piv-investigate-issue 创建）实施 GitHub issue 的修复——先做漂移检查，再切分支、实现、添加回归测试并验证。适合在调查产物已存在、准备修复该 issue 时使用。
argument-hint: [github-issue-id]
allowed-tools: Read, Write, Edit, Bash(ruff:*), Bash(mypy:*), Bash(pytest:*), Bash(npm:*), Bash(bun:*)
---

# 实施 Issue 修复：GitHub Issue #$ARGUMENTS

## 前置条件

**本技能基于 RCA 文档实施 GitHub issue 的修复：**
- 在带有 GitHub 远程仓库的本地 Git 仓库中工作
- RCA 文档存在于 `docs/issues/issue-$ARGUMENTS.md`
- GitHub CLI 已安装并认证（可选，用于状态更新）

## 要参考的 RCA 文档

读取 RCA：`docs/issues/issue-$ARGUMENTS.md`

**可选 - 查看 GitHub issue 获取上下文：**
```bash
gh issue view $ARGUMENTS
```

## 实施说明

### 1. 阅读并理解 RCA

- 透彻阅读整份 RCA 文档
- 审阅 GitHub issue 详情（issue #$ARGUMENTS）
- 理解根因
- 审阅提议的修复策略
- 记下所有要修改的文件
- 审阅测试需求

### 2. 验证当前状态——并检查漂移

在做更改之前：
- 确认 issue 仍然存在。
- **漂移检查：** 逐一阅读 RCA 点名的文件，与 RCA 中的"当前代码"片段/行引用对照。如果代码自 RCA 之后**实质改变**，**立即停下**——把漂移摆到明面上，建议对 issue #$ARGUMENTS 重新运行 `piv-investigate-issue`，而不是实施一份过时的计划。
- 确认提议的修复仍然针对根因——不要静默偏离。

### 2b. 切到正确的分支

- **在 worktree 中？** 用它（它就是为这项工作创建的）。
- **在 base 分支上，工作树干净？** 创建修复分支——`git checkout -b fix/issue-$ARGUMENTS-<slug>`（用 `git symbolic-ref refs/remotes/origin/HEAD` 检测 base；绝不硬编码 `main`）。
- **已经在特性/修复分支上？** 用它（如果名字没引用 #$ARGUMENTS，警告）。
- **base 分支上工作树脏？** 停下——请用户先提交或 stash。

### 3. 实施修复

遵循 RCA 的"提议的修复"章节：

**对每个要修改的文件：**

#### a. 阅读现有文件
- 理解当前实现
- 定位 RCA 中提到的具体代码

#### b. 做修复
- 按 RCA 描述实施更改
- 完全遵循修复策略
- 保持代码风格和约定
- 如果修复不明显，添加注释

#### c. 处理相关更改
- 更新受修复影响的任何相关代码
- 确保整个代码库的一致性
- 如有需要更新导入

**坚守计划：** 只实施 RCA 指定的内容——不要重构无关代码或添加计划外的"改进"。如果必须偏离，记下改了什么、为什么，并在报告（和 PR）中明确说明。

### 4. 添加/更新测试

遵循 RCA 的"测试需求"：

**创建测试用例：**
1. 验证修复解决了 issue
2. 测试与 bug 相关的边界情况
3. 确保相关功能无回归
4. 测试引入的任何新代码路径

**测试文件位置：**
- 遵循项目的测试结构
- 与源文件位置对应
- 使用描述性测试名称

**测试实现：**
```python
def test_issue_$ARGUMENTS_fix():
    """测试 issue #$ARGUMENTS 已修复。"""
    # Arrange - 设置导致 bug 的场景
    # Act - 执行之前失败的代码
    # Assert - 验证现在正常工作
```

### 5. 运行验证

执行 RCA 中的验证命令：

```bash
# 运行 linters
[来自 RCA 验证命令]

# 运行类型检查
[来自 RCA 验证命令]

# 运行测试
[来自 RCA 验证命令]
```

**如果验证失败：**
- 修复问题
- 重新运行验证
- 全部通过前不要继续

### 6. 验证修复

**手动验证：**
- 遵循 RCA 的复现步骤
- 确认 issue 不再发生
- 测试边界情况
- 检查意外副作用

### 7. 更新文档

如有需要：
- 更新代码注释
- 更新 API 文档
- 如果面向用户，更新 README
- 添加关于修复的备注

## 输出报告

### 修复实施摘要

**GitHub Issue #$ARGUMENTS**：[简短标题]

**Issue URL**：[GitHub issue URL]

**根因**（来自 RCA）：
[根因的一行摘要]

### 所做的更改

**修改的文件：**
1. **[文件路径]**
   - 更改： [改了什么]
   - 行数： [行号]

2. **[文件路径]**
   - 更改： [改了什么]
   - 行数： [行号]

### 新增测试

**创建/修改的测试文件：**
1. **[测试文件路径]**
   - 测试用例： [列出添加的测试函数]

**测试覆盖：**
- ✅ 修复验证测试
- ✅ 边界情况测试
- ✅ 防回归测试

### 验证结果

```bash
# Linter 输出
[展示 lint 结果]

# 类型检查输出
[展示类型检查结果]

# 测试输出
[展示测试结果 - 全部通过]
```

### 验证

**手动测试：**
- ✅ 遵循复现步骤 - issue 已解决
- ✅ 测试了边界情况 - 全部通过
- ✅ 未引入新问题
- ✅ 原始功能保留

### 与 RCA 的偏离

[无 — 按指定实施 | 列出每条偏离 + 原因]

### 文件摘要

**总更改：**
- X 个文件修改
- Y 个文件创建（测试）
- Z 行新增
- W 行删除

### 准备提交

所有更改完成并验证。准备使用 `piv-commit` 技能。

**建议的提交消息：**
```
fix(scope): 解决 GitHub issue #$ARGUMENTS - [简短描述]

[修复了什么以及如何修复的摘要]

Fixes #$ARGUMENTS
```

**注意：** 在提交消息中使用 `Fixes #$ARGUMENTS` 会在合并到默认分支时自动关闭 GitHub issue。

### 可选：更新 GitHub Issue

**向 issue 添加实施评论：**
```bash
gh issue comment $ARGUMENTS --body "修复已在提交 [commit-hash] 中实施。准备评审。"
```

**更新 issue 标签（如有需要）：**
```bash
gh issue edit $ARGUMENTS --add-label "fixed" --remove-label "bug"
```

**关闭 issue（如果未通过提交消息自动关闭）：**
```bash
gh issue close $ARGUMENTS --comment "已修复并合并。"
```

## 备注

- 如果 RCA 文档缺失或不完整，先要求用 `piv-investigate-issue` 技能为 issue #$ARGUMENTS 创建它
- 如果你发现 RCA 分析不正确，记录发现并更新 RCA
- 如果在实施中发现其他问题，为它们记单独的 GitHub issues 和 RCAs
- 完全遵循项目编码标准
- 在宣布完成前确保所有验证通过
- 提交消息 `Fixes #$ARGUMENTS` 会把提交链接到 GitHub issue
