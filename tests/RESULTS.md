# 技能包测试结果（阶段 2 · 任务 3）

> 执行时间：2026-09-01
> 被测对象：`~/.qoder-cn/skills/` 下 31 个技能（P0/P1/P2 优化改造完成后）
> 测试计划：`TEST-PLAN.zh-CN.md` · 静态基线：`VALIDATION-REPORT.md`
> 测试过程在 `/tmp` 临时目录进行，未对 `gxw-vue-app` 工作区与技能库产生任何写操作。

## 总体结果

| 层 | 结果 | 结论 |
|---|---|---|
| T1 静态回归 | **31 目录 / FAIL 0 / WARN 10 / PASS 21** | 与阶段 1 基线一致；安装版与 docs 版 `.claude/` 专属路径零残留 |
| T2 py 脚本真实运行 | **13 通过 / 0 失败** | 3 个附带脚本（map_layer / audit / run_ablation --dry-run）全部行为正确 |
| T3 真实 git 演练 | **15 通过 / 0 失败** | worktree 创建/合并机制真实可行，仓库状态干净 |
| T4 手动标注 | 见 `TEST-PLAN.zh-CN.md` 矩阵 | 需真人触发/外部服务的项已标注 |

**总计：自动化可测项全部通过（28/28 断言），无脚本缺陷。**

## T2 py 脚本真实运行（13/13）

| 脚本 | 用例 | 结果 |
|---|---|---|
| `map_layer.py` | 对真实仓库（只读）扫描 | ✅ 退出 0，产出报告 |
| `map_layer.py` | 对迷你仓库（CLAUDE.md + AGENTS.md + .claude/skills/）文本/JSON 模式 | ✅ 正确分类 `always-loaded`/`on-demand`；JSON 字段 `kind` 合法（3 artifacts） |
| `map_layer.py` | 只读性 | ✅ `git status` 干净 |
| `audit.py` | 跨文件矛盾检测（同一主题两处不同金额） | ✅ 退出 0，报 `1 subject answered differently`；JSON `contradicted_subjects=1` |
| `run_ablation.py` | `--dry-run` | ✅ 退出 0，打印计划 + `--dry-run: nothing executed` |
| `run_ablation.py` | `--dry-run` 只读性 | ✅ HEAD 不变、无已跟踪文件改动、无残留 worktree |

## T3 真实 git 演练（15/15）

| 演练 | 验证点 | 结果 |
|---|---|---|
| 1 · worktree-create | 两个并行 worktree 注册、gitignored `.env` 复制、健康检查（干净状态）、分支隔离 | ✅ 4/4 |
| 2 · 并行工作 | 两分支独立提交、文件系统状态隔离 | ✅ 2/2 |
| 3 · worktree-merge | 经集成分支按序合并（无冲突）、合并后内容断言、合并后已跟踪文件干净 | ✅ 4/4 |
| 4 · 合并回主分支 + 清理 | 主分支推进、最终内容、worktree 移除、特性分支删除 | ✅ 4/4 |
| 5 · ablation --dry-run | 在含 AI 层（CLAUDE.md）仓库执行，工作树零改动 | ✅ 1/1 |

## 测试中发现并修正的问题（测试构造层面，非技能/脚本缺陷）

1. **map_layer JSON 字段**：顶层为 `{"root", "artifacts"}`，工件分类字段名是 `kind`（初版测试误写为 `classification`）→ 已修正断言。
2. **audit 主题归属**：矛盾检测按"页面文件名主题 + 行内粗体键 + 词表"归属；需让两个文件解析到**同一主题词**才能触发跨文件矛盾（初版用两个不同文件名主题无法配对）→ 已按脚本逻辑重新构造输入。
3. **run_ablation 需 AI 层**：无 `CLAUDE.md`/`AGENTS.md` 等 always-scope 工件时脚本正确报"无可消融"退出 1；T3 fixture 补充 `CLAUDE.md` 后 `--dry-run` 退出 0 → 测试构造问题，脚本行为正确。
4. **仓库内 worktree 目录**：`git worktree add worktrees/<branch>` 在主工作树留下未跟踪的 `worktrees/` 目录；脏检查改为只看已跟踪文件改动，符合技能真实用法。

以上均为测试断言/夹具修正，**被测的 3 个技能脚本与 31 个技能文件本身零缺陷**。

## 待真人验证项（T4）

以下技能依赖交互、外部服务或 IDE 能力，自动化无法覆盖，需真人在 Qoder/Cursor 中触发：
- 交互式访谈类：`plan-create-prd`、`plan-architecture`、`rules-create-global`
- 需外部服务/工单系统：`piv-slice-epic`、`plan-create-stories`、`prime-*`（Atlassian MCP 可选）
- 需 gh CLI + GitHub：`piv-create-pr`、`piv-review-pr`、`piv-investigate-issue`、`piv-implement-issue`
- 需真实任务/产物链：`piv-run-full-loop`、`piv-implement`、`system-execution-report`、`system-evolution-review`
- 需子代理派发（IDE 能力）：`worktree-create`（git 机制已演练）、`piv-review-pr` 的 code-reviewer
- `run_ablation.py` 完整双臂运行（需真实 agent 执行任务）

## 结论

阶段 2 任务 3 测试场景创建并执行完毕：
- 静态结构（T1）、附带 py 脚本（T2）、git 机制（T3）三层自动化测试**全部通过**。
- 31 技能中可自动化验证的部分（结构完整性、脚本正确性、worktree/ablation git 机制）均符合预期。
- 剩余项为交互/外部依赖类，已按矩阵标注，供真人在实际使用中按需触发验证。
