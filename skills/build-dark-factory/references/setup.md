# 设置

这个文件里的每一条都弄坏过一个真实工厂。没有一条有趣，每一条都是承重的，而且它是项目里没人写下来的那一半——你可以有五个完美组件，却有一个从未完成一圈的工厂，因为行尾在检出时被重写了。

在 **Phase 6**，触发器要上的时候读这个。在 Phase 0b 浏览前置条件，这样你在一开始就拒绝，而不是半途而废。

---

## 前置条件，在访谈之前

检查仓库时确认这些。每一条如果缺失且无法安排，都是拒绝。

| | 为什么在清单上 |
|---|---|
| **一个编码 agent，在将要运行工厂的机器上认证好** | 不是最好的那个。是今天能用的那个。 |
| **`gh` 已认证**，如果状态在 GitHub 上 | 调度器、门和合并都 shell 出去调它。 |
| **一台保持开机的机器** | 放在会休眠的笔记本上的工厂，是一个只在你碰巧醒着时才运行的工厂，而那正是你想停止做的事。 |
| **一种启动应用的方式** | 没有它组件 5 就无从立足。 |
| **一条能跑的测试命令** | 建在零检查之上的暗工厂是一台合并貌似合理代码的机器。 |
| **一个应用真的能跑 E2E 的地方** | 临时 CI runner 让长 E2E 和应用启动别扭。选之前先检查。 |

### 没人替你解决的凭据问题

**agent 凭据会在运行中途静默过期。** 每个 agent，无一例外。工厂会把这件事表现为一个因无关原因失败的节点。

- 检查你认证的东西的过期时间，把续期放进你放 cron 的同一个地方。
- 让 runner 读 agent 自己的 JSON 结果并报告真正的终止原因。runner 模板里的 `node_failure.py` 做这个：预算耗尽、工具拒绝、崩溃和拒绝是四种不同的东西，其中只有三种是 bug。
- 一个退出 0 却什么都没做的节点是这个失败的正常形态。**对产物断言，而不是对退出码断言。** 一个没有产出 commit、PR 或 diff 的运行没有成功，无论它返回什么。

---

## 平台税

### 行尾会弄坏每个脚本，在你没看着的那台机器上

如果仓库曾经在开了 `core.autocrlf` 的 Windows 上检出，每个 `*.sh` 都会变 CRLF，在运行工厂的 Linux 机器上每个都会失败：

```
bad interpreter: /usr/bin/env bash^M
```

读起来像*"文件不存在"*。在仓库里钉死它，让它不依赖任何人的 git 配置：

```gitattributes
* text=auto eol=lf
*.sh text eol=lf
```

### Windows 路径长度

一旦 worktree 路径加一个 vendored 文件超过 260 个字符，`git worktree add` 会以 "Filename too long" 失败。验证器的 worktree 路径比实现者的长，长度恰好是它加的那个词的长度，所以这出现在验证而不是实现上，把你引到错误的地方找原因。

```bash
git config core.longpaths true
```

另外把 worktree 路径按 issue *编号*命名，而不是按 issue slug。

### 编码，任何跨进程边界的东西

Windows 默认 stdio 为 ANSI 代码页。一条正确的拒绝评论，从一个进程管道到另一个，到达 GitHub 时每个非 ASCII 字符都变成了 U+FFFD——而没人注意到，因为之后唯一检查的是退出码。

```bash
export PYTHONIOENCODING=utf-8
```

并且显式解码子进程输出。`subprocess(text=True)` 使用平台代码页，意味着一个*验证器*可能读不了一个完全正常的产物并把它报为损坏。误报花的信任和漏报一样多。

---

## 在第一个能提交的工作流之前

运行这个。它花一秒，是失误和发布之间的区别：

```bash
git check-ignore -v .env secrets.json credentials.json <每个带 token 的配置文件>
```

**空输出意味着你的下一次运行会发布你的密钥。** PR 步骤里的 `git add -A` 会扫走任何没被忽略的东西，在公开仓库上那就是发布——事后轮换是清理，不是修复。

无法*编辑*受保护文件不会阻止 `git add -A` 提交一个第一次出现的文件。把检查作为节点放进工作流，而不是放进人类读的清单。runner 模板在它的 pre-flight 里做这个。

---

## 调度

### cron，在一台保持开机的机器上

```cron
*/30 * * * * cd /path/to/repo && bash factory/orchestrator.sh >> /var/log/factory.log 2>&1
```

**每 30 分钟。比感觉上该有的慢。** 快速循环会在你注意到错误之前把错误的花费放大。

每次运行都捕获 stdout 和 stderr。第一个无人值守夜晚的早晨，你最想要的是一次什么都没做的运行的日志。

### systemd timer，如果你想让运行不自我重叠

`OnUnitInactiveSec` 的 timer 在前一次运行*结束*后开始计时，cron 不会。一旦一圈的时间长于间隔，就值得用。

### Windows 任务计划程序

注册任务在登录时运行并失败重启。注意除非你另行配置，否则它只在有人登录时运行——一个表现为"工厂夜里停了"的细节。

### GitHub Actions，和两个陷阱

如果你改为在 Actions 里调度：

