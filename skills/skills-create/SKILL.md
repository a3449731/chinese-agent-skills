---
name: skills-create
description: 以你自己的方式编写一个新的 AI 助手技能（Qoder/Cursor/Claude Code 通用，格式同为 SKILL.md），或把臃肿的技能重构为精简的 SKILL.md + references/。在你想"创建一个技能"、"写一个新技能"、"把提示词或命令变成技能"、"把技能拆分进 references"、"修剪 SKILL.md"，或调用 /skills-create 时使用。元技能——一个制造技能的技能。
argument-hint: "[create <name> | refactor <path/to/SKILL.md>]  （留空 = 问要哪个）"
---

# Skills Create —— 元技能

一个编写和重构技能的技能。两份工作：

- **创建**（Create）一个全新技能（从零开始，或从现有提示词/命令）。
- **重构**（Refactor）一个臃肿的技能——把细节拆进 `references/`、把输出形状移进 `templates/`、把 `SKILL.md` 修剪成一根指向各处的精简主干。

**它按它教导的方式构建：** 精简的正文把细节推迟到 `references/`。这就是渐进披露（progressive disclosure），而本技能是它自己的工作示例。**一切都是可组合的 markdown：** 一个技能是一个 `SKILL.md` 加上 AI 助手只在需要时才加载的可选文件。

## 规定工艺，而不是内容

在**技能如何构建**上要**严格**，在**任何给定技能——或它的输出——应该包含什么**上要**不持立场**。

- **要规定的（坚定、普遍适用）：** 渐进披露 · 第三人称、触发词丰富的 `description` · 祈使式、精简的正文 · 无重复 · 每个打包的文件都接线 · 有意的调用控制 · 匹配技能类型的验证。（见 `references/skill-standards.md`。）
- **不要规定的（作者的决定）：** 计划/PRD/报告应该有哪些章节、领域词汇、输出形状、有哪些阶段。不存在标准输出——引导作者做出好决策，绝不递给他们一个固定的。

对工艺严格，让作者在内容上保持自由。*（引导，而非规定——以及"拿来 vs 建造"：当你拥有某个流程并希望它遵循你的方式时，你就**建造**一个技能。）*

## 先给技能分类

在应用工艺之前先钉死**类型**——指导是成比例的，不是一刀切：

| 类型 | 它是什么 | 应用 |
|---|---|---|
| **工作流（Workflow）** | 一个多步骤程序（计划、评审、发布） | 完整视角，包括可验证的验证门 |
| **产物生成器（Artifact-generator）** | 产出文档/输出 | Context-is-King + *建议的*（绝不强制的）输出形状 |
| **知识/参考（Knowledge / reference）** | AI 助手查阅的事实 | Context-is-King + 信息密集；**没有**阶段，**没有**验证循环 |
| **工具包装（Tool-wrapper）** | 驱动脚本 / CLI / API | 一个确定性脚本 + 锐利的触发词；验证 = 工具自身的退出码 |

一个技能可以混合类型——应用所有适用项的交集。绝不把工作流的机制（阶段、循环、输出骨架）强加到知识技能上。完整细节：`references/skill-standards.md` → 技能类型。

## 第 0 步 —— 挑选模式（从 `$ARGUMENTS`）

解析 **`$ARGUMENTS`** 来挑选模式和目标：
- 以 **`create [<name>]`** 开头（或显然是一个新技能请求）→ **create** 模式；如果给了 `<name>` 就用作技能名 → 遵循 `references/creating-skills.md`。
- 以 **`refactor <path/to/SKILL.md>`** 开头（或指向一个现有技能）→ 对该路径执行 **refactor** 模式 → 遵循 `references/refactoring-skills.md`。
- **空白或不明确** → 问用哪个模式、技能/目标是什么。不要猜。

两种模式都遵守同样的工艺规则 → 先读 `references/skill-standards.md`。

## Create —— 快速主干（完整细节：`references/creating-skills.md`）
1. **收集上下文** —— 应该触发它的字面短语、任务从始至终、坑、要借鉴的模式。问用户；先别写。
2. **规划资源** —— 什么重复 → `scripts/`；什么为工作提供信息 → `references/`；什么塑造输出 → `templates/`；你不拥有/上游会变的 → 引用一个路径/URL；只在运行时存在 → 收集它（问用户、读 git/代码库）。
3. **搭脚手架** —— 把 `templates/SKILL.template.md` 复制到 `<个人技能目录>/<name>/SKILL.md`（Qoder 国内版 `~/.qoder-cn/skills/`、国际版 `~/.qoder/skills/`、Claude Code `~/.claude/skills/`、Codex `~/.codex/skills/`、Cursor `~/.cursor/skills/`；跨项目可用；团队共享改放项目级技能目录，如 `.qoder/skills/<name>/SKILL.md`）；只在计划需要时添加 `references/` / `templates/`。
4. **先写主干** —— 第三人称、触发词丰富的 `description`；祈使式、精简的正文；把细节推给 references。在写 references 之前先让它*能被触发*。
5. **验证与迭代** —— `references/validation.md`（检查清单 → 触发测试 → 真刀真枪跑一遍）。

## Refactor —— 快速主干（完整细节：`references/refactoring-skills.md`）
1. **盘点** SKILL.md —— 把每个块标记为*主干*（保留）或*可提取*（输出模板、模式、长示例、穷尽的模式/边界情况清单）。
2. **逐字提取** 到目标技能的 `references/`（输出形状则进 `templates/`）——不要改写任何影响行为的措辞。
3. **用指针替换** —— 对**始终需要**的内容，放一行*必读*（"在产出输出前，读取 `templates/<x>.md`"）；对有时需要的内容，放惰性指针。
4. **行为保持检查** —— 与之前相同的流程、相同的输出。什么都没丢，什么都没重复。
5. **验证** —— `references/validation.md`。

> **重构的头号风险：** 把一个*始终需要*的输出格式移进惰性加载的 reference，导致 AI 助手忘记读它、输出悄悄改变。每次做这样的提取都必须配一行必读。

## 什么时候值得建技能
当你**拥有一个流程**、并希望 AI 助手反复遵循*你的*方式时——"拿来 vs 建造"规则。粗略阈值：你大概用同样的话提示了 ~3 次（三连法则，Rule of Three）→ 把它存成技能。不要为一次性的事、或为所有者已经发布了好技能的工具建技能。

## 资源
- `references/skill-standards.md` —— 工艺规则：技能类型、解剖结构、上下文来源、frontmatter 规范、渐进披露、写作语气、无重复、"结构意味着维护者"、接线、可移植性。
- `references/creating-skills.md` —— 完整创建手册（包括移植现有提示词/命令）。
- `references/refactoring-skills.md` —— 完整拆分与修剪手册，带前后对比。
- `references/validation.md` —— 验证门（结构 · description · 正文 · 披露 · 行为 · 触发测试）。
- `templates/SKILL.template.md` —— 用来搭脚手架的精简 SKILL.md 骨架。
