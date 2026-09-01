# 保证层接入细节（各层照抄，不要凭记忆）

本文件按保证层分节。接入前先确认目标仓库现状（是否已有 `.husky/`、`.github/workflows/`、`.claude/settings.json`），已有内容一律**追加/合并**，绝不覆盖。

---

## 1. git 钩子（默认层）

守卫脚本统一放 `scripts/guards/`，文件名即模式（`pre-commit`、`pre-push`、`commit-msg`——模板按文件名识别模式）。接入分两种情况：

### 1a. 仓库已有 husky（存在 `.husky/` 目录）

在对应钩子文件末尾**追加**一行调用（不要动已有内容）：

```bash
# .husky/pre-commit（追加到已有内容之后）
python3 scripts/guards/pre-commit
```

husky v9+ 钩子文件就是普通脚本（无需 shebang/`. "$(dirname "$0")/_/husky.sh"` 行）；更老版本保持文件原有头部不动，只追加调用行。追加后确认可执行：`chmod +x .husky/pre-commit`。

### 1b. 无 husky：原生钩子 + 版本控制目录

`.git/hooks/` 不随仓库分发，所以把钩子本体放在版本控制目录（如 `scripts/hooks/`）并让 git 指向它：

```bash
mkdir -p scripts/hooks
# scripts/hooks/pre-commit：
#!/bin/sh
python3 scripts/guards/pre-commit
```

```bash
chmod +x scripts/hooks/pre-commit
git config core.hooksPath scripts/hooks
```

> `core.hooksPath` 是本机配置，不随仓库分发——新克隆者需重跑一次该命令。可在仓库 README 的"开发环境"小节记录这一步；也可提供 `scripts/setup-hooks.sh` 一键执行。
> **冲突检查**：设置 `core.hooksPath` 会让 `.git/hooks/` 全部失效。若项目同时有 husky 或其他钩子管理器，回到 1a 方案，不要并存。

### 钩子语义速查（写守卫前必读）

| 钩子 | 触发时机 | 参数/输入 | 非零退出的效果 |
|---|---|---|---|
| `pre-commit` | `git commit` 创建提交对象前 | 无 | 提交被取消 |
| `commit-msg` | 消息写入后、提交完成前 | `$1` = 消息文件路径 | 提交被取消 |
| `pre-push` | `git push` 传输前 | `$1`=远端名 `$2`=远端 URL；stdin 每行 `<local ref> <local sha> <remote ref> <remote sha>` | 推送被取消 |

- `pre-push` 的 stdin 行可用于精确判断（如只测即将推送的分支），但"测试门"场景直接跑命令即可——模板就是这么做的。
- 所有本地钩子都可被 `--no-verify` 绕过，这是必须向用户讲明的边界；不可妥协的保证要配 CI 补位（第 2 节）。

---

## 2. GitHub Actions CI 门禁（补位层）

`.github/workflows/<name>.yml` 新建或在已有 workflow 中追加 job。最小守卫示例（复用同一份守卫脚本，本地与 CI 同一真相）：

```yaml
name: guards
on:
  pull_request:
  push:
    branches: [main]

jobs:
  guard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      # 复用本地同一份守卫（按仓库语言补 setup-node 等）
      - name: pre-commit guard
        run: python3 scripts/guards/pre-commit --mode pre-commit
      - name: test gate
        run: npm ci && npm test
```

- check 失败会阻止 PR 合并（若仓库开启 branch protection / required checks——需提醒用户在仓库设置里把该 check 设为必需）。
- CI 环境无本地状态，守卫必须自包含；这也是复用同一份脚本的价值：本地绕过的人，逃不过 CI。

---

## 3. Claude Code hooks 分支（仅 Claude Code 用户）

当用户要的是**会话内**对 AI 助手动作的实时阻止/反应（"AI 助手不许读 `.env`"、"测试没绿不许停"），才走本分支——这是 Claude Code 专属机制，其他工具无等价物。要点（写前请抓取官方文档确认事件名与协议，其会持续演变：https://code.claude.com/docs/en/hooks）：

- **事件选择**：阻止型目标（阻止动作/阻止结束/门禁提示词）用 **PreToolUse / Stop / UserPromptSubmit**；观察反应型（格式化、记录、注入上下文）用 **PostToolUse / SessionStart / Notification**。Pre = 保证/门禁；Post = 反应/记录。
- **执行协议**：Claude Code 经 **stdin** 传入 JSON（含 `session_id`、`cwd`、`hook_event_name`，工具事件另含 `tool_name`+`tool_input`）；**`exit 0`** 放行（UserPromptSubmit/SessionStart 的 stdout 会注入上下文）；**`exit 2`** 阻止（stderr 内容作为原因反馈给 AI 助手）；其他退出码为非阻止性错误。
- **脚本位置与运行**：`.claude/hooks/<event_snake_case>.py`，官方示例用 `uv run --script`（单文件 + 内联元数据）；机器上没有 `uv` 时，纯标准库脚本直接 `python3 .claude/hooks/<name>.py` 一样工作。
- **故障开放**：意外错误一律 `exit 0`，坏钩子不得毁掉会话；唯一有意的非零是刻意的 `exit 2`。
- **Stop/SubagentStop 必须先查 `stop_hook_active`**，为真时 `exit 0`，否则阻止停止→继续工作→再停止→再阻止，死循环。
- **跑项目命令**：钩子解释器没有项目依赖——命令逐字作为 shell 字符串、在项目 `cwd` 运行（照抄 `scripts/guard_template.py` 的 `_run_project_command()`）；绝不用 `sys.executable` 重建。
- **接入**：编辑 `.claude/settings.json`，**合并**进已有 `hooks` 块：

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Edit|Write|Read",
        "hooks": [ { "type": "command", "command": "python3 .claude/hooks/pre_tool_use.py" } ] }
    ]
  }
}
```

- **交付前双向验证**：喂示例 stdin 检查退出码（该拦的拦、该放的放），方法与第 4 节相同。

---

## 4. 双向验证清单（所有层通用）

在目标仓库里真实跑，不模拟：

```bash
# pre-commit 示例：该拦的
echo secret > .env && git add .env
python3 scripts/guards/pre-commit; echo "exit=$?"   # 期望 2
git restore --staged .env && rm .env

# 该放的
echo ok > README.md && git add README.md
python3 scripts/guards/pre-commit; echo "exit=$?"   # 期望 0
git restore --staged README.md && rm README.md
```

- `pre-push` 守卫：先让 `TEST_COMMAND` 真实失败（如临时改坏一个测试）验证退出非零，再恢复验证退出 0——**两个方向都必须测**。
- `commit-msg` 守卫：写一个合规消息文件与一个不合规消息文件分别喂入。
- 接入钩子后，再做一次端到端：真实 `git commit`（观察钩子被触发），确认链路通。
- 故障开放检查：把守卫某个依赖弄坏（如 `git` 不在 PATH 的场景难以构造，可直接对模板注入异常断言）——模板层面由测试套件覆盖。
