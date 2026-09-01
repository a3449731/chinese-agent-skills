#!/usr/bin/env python3
"""把本仓库的 33 个中文技能安装到你的 AI 工具个人技能目录。

纯标准库，macOS / Linux / Windows 均可（Windows 用 `python install.py`）。

用法:
  python install.py --tool qoder-cn            # Qoder 国内版  ~/.qoder-cn/skills/
  python install.py --tool qoder               # Qoder 国际版  ~/.qoder/skills/
  python install.py --tool claude              # Claude Code  ~/.claude/skills/
  python install.py --tool codex               # Codex        ~/.codex/skills/
  python install.py --tool cursor              # Cursor       ~/.cursor/skills/（需 v0.50+）

可选:
  --skills a,b,c   只安装指定技能（逗号分隔，默认全部 33 个）
  --dest 目录      覆盖目标目录（路径与上表不符时用这个）
  --force          覆盖已存在的同名技能（默认跳过并列出不覆盖项）
  --dry-run        只打印将要做的事，不复制

安装后重启（或新开）会话，技能即被扫描生效。
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

TARGETS = {
    "qoder-cn": Path.home() / ".qoder-cn" / "skills",
    "qoder": Path.home() / ".qoder" / "skills",
    "claude": Path.home() / ".claude" / "skills",
    "codex": Path.home() / ".codex" / "skills",
    "cursor": Path.home() / ".cursor" / "skills",
}

REPO_SKILLS = Path(__file__).resolve().parent / "skills"


def main() -> int:
    ap = argparse.ArgumentParser(description="安装 33 个中文技能到 AI 工具的个人技能目录")
    ap.add_argument("--tool", required=True, choices=sorted(TARGETS),
                    help="目标工具：" + "、".join(sorted(TARGETS)))
    ap.add_argument("--skills", default="", help="只装指定技能，逗号分隔（默认全部）")
    ap.add_argument("--dest", default="", help="覆盖目标目录")
    ap.add_argument("--force", action="store_true", help="覆盖已存在的同名技能")
    ap.add_argument("--dry-run", action="store_true", help="只打印，不复制")
    args = ap.parse_args()

    if not REPO_SKILLS.is_dir():
        print(f"错误：找不到技能源目录 {REPO_SKILLS}", file=sys.stderr)
        return 1

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


if __name__ == "__main__":
    sys.exit(main())
