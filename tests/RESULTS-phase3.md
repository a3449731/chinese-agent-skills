# 技能包测试结果（阶段 3 · 任务 4/5：远期技能落地）

> 执行时间：2026-09-01
> 被测对象：`hooks-create`（改造安装）、`build-dark-factory`（全量落地 + 演示仓库建厂）
> 演示仓库：`~/Desktop/GXW/dark-factory-demo`（与 `gxw-vue-app` 完全隔离）
> 前置：阶段 1（校验/审查）、阶段 2（测试，31 技能全过）见 `RESULTS.md`

## 总体结果

| 层 | 结果 | 结论 |
|---|---|---|
| T5 hooks 保证层 | **14/14 通过** | 三种守卫双向验证 + 故障开放 + 端到端真实提交拦截 |
| T6-1 脚本层 | **4 个自带测试全绿 + 体检 0 FAIL/0 WARN** | doctor 22/22、runner 56/56、--mutate 全捕获、audit 12/12 |
| T6-2 验证装置有效性 | **变异 6/6 拦截** | 注入缺陷→门禁红；修复→绿（无人值守可信赖的核心证据） |
| T6-3 端到端 | **真实走通（本地编排）** | issue 0002 → 规划→实现→门禁→人工审阅→合并→部署，新功能实测上线 |
| T6-4 回归 | **33 目录 / FAIL 0；既有套件零失败** | validate 33/33、run_py 13/13、run_git 15/15、run_hooks 14/14；gxw-vue-app 零污染 |

## 任务 4：hooks-create 改造与安装

- **设计**：事件映射表重写为"用户目标→保证层"映射（6 层）；保留原版精华（故障开放、双向自证、覆盖诚实、`--no-verify` 边界、`sys.executable` 禁令）。
- **交付**：`SKILL.md`（94 行）+ `scripts/guard_template.py`（165 行纯标准库）+ `references/layers.md`（husky/原生钩子/CI/Claude Code 分支接入细节）；安装到 `~/.qoder-cn/skills/hooks-create/`，docs 同步。
- **T5 证据**（`run_hooks_tests.sh`，临时仓库自动清理）：
  - pre-commit：暂存 `.env` 被拒（退 2）、正常文件放行（退 0）
  - commit-msg：conventional 消息放行、不合规拒绝
  - pre-push：项目命令（`shell=True` 逐字运行）绿放行、红阻止
  - 故障开放：非 git 环境、未知模式均退 0
  - 端到端：真实 `git commit` 含 `.env` 被钩子阻止（git 退 1）、合规提交成功

## 任务 5：build-dark-factory 全量落地

### 5a 依赖（用户决策：先纯本地建厂，GitHub 后补）

- `gh` 2.98.0 / `uv` 0.12.8 经 brew 安装；`gh` 未登录 → files 本地后端
- 本机补 `python` → python3.11 软链（模板硬编码 `python`，不改模板）

### 5b 安装门禁（自带 4 测试）

| 测试 | 结果 |
|---|---|
| `_test_factory_doctor.py` | 22/22 |
| `_test_runner.py` | 56/56（修复本机 `python` 缺失后） |
| `_test_runner.py --mutate` | 注入缺陷全部被套件捕获 |
| `_test_audit_runner.py` | 12/12（修复作者硬编码 Windows 路径后，对 docs 英文原版树运行） |

### 5c 演示仓库建厂（按技能自身流程逐阶段，17 个提交）

| 阶段 | 产出 | 可证明在工作的证据 |
|---|---|---|
| Phase 0 | PRD + tasklist 行走骨架（add/list/done） | 单测 5 个通过 |
| 组件 4 指导层 | MISSION/FACTORY_RULES/CLAUDE（含可观察性/棘轮规则） | doctor provenance/scope 检查通过 |
| 组件 5 验证装置 | cli 驱动 + 8 步 e2e + 3 场景留出 + 6 缺陷变异集 | 全门禁绿（见 T6-2） |
| 组件 1 工作流仓库 | config/guard/floor/prompts 适配（9 占位符全清） | guard 对干净 diff `PROTECTED_OK` |
| 组件 3 部署 | 快照 + CURRENT 指针 + HISTORY 回滚 + 健康检查 | 首部署✓、空快照拒绝✓、回滚✓、再前进✓ |
| 组件 2 触发器 | cron 方案（30 分钟） | 拨盘 0 时 `--install` 被拒（预期安全行为） |
| 手动一圈 | issue 0002（`count` 子命令）全流程 | 见下 |

