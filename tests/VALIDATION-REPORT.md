# 技能包静态校验报告（阶段 1 测试基线）

- 校验时间: （脚本运行日）
- 技能目录: `/Users/yang/.qoder-cn/skills`
- 目录数: 31（预期 31）| FAIL: 0 | WARN: 10 | PASS: 21

| 技能 | 行数 | 状态 | 问题 |
|---|---|---|---|
| ablate-ai-layer | 111 | WARN | C4 无 argument-hint（可接受） |
| agent-browser | 74 | WARN | C4 无 argument-hint（可接受） |
| ast-grep | 343 | WARN | C4 无 argument-hint（可接受） |
| opportunity-scan | 68 | PASS | - |
| piv-commit | 31 | WARN | C4 无 argument-hint（可接受） |
| piv-create-pr | 87 | PASS | - |
| piv-fix-review-findings | 47 | PASS | - |
| piv-implement | 122 | PASS | - |
| piv-implement-issue | 240 | PASS | - |
| piv-investigate-issue | 240 | PASS | - |
| piv-plan-implementation | 497 | WARN | C5 行数 497（接近上限 500，仅记录） |
| piv-review-changes | 115 | WARN | C4 无 argument-hint（可接受） |
| piv-review-pr | 78 | PASS | - |
| piv-run-full-loop | 77 | PASS | - |
| piv-slice-epic | 78 | PASS | - |
| piv-validate | 77 | WARN | C4 无 argument-hint（可接受） |
| plan-architecture | 132 | PASS | - |
| plan-create-prd | 109 | PASS | - |
| plan-create-stories | 75 | PASS | - |
| prime-backend | 107 | PASS | - |
| prime-codebase | 102 | PASS | - |
| prime-frontend | 100 | PASS | - |
| rules-check-drift | 59 | PASS | - |
| rules-create-global | 122 | PASS | - |
| second-brain-audit | 163 | WARN | C4 无 argument-hint（可接受） |
| setup-ai-tutor | 81 | WARN | C4 无 argument-hint（可接受） |
| skills-create | 72 | PASS | - |
| system-evolution-review | 193 | PASS | - |
| system-execution-report | 74 | WARN | C4 无 argument-hint（可接受） |
| worktree-create | 64 | PASS | - |
| worktree-merge | 52 | PASS | - |

## 术语残留命中（人工判定）

- `piv-commit`: bare agent @L28: 仅当 `.claude/` 下有文件被修改或添加时才包含此章节（CLAUDE.md、`.claude/references/`、`.claude/skills/`、`.claude/agents/` 
- `piv-investigate-issue`: bare agent @L38: - **`research-agent`**（第二个探索者）— 找到相关代码在哪里 + 可借鉴的模式：issue 中的错误字符串、相关函数/模块、类似实现、现有测试模式。
- `piv-review-pr`: bare agent @L37: 如果项目有 **`code-reviewer`** 子代理（`.claude/agents/code-reviewer.md`），把深度检查交给它；否则在本会话中用干净上下文评审——它对照项目标准评审
- `rules-create-global`: bare agent @L70: - **推给按需加载** → 反复出现但属于任务*类型*特定的模式 → 按需加载的参考资料（Claude Code 上是 `.claude/references/<topic>.md`；你的工具找得到

## 人工判定结论（2026-09-01）

1. **残留段 4 条均为 Claude Code 专属路径/专名，非低级术语残留**，归任务 2 专属审查范围（见 `COMPATIBILITY-REVIEW.zh-CN.md`）：
   - `piv-commit` L28：`.claude/agents/` 路径
   - `piv-investigate-issue` L38：`research-agent` 子代理名
   - `piv-review-pr` L37：`.claude/agents/code-reviewer.md` 路径
   - `rules-create-global` L70：`.claude/references/` 与 `.agent/` 路径
2. **已修复的低级问题（10 处，安装目录与 docs/skills 资料库同步）**：
   - `ablate-ai-layer`：承重→关键 ×2、与 agent 无关→与 AI 助手无关 ×1
   - `skills-create`：agent 忘记→AI 助手忘记 ×1
   - `piv-plan-implementation`：执行 agent→执行 AI 助手 ×4
   - `piv-investigate-issue`：派发专门 agent→派发专门 AI 助手 ×1
   - `piv-review-pr`：code-reviewer agent→code-reviewer 子代理 ×1
3. **脚本误报排除（validate_skills.py 已加 EXCLUDE_LINE_TOKENS）**：agent-browser（CLI 产品名）、AGENTS.md、.agents/、agents.md、agentcore 等专名行不再报残留。
4. **C4 WARN（9 技能无 argument-hint）**：对照英文原版确认原版即无此字段（无参数或参数可选技能），非翻译遗漏 → 接受。
5. **C5 WARN（piv-plan-implementation 497 行）**：接近 500 上限，仅记录，不处理。
6. **环境清理**：已删除 3 个 .DS_Store（技能库根、ablate-ai-layer/、skills-create/）。
7. **基线声明**：本报告为阶段 2 测试基线；阶段 2 不再全量重复静态校验，仅对上述修复项做回归确认。

## P0/P1/P2 优化改造回归（2026-09-01 下午）

**触发**：用户指示"优化阶段一的 P0/P1/P2，完成后执行阶段 2 测试"。本批为阶段 1 审查报告（COMPATIBILITY-REVIEW.zh-CN.md）的落地改造。

**改造范围（安装目录 ~/.qoder-cn/skills/ 与 docs/skills 资料库同步）**：
- **P0（3 技能 13 处）**：piv-run-full-loop（6 处 `.claude/skills/` 引用 → `~/.qoder-cn/skills/` + `docs/ai/plans/`）、system-evolution-review（3 处）、skills-create（SKILL.md + references/creating-skills.md + validation.md 脚手架/验证命令 `.claude/skills/` → `~/.qoder-cn/skills/` 或 `.qoder/skills/`）
- **P1（9 技能 27 处）**：产出目录 `.claude/plans|reports|code-reviews|execution-reports|system-reviews` → `docs/ai/` 同名子目录；读取约定 `.claude/references/conventions.md` → `AGENTS.md`/`CLAUDE.md` 的 `## commit`/`## pr` 章节；`.claude/references/` → 项目声明的参考资料（含 `.qoder/rules/`）；子代理 → Qoder create-subagent / Agent 工具 CodeReview 子代理
- **P2（8 技能 10 处）**：AskUserQuestion → 问题工具（AskUserQuestion）；/init → 初始化流程；日志位置与能力文档补 Qoder；Task 工具 → Agent 工具并行派发；Atlassian MCP 未配置时跳过（prime-* 三件套 + piv-slice-epic 本地 ticket 降级）

**回归结果（validate_skills.py 重跑）**：
- 目录数 31（预期 31）| **FAIL: 0** | WARN: 10（9×C4 argument-hint 可接受 + 1×C5 行数仅记录）| PASS: 21 —— 与阶段 1 基线完全一致
- 安装目录与 docs 版残留检查：`.claude/plans|reports|code-reviews|execution-reports|system-reviews|conventions|skills/` 路径、`多个 Task 调用`、`外加一个起步的` 全部 **零残留**
- 术语残留命中 3 条，均为已判明合理引用：`research-agent`（piv-investigate-issue 子代理名，审查确认保留）、`code-reviewer`（piv-review-pr 子代理名，审查确认保留）、`.agent/`（rules-create-global 跨工具说明，Cursor 规则目录）

**结论**：P0/P1/P2 全部落地，静态校验与阶段 1 基线一致，可进入阶段 2 测试。
