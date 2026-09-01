# Worktree 设置 — 通用检查清单

git worktree 共享仓库的对象存储和**被跟踪**的文件，但其他方面是一次*全新检出*。它缺少 git 不跟踪的一切，以及一切机器本地状态。要真正准备好开发、运行和验证，一个 worktree 需要下面的条目。清单是**项目无关的**——从仓库检测具体细节（见 *检测具体细节*），绝不假设技术栈。

## 一个全新 worktree 需要什么

1. **从正确基础拉出的一条分支。** 从预期基础在新分支上创建 worktree——通常是仓库的默认分支（`origin/HEAD`），用于匹配远程的干净树；或当前 `HEAD`，用于携带进行中的工作。把它放在一个被 gitignore 的根下（`worktrees/<branch>`），这样它永远不会出现在主检出的 untracked 文件里。

2. **被 gitignore 的配置与密钥——常被漏掉的一层。** 全新检出没有应用运行时读的任何 untracked 文件：`.env`、`.env.local`、`.env.<stage>`、凭据/服务账号 JSON、`*.pem` 和其他密钥、`.npmrc` / `.pypirc`、本地设置（`.claude/settings.local.json`）以及类似的东西。把这些从主工作树复制进 worktree。确认每个都真的被忽略（`git check-ignore <f>`），这样被跟踪的文件永远不会被重复。如果仓库带 `.worktreeinclude`，用那个清单作为"复制什么"的事实源。

3. **依赖。** 用项目自己的包管理器安装，从存在的 manifest/lockfile 检测。monorepo 需要每个包装一次（例如一个后端和一个前端）。*装进* worktree，让它的环境与主检出隔离。

4. **语言运行时与一个隔离的环境。** 用项目钉住的运行时版本（`.python-version`、`.nvmrc`、`.tool-versions`、manifest 里的 `go`/`node` 字段）。*在* worktree 内部创建 virtualenv / `node_modules`——绝不共享主检出的——这样版本可以按分支不同。

5. **安装不会产生的生成或下载产物。** 如果应用需要 codegen（protobuf、GraphQL、ORM 客户端）、编译产物、或下载的模型/缓存才能启动，跑项目的 generate/build 步骤。没有就跳过。

6. **并发运行的隔离。** 只有当你真的会同时在几个 worktree 里*运行*服务时：给每个 worktree 的每个长运行服务一个不同的**端口**，让它们不冲突；在应用写入共享本地数据库的地方，每个 worktree 一个单独的**数据库或 schema**（或一个可丢弃的容器化 DB）。如果你只构建和测试、不提供服务，跳过这个。

7. **验证——一个检测到的健康检查。** 交出之前证明 worktree 能用。用项目支持的最便宜的有意义检查，按顺序：启动应用并打它的健康端点（如果它暴露了）→ 否则一个快速构建 / 类型检查 / 测试收集冒烟 → 否则至少确认依赖已解析、应用能导入/构建。检测命令；不要假设一个。

8. **注册与之后的清理。** worktree 现在被跟踪（`git worktree list`）。知道它存在，这样它的分支合并后可以被移除（`git worktree remove <path>`），过期的 worktree 不会堆积。

## 检测具体细节（按仓库，不假设）

- **安装命令** —— 从存在的 lockfile/manifest：`uv.lock`/`pyproject.toml` → `uv sync`；`poetry.lock` → `poetry install`；`requirements.txt` → `pip install -r requirements.txt`；`package-lock.json` → `npm ci`；`pnpm-lock.yaml` → `pnpm install`；`yarn.lock` → `yarn`；`bun.lockb` → `bun install`；`Cargo.toml` → `cargo build`；`go.mod` → `go mod download`；`Gemfile` → `bundle install`；`composer.json` → `composer install`。多个存在 → monorepo；在每个自己的包目录里各自安装。
- **要复制的 env/config 文件** —— 把仓库被忽略的 untracked 文件与常见 secret/config 模式相交：`git ls-files --others --ignored --exclude-standard` 过滤到 `.env*`、`*.local`、密钥/凭据文件。或者读 `.worktreeinclude`（如果存在）。子目录也要检查（例如 `backend/.env`、`app/.env`）。
- **运行命令 + 端口** —— 检查 README、manifest 的 scripts（`package.json` `scripts`、`pyproject` 入口点）、一个 `Procfile`、`docker-compose.yml` 或一个 `Makefile`；从 env 或 config 读一个 `PORT` / `*_PORT`。
- **健康端点** —— 在代码/README 里 grep 健康路由（`/health`、`/api/health`、`/healthz`、`/ping`）或 `docker-compose.yml` 里的 `healthcheck`。没有 → 落回构建/测试冒烟。
- **验证命令** —— 优先**用 CI 已经在跑的**：读 `.github/workflows/*`、一个 `Makefile`、或 manifest 的 test/lint scripts，复用那些确切命令（测试运行器、类型检查器、linter）。CI 是项目自己"什么证明这段代码能用"的事实源——如果仓库用别的，不要发明 `pytest`/`mypy`。

> **检测，不要硬编码** —— 上面的一切都在运行时从目标仓库发现。
