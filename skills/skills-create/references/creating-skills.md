# 创建一个技能（Skill）

先读 `skill-standards.md`。这是完整的创建手册（runbook）。

## 第 1 步 — 收集上下文（Context is King）

先什么都别写。从用户或代码库收集：
- **触发器** — 某人会说出的、应该调用这个技能的准确短语。直接问：*"你会输入或说出什么来触发它？"* 抓 3–6 个具体短语。
- **任务** — 技能做什么，从头到尾。最终产物或输出是什么？
- **坑与模式** — 不明显的领域知识、仓库里要模仿的现有模式、一个新手 AI 助手会搞错的约束。
- **范围边界** — 一个技能 = 一个能力。两个不相关的能力 = 两个技能。

先问最重要的问题；不要让用户淹没在问卷里。记住上下文可以**打包**、**指向**（路径/URL）、或**运行时收集**（问用户、读 git/代码库）——按技能决定。

## 第 2 步 — 规划资源

把任务的每个部分分类（见 `skill-standards.md` → Anatomy / Context sources）：
- 每次都要跑的代码 / 需要确定性可靠的 → `scripts/`（Python 用 PEP 723）。
- 为工作提供信息的细节（schema、穷举模式、边界案例）→ `references/`。
- 输出必须遵循的固定形状 → `templates/`。
- 被嵌入/复制进输出的文件 → `assets/`。
- 你不拥有 / 上游会变的上下文 → 在正文里引用一个**路径或 URL**；不要打包。
- 只在运行时存在的上下文 → 指示 agent **收集它**。

在搭脚手架之前把清单写下来。它是技能的蓝图。

## 第 3 步 — 搭脚手架

```bash
# 个人技能库（跨项目可用）；团队共享改放项目级 .qoder/skills/
mkdir -p ~/.qoder-cn/skills/<name>
cp ~/.qoder-cn/skills/skills-create/templates/SKILL.template.md ~/.qoder-cn/skills/<name>/SKILL.md
# add references/ templates/ scripts/ assets/ only as the plan requires
```

命名：`lowercase-hyphen`、描述性、如果是某个家族的一部分就加前缀（技能包的 `piv-*`、`plan-*`、`rules-*`、`prime-*`）。**目录名 = `/命令`。**

## 第 4 步 — 先写主干（渐进式成功）

按标准写 `SKILL.md`：
- **Description** — 第三人称，以它做什么开头，然后 "Use when …" 带上第 1 步的字面触发器。把 `/name` 调用作为一个触发器包含进去。
- **正文（祈使语气）** — 只写决策逻辑 + 工作流。每个步骤以动词开头。某一步需要大量细节时，写一行指向 reference 的指针，而不是内联。
- **调用方式** — 对普通的读/规划技能，省略 `user-invocable` / `disable-model-invocation`（两条路都开）；如果它是分发的*且*有副作用，设 `disable-model-invocation: true`（见 standards）。
- 以 **Resources** 章节结尾，列出每个打包的文件。

在写 references 之前，先让这个最小版本**能触发、能工作**。一个不触发的主干比一个没人到达的完美 reference 更值得修。

## 第 5 步 — 填充资源

写规划好的 `references/` / `templates/` / `scripts/`。应用不重复原则：内容移进 reference 时，**把它从正文移除**并留一个指针。对技能必须 ALWAYS 遵循的输出格式，放进 `templates/` + 加一行必读说明（"产生输出之前，读 `templates/<x>.md`"）。偶尔需要的细节给一个惰性指针。

## 第 6 步 — 验证并迭代
跑 `validation.md` 里的每一道门（结构 · 描述 · 正文 · 渐进披露 · 触发器测试）。然后在**真实任务**上用它，观察 agent 在哪里挣扎——自动调用失败就强化触发器，误用就澄清或移动内容。把修复折回去。

## 移植现有提示词或命令（v1 → v2 的动作）

这门课把它的 v1 slash-*commands* 变成了 v2 *skills*——你经常要做同样的动作。**保真第一，优化第二：** 移植是行为保持，不是重新设计。
1. 把正文**逐字**移进 `~/.qoder-cn/skills/<name>/SKILL.md`（或项目级 `.qoder/skills/<name>/SKILL.md`）——它是被证明过的流程/输出。
2. 只转换 frontmatter：加 `name`，用触发器短语扩展 `description`，保留 `argument-hint`/`allowed-tools`/`model`。
3. 删除旧命令文件，这样没有重复的 `/name`。
4. 如果正文很长，交给 `refactoring-skills.md` 拆分——那是**独立**的一步，在逐字移植被证明之后。
