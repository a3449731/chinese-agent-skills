# 技能标准（Skill Standards）

每个技能都遵守的规则——无论创建还是重构。这是共享的"策展上下文"；放在这里，不要复制进工作流文件。它们管辖**手艺**（技能怎么建），从不管辖**内容**（计划/PRD/报告的章节、领域词汇、输出形状）——那是作者按项目自己决定的。手艺上严格，内容上中立。

## 技能类型

应用规则前先分类——指导是成比例的：

| 类型 | 它是什么 | 应用 |
|---|---|---|
| **工作流（Workflow）** | 多步骤流程（规划、评审、发布） | 完整镜头，包括可验证的验证门 |
| **产物生成器（Artifact-generator）** | 产出一个文档/输出 | Context-is-King + 一个*建议*（从不强制）的输出形状；只有它自我检查时才验证 |
| **知识/参考（Knowledge / reference）** | AI 助手查阅的事实 | Context-is-King + 信息密集；**没有**阶段，**没有**验证循环 |
| **工具包装（Tool-wrapper）** | 驱动一个脚本 / CLI / API | 确定性脚本 + 尖锐触发器；验证 = 工具的退出状态 |

一个技能可以混合类型——应用并集。你绝不做的是把工作流技能的机制（阶段、验证循环、输出骨架）强加给一个不是工作流技能的技能。

## 解剖结构

```
skill-name/
├── SKILL.md          # required: YAML frontmatter + markdown body
├── references/       # docs the agent READS on demand (schemas, patterns, edge cases)
├── templates/        # shapes the OUTPUT follows (report skeletons, output formats)
├── assets/           # non-text resources copied/embedded into the result
└── scripts/          # executable code, RUN without loading its source into context
```

- **references/** = "读这个来为工作提供信息。"
- **templates/** = "产生输出时遵循这个形状。"
- **assets/** = "把这个复制/嵌入进结果。"
- **scripts/** = "执行这个来做确定性、零 token 的工作。"

## 上下文来源

Context is King，但它不必全都打包。从最便宜且合适的地方取——而且策展，不要倾倒：

1. **内联**（在 `SKILL.md` 里）——每次运行都需要的基本内容。总是加载；保持为主干。
2. **打包**（`references/`、`templates/`、`assets/`、`scripts/`）——按需披露。
3. **外部指针**——仓库文件路径或 URL（可选 `#anchor`）。某一步需要时读/取；不复制任何东西。用于你不拥有的文档，或复制就会过期的内容。
4. **运行时收集**——技能运行时获得它：问用户（交互式 PRD 技能），或检查环境（读 git 状态、扫代码库、调用工具）。

按**所有权 + 易变性**选择：打包你拥有且想要版本化的；指向你不拥有的或上游会变的；在运行时收集只存在于当下的。

## Frontmatter 规范

| 字段 | 必需 | 约束 | 说明 |
|-------|----------|------------|-------|
| `name` | 是 | ≤64 字符，lowercase-hyphen，**与目录匹配** | 目录名变成 `/the-command` |
| `description` | 是 | ≤1024 字符，第三人称，非空 | 触发器——它做什么 + 何时用 + 字面用户短语 |
| `argument-hint` | 否 | 字符串 | 自动补全提示，例如 `<path/to/plan.md> [--base <branch>]` |
| `allowed-tools` | 否 | 字符串/列表 | 激活时无需提示即可使用的工具 |
| `model` / `effort` | 否 | 模型 / 级别 | 按技能的执行覆盖 |
| `disable-model-invocation` | 否 | 布尔 | `true` = 仅用户（不自动调用） |
| `user-invocable` | 否 | 布尔 | `false` = 仅 agent，从 `/` 隐藏 |

**调用控制是一个深思熟虑的决定，它取决于上下文。** 个人的读/规划技能可以保持完全开放（省略两个标志）。但一个**分发的**技能（随插件发布）如果自动调用一个**有副作用**的动作——提交、推送、删除——可能惊吓别人的 agent；对这类，在分发副本里设 `disable-model-invocation: true`。让开放程度匹配"谁运行它"和"它做什么"。

其他可选字段存在（`when_to_use`、`disallowed-tools`、`paths`、`hooks`、`context: fork`、`shell`）——只在技能需要时才伸手拿，并**对照当前的 Claude Code skills 文档确认**（字段集会演变）。

## 渐进披露（核心机制）

三个加载级别——围绕它们设计每个技能：

1. **元数据**（`name` + `description`）——总在上下文中。约 100 词。触发器预算。
2. **正文**（`SKILL.md`）——技能触发时加载。目标 **1,500–2,000 词**，硬上限约 5k。每次使用都付费。
3. **资源**（`references/`、`templates/`、`scripts/`）——只在 AI 助手伸手拿时加载。实际上无限；脚本花费约零上下文（只有它们的输出进入对话）。

**含义：** 决策主干 + 工作流进正文；笨重的、偶尔需要的、或输出形状化的细节进资源。*（这个技能就是它自己的例子——精瘦的正文，细节在这里。）*

## 写作语态 — 两种不同的语域
- **`description` → 第三人称，带字面触发器短语。**
  - 好：`Extract text and tables from PDFs… Use when the user mentions PDFs, forms, or document extraction.`
  - 坏：`Helps with documents.`（模糊）· `Use this when you…`（语态错、无触发器）
- **正文 → 祈使 / 不定式，不是第二人称。**
  - 好：`Validate the output before reporting.` · `To extract fields, run scripts/analyze.py.`
  - 坏：`You should run the script.` · `Claude will validate the output.`

## 不重复

一个事实恰好活在一个地方——正文**或**一个 reference，绝不同时两者。细节优先放 references；正文只留主干 + 指针。重复是技能腐烂的方式（两份拷贝会漂移）。

## 结构意味着一个维护者

如果技能的输出携带**有状态**的章节——状态标记、生命周期/元数据、修订日志、进度清单——*某个东西*必须保持它们更新：同技能在后续运行、一个伴生技能、或一个显式步骤。**绝不要给一个没有任何东西更新的有状态章节做模板。** 一个没有步骤追加的"modified"字段，或没有构建者翻转的状态标记，是悄悄对读者撒谎的死重。当你给一个有状态章节做模板时，命名它的维护者。

## 接线

每个打包的文件都必须从 `SKILL.md` 链接（正文以 **Resources** 清单结尾，每行一条说明何时读它）——否则 AI 助手不知道它存在。保持 references **一层深**（直接从 SKILL.md 链接），不要嵌套链。外部指针（路径、URL）在使用点内联引用，但必须可解析——死指针是坏技能。

## 可移植性（跨工具）

- 可移植核心是 `name` + `description` + 正文 + 打包文件。其他工具（Cursor、Gemini CLI、AGENTS 生态）会忽略未知的 Claude 专用字段而不是报错。
- 保持正文的*核心价值*提供商无关；注明 Claude 专用机制（子代理扇出、Stop-hook 循环）在其他地方降级的地方。
- 让 `scripts/` 自包含：Python 用 PEP 723 内联依赖（`uv` 可运行，无需设置），并且**从 cwd / `git rev-parse --show-toplevel` 派生项目根，绝不从 `__file__`**——脚本随技能发布但在*用户*的项目上操作，所以从它自己位置来的路径一旦被安装到别处就坏了。
- **单一事实源。** 一个技能恰好活在一个地方。如果它必须在两个地方存在（dogfood 副本 + 分发插件），从一个生成另一个——绝不手工维护两个，否则它们漂移。
