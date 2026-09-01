#!/usr/bin/env python3
"""把本仓库的 33 个中文技能安装到你的 AI 工具——插件式整包（默认）或逐技能复制。

纯标准库，macOS / Linux / Windows 均可（Windows 用 `python install.py`）。

插件式整包（默认，一次安装、统一升级/卸载）:
  python3 install.py --tool claude             # Claude Code 插件（自动调用 claude CLI）
  python3 install.py --tool qoder-cn           # Qoder 国内版（qodercli 存在时自动装，否则给指引）
  python3 install.py --tool qoder              # Qoder 国际版（同上）

逐技能复制（Cursor / Codex 无插件系统，或任何平台想退回复制式时）:
  python3 install.py --tool cursor --mode copy   # ~/.cursor/skills/（需 v0.50+）
  python3 install.py --tool codex --mode copy    # ~/.codex/skills/

打包与可选参数:
  --package [目录]   打可分发 zip（Qoder 插件格式，默认输出到仓库根）
  --mode plugin|copy|auto   安装形态；auto = claude/qoder 走插件，其余走复制
  --skills a,b,c     仅 copy 模式：只装指定技能（逗号分隔，默认全部）
  --dest 目录        仅 copy 模式：覆盖目标目录
  --force            仅 copy 模式：覆盖已存在的同名技能（默认跳过）
  --dry-run          只打印将要做的事，不执行
  --yes              插件模式：不询问，允许覆盖已有市场/插件安装

安装后重启（或新开）会话，技能即被扫描生效。
升级：claude plugin update chinese-agent-skills；卸载：claude plugin uninstall chinese-agent-skills。
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
REPO_SKILLS = REPO_ROOT / "skills"
PLUGIN_NAME = "chinese-agent-skills"

TARGETS = {
    "qoder-cn": Path.home() / ".qoder-cn" / "skills",
    "qoder": Path.home() / ".qoder" / "skills",
    "claude": Path.home() / ".claude" / "skills",
    "codex": Path.home() / ".codex" / "skills",
    "cursor": Path.home() / ".cursor" / "skills",
}

# 支持插件式整包安装的工具（其余只有复制式）
PLUGIN_TOOLS = {"claude", "qoder", "qoder-cn"}

# zip 打包只带这些顶层条目（排除 .git、tests、archive 等）
PACKAGE_INCLUDE = (".qoder-plugin", ".claude-plugin", "skills", "assets",
                   "README.md", "LICENSE")


def plugin_version() -> str:
    manifest = REPO_ROOT / ".qoder-plugin" / "plugin.json"
    try:
        return json.loads(manifest.read_text(encoding="utf-8")).get("version", "0.0.0")
    except (OSError, json.JSONDecodeError):
        return "0.0.0"


def run(cmd: list[str]) -> int:
    print(f"  $ {' '.join(cmd)}")
    return subprocess.call(cmd)


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def confirm(prompt: str, yes: bool) -> bool:
    if yes:
        return True
    try:
        return input(f"{prompt} [y/N] ").strip().lower() in ("y", "yes")
    except EOFError:
        return False


def install_plugin_claude(dry_run: bool, yes: bool) -> int:
    if not have("claude"):
        print("未检测到 `claude` CLI。请在 Claude Code 会话里手动执行：")
        print(f"  /plugin marketplace add {REPO_ROOT}")
        print(f"  /plugin install {PLUGIN_NAME}@{PLUGIN_NAME}")
        return 1

    known = Path.home() / ".claude" / "plugins" / "known_marketplaces.json"
    if known.exists() and PLUGIN_NAME in known.read_text(encoding="utf-8", errors="ignore"):
        if not confirm(f"市场 {PLUGIN_NAME} 已存在，重新 add 会刷新它，继续？", yes):
            return 1
    if dry_run:
        print(f"[dry-run] claude plugin marketplace add {REPO_ROOT}")
        print(f"[dry-run] claude plugin install {PLUGIN_NAME}@{PLUGIN_NAME}")
        return 0

    rc = run(["claude", "plugin", "marketplace", "add", str(REPO_ROOT)])
    if rc != 0:
        print("市场添加失败。", file=sys.stderr)
        return rc
    rc = run(["claude", "plugin", "install", f"{PLUGIN_NAME}@{PLUGIN_NAME}"])
    if rc != 0:
        print("插件安装失败。", file=sys.stderr)
        return rc
    print(f"\n完成：{PLUGIN_NAME} 已作为整包插件安装。重启会话生效。")
    print(f"升级: claude plugin update {PLUGIN_NAME}")
    print(f"卸载: claude plugin uninstall {PLUGIN_NAME}")
    return 0


def install_plugin_qoder(tool: str, dry_run: bool) -> int:
    hint = [
        f"未检测到 `qodercli`。可选安装方式：",
        f"  1. 装了 qodercli 的环境（本仓库即插件市场）：",
        f"       qoder plugins marketplace add a3449731/chinese-agent-skills",
        f"       qoder plugins install {PLUGIN_NAME}",
        f"  2. Qoder IDE：python3 install.py --package 生成 zip，",
        f"     在 扩展 → 插件 → 添加插件 → 上传插件 中导入",
    ]
    if not have("qodercli"):
        print("\n".join(hint))
        return 0
    if dry_run:
        print(f"[dry-run] qodercli plugin install --scope user {REPO_ROOT}")
        return 0
    rc = run(["qodercli", "plugin", "install", "--scope", "user", str(REPO_ROOT)])
    if rc != 0:
        print("\n".join(hint))
        return rc
    print(f"\n完成：{PLUGIN_NAME} 已作为整包插件安装（{tool}）。重启会话生效。")
    return 0


def package_zip(out_dir: str, dry_run: bool) -> int:
    version = plugin_version()
    out = (Path(out_dir) if out_dir else REPO_ROOT).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    zip_path = out / f"{PLUGIN_NAME}-{version}.zip"

    missing = [e for e in PACKAGE_INCLUDE if not (REPO_ROOT / e).exists()]
    if missing:
        print(f"错误：打包所需条目缺失：{', '.join(missing)}", file=sys.stderr)
        return 1

    print(f"打包: {zip_path}（版本 {version}）")
    if dry_run:
        for e in PACKAGE_INCLUDE:
            print(f"  [dry-run] 含: {e}")
        return 0

    count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for entry in PACKAGE_INCLUDE:
            src = REPO_ROOT / entry
            if src.is_file():
                zf.write(src, entry)
                count += 1
                continue
            for p in sorted(src.rglob("*")):
                if p.is_file() and p.name != ".DS_Store":
                    zf.write(p, p.relative_to(REPO_ROOT).as_posix())
                    count += 1
    print(f"完成：{count} 个文件 → {zip_path}")
    print("该 zip 可直接在 Qoder 插件管理中安装（zip 根即 .qoder-plugin/plugin.json）。")
    return 0


def copy_skills(args: argparse.Namespace) -> int:
    dest = Path(args.dest).expanduser() if args.dest else TARGETS[args.tool]
    wanted = {s.strip() for s in args.skills.split(",") if s.strip()}

    sources = sorted(p for p in REPO_SKILLS.iterdir()
                     if p.is_dir() and (p / "SKILL.md").exists())
    if wanted:
        missing = wanted - {p.name for p in sources}
        if missing:
            print(f"错误：仓库里没有这些技能：{', '.join(sorted(missing))}", file=sys.stderr)
            return 1
        sources = [p for p in sources if p.name in wanted]

    print(f"源:   {REPO_SKILLS}（{len(sources)} 个技能）")
    print(f"目标: {dest}（{args.tool}）")
    if args.dry_run:
        print("[dry-run] 以下内容将被复制：")

    installed, skipped = [], []
    for src in sources:
        dst = dest / src.name
        if dst.exists() and not args.force:
            skipped.append(src.name)
            continue
        if not args.dry_run:
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        installed.append(src.name)

    for name in installed:
        print(f"  [{'将安装' if args.dry_run else '已安装'}] {name}")
    for name in skipped:
        print(f"  [跳过：已存在，--force 可覆盖] {name}")

    print(f"\n完成：安装 {len(installed)}，跳过 {len(skipped)}。")
    if installed and not args.dry_run:
        print("重启（或新开）会话后生效。")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="插件式整包（默认）或逐技能复制安装 33 个中文技能")
    ap.add_argument("--tool", choices=sorted(TARGETS),
                    help="目标工具：" + "、".join(sorted(TARGETS)) +
                         "（--package 时可省略）")
    ap.add_argument("--mode", default="auto", choices=("auto", "plugin", "copy"),
                    help="安装形态；auto = claude/qoder/qoder-cn 走插件，其余走复制")
    ap.add_argument("--package", nargs="?", const=str(REPO_ROOT), default=None,
                    metavar="输出目录", help="打可分发 zip（默认输出到仓库根）后退出")
    ap.add_argument("--skills", default="", help="仅 copy 模式：只装指定技能，逗号分隔")
    ap.add_argument("--dest", default="", help="仅 copy 模式：覆盖目标目录")
    ap.add_argument("--force", action="store_true", help="仅 copy 模式：覆盖已存在的同名技能")
    ap.add_argument("--dry-run", action="store_true", help="只打印，不执行")
    ap.add_argument("--yes", action="store_true", help="插件模式：跳过确认直接执行")
    args = ap.parse_args()

    if not REPO_SKILLS.is_dir():
        print(f"错误：找不到技能源目录 {REPO_SKILLS}", file=sys.stderr)
        return 1

    if args.package is not None:
        return package_zip(args.package, args.dry_run)

    if not args.tool:
        print("错误：请指定 --tool（或用 --package 打包）", file=sys.stderr)
        return 2

    mode = args.mode
    if mode == "auto":
        mode = "plugin" if args.tool in PLUGIN_TOOLS else "copy"

    if mode == "plugin":
        if args.tool not in PLUGIN_TOOLS:
            print(f"{args.tool} 没有插件系统，自动改用复制式（--mode copy）。")
            return copy_skills(args)
        if args.tool == "claude":
            return install_plugin_claude(args.dry_run, args.yes)
        return install_plugin_qoder(args.tool, args.dry_run)

    return copy_skills(args)


if __name__ == "__main__":
    sys.exit(main())
