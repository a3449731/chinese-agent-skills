#!/usr/bin/env python3
"""守卫脚本模板（纯标准库，跨工具）。

复制本文件到目标仓库的 scripts/guards/ 下，按需启用一种模式：
  - pre-commit：按 BLOCKED_PATTERNS 检查暂存文件，命中即阻止提交
  - pre-push  ：在仓库根逐字运行 TEST_COMMAND，非零即阻止推送
  - commit-msg：按 MSG_REGEX 校验提交消息，不匹配即拒绝提交

使用约定（详见 hooks-create 技能）：
  - 故障开放：任何意外错误都退出 0（只打印警告），坏守卫不得把用户锁在门外
  - 用户唯一要编辑的是下方常量区
  - 项目命令永远用 shell 字符串在仓库根运行，绝不用 sys.executable 重建

退出码：0 = 放行；2 = 阻止（原因打印到 stderr）
"""
from __future__ import annotations

import fnmatch
import os
import re
import subprocess
import sys
from pathlib import Path

# ─── 用户常量区（只改这里）───────────────────────────────────────────

# pre-commit：暂存文件中命中任一模式即阻止（支持 fnmatch 通配符）
BLOCKED_PATTERNS: list[str] = [
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
]

# pre-push：用户自己的测试命令，逐字执行（例："npm test" / "pytest -q"）
TEST_COMMAND = "npm test"

# 命令必须从子目录运行时改这里（相对仓库根，例："app/backend"）；否则留空
COMMAND_SUBDIR = ""

# commit-msg：提交消息必须匹配的正则（例：conventional 格式）
MSG_REGEX = r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?: .+"

# ─── 以下一般不需要改 ────────────────────────────────────────────────


def _repo_root() -> Path:
    """git 仓库根目录；获取失败返回当前目录。"""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return Path(out.stdout.strip())
    except Exception:
        return Path.cwd()


def _staged_files() -> list[str]:
    """当前暂存（将被提交）的文件列表。"""
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True, check=True,
    )
    return [l for l in out.stdout.splitlines() if l.strip()]


def _run_project_command(root: Path) -> int:
    """把 TEST_COMMAND 逐字作为 shell 字符串在仓库（子）目录中运行。

    [CRITICAL] 绝不用 sys.executable 重建命令——守卫的解释器没有项目依赖。
    Node 项目走包管理器脚本即可；Python 项目若存在 .venv/venv，把它的
    bin 目录放到 PATH 最前，让命令用上项目自己的依赖。
    """
    cwd = root / COMMAND_SUBDIR if COMMAND_SUBDIR else root
    env = os.environ.copy()
    for candidate in (".venv", "venv"):
        for bindir in ("bin", "Scripts"):
            venv_bin = root / candidate / bindir
            if venv_bin.is_dir():
                env["VIRTUAL_ENV"] = str(root / candidate)
                env["PATH"] = os.pathsep.join([str(venv_bin), env.get("PATH", "")])
                break
    result = subprocess.run(
        TEST_COMMAND, shell=True, capture_output=True, text=True,
        cwd=str(cwd), env=env,
    )
    if result.returncode != 0:
        tail = (result.stdout + result.stderr).strip().splitlines()
        sys.stderr.write("项目命令失败（最后 20 行）：\n")
        for line in tail[-20:]:
            sys.stderr.write(f"  {line}\n")
    return result.returncode


def guard_pre_commit() -> int:
    hits = [
        f for f in _staged_files()
        if any(fnmatch.fnmatch(os.path.basename(f), p) or fnmatch.fnmatch(f, p)
               for p in BLOCKED_PATTERNS)
    ]
    if hits:
        sys.stderr.write(
            "pre-commit 守卫阻止了提交：暂存区包含受保护文件：\n"
            + "".join(f"  - {h}\n" for h in hits)
            + "如确需提交，请从暂存区移除（并把它加入 .gitignore）。\n"
        )
        return 2
    return 0


def guard_pre_push() -> int:
    if _run_project_command(_repo_root()) != 0:
        sys.stderr.write(
            f"pre-push 守卫阻止了推送：命令未通过 —— {TEST_COMMAND}\n"
            "修复后再推；紧急绕过需显式 --no-verify（会被记录/审查）。\n"
        )
        return 2
    return 0


def guard_commit_msg() -> int:
    # commit-msg 钩子的第一个参数是消息文件路径
    msg_file = sys.argv[1] if len(sys.argv) > 1 else ""
    if not msg_file or not os.path.isfile(msg_file):
        return 0  # 故障开放：拿不到消息就放行
    msg = Path(msg_file).read_text(encoding="utf-8", errors="replace")
    first_line = next((l for l in msg.splitlines() if l.strip() and not l.startswith("#")), "")
    if not re.match(MSG_REGEX, first_line):
        sys.stderr.write(
            "commit-msg 守卫拒绝了提交：消息不符合约定格式。\n"
            f"  收到：{first_line!r}\n"
            f"  要求匹配：{MSG_REGEX}\n"
        )
        return 2
    return 0


MODES = {
    "pre-commit": guard_pre_commit,
    "pre-push": guard_pre_push,
    "commit-msg": guard_commit_msg,
}


def main() -> int:
    mode = sys.argv[0].rsplit("/", 1)[-1]  # 文件名即模式（复制时按钩子命名）
    guard = MODES.get(mode)
    if guard is None:
        # 也支持 --mode 显式指定，便于单独测试
        for i, a in enumerate(sys.argv[1:], start=1):
            if a == "--mode" and i + 1 < len(sys.argv):
                guard = MODES.get(sys.argv[i + 1])
    if guard is None:
        sys.stderr.write(f"guard: 未知模式（文件名/参数应为 {', '.join(MODES)}）——放行\n")
        return 0
    try:
        return guard()
    except Exception as exc:  # 故障开放：意外错误不阻塞用户
        sys.stderr.write(f"guard: 内部错误（故障开放，放行）：{exc}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
