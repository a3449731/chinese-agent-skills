# Claude Code 专属痕迹审查报告（Qoder/Cursor 兼容性）

> 存档说明：本文件原为 gxw-vue-app/docs/skills 资料库的历史文档，2026-09-01 归档至本仓库；最新内容以本仓库 README 为准。
>

> 审查对象：`~/.qoder-cn/skills/` 下 31 个已安装技能（2026-09-01）
> 审查性质：只读审查，**未改动任何技能文件**；本报告给出逐技能改造建议，由用户决定是否执行
> 判定基准：Qoder 个人技能库（`~/.qoder-cn/skills/`）与项目规则（AGENTS.md / CLAUDE.md / .qoder/）；Cursor 项目规则（.cursor/rules）

## 总体结论

31 个技能中 **27 个可直接在 Qoder/Cursor 使用**（其中 8 个为"已适配确认"、19 个无专属痕迹或仅有可选依赖），**4 个存在需要优先处理的专属痕迹**：

| 优先级 | 技能 | 问题本质 |
|---|---|---|
| P0（引用已失效） | piv-run-full-loop、system-evolution-review、skills-create | 引用 `.claude/skills/` 路径，但技能实际安装在 `~/.qoder-cn/skills/`，按原路径执行必然找不到 |
| P1（约定不被加载） | piv-plan-implementation、piv-implement、piv-review-pr、piv-review-changes、piv-commit、piv-create-pr、system-execution-report、rules-create-global、rules-check-drift | 产出/读取 `.claude/` 系列目录，Qoder 项目无此约定，跨会话衔接断链 |
| P2（措辞/链接/可选依赖） | opportunity-scan、worktree-merge、piv-investigate-issue、prime-codebase/frontend/backend、plan-*、piv-slice-epic | 工具措辞、文档链接、Atlassian MCP 等，不影响功能，可改可不改 |

不存在"机制级不可移植"的技能（原两个远期锚定技能已在阶段 3 落地，见第五节结论）。

---

## 一、P0：引用路径已失效（3 技能）

技能安装位置是 `~/.qoder-cn/skills/<name>/SKILL.md`，但下列技能正文仍引用 Claude Code 生态路径 `.claude/skills/<name>/SKILL.md` 与 `.claude/plans/`，在 Qoder 环境按原文执行必然找不到文件。

### 1. piv-run-full-loop（全流程链式调用）
- 位置：L19、L27、L37、L47（技能路径引用）；L63、L68（计划产出路径）
- 专属内容：`运行 prime-codebase 技能（.claude/skills/prime-codebase/SKILL.md）`、`用计划文件路径运行 piv-implement 技能（.claude/skills/piv-implement/SKILL.md）：.claude/plans/[feature-name].md`
- 为什么专属：`.claude/skills/` 是 Claude Code 技能安装目录；Qoder 个人技能在 `~/.qoder-cn/skills/`
- Qoder/Cursor 等价方案：改为"运行已安装的 `prime-codebase` 技能（个人技能库，或调用 /prime-codebase）"；计划路径改为项目内约定目录（见 P1 统一方案）
- 改动量：低（6 处文本）｜优先级：**P0**

### 2. system-evolution-review（系统演化评审）
- 位置：L35、L43（技能路径引用）；L107（产出路径）
- 专属内容：`.claude/skills/piv-plan-implementation/SKILL.md`、`.claude/skills/piv-implement/SKILL.md`、`.claude/system-reviews/`
- 为什么专属：同上
- Qoder/Cursor 等价方案：技能路径改为个人技能库；产出目录并入 P1 统一方案
- 改动量：低（3 处）｜优先级：**P0**

### 3. skills-create（制造技能的技能，元技能）
- 位置：SKILL.md L50；references/creating-skills.md L30-31、L57；references/validation.md L10-11、L36
- 专属内容：脚手架命令 `mkdir -p .claude/skills/<name>`、`cp .claude/skills/skills-create/templates/SKILL.template.md ...`、验证命令 `ls -R .claude/skills/<name>`；`skill-reviewer`（Claude Code 原生评审子代理）
- 为什么专属：整套脚手架按 Claude Code 技能目录约定编写；在 Qoder 中执行会把新技能建到错误的目录（.claude/skills/ 不被 Qoder 扫描）
- Qoder/Cursor 等价方案：脚手架目标改为 `~/.qoder-cn/skills/<name>/`（个人技能库，跨项目可用）或 `.qoder/skills/<name>/`（项目级）；验证命令同步；`skill-reviewer` 改为复用 `code-reviewer` 子代理或人工评审（Qoder 无原生 skill-reviewer）
- 改动量：中（主文件 1 处 + references 3 文件 6 处）｜优先级：**P0**

