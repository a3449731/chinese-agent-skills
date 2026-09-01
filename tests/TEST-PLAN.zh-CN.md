# 技能包测试计划（阶段 2 · 任务 3）

> 存档说明：本文件原为 gxw-vue-app/docs/skills 资料库的历史文档，2026-09-01 归档至本仓库；最新内容以本仓库 README 为准。
>

> 被测对象：`~/.qoder-cn/skills/` 下 31 个技能（截至 2026-09-01，P0/P1/P2 优化改造完成后）
> 测试基线：`VALIDATION-REPORT.md`（阶段 1 静态校验，31 目录 / 0 FAIL / 10 WARN 可接受 / 21 PASS）
> 本计划遵循用户决策：**不重复全量静态校验**（以阶段 1 报告为基线），只做动态测试 + 修复项定向回归。

## 测试分层

| 层 | 名称 | 方式 | 覆盖 |
|---|---|---|---|
| T1 | 静态回归 | 重跑 `validate_skills.py` + 残留 grep | P0/P1/P2 改造的 18 个技能文件（安装版 + docs 版） |
| T2 | py 脚本真实运行 | `run_py_tests.py` | 3 个附带 py 脚本的技能：ablate-ai-layer（map_layer.py / run_ablation.py）、second-brain-audit（audit.py） |
| T3 | 真实 git 演练 | `run_git_tests.sh` | worktree-create / worktree-merge 的核心 git 机制、run_ablation --dry-run 只读性 |
| T4 | 手动标注 | 矩阵表 | 31 技能中需真人触发/依赖外部服务的项 |

## T1 静态回归（已完成）

- 重跑 `validate_skills.py`：31 目录 / **FAIL 0** / WARN 10（9×C4 argument-hint 对照英文原版确认原版即无，1×C5 行数仅记录）/ PASS 21，与阶段 1 基线一致。
- 残留 grep：`.claude/plans|reports|code-reviews|execution-reports|system-reviews|conventions|skills/`、`多个 Task 调用`、`外加一个起步的` 在安装版与 docs 版 **零残留**。
- 结论记录于 `VALIDATION-REPORT.md`「P0/P1/P2 优化改造回归」小节。

## T2 py 脚本真实运行

测试对象与用例（详见 `run_py_tests.py`，纯标准库）：

| 脚本 | 真实用例 | 断言 |
|---|---|---|
| `ablate-ai-layer/scripts/map_layer.py` | ① 对 gxw-vue-app 仓库（真实仓库）② 对临时迷你仓库（含 CLAUDE.md + AGENTS.md + .claude/skills/）③ `--json` 模式 | 退出码 0；输出含 `always-loaded`/`on-demand` 分类；--json 为合法 JSON 且包含两类文件；只读（不改动仓库） |
| `second-brain-audit/scripts/audit.py` | 构造临时笔记目录：2 个文件对同一主题给出矛盾值 + 1 个无矛盾文件 | 退出码 0；输出发现矛盾（两个文件都出现在报告中）；`--json` 为合法 JSON 且含 contradiction 条目；只读 |
| `ablate-ai-layer/scripts/run_ablation.py` | 临时 git 仓库（含 CLAUDE.md + task.md），`--dry-run` | 退出码 0；打印计划且 `--dry-run: nothing executed`；**工作树未被修改**（`git status` 干净）；不创建残留 worktree |

## T3 真实 git 演练

在 `/tmp` 临时仓库真实执行（详见 `run_git_tests.sh`），演练 worktree-create / worktree-merge 技能的核心 git 机制：

1. **worktree-create 机制**：`git worktree add` 两个并行分支（feat-a、feat-b），每个 worktree 独立；模拟技能要求的"复制 gitignored 配置"（.env 从主树复制）与健康检查（`git status --porcelain` 干净）。
2. **worktree-merge 机制**：经中转集成分支（integration）按序合并两个特性分支，每次合并后验证（文件内容断言），`--no-ff` 合并回主分支，最后清理 worktree 与分支。
3. **run_ablation.py --dry-run**（与 T2 同一脚本，此处以 shell 视角验证）：在演练仓库上执行，确认工作树零改动。