**手动一圈（真实 `claude -p` 驱动）**：prime→plan→implement→guard→review→judge→
`GATE_PASS_HELD`（22 条假设，人工审阅后合并）→ squash 合并 → 部署；新功能在快照实测
`open: 1` → `done` → `open: 0`。途中三次**机制证明**：
1. 凭证 401 时节点失败被正确归因（NODE_FAILURE 写明原因）并升级 needs-human，不静默；
2. 人工提交与分支冲突时工厂拒绝猜测合并、升级人工；
3. judge 把 files 后端的状态记录误判为"分离被破坏"→ 提示词加 files 后端例外（人工评审），重验通过。

另有 allowlist 证据：节点被拒绝 Bash 后改用被允许的读法完成任务（NODE_DENIED→NODE_OK）。

### 5d T6 测试矩阵

- **T6-1**：自带 4 测试全绿（5b）；`factory_doctor --repo . --audit` 终态 **0 FAIL · 0 WARN · 16 OK**（scaffold 标记全移除：模板残留 `harness/holdout/` 删除、7 份提示词头替换为本厂自述）。
- **T6-2**：`python harness/ci.py` → `MUTATIONS_TOTAL=6 / CAUGHT=6 / NOT_INJECTED=0`，同跑 `STATIC_OK / UNIT tests=5 / E2E steps=8 / HOLDOUT 3场景8断言 / GATE_OK`。
- **T6-3**：端到端见 5c"手动一圈"。降级标注：后端为本地 `claude -p`（用户自定义代理），GitHub issues/PR/Actions 未启用（`gh` 未登录）——编排、状态机、门禁、合并、部署全部真实发生，仅远端协作面待补。
- **T6-4**：`validate_skills.py` 33 目录（预期 33，FAIL 0）；`run_py_tests.py` 13/13、`run_git_tests.sh` 15/15、`run_hooks_tests.sh` 14/14；`gxw-vue-app` 工作树无测试污染（临时目录全部自动清理、无残留 worktree）。

## 测试中发现并修复的问题

| # | 问题 | 归属 | 修复 |
|---|---|---|---|
| 1 | `_test_audit_runner.py` 硬编码作者 Windows 路径 | 技能脚本缺陷 | 改为参数/脚本位置推断（同步 docs 与安装版） |
| 2 | 模板硬编码 `python`，macOS 无 | 本机环境 | 建软链（不改模板，尊重设计） |
| 3 | e2e 空标题用例经 `shlex(posix=False)` 变成字面量 `""` 通过 | 测试构造（驱动语义） | 改 `run("add")` 无参形式 |
| 4 | judge 对 files 后端状态记录误判"分离被破坏" | 提示词适配缺口 | judge.md 加 files 后端例外（人工评审后提交） |
| 5 | 健康命令 `$(mktemp -d)` 在 config 加载时展开泄漏目录 | 建厂配置 | 改 eval 时求值 + 固定 `.factory/health-home` |
| 6 | claude CLI 凭证 401 | 用户环境 | 用户更新 key 后全部节点可用 |

## 手动项清单（交用户决定）

1. **真实过夜循环**：拨盘仍为 0；升档（0→1…）与 `install-trigger.sh --install` 武装触发器由用户择时执行（技能要求每档观察一个完整周期）。
2. **真实产品仓库建厂**：需用户自己的 PRD，对目标仓库调用 `build-dark-factory` 技能。
3. **GitHub 面补齐**：`gh auth login` 后，演示/真实工厂可切换到 GitHub Issues/PR/Actions 后端（含定时触发与 PR 门禁）。
4. **技能真实触发验证**：在 IDE 中说"帮我写个钩子…"/"给这个仓库建一座暗工厂"，确认两个技能按描述匹配加载。
