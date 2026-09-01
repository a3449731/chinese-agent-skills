---
name: ast-grep
description: 结构化代码搜索指南（Qoder/Cursor 版）：按代码结构（抽象语法树 AST 模式）搜索代码库、查找特定代码结构、执行超出纯文本搜索的复杂代码查询。触发词：搜索代码模式、查找特定语言构造、定位具有特定结构特征的代码。主路径：Qoder 的 Grep（ripgrep）+ LSP + SearchCodebase 组合；可选高级路径：安装 ast-grep CLI 后使用完整的规则语法。
---

# ast-grep 代码搜索

## 概述

本技能帮助把自然语言查询翻译成用于结构化代码搜索的规则。规则语法以 ast-grep 为基准（原子/关系/复合规则、元变量、stopBy），并映射到 Qoder/Cursor 的实际执行能力。ast-grep 使用抽象语法树（AST）模式，基于代码的结构而非纯文本匹配代码，能在大型代码库上实现强大而精确的代码搜索。

## 执行路径：Qoder / Cursor 内置能力优先

本技能的规则方法论是通用知识，先尝试用 Qoder/Cursor 的内置能力落地，必要时再上 ast-grep CLI：

| 需求 | 主路径（无需安装） | 高级路径（ast-grep CLI） |
|---|---|---|
| 简单文本 / 正则搜索 | Qoder Grep 工具（ripgrep 引擎，支持正则与上下文行） | `ast-grep run --pattern 'console.log($ARG)'` |
| 查找符号定义 / 引用 | LSP（Go to Definition / Find References / Workspace Symbol） | `kind` + 关系规则 |
| 语义级检索 | Qoder SearchCodebase（按含义找代码） | — |
| AST 结构精确匹配（"包含 await 的函数"） | 先试 Grep + LSP 组合；搞不定再装 CLI | `scan --inline-rules`（YAML 规则） |

Cursor 对应：⌘⇧F 全局搜索（支持正则）、右键 Go to Definition / Find All References、Ask 模式的语义搜索。后文的规则编写章节（第 3 步、技巧、常见用例）是方法论核心，无论走哪条路径都适用。

## 何时使用本技能

当用户出现以下情况时使用本技能：
- 需要用结构化匹配搜索代码模式（例如"找到所有没有错误处理的 async 函数"）
- 想定位特定的语言构造（例如"找到所有带特定参数的函数调用"）
- 请求需要理解代码结构而不仅仅是文本的搜索
- 要求搜索具有特定 AST 特征的代码
- 需要执行传统文本搜索无法处理的复杂代码查询

## 通用工作流

遵循这个流程来帮助用户编写有效的 ast-grep 规则：

### 第 1 步：理解查询

清楚理解用户想找什么。需要时问澄清性问题：
- 他们在找什么具体的代码模式或结构？
- 用哪种编程语言？
- 有没有需要考虑的特定边界情况或变体？
- 匹配中应该包含或排除什么？

### 第 2 步：创建示例代码

写一段代表用户想匹配内容的简单代码片段。保存到临时文件中供测试。

**示例：**
如果要搜索"使用 await 的 async 函数"，创建一个测试文件：

```javascript
// test_example.js
async function example() {
  const result = await fetchData();
  return result;
}
```

### 第 3 步：编写 ast-grep 规则

把模式翻译成 ast-grep 规则。从简单开始，需要时再加复杂度。

**关键原则：**
- 关系规则（`inside`、`has`）总是用 `stopBy: end`，确保搜索走完整个方向
- 简单结构用 `pattern`
- 复杂结构用 `kind` + `has`/`inside`
- 用 `all`、`any` 或 `not` 把复杂查询拆成更小的子规则

**示例规则文件（test_rule.yml）：**
```yaml
id: async-with-await
language: javascript
rule:
  kind: function_declaration
  has:
    pattern: await $EXPR
    stopBy: end
```

完整规则文档见 `references/rule_reference.md`。

### 第 4 步：测试规则

