# 中文技能包：索引与触发方式速查

> 存档说明：本文件原为 gxw-vue-app/docs/skills 资料库的历史文档，2026-09-01 归档至本仓库；最新内容以本仓库 README 为准。
>

本目录是 **Cole Medin 技能体系的中文重整版资料库**：英文原版 + 中文重整版并存，英文原版一律不改。中文重整版已安装到个人技能目录 `~/.qoder-cn/skills/`（跨项目可用），共 **33 个技能**（含两个原远期锚定技能：hooks-create 已改造为跨工具确定性保证技能，build-dark-factory 已全量落地并在演示仓库建厂验证）。

## 怎么用

在 Qoder 中，技能按**语义匹配自动触发**：直接用自然语言描述你的需求（触发示例见下），Qoder 会依据技能 frontmatter 的 `description` 匹配并加载对应技能；也可在提示中显式输入技能名（如 `/piv-validate`）。无需手动安装或配置。

技能间按**双循环框架**衔接：外层循环（加载上下文 → 规划 → 切片）产出工作单元，内层循环（PIV：计划 → 实现 → 验证 → 评审 → 提交 → PR）逐个消费。下面按此顺序索引。

---

## 第一层：上下文与规划（7 个）

| 技能 | 一句话用途 | 中文触发示例 |
|---|---|---|
| `prime-codebase` | 快速建立对代码库的深度理解（结构、文档、关键文件），规划与实现前先加载全局 | "先了解一下这个项目的整体结构再开始" / "帮我加载代码库上下文" |
| `prime-frontend` | 只聚焦前端（组件、路由、状态、样式），不加载无关后端代码 | "我要改前端部分，先看看前端结构" |
| `prime-backend` | 只聚焦后端（API 路由、服务、数据模型、数据库层） | "后端要加个接口，先摸清后端结构" |
| `plan-create-prd` | 交互式访谈生成 PRD：问题 · 证据 · 假设 · 用户 · MVP · 成功指标 · 非目标（只写做什么/为什么，不碰怎么做） | "帮我为这个新项目写一份 PRD" |
| `plan-architecture` | 探索"如何实现"意图：方案、技术栈、数据形态、风险项，产出高层架构决策文档 | "这个功能应该用什么架构实现？" / "帮我做技术选型" |
| `plan-create-stories` | 把 PRD 分解成工程师可直接用的 ticket（Jira/GitHub issues） | "把这份 PRD 拆成 tickets" |
| `piv-slice-epic` | 把 epic（连同架构决策）切成 PIV 大小的 ticket 并画依赖图（全新项目用 PRD 输入） | "把这个 epic 切成小 ticket" / "把 PRD 拆成可执行的任务" |

## 第二层：PIV 实现循环（11 个）

| 技能 | 一句话用途 | 中文触发示例 |
|---|---|---|
| `piv-plan-implementation` | 针对单个 ticket/特性，经代码库分析 + 澄清访谈产出一步到位的实现计划 | "为这个 ticket 做一份实现计划" / "先规划再写代码" |
| `piv-investigate-issue` | 调查 GitHub issue 根因（并行探索 + 5 Whys），产出可评审的 RCA 产物 | "帮我调查这个 bug 的根因" |
| `piv-implement-issue` | 依据 RCA 产物实施修复：漂移检查、切分支、实现、回归测试、验证 | "按调查结果修这个 issue" |
| `piv-implement` | 按计划逐任务实现，每步都验证 | "按计划实现这个功能" |
| `piv-validate` | 运行项目完整验证套件（测试/类型/lint）并报告整体健康度 | "提交前帮我跑一遍全部验证" |
| `piv-review-changes` | 对最近改动做提交前技术评审，作为质量门禁 | "帮我评审一下我改的代码" |
| `piv-commit` | 原子化创建 git 提交，conventional 标签消息 | "帮我提交这些更改" |
| `piv-create-pr` | 推送分支并开 PR（自动检测 base、清晰正文、返回 URL） | "帮我开一个 pull request" |
| `piv-review-pr` | 完整 PR 评审：验证 + 全新视角评审 + 严重度分类 + 发布结论（人工批准前的自动化门禁） | "评审这个 PR" |
| `piv-fix-review-findings` | 对评审发现分级处理：逐条修复 + 配测试 + 验证 + 推送 | "把评审意见修掉" |
| `piv-run-full-loop` | 链式调用四个核心 PIV 技能，从一句话描述全自动开发完整特性 | "从零把这个功能完整做出来" |