- **定时工作流只从默认分支运行。** 坐在特性分支上的 cron 什么都不做，永远如此，没有任何警告。
- **在公开仓库上，GitHub 会在 60 天无仓库活动后禁用定时工作流。** 一个变安静的工厂会因为安静被关掉，然后一直关着——看起来和"它没什么可做的"一模一样。

还有一个杀部署而不是杀调度的：**GitHub 不会对使用默认 `GITHUB_TOKEN` 提交的 commit 触发工作流。** 见 `deployment.md`。

---

## 开启它

拨盘在代码里强制执行，不是在文件里记录。`orchestrator.sh` 拒绝在 `FACTORY_AUTONOMY=1` 以下派发，并把每个后续动作守在自己的级别。

```bash
bash factory/orchestrator.sh --dry-run          # 说出它会做什么，什么都不做
FACTORY_AUTONOMY=1 bash factory/orchestrator.sh # 单次调用，不持久
```

先在环境里设置**一次调用**，只有看完那个级别的一整圈之后才放进 cron。从 1 升到 2，再升到 **3**——每一级看一圈是赢得下一级的东西，而不是停止的理由。

**3 级才是它本该到达的地方。** 1 级和 2 级是你安全到达那里的方式；两者都不是目的地。没有留出集时 `factory_doctor` 拒绝 3，所以拨盘不能跑在证据前面。

### 停止按钮，以及故意测试它

两个，因为它们在不同的地方失败：

1. **一个本地 kill 文件。** 网络断开时也能用，那正是你最需要它的时候。
2. **一个远程标签。** 从手机就能触达，那是它存在的全部理由。

**远程那一半必须默认关闭（fail closed）。**"移除标签以停止"是显而易见的設計，但它反了：缺失的标签无法与列出它失败的 API 调用区分，所以一次网络波动读起来像"继续"。做成你*添加*的标签，并把任何列出它的错误当作已停止。

**在无人值守之前故意用它一次**，把日期写下来。从未用过的停止按钮是一个没人知道它好不好用的停止按钮。

---

## 第一个无人值守的夜晚

- **第一天就计量 token，不要等第一张发票。** 对它的成本预测每次都错 10-20 倍，方向相同。在 `trap` 里记录成本，让它扛过运行失败——那正是你最想知道它花了多少钱的时候。
- **并发从 1 开始。** 只在串行版本无聊之后提高，提高时加每目标锁，否则两次运行会操作同一个 PR，第二个会评审第一个还在编辑的树。
- **从 trap 释放并发锁，不要从下一条语句。** `set -e` 会被后台子 shell 继承，所以一个非零退出的工作流——一次升级、一道被堵的门、任何东西——跳过释放，把调度器永远卡死。之后每次运行都记录"容量已满，什么都没派发"并退出 0，看起来就像一个无事可做的工厂。
- **派发之前先推送。** 工厂对世界的视图是 `origin`。未推送的本地工作对它不可见，它会自信地对一个已不存在的过去构建，所有标记全绿。
- **恰好一个升级通道，并让它安静。** 如果什么都通知，你会把它静音，然后什么都不通知。

### 接通那一个通道

`needs-human` 是唯一人类必须行动的状态，所以它是唯一允许打扰人类的状态。这个工厂写的其他一切都等着被发现——而在无人值守的系统中，"等着被发现"意味着你下次想起来看的时候才知道。在 `factory/config.sh` 里设置 `FACTORY_NOTIFY_CMD`；它在 stdin 上接收原因，`$1` 是目标，它从三条通往 `needs-human` 的路径被调用（runner、被堵的门、修复尝试上限）。

**消息到达 STDIN。** `argv[1]` 只是目标，用于路由或主题行。下面每个例子都读 stdin；如果你自己写一个并反射性地伸手拿 `"$1"`——单行 Slack curl 是明显案例——你会得到一个正文整个是 `.factory/prs/0001.md` 的告警，它告诉你"出事了"而不告诉你出了什么事。

```bash
# Slack 传入 webhook
FACTORY_NOTIFY_CMD='xargs -0 -I{} curl -s -X POST -H "Content-type: application/json" \
  -d "{\"text\":\"{}\"}" "$SLACK_WEBHOOK_URL"'

# ntfy.sh - 手机通知，无需写 app
FACTORY_NOTIFY_CMD='curl -s -d @- https://ntfy.sh/my-factory-topic'

# macOS 桌面
FACTORY_NOTIFY_CMD='xargs -0 -I{} osascript -e "display notification \"{}\" with title \"factory\""'

# Linux 桌面
FACTORY_NOTIFY_CMD='xargs -0 -I{} notify-send "dark factory" "{}"'

# 一个你真的会看的文件，如果你宁愿 tail 也不愿被打扰
FACTORY_NOTIFY_CMD='tee -a /var/log/factory-escalations.log'
```

**像测试停止按钮一样测试它：故意，一次。** 把 runner 指向一个不存在的 issue，确认消息到达。

```bash
bash factory/run-workflow.sh implement-issue issues/does-not-exist.md
```

还在手工驱动圈的时候，留着不设置是合法选择，runner 会大声说出来而不是假装——`NOT NOTIFIED - FACTORY_NOTIFY_CMD unset; this waits in .factory/needs-human.md`。不要那样到 3 级。