**Qoder 路径：** 把示例代码写入临时文件后，直接用 Grep 工具按简化后的模式搜索它来验证（正则或字面量）；需要确认 AST 结构时用 LSP 查看符号。**CLI 路径（可选）：** 装了 ast-grep 后用下面的命令精确验证规则。

用 ast-grep CLI 验证规则能匹配示例代码。有两种主要方法：

**方案 A：内联规则测试（快速迭代用）**
```bash
echo "async function test() { await fetch(); }" | ast-grep scan --inline-rules "id: test
language: javascript
rule:
  kind: function_declaration
  has:
    pattern: await \$EXPR
    stopBy: end" --stdin
```

**方案 B：规则文件测试（复杂规则推荐）**
```bash
ast-grep scan --rule test_rule.yml test_example.js
```

**没有匹配时的调试：**
1. 简化规则（移除子规则）
2. 关系规则如果没有就加 `stopBy: end`
3. 用 `--debug-query` 理解 AST 结构（见下文）
4. 检查 `kind` 值对该语言是否正确

### 第 5 步：搜索代码库

**Qoder 路径：** 简单模式直接用 Grep 工具（ripgrep 正则，必要时带 `-C` 上下文行）；符号定位用 LSP；语义查询用 SearchCodebase。需要 AST 级精确匹配时才用 CLI。**CLI 路径（可选）：**

一旦规则能正确匹配示例代码，搜索实际代码库：

**简单模式搜索：**
```bash
ast-grep run --pattern 'console.log($ARG)' --lang javascript /path/to/project
```

**基于规则的复杂搜索：**
```bash
ast-grep scan --rule my_rule.yml /path/to/project
```

**内联规则（不创建文件）：**
```bash
ast-grep scan --inline-rules "id: my-rule
language: javascript
rule:
  pattern: \$PATTERN" /path/to/project
```

## ast-grep CLI 命令（可选高级路径）

以下命令需要先安装 CLI：`npm i -g @ast-grep/cli`（或 `brew install ast-grep`）。日常搜索先用 Qoder 的 Grep + LSP + SearchCodebase；需要精确 AST 结构匹配（kind / has / inside 等）时再用它。调试规则可借助 `ast-grep playground` 在线工具。

### 检查代码结构（--debug-query）

转储 AST 结构来理解代码如何被解析：

```bash
ast-grep run --pattern 'async function example() { await fetch(); }' \
  --lang javascript \
  --debug-query=cst
```

**可用格式：**
- `cst`：具体语法树（显示所有节点，包括标点）
- `ast`：抽象语法树（只显示命名节点）
- `pattern`：显示 ast-grep 如何解释你的模式

**用它来：**
- 找到节点正确的 `kind` 值
- 理解你想匹配的代码结构
- 调试为什么模式不匹配

**示例：**
```bash
# 查看目标代码的结构
ast-grep run --pattern 'class User { constructor() {} }' \
  --lang javascript \
  --debug-query=cst

# 查看 ast-grep 如何解释你的模式
ast-grep run --pattern 'class $NAME { $$$BODY }' \
  --lang javascript \
  --debug-query=pattern
```

### 测试规则（scan 配 --stdin）

不创建文件测试规则对代码片段的匹配：

```bash
echo "const x = await fetch();" | ast-grep scan --inline-rules "id: test
language: javascript
rule:
  pattern: await \$EXPR" --stdin
```

**加 --json 获得结构化输出：**
```bash
echo "const x = await fetch();" | ast-grep scan --inline-rules "..." --stdin --json
```

### 用模式搜索（run）

基于模式的简单搜索，匹配单个 AST 节点：

```bash
# 基本模式搜索
ast-grep run --pattern 'console.log($ARG)' --lang javascript .

# 搜索特定文件
ast-grep run --pattern 'class $NAME' --lang python /path/to/project

# 程序化使用的 JSON 输出
ast-grep run --pattern 'function $NAME($$$)' --lang javascript --json .
```