---

## 二、P1：.claude/ 产出与约定目录不被加载（9 技能）

`.claude/` 系列目录是 Claude Code 的目录约定；Qoder/Cursor 项目不会自动加载其中内容，且 gxw-vue-app 等 Qoder 项目没有这些目录。单次执行仍可用（路径存在与否不影响技能本身运行），但**跨技能/跨会话衔接会断链**（piv-implement 写的报告，piv-review-pr 读不到；plans 目录无人消费等）。

### 统一改造建议（适用以下全部技能）
将产出目录从 `.claude/*` 统一改为项目内约定目录，建议 `docs/ai/`（plans、reports、code-reviews、execution-reports、system-reviews 各子目录），并在项目 AGENTS.md 中声明该约定；读取约定从 `.claude/references/conventions.md` 改为 AGENTS.md/CLAUDE.md 的 `## commit` / `## pr` 章节（Qoder、Cursor、Claude Code 均读取根级 AGENTS.md）。

| 技能 | 位置 | 专属内容 | 建议 |
|---|---|---|---|
| piv-plan-implementation | L76、L219、L439、L444 | `.claude/references`、`.claude/plans/` | 读取 → AGENTS.md/CLAUDE.md；产出 → docs/ai/plans/ |
| piv-implement | L86 | `.claude/reports/` | → docs/ai/reports/ |
| piv-review-pr | L27-28、L37、L59、L63、L65、L67 | `.claude/references/`、`.claude/agents/code-reviewer.md`、`.claude/code-reviews/` | 约定 → AGENTS.md；子代理 → Qoder 等价（见下）；产出 → docs/ai/code-reviews/ |
| piv-review-changes | L28、L86 | `.claude/references/`、`.claude/code-reviews/` | 同上 |
| piv-commit | L12、L28、L30 | `.claude/references/conventions.md`、AI 层章节检查 `.claude/` | 约定 → AGENTS.md `## commit` 章节；AI 层检查范围 → AGENTS.md/.qoder/ 等 |
| piv-create-pr | L37、L40 | `.claude/references/conventions.md`、`.claude/reports/` | 约定 → AGENTS.md `## pr` 章节；报告读取路径跟随 piv-implement |
| system-execution-report | L21 | `.claude/execution-reports/` | → docs/ai/execution-reports/ |
| rules-create-global | L56-57、L70、L96、L115 | `CLAUDE.md`（原生文件说明）、`code.claude.com/docs` 链接、`.claude/references/` 占位文档 | CLAUDE.md 保留（Qoder/Cursor 均可读根级 CLAUDE.md）；建议补充"Qoder/Cursor 下参考资料放 .qoder/rules/ 或 docs/ai/references/"；链接补 Qoder 文档 |
| rules-check-drift | L15 | 忽略范围含 `.claude/` 的 agent/command/skill 文件 | 忽略范围补充 `.qoder/`、`.qoder-cn/` 等 |

改动量：每技能 1-6 处文本替换，整体为一次批量替换任务（低-中）｜优先级：**P1**

---

## 三、P2：工具措辞、文档链接、可选外部依赖（不阻断使用）

| 技能 | 位置 | 专属内容 | 判定与建议 |
|---|---|---|---|
| worktree-merge | L40 | `AskUserQuestion` | Qoder 有同名工具，**无需改**；如需更通用可写"用问题工具（AskUserQuestion）询问" |
| rules-create-global | L3（description） | `/init`（Claude Code 内置命令） | Qoder 无 /init；建议改为"替换泛化的初始化输出"，description 同步更新 |
| opportunity-scan | L25、L33 | `~/.claude/projects/` 日志示例、`code.claude.com/docs` 能力文档 | 示例性质（本身是"与具体 AI 助手无关"设计）；建议补一句 Qoder 日志位置（如 ~/.qoder-cn/ 下会话记录）与 Qoder 可扩展性文档 |
| piv-investigate-issue | L36、L38 | "一条消息、多个 Task 调用"、`codebase-analyst`/`research-agent` 子代理名 | Task 工具是 Claude Code 子代理工具名；Qoder 等价为 Agent 工具并行派发；子代理名可保留为角色名或改为 Qoder 自定义子代理 |
| prime-codebase/frontend/backend | 各 L24、L25、L30 | `mcp__atlassian__getAccessibleAtlassianResources` 等工具名 | MCP 协议通用，工具名格式 `mcp__server__tool` 在 Qoder 中同样可解析；**只需在 Qoder 安装 atlassian MCP 服务器即可用**；未安装时技能已有本地降级（不传 Jira/Confluence 参数即跳过）→ 建议在技能中补一句"未配置 Atlassian MCP 时跳过该步" |
| piv-slice-epic | L3、L17、L49、L76 | Atlassian MCP（Jira）、Archon tasks | 同上；本地 fallback（docs/tickets/）已存在 → 可选 |
| plan-architecture | L9、L77 | Atlassian MCP | 同上 |
| plan-create-prd | L79 | Atlassian MCP（Confluence/Jira 目标） | 同上 |
| plan-create-stories | L46 | Atlassian MCP 服务器 | 同上 |
| piv-plan-implementation | L15 | Atlassian MCP + `gh issue view` | gh 为通用 CLI，非专属；Atlassian 可选 |

