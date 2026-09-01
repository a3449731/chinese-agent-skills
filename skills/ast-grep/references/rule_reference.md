# ast-grep 规则参考

本文档提供 ast-grep 规则语法的全面文档，覆盖所有规则类型和元变量。

## ast-grep 规则简介

ast-grep 规则是用于匹配和过滤抽象语法树（AST）节点的声明式规范。它们通过定义 AST 节点必须满足的条件，实现结构化代码搜索和分析。

### 规则类别

ast-grep 规则分为三类：

* **原子规则（Atomic Rules）**：基于内在属性匹配单个 AST 节点，如代码模式（`pattern`）、节点类型（`kind`）或文本内容（`regex`）。
* **关系规则（Relational Rules）**：基于目标节点相对于其他节点的位置或关系定义条件（如 `inside`、`has`、`precedes`、`follows`）。
* **复合规则（Composite Rules）**：使用逻辑运算（AND、OR、NOT）组合其他规则，形成复杂的匹配标准（如 `all`、`any`、`not`、`matches`）。

## ast-grep 规则对象解剖

ast-grep 规则对象是定义 ast-grep 如何识别和过滤 AST 节点的核心配置单元。它通常以 YAML 格式编写。

### 一般结构

ast-grep 规则对象中的每个字段都是可选的，但至少必须存在一个"正向"键（如 `kind`、`pattern`）。

一个节点匹配一条规则，当且仅当它满足该规则对象中定义的所有字段，这意味着隐式的逻辑 AND 运算。

对于使用依赖先前匹配的元变量的规则，建议使用显式的 `all` 复合规则来保证执行顺序。

### 规则对象属性

| 属性 | 类型 | 类别 | 用途 | 示例 |
| :--- | :--- | :--- | :--- | :--- |
| `pattern` | 字符串或对象 | 原子 | 按代码模式匹配 AST 节点。 | `pattern: console.log($ARG)` |
| `kind` | 字符串 | 原子 | 按 kind 名称匹配 AST 节点。 | `kind: call_expression` |
| `regex` | 字符串 | 原子 | 用 Rust 正则匹配节点的文本。 | `regex: ^[a-z]+$` |
| `nthChild` | number、string、Object | 原子 | 按节点在父级子节点中的索引匹配。 | `nthChild: 1` |
| `range` | RangeObject | 原子 | 按基于字符的起止位置匹配节点。 | `range: { start: { line: 0, column: 0 }, end: { line: 0, column: 10 } }` |
| `inside` | 对象 | 关系 | 目标节点必须在匹配子规则的节点内部。 | `inside: { pattern: class $C { $$$ }, stopBy: end }` |
| `has` | 对象 | 关系 | 目标节点必须有匹配子规则的后代节点。 | `has: { pattern: await $EXPR, stopBy: end }` |
| `precedes` | 对象 | 关系 | 目标节点必须出现在匹配子规则的节点之前。 | `precedes: { pattern: return $VAL }` |
| `follows` | 对象 | 关系 | 目标节点必须出现在匹配子规则的节点之后。 | `follows: { pattern: import $M from '$P' }` |
| `all` | Array\<Rule\> | 复合 | 所有子规则都匹配时匹配。 | `all: [ { kind: call_expression }, { pattern: foo($A) } ]` |
| `any` | Array\<Rule\> | 复合 | 任一子规则匹配时匹配。 | `any: [ { pattern: foo() }, { pattern: bar() } ]` |
| `not` | 对象 | 复合 | 子规则不匹配时匹配。 | `not: { pattern: console.log($ARG) }` |
| `matches` | 字符串 | 复合 | 预定义的工具规则匹配时匹配。 | `matches: my-utility-rule-id` |

## 原子规则

原子规则基于节点的内在属性匹配单个 AST 节点。

### pattern：字符串和对象形式

`pattern` 规则基于代码模式匹配单个 AST 节点。

**字符串模式**：直接用 ast-grep 的模式语法加元变量匹配。

```yaml
pattern: console.log($ARG)
```

**对象模式**：对模糊模式或特定上下文提供细粒度控制。

* `selector`：精确定位已解析模式中要匹配的特定部分。
  ```yaml
  pattern:
    selector: field_definition
    context: class { $F }
  ```

* `context`：提供周围的代码上下文以保证正确解析。

* `strictness`：修改模式的匹配算法（`cst`、`smart`、`ast`、`relaxed`、`signature`）。
  ```yaml
  pattern:
    context: foo($BAR)
    strictness: relaxed
  ```

### kind：按节点类型匹配

`kind` 规则按 `tree_sitter_node_kind` 名称匹配 AST 节点，该名称源自语言的 Tree-sitter 语法。适合针对 `call_expression` 或 `function_declaration` 等结构。

```yaml
kind: call_expression
```

### regex：基于文本的节点匹配

`regex` 规则用 Rust 正则表达式匹配 AST 节点的整个文本内容。它不是"正向"规则，意味着它匹配任何文本满足正则的节点，无论其结构 kind 是什么。

### nthChild：按位置匹配节点

`nthChild` 规则按节点在其父级子节点列表中从 1 开始的索引查找节点，默认只统计具名节点。

* `number`：匹配精确的第 n 个子节点。示例：`nthChild: 1`
* `string`：用 An+B 公式匹配位置。示例：`2n+1`
* `Object`：提供细粒度控制：
  * `position`：`number` 或 An+B 字符串。
  * `reverse`：`true` 表示从末尾计数。
  * `ofRule`：在计数前过滤兄弟列表的 ast-grep 规则。

### range：基于位置的节点匹配