**何时使用：**
- 简单、单节点的匹配
- 不需要复杂逻辑的快速搜索
- 不需要关系规则（inside/has）时

### 用规则搜索（scan）

基于 YAML 规则的搜索，用于复杂结构查询：

```bash
# 用规则文件
ast-grep scan --rule my_rule.yml /path/to/project

# 用内联规则
ast-grep scan --inline-rules "id: find-async
language: javascript
rule:
  kind: function_declaration
  has:
    pattern: await \$EXPR
    stopBy: end" /path/to/project

# JSON 输出
ast-grep scan --rule my_rule.yml --json /path/to/project
```

**何时使用：**
- 复杂的结构搜索
- 关系规则（inside、has、precedes、follows）
- 复合逻辑（all、any、not）
- 需要完整 YAML 规则的全部能力时

**提示：** 对关系规则（inside/has），总是加 `stopBy: end` 确保完整遍历。

## 编写有效规则的技巧

### 总是使用 stopBy: end

对关系规则，除非有特定理由，总是用 `stopBy: end`：

```yaml
has:
  pattern: await $EXPR
  stopBy: end
```

这确保搜索遍历整个子树，而不是停在第一个不匹配的节点。

### 从简单开始，再增加复杂度

从最简单的可行规则开始：
1. 先试 `pattern`
2. 不行就试 `kind` 匹配节点类型
3. 需要时加关系规则（`has`、`inside`）
4. 复杂逻辑用复合规则（`all`、`any`、`not`）组合

### 使用正确的规则类型

- **Pattern**：用于简单、直接的代码匹配（例如 `console.log($ARG)`）
- **Kind + 关系**：用于复杂结构（例如"包含 await 的函数"）
- **复合**：用于逻辑组合（例如"有 await 但不在 try-catch 里的函数"）

### 用 AST 检查调试

规则不匹配时：
1. 用 `--debug-query=cst` 查看实际 AST 结构
2. 检查元变量是否被正确识别
3. 验证节点 `kind` 与预期一致
4. 确保关系规则在正确的方向搜索

### 内联规则中的转义

使用 `--inline-rules` 时，在 shell 命令中转义元变量：
- 用 `\$VAR` 而不是 `$VAR`（shell 会把 `$` 解释为变量）
- 或用单引号：`'$VAR'` 在大多数 shell 中有效

**示例：**
```bash
# 正确：转义了 $
ast-grep scan --inline-rules "rule: {pattern: 'console.log(\$ARG)'}" .

# 或使用单引号
ast-grep scan --inline-rules 'rule: {pattern: "console.log($ARG)"}' .
```

## 常见用例

### 查找带特定内容的函数

找到使用 await 的 async 函数：
```bash
ast-grep scan --inline-rules "id: async-await
language: javascript
rule:
  all:
    - kind: function_declaration
    - has:
        pattern: await \$EXPR
        stopBy: end" /path/to/project
```

### 查找特定上下文中的代码

找到类方法里的 console.log：
```bash
ast-grep scan --inline-rules "id: console-in-class
language: javascript
rule:
  pattern: console.log(\$\$\$)
  inside:
    kind: method_definition
    stopBy: end" /path/to/project
```

### 查找缺失预期模式的代码

找到没有 try-catch 的 async 函数：
```bash
ast-grep scan --inline-rules "id: async-no-trycatch
language: javascript
rule:
  all:
    - kind: function_declaration
    - has:
        pattern: await \$EXPR
        stopBy: end
    - not:
        has:
          pattern: try { \$\$\$ } catch (\$E) { \$\$\$ }
          stopBy: end" /path/to/project
```

## 资源

### references/
包含 ast-grep 规则语法的详细文档：
- `rule_reference.md`：全面的 ast-grep 规则文档，涵盖原子规则、关系规则、复合规则和元变量

需要详细规则语法信息时加载这些参考资料。规则语法本身与执行工具无关：在 Qoder 中优先用 Grep + LSP + SearchCodebase 落地，需要 AST 级精确匹配时安装 ast-grep CLI 使用本参考。
