---
name: <skill-name>
description: <它做什么，一个短语>. Use when the user wants to "<trigger 1>", "<trigger 2>", "<trigger 3>", or invokes /<skill-name>.
argument-hint: <可选：预期参数，例如 <path> [--flag]>
---

# <技能标题>

<一两句话：技能的目的和最终产物/输出。从这里开始用祈使语气。>

<!-- 下面的章节是起点建议，不是必需形状。按此技能的类型（workflow / artifact-generator / knowledge / tool-wrapper）保留、删掉、改名或重排。
     一个知识技能可能根本没有 Workflow；一个工具包装技能可能主要是 Resources 指针。内容你自己决定。 -->

## 何时使用
<这适用的情境。呼应 description 的触发器。>

## 工作流
1. <以动词开头的步骤。> <如果某一步需要大量细节，指向一个 reference，不要内联：见 `references/<x>.md`。>
2. <以动词开头的步骤。>
3. <产生输出的步骤。> 产生输出之前，读 `templates/<output-format>.md` 并严格遵循它。

## 坑
- <一个不明显的约束，agent 否则会搞错。>

## 资源
- `references/<x>.md` — <何时读它>
- `templates/<output-format>.md` — <必需的输出形状>
- `scripts/<y>.py` — <它做什么；运行它，不要读它>

<!-- 作者提醒（发布前删除）：
- description: 第三人称 + 字面触发器短语 + /name。≤1024 字符。
- 正文: 祈使语气、精瘦（1,500–2,000 词）。细节 → references/。输出形状 → templates/。
- 让结构匹配技能类型；不要把工作流形状强加给知识技能。
- 上下文可以打包、外部（正文引用的路径/URL）、或运行时收集——按所有权/易变性选。
- 调用方式: 对开放的读/规划技能省略 user-invocable/disable-model-invocation；对分发的、有副作用的设
  disable-model-invocation。
- 从 Resources 接线每个打包文件。正文<->references 不重复。用 references/validation.md 验证。
-->