---

## 四、已适配确认（8 技能，无需改动）

| 技能 | 适配状态 |
|---|---|
| agent-browser | 批次 4 已重写：主路径 = Qoder Browser 子代理 / Cursor 浏览器预览；agent-browser CLI 降为可选高级路径 |
| ast-grep | 批次 4 已重写：主路径 = Qoder Grep + LSP + SearchCodebase；CLI 规则语法为可选 |
| worktree-create | 批次 4 已适配：设置子代理经 Agent 工具派发，README 说明 Qoder/Cursor 执行路径 |
| worktree-merge | 已适配（仅 AskUserQuestion 措辞，见 P2） |
| ablate-ai-layer | 本身 agent-agnostic：扫描 CLAUDE.md/AGENTS.md/.claude/.agents/.cursor/rules 等全部主流 AI 层格式 |
| setup-ai-tutor | 无专属痕迹（示例项目专用） |
| piv-implement-issue | 无专属痕迹（gh 通用 CLI） |
| second-brain-audit | 无专属痕迹（含独立 py 脚本，跨工具通用） |

## 五、远期技能落地结论（阶段 3，取代原"适配待定"）

两个远期锚定技能均已安装并通过真实测试，不再有"待定"项：

- **hooks-create → 改造为跨工具确定性保证技能（已安装）**：原版以 Claude Code 生命周期事件为骨架，改造版以"用户目标→保证层"为骨架：git pre-commit/pre-push/commit-msg 钩子（能阻止）为主路径，GitHub Actions 补位，Claude Code hooks 作为一个分支保留（仅 Claude Code 用户），IDE 规则层诚实标注为软约束。守卫模板纯标准库、故障开放、双向验证；T5 套件 14/14 通过。
- **build-dark-factory → 全量落地（已安装）**：五组件（指导层/验证装置/工作流仓库/部署/触发器）在演示仓库 `dark-factory-demo` 真实建成；变异测试 6/6 拦截、`factory_doctor` 0 FAIL/0 WARN、手动一圈端到端走通（issue→规划→实现→门禁→人工审阅→合并→部署）。Claude Code 专属痕迹的处理：治理文件保留 CLAUDE.md（建在目标仓库、跨工具可读）；后端 `claude -p` 可替换（`FACTORY_AGENT` 单一可执行体约定）；GitHub 集成（issues/PR/Actions）在 `gh` 登录后启用，未登录时自动回退 files 本地后端。
- 证据与手动项清单见 `docs/skills/tests/RESULTS-phase3.md`。

## 六、不动作清单（保留专名）

- `agent-browser`、`AGENTS.md`、`agents.md`（规范站点）、`research-agent`/`codebase-analyst`（子代理角色名）、`.agent/`（跨工具参考目录示例）——均非残留
- `gh` 命令、`git worktree`——通用 CLI，非 Claude 专属
- CLAUDE.md 本身——Qoder/Cursor 均读取根级 CLAUDE.md/AGENTS.md，非硬专属；建议新项目以 AGENTS.md 为主（开放标准）

## 七、建议执行顺序

1. **P0 批次**：piv-run-full-loop、system-evolution-review、skills-create 路径改造（3 技能，文本级）
2. **P1 批次**：9 技能统一目录约定改造（建议同时定 AGENTS.md 约定段）
3. **P2 批次**：随改随清（/init 措辞、链接补充、MCP 说明）
4. 每批次后重跑 `docs/skills/tests/validate_skills.py` 回归，并同步 docs/skills/ 资料库

## 附录：与测试计划的关系

- 本报告为任务 2 交付物；阶段 2（任务 3）测试场景将把"专属痕迹是否已按用户决定改造"纳入回归范围
- 阶段 2 的 TEST-PLAN 将标注：P0 技能在 Qoder 环境的关键路径用例（如 piv-run-full-loop 引用的技能是否可解析）为必测项