不执行的部分（依赖外部/人工，标注于 T4）：
- run_ablation 完整双臂运行（需真实 agent 执行任务，无法自动化）
- worktree 技能中"派发设置子代理"（子代理属 IDE 能力）

## T4 31 技能测试矩阵

覆盖方式：**S**=静态校验（validate_skills.py C1-C8）、**P**=py 脚本真实运行、**G**=git 演练、**M**=需手动（依赖交互/外部服务/工具链）。

| 技能 | 覆盖 | 手动标注内容 |
|---|---|---|
| ablate-ai-layer | S + P | run_ablation 完整双臂需真实 agent |
| agent-browser | S | 浏览器自动化需真实浏览器（Qoder Browser 子代理） |
| ast-grep | S | AST 搜索需真实代码库；Qoder 用 Grep/LSP 组合 |
| opportunity-scan | S | 输出 HTML 报告需真实会话日志 |
| piv-commit | S | 提交消息质量需真人判断 |
| piv-create-pr | S | 需 gh CLI + GitHub 远端 |
| piv-fix-review-findings | S | 需评审发现产物 |
| piv-implement | S | 需计划文件 + 真实实现 |
| piv-implement-issue | S | 需 RCA 产物 + GitHub issue |
| piv-investigate-issue | S | 需 GitHub issue + 子代理派发 |
| piv-plan-implementation | S | 需 ticket/需求 + 澄清访谈 |
| piv-review-changes | S | 需未提交更改 + 评审报告 |
| piv-review-pr | S | 需 gh CLI + PR + code-reviewer 子代理 |
| piv-run-full-loop | S | 全自动特性开发需真实任务 |
| piv-slice-epic | S | 需 epic 文档 + 工单系统 |
| piv-validate | S | 需项目验证套件（本项目可跑 npm test 试） |
| plan-architecture | S | 交互式访谈 |
| plan-create-prd | S | 交互式访谈 |
| plan-create-stories | S | 需 PRD + 工单系统 |
| prime-backend | S | 需真实代码库（本项目后端段可试） |
| prime-codebase | S | 需真实代码库（本项目可试） |
| prime-frontend | S | 需真实代码库（本项目前端可试） |
| rules-check-drift | S | 需近期更改 + 规则文件（本项目 AGENTS.md 可试） |
| rules-create-global | S | 交互式推导（本项目全新/存量均可试） |
| second-brain-audit | S + P | 完整审计需真实笔记库 |
| setup-ai-tutor | S | 需克隆 AI Tutor 项目（示例项目专用） |
| skills-create | S | 创建新技能需真人验收 |
| system-evolution-review | S | 需实现报告产物 |
| system-execution-report | S | 需刚完成的实现 |
| worktree-create | S + G | 子代理派发需 IDE；git 机制已演练 |
| worktree-merge | S + G | 完整套件运行需项目验证；git 机制已演练 |

## 执行顺序与验收标准

1. T1 → T2 → T3 顺序执行，产出 `RESULTS.md`。
2. 验收标准：
   - T1：FAIL 0（已达成）。
   - T2：3 个脚本全部退出码 0 且断言通过（失败记入 RESULTS.md 并分析是脚本 bug 还是测试构造问题）。
   - T3：worktree 创建/合并全流程真实成功，仓库状态干净。
   - T4：矩阵标注完成，明确哪些项留给真人验证。

## 测试环境与清理

- 全部测试在 `/tmp/skill-test-*` 临时目录进行；`gxw-vue-app` 仅被 map_layer.py 只读扫描，不产生任何写操作。
- 测试结束自动清理临时目录、临时 worktree、临时分支（`trap` 保证）。
- 不触碰 `~/.qoder-cn/skills/` 与 `docs/skills/` 的任何文件。