`range` 规则基于节点基于字符的起止位置匹配 AST 节点。`RangeObject` 定义 `start` 和 `end` 字段，每个都有基于 0 的 `line` 和 `column`。`start` 包含，`end` 排除。

## 关系规则

关系规则基于目标相对于其他 AST 节点的位置过滤目标。它们可以包含 `stopBy` 和 `field` 选项。

### inside：在父节点内匹配

要求目标节点在匹配 `inside` 子规则的另一个节点内部。

```yaml
inside:
  pattern: class $C { $$$ }
  stopBy: end
```

### has：用后代节点匹配

要求目标节点有匹配 `has` 子规则的后代节点。

```yaml
has:
  pattern: await $EXPR
  stopBy: end
```

### precedes 和 follows：顺序节点匹配

* `precedes`：目标节点必须出现在匹配 `precedes` 子规则的节点之前。
* `follows`：目标节点必须出现在匹配 `follows` 子规则的节点之后。

两者都包含 `stopBy` 但不包含 `field`。

### stopBy 和 field：细化关系搜索

**stopBy**：控制关系规则的搜索终止。

* `"neighbor"`（默认）：当紧邻的周围节点不匹配时停止。
* `"end"`：搜索到方向的尽头（`inside` 是根，`has` 是叶子）。
* `Rule object`：当周围节点匹配提供的规则时停止（包含）。

**field**：指定目标节点内应匹配关系规则的子节点。只用于 `inside` 和 `has`。

**最佳实践**：拿不准时，总是用 `stopBy: end` 确保搜索到达方向的尽头。

## 复合规则

复合规则用逻辑运算组合原子规则和关系规则。

### all：规则的合取（AND）

只有当列表中的所有子规则都匹配时，节点才匹配。保证规则匹配的顺序，对元变量很重要。

```yaml
all:
  - kind: call_expression
  - pattern: console.log($ARG)
```

### any：规则的析取（OR）

列表中任一子规则匹配时，节点匹配。

```yaml
any:
  - pattern: console.log($ARG)
  - pattern: console.warn($ARG)
  - pattern: console.error($ARG)
```

### not：规则的否定（NOT）

单一子规则不匹配时，节点匹配。

```yaml
not:
  pattern: console.log($ARG)
```

### matches：规则复用与工具规则

接受一个规则 id 字符串，引用的工具规则匹配时匹配。支持规则复用和递归规则。

## 元变量

元变量是模式中用于匹配 AST 动态内容的占位符。

### $VAR：单个具名节点捕获

捕获 AST 中的单个具名节点。

* **有效**：`$META`、`$META_VAR`、`$_`
* **无效**：`$invalid`、`$123`、`$KEBAB-CASE`
* **示例**：`console.log($GREETING)` 匹配 `console.log('Hello World')`。
* **复用**：`$A == $A` 匹配 `a == a` 但不匹配 `a == b`。

### $$VAR：单个未具名节点捕获

捕获单个未具名节点（例如运算符、标点）。

**示例**：要匹配 `a + b` 中的运算符，用 `$$OP`。

```yaml
rule:
  kind: binary_expression
  has:
    field: operator
    pattern: $$OP
```

### $$$MULTI_META_VARIABLE：多节点捕获

匹配零个或多个 AST 节点（非贪婪）。适合数量可变的参数或语句。

* **示例**：`console.log($$$)` 匹配 `console.log()`、`console.log('hello')` 和 `console.log('debug:', key, value)`。
* **示例**：`function $FUNC($$$ARGS) { $$$ }` 匹配参数/语句数量可变的函数。

### 非捕获元变量（_VAR）

以下划线（`_`）开头的元变量不被捕获。即使命名相同，它们也可以匹配不同的内容，优化性能。

* **示例**：`$_FUNC($_FUNC)` 匹配 `test(a)` 和 `testFunc(1 + 1)`。

### 元变量检测的重要注意事项

* **语法匹配**：只识别精确的元变量语法（如 `$A`、`$$B`、`$$$C`）。
* **独占内容**：元变量文本必须是 AST 节点内的唯一文本。
* **不工作**：`obj.on$EVENT`、`"Hello $WORLD"`、`a $OP b`、`$jq`。

ast-grep playground 对调试模式和可视化元变量很有用。

## 常见模式与示例

### 查找含特定内容的函数

查找包含 await 表达式的函数：

```yaml
rule:
  kind: function_declaration
  has:
    pattern: await $EXPR
    stopBy: end
```

### 查找特定上下文内的代码

查找类方法内的 console.log 调用：

```yaml
rule:
  pattern: console.log($$$)
  inside:
    kind: method_definition
    stopBy: end
```

### 组合多个条件

查找使用 await 但没有 try-catch 的异步函数：

```yaml
rule:
  all:
    - kind: function_declaration
    - has:
        pattern: await $EXPR
        stopBy: end
    - not:
        has:
          pattern: try { $$$ } catch ($E) { $$$ }
          stopBy: end
```

### 匹配多个备选

查找任何类型的 console 方法调用：

```yaml
rule:
  any:
    - pattern: console.log($$$)
    - pattern: console.warn($$$)
    - pattern: console.error($$$)
    - pattern: console.debug($$$)
```

## 故障排查技巧

1. **规则不匹配**：用 `dump_syntax_tree` 查看实际的 AST 结构
2. **关系规则问题**：确保为深度搜索设置了 `stopBy: end`
3. **节点 kind 错误**：查语言的 Tree-sitter 语法获取正确的 kind 名称
4. **元变量不工作**：确保它是其 AST 节点中的唯一内容
5. **模式太复杂**：用 `all` 把它拆成更简单的子规则
