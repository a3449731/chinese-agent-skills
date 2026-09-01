---
name: worktree-create
description: 为一个或多个 git worktree 创建并行开发环境——每个在自己的分支上、复制 gitignored 配置、安装依赖、做健康检查——通过为每个 worktree 派发一个设置子代理实现。在开始隔离的并行工作、同时运行多个 PIV 循环、或用户说"设置 worktrees"、"创建一个 worktree"、"启动并行分支"、或调用 /worktree-create 时使用。
argument-hint: "[branch ...]  （一个或多个分支名；留空 = 问）"
---

# Worktree Create

从分支列表搭起**任意数量**的隔离 git worktree——每个从正确的 base 创建、得到它的 gitignored 配置、它的依赖、和一次健康检查——通过为每个 worktree 派发一个设置子代理让它们并行运行。每个 worktree 的准备工作与应用无关，全部**从仓库检测**，绝不硬编码。

## 执行环境（Qoder / Cursor）

git worktree 是纯 git 功能，跨工具通用。在 Qoder 中，所有命令通过 **Bash 工具（终端）** 执行；在 Cursor 中通过内置终端执行。子代理派发：Qoder 用 **Agent 工具**；不支持并行子代理的环境按顺序逐个执行。

## 输入

`$ARGUMENTS` 是要创建的分支列表。

- **没给** → 问要创建哪些分支（或提议从进行中的 ticket 推导）。不要猜。
- **一个** → 内联设置单个 worktree（扇出一个是多余的）。
- **两个或更多** → 每个分支扇出一个子代理，并行。

## 扇出前先检测一次项目设置

读取 `references/worktree-setup.md` —— 它列出了全新 worktree 需要的一切，以及如何逐项从仓库检测。从**这个**仓库确定（不是从假设），一次：

- **安装命令**（monorepo → 每个包一个），
- **要复制的 gitignored env/配置文件**（或仓库的 `.worktreeinclude`），
- **验证/健康检查命令**（应用暴露健康端点就用它，否则构建/测试冒烟——偏好 CI 跑的那个），
- **一个 base 端口**，仅当健康检查会启动服务时。

挑选一个 worktree 根目录（`worktrees/<branch>`，gitignored），如果会启动服务，给每个 worktree 分配一个不同的端口 = `base + index`，这样并行服务器不会冲突。

## 每个分支派发一个设置子代理（并行）

用 Agent 工具一次性派发全部子代理（Qoder），让它们并行；不支持并行的环境按顺序逐个执行。给每个子代理同样的提示词，只替换 `BRANCH` 和 `PORT`：

```
为分支设置一个 git worktree：BRANCH   （分配的端口：PORT，只有你启动服务时才相关）

遵循本技能附带的 `references/worktree-setup.md` 检查清单。具体来说：
1. 从 base 分支创建 worktree：  git worktree add worktrees/BRANCH -b BRANCH
2. 把项目需要的 gitignored 配置/机密复制进 worktrees/BRANCH
   （为本仓库检测出的 env/配置文件；复制前用 `git check-ignore` 逐个验证）。
3. 用项目检测出的包管理器安装依赖（monorepo 则每个包都装）。
4. 运行应用启动所需的任何 generate/build 步骤（没有就跳过）。
5. 验证：运行检测出的健康检查（如有健康端点则启动并访问 PORT 上的健康端点，
   否则构建/类型检查/测试冒烟）。然后停掉你启动的任何服务器。

精确报告：worktree 路径 · 分支 · 依赖已安装（是/否）· 健康检查（PASS/FAIL）· 任何错误。
```

把检测出的命令（安装、env 文件列表、健康检查）填进模板。单个分支时，直接运行步骤而不是生成子代理。

## 汇总并报告

收集报告并打印每个 worktree 的摘要（路径 · 分支 · 依赖 · 健康 · 端口）、一行合并的 `N 个 worktree 已就绪`、下一步（打开每个 worktree / 在里面启动一个 PIV 循环），以及清理提醒：分支合并后执行 `git worktree remove worktrees/<branch>`。

如果任何 worktree 的健康检查失败，明确标出它，**不要**报告它已就绪。

## 资源

- `references/worktree-setup.md` —— 通用、与应用无关的检查清单，覆盖全新 worktree 需要的一切，以及如何按项目检测每一块。在检测设置前读取它。
