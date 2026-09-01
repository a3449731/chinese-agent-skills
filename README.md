# 中文 Agent 技能包（33 个）

一套可直接安装的中文 AI 编码技能：上下文加载、规划、PIV 实现循环、治理与元技能、工具类四层，共 **33 个**。同一份 `SKILL.md` 文件可安装到 Qoder、Claude Code、Codex、Cursor 的个人技能目录，纯标准库脚本，macOS / Linux / Windows 均可。

## 出处与许可

本仓库是 [coleam00/skills](https://github.com/coleam00/skills)（作者 Cole Medin，MIT 许可）的**中文重整/翻译版**（衍生作品）：

- 原仓库为 MIT（"Take them, fork them, rewrite them."），本仓库保留同一 MIT 文本与原作者版权行，见 [LICENSE](LICENSE)
- 中文重整内容（翻译、术语统一、结构调整）与新增部分（安装器、测试套件、改造技能）同样以 MIT 发布
- 统一术语：AI 助手（agent）、工单系统（tracker）、全新项目/存量项目（greenfield/brownfield）、加载上下文（primed）、指路文档（steering document）、门禁（gate）、漂移（drift）

## 安装

需要本机有 `git` 与本仓库的克隆。安装器为纯标准库，Windows 用 `python install.py`，macOS/Linux 用 `python3 install.py`。

**方法一：安装器（推荐）**

```bash
python3 install.py --tool qoder-cn   # Qoder 国内版  ~/.qoder-cn/skills/
python3 install.py --tool qoder      # Qoder 国际版  ~/.qoder/skills/
python3 install.py --tool claude     # Claude Code   ~/.claude/skills/
python3 install.py --tool codex      # Codex         ~/.codex/skills/
python3 install.py --tool cursor     # Cursor        ~/.cursor/skills/（需 v0.50+，并在 Settings → Rules 开启 Import Agent Skills）
```

可选参数：`--skills a,b` 只装指定技能；`--dest 目录` 覆盖目标路径；`--force` 覆盖已有同名技能（默认跳过并列出不覆盖项）；`--dry-run` 只打印不复制。**升级 = 重跑安装器加 `--force`**。安装后重启会话生效。

**方法二：手动复制**

把 `skills/<技能名>/` 整目录复制到上表对应目录即可。

## 技能索引（四层）

技能按**双循环框架**组织：外层循环（加载上下文 → 规划 → 切片）产出工作单元，内层循环（PIV：计划 → 实现 → 验证 → 评审 → 提交 → PR）逐个消费。技能按 `description` 语义自动触发，也可显式输入技能名。

### 第一层：上下文与规划（7 个）

| 技能 | 一句话用途 |
|---|---|
| `prime-codebase` | 快速建立对代码库的深度理解（结构、文档、关键文件），规划与实现前先加载全局 |
| `prime-frontend` | 只聚焦前端（组件、路由、状态、样式），不加载无关后端代码 |
| `prime-backend` | 只聚焦后端（API 路由、服务、数据模型、数据库层） |
| `plan-create-prd` | 交互式访谈生成 PRD：问题 · 证据 · 假设 · 用户 · MVP · 成功指标 · 非目标（只写做什么/为什么，不碰怎么做） |
| `plan-architecture` | 探索"如何实现"：方案、技术栈、数据形态、风险项，产出高层架构决策文档 |
| `plan-create-stories` | 把 PRD 分解成工程师可直接用的 ticket（Jira/GitHub issues） |
| `piv-slice-epic` | 把 epic（连同架构决策）切成 PIV 大小的 ticket 并画依赖图 |

### 第二层：PIV 实现循环（11 个）

| 技能 | 一句话用途 |
|---|---|
| `piv-plan-implementation` | 针对单个 ticket/特性，经代码库分析 + 澄清访谈产出一步到位的实现计划 |
| `piv-investigate-issue` | 调查 GitHub issue 根因（并行探索 + 5 Whys），产出可评审的 RCA 产物 |
| `piv-implement-issue` | 依据 RCA 产物实施修复：漂移检查、切分支、实现、回归测试、验证 |
| `piv-implement` | 按计划逐任务实现，每步都验证 |
| `piv-validate` | 运行项目完整验证套件（测试/类型/lint）并报告整体健康度 |
| `piv-review-changes` | 对最近改动做提交前技术评审，作为质量门禁 |
| `piv-commit` | 原子化创建 git 提交，conventional 标签消息 |
| `piv-create-pr` | 推送分支并开 PR（自动检测 base、清晰正文、返回 URL） |
| `piv-review-pr` | 完整 PR 评审：验证 + 全新视角评审 + 严重度分类 + 发布结论（人工批准前的自动化门禁） |
| `piv-fix-review-findings` | 对评审发现分级处理：逐条修复 + 配测试 + 验证 + 推送 |
| `piv-run-full-loop` | 链式调用四个核心 PIV 技能，从一句话描述全自动开发完整特性 |

### 第三层：治理与 Meta-skills（11 个）

| 技能 | 一句话用途 |
|---|---|
| `rules-check-drift` | 检查规则文件（CLAUDE.md/AGENTS.md）是否与代码库漂移，附最小编辑建议 |
| `rules-create-global` | 从 PRD/架构或已加载的代码库推导项目全局规则 |
| `second-brain-audit` | 审计第二大脑/笔记/记忆中的过时事实，修复最糟的一处并防止复发 |
| `system-execution-report` | 生成实现报告：做了什么、偏离了什么、遇到什么挑战 |
| `system-evolution-review` | 元层面评审实现与计划的偏差，推荐 AI 层改进（找流程 bug，不是代码 bug） |
| `opportunity-scan` | 扫描真实协作过程，找出接下来该编码什么（反应式/主动式），产出 HTML 报告 |
| `setup-ai-tutor` | 本地搭建并启动 AI Tutor 示例项目（示例专用，装进自己项目时需适配） |
| `skills-create` | 元技能：创建新技能，或把臃肿技能重构为 SKILL.md + references/ |
| `ablate-ai-layer` | 双臂实验测量 AI 指令是否配得上它们的位置，在临时 worktree 中运行，绝不触碰工作树 |
| `hooks-create` ★ | **改造版**：为仓库编写跨工具的确定性保证层（git 钩子/脚本守卫/CI 门禁），挑层、写脚本、接入并双向证明 |
| `build-dark-factory` ★ | **改造版**：为产品仓库搭建无人值守自动化工厂——指导层、验证装置（含变异测试）、工作流运行器、部署、触发器五组件，拨盘 0-5 渐进自主 |

★ = 与原版有实质差异的改造技能：`hooks-create` 扩展为跨工具确定性保证技能；`build-dark-factory` 为全量落地版（五组件 + 自带测试）。

### 第四层：工具类（4 个）

| 技能 | 一句话用途 |
|---|---|
| `agent-browser` | 浏览器自动化操作指南：导航、填表、点击、截图、抓数据、测 Web 应用 |
| `ast-grep` | 结构化代码搜索指南：按代码结构搜索，主路径为 ripgrep + LSP + 语义搜索组合 |
| `worktree-create` | 创建并行开发 worktree（各占分支、复制配置、装依赖、健康检查） |
| `worktree-merge` | 经安全的中转集成分支合并并行 worktree 的分支，每步验证 |

## 平台支持

| 平台 | 支持情况 |
|---|---|
| macOS / Linux | 全部 33 个技能可用 |
| Windows | 纯文档与纯 Python 脚本的技能可用；`build-dark-factory` 的运行器模板为 bash 脚本，**需 Git Bash 或 WSL**；`hooks-create` 在 Git Bash/WSL 下同样可用 |

## 兼容性说明（如实标注）

- 技能按 **Qoder 的工具名与约定**编写。Claude Code、Codex、Cursor 具备等价能力，绝大多数技能可直接使用；个别差异举例：技能提到的 `Agent`（子代理）在 Claude Code 对应 Task、`SearchCodebase` 对应其语义搜索能力，使用时助手一般会自行对等
- 涉及 GitHub 的技能（`piv-investigate-issue`、`piv-create-pr`、`piv-review-pr` 等）需要 `gh` CLI 且已 `gh auth login`；无 GitHub 时这些环节自动退化为本地流程
- 各技能外部依赖：`git`（多数技能）、`gh`（GitHub 面）、`python3`（ablate-ai-layer、second-brain-audit、hooks-create、build-dark-factory 的脚本）、`claude` / `codex` CLI（build-dark-factory 运行器，二选一即可）
- Cursor 需要 v0.50+ 并在 Settings → Rules 开启 **Import Agent Skills** 才会加载

## 测试

```bash
python3 tests/validate_skills.py     # 结构与内容校验（33 目录，期望 FAIL 0）
python3 tests/run_py_tests.py        # 随附 Python 脚本实测（13 项）
bash tests/run_git_tests.sh          # git/worktree 真实演练（15 项）
bash tests/run_hooks_tests.sh        # hooks-create 保证层双向验证（14 项）
```

技能根目录默认取仓库内 `skills/`，可用环境变量覆盖：`SKILLS_DIR`（py/git 套件）、`GUARD_TEMPLATE`（hooks 套件）、`REAL_REPO`（py 套件的只读目标仓库）。历史测试报告存档于 `tests/RESULTS.md`、`tests/RESULTS-phase3.md`、`tests/VALIDATION-REPORT.md`。

## 仓库结构

```
├── README.md        # 本文件
├── LICENSE          # MIT（原作者版权行 + 中文重整版声明）
├── skills/          # 33 个技能（每个目录含 SKILL.md 及随附资源）
├── install.py       # 跨平台安装器（纯标准库）
├── tests/           # 4 个测试脚本 + 3 份历史报告
├── .gitattributes   # 脚本强制 LF，防 Windows CRLF 破坏
└── .gitignore
```
