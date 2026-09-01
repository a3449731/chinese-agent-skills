# 重构一个技能（拆分与瘦身）

先读 `skill-standards.md`。当 `SKILL.md` 长胖了——正文很长、每次使用都加载（并花费 token），而其中大部分只是偶尔需要——用它。重构是**事后应用的渐进披露**：把细节拉进 `references/`/`templates/`，留下一个由指针组成的精瘦主干。

## 第 1 步 — 盘点

读目标 `SKILL.md`，把每个块分类：
- **主干（留在正文）：** description、决策逻辑、分步工作流、指针。
- **可提取（移出去）：** 输出格式模板、schema、长的工作示例、穷举模式目录、故障排查 / 边界案例清单——任何笨重的或只是*偶尔*需要的。

## 第 2 步 — 逐字提取

把每个可提取的块移进目标技能自己的 `references/`（输出形状进 `templates/`）。**不要改写任何影响行为的东西**——重构保持行为；重写是另一项变更。

## 第 3 步 — 用指针替换
- **总是需要**的内容（例如 AI 助手必须始终遵循的输出格式）→ **必读**行：*"产生输出之前，读 `templates/<x>.md` 并严格遵循它。"*
- **有时需要**的内容 → **惰性指针：** *"边界案例见 `references/<x>.md`。"*

## 第 4 步 — 行为保持检查
瘦身后的技能 + 它的资源必须驱动和之前**相同的流程、相同的输出**。在原文内联内容的每一个点上，正文现在都在正确的时间到达正确的指针。没有丢弃，没有重复。**拿不准就留在正文里**——更小的 token 收益不值得一次行为变更。

## 第 5 步 — 验证
跑 `validation.md`，**门 5（行为保持）不可商量**——改变输出的重构是回归，不是清理。

## 之前 / 之后（草图）

**之前** — 一个 400 行的 `SKILL.md`：description · 工作流 · 一个 120 行输出模板 · 一个 90 行边界案例目录 · 一个长的工作示例。

**之后：**
```
the-skill/
├── SKILL.md                  # description · workflow · "Before output, read templates/report.md" · Resources
├── templates/report.md       # the 120-line output format (mandatory-read)
└── references/
    ├── edge-cases.md          # the 90-line catalog (lazy pointer)
    └── example.md             # the worked example (lazy pointer)
```
正文现在触发和加载都便宜；大块内容只在某一步伸手拿它时才加载。

> **第一大风险：** 把*总是需要*的输出格式移进一个惰性加载的 reference，导致 agent 忘记读它、输出悄悄变化。总是把那类提取配上一行必读说明——并在门 5 里验证它。