## 第三层：治理与 Meta-skills（11 个）

| 技能 | 一句话用途 | 中文触发示例 |
|---|---|---|
| `rules-check-drift` | 检查规则文件（CLAUDE.md/AGENTS.md）是否与代码库漂移，附最小编辑建议 | "检查一下规则文件还准不准" |
| `rules-create-global` | 从 PRD/架构或已加载的代码库推导项目全局规则（CLAUDE.md + .claude/） | "为这个项目初始化规则文件" |
| `second-brain-audit` | 审计第二大脑/笔记/记忆中的过时事实，修复最糟的一处并防止复发 | "我的笔记里有哪些已经过时了？" / "记忆腐烂了怎么办" |
| `system-execution-report` | 生成实现报告：做了什么、偏离了什么、遇到什么挑战（系统评审的输入） | "为刚完成的功能写一份实现报告" |
| `system-evolution-review` | 元层面评审实现与计划的偏差，推荐 AI 层改进（找流程 bug，不是代码 bug） | "评审一下这次实现和计划差在哪" |
| `opportunity-scan` | 扫描真实协作过程，找出接下来该编码什么（反应式/主动式），产出 HTML 报告 | "看看我最近的使用记录，有什么值得做" |
| `setup-ai-tutor` | 本地搭建并启动 AI Tutor 示例项目（环境、依赖、数据库、迁移、开发服务器） | "把 AI Tutor 跑起来" |
| `skills-create` | 元技能：以你自己的方式创建新技能，或把臃肿技能重构为 SKILL.md + references/ | "创建一个技能" / "把这个流程变成技能" |
| `ablate-ai-layer` | 双臂实验测量 AI 指令是否配得上它们的位置，在临时 worktree 中运行，绝不触碰工作树 | "我的 CLAUDE.md 还有用吗？" / "帮我精简 AI 层" |
| `hooks-create` | 为仓库编写跨工具的确定性保证层（git 钩子/脚本守卫/CI 门禁），挑层、写脚本、接入并双向证明 | "绝不允许把 .env 提交进仓库" / "测试没绿不许推送" |
| `build-dark-factory` | 为产品仓库搭建无人值守自动化工厂：指导层、验证装置（含变异测试）、工作流运行器、部署、触发器五组件，拨盘 0-5 渐进自主 | "给这个仓库建一座暗工厂" / "我要无人值守的自动开发循环" |

## 第四层：工具类（4 个，Qoder/Cursor 适配版）

| 技能 | 一句话用途 | 中文触发示例 |
|---|---|---|
| `agent-browser` | 浏览器自动化操作指南（Qoder 版）：导航、填表、点击、截图、抓数据、测 Web 应用 | "打开这个网站帮我填个表单" / "自动化浏览器操作" |
| `ast-grep` | 结构化代码搜索指南（Qoder 版）：按 AST 模式搜索代码结构，Grep + LSP + SearchCodebase 主路径 | "搜索所有调用这个函数的地方" / "找出所有 console.log" |
| `worktree-create` | 创建并行开发 worktree（各占分支、复制配置、装依赖、健康检查） | "设置 worktrees 并行开发" / "创建一个 worktree" |
| `worktree-merge` | 经安全的中转集成分支合并并行 worktree 的分支，每步验证 | "合并我的 worktrees" / "集成这些分支" |

## 维护说明

- **安装目录**：`~/.qoder-cn/skills/<skill-name>/`（主文件 `SKILL.md` = 中文重整版；`references/`、`scripts/`、`templates/` 随附）
- **资料库**：本目录 `<skill-name>/SKILL.md`（英文原版）与 `SKILL.zh-CN.md`（中文重整版）并存；重新安装时把中文版复制为安装目录的 `SKILL.md`，references 的 zh-CN 版重命名为无后缀以匹配引用路径
- **统一术语**：AI 助手（agent）、工单系统（tracker）、全新项目/存量项目（greenfield/brownfield）、加载上下文（primed）、指路文档（steering document）、门禁（gate）、漂移（drift）等，全包一致
