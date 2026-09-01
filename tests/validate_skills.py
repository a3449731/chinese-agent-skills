#!/usr/bin/env python3
"""Validate the installed skills pack (33 skills) against the delivery spec.

Checks (each skill):
  C1  skill directory present, name is kebab-case
  C2  SKILL.md exists
  C3  frontmatter: name == dirname; description non-empty
  C4  frontmatter: argument-hint present (WARN if missing)
  C5  SKILL.md < 500 lines
  C6  relative refs (references/scripts/templates prefix) resolve to real files
  C7  cross-references to other skill names are in the known 33-skill set
  C8  terminology residue: bare "agent(s)", Greenfield/Brownfield, 绿地/棕地,
      承重, 转向文档 (contexts are printed for manual judgment)

Usage:
  python validate_skills.py [skills_dir] [--report PATH]

Output: PASS/FAIL/WARN table per skill, summary counts, and a markdown report
used as the stage-2 test baseline. Pure standard library, read-only.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Known skills: 33 installed (both former future-anchored skills delivered)
KNOWN_SKILLS = {
    "ablate-ai-layer", "agent-browser", "ast-grep", "opportunity-scan",
    "piv-commit", "piv-create-pr", "piv-fix-review-findings", "piv-implement",
    "piv-implement-issue", "piv-investigate-issue", "piv-plan-implementation",
    "piv-review-changes", "piv-review-pr", "piv-run-full-loop", "piv-slice-epic",
    "piv-validate", "plan-architecture", "plan-create-prd", "plan-create-stories",
    "prime-backend", "prime-codebase", "prime-frontend", "rules-check-drift",
    "rules-create-global", "second-brain-audit", "setup-ai-tutor", "skills-create",
    "system-evolution-review", "system-execution-report", "worktree-create",
    "worktree-merge", "hooks-create", "build-dark-factory",
}
INSTALLED = set(KNOWN_SKILLS)

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.S)
NAME_RE = re.compile(r"^name:\s*([^\s]+)", re.M)
DESC_RE = re.compile(r"^description:\s*(.+)$", re.M)
ARGHINT_RE = re.compile(r"^argument-hint:", re.M)
REF_RE = re.compile(r"\]\(((?:references|scripts|templates)/[^)\s]+)\)")
SKILL_TOKEN_RE = re.compile(r"(?:/|\b)([a-z]+-[a-z-]+)\b")

RESIDUE_PATTERNS = [
    ("bare agent", re.compile(r"\bagents?\b")),
    ("Greenfield", re.compile(r"\bGreenfield\b")),
    ("Brownfield", re.compile(r"\bBrownfield\b")),
    ("绿地", re.compile(r"绿地")),
    ("棕地", re.compile(r"棕地")),
    ("承重", re.compile(r"承重")),
    ("转向文档", re.compile(r"转向文档")),
]


# Known proper-name tokens whose line contains no real residue
# (product names, file/path names, URL hostnames matched by the bare-agent regex)
EXCLUDE_LINE_TOKENS = ("agent-browser", "AGENTS", ".agents", "agents.md", "agentcore")


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = m.group(1)
    return {
        "name": (NAME_RE.search(fm).group(1).strip() if NAME_RE.search(fm) else ""),
        "description": bool(DESC_RE.search(fm)),
        "argument_hint": bool(ARGHINT_RE.search(fm)),
    }


def check_skill(skill_dir: Path) -> dict:
    name = skill_dir.name
    issues, warns = [], []

    # C1 dirname kebab-case
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        issues.append(f"C1 目录名非 kebab-case: {name}")

    # C2 SKILL.md
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return {"name": name, "issues": issues + ["C2 缺少 SKILL.md"],
                "warns": warns, "lines": 0, "refs": [], "cross": []}
    text = skill_md.read_text(encoding="utf-8")

    # C3/C4 frontmatter
    fm = parse_frontmatter(text)
    if not fm:
        issues.append("C3 frontmatter 缺失")
    else:
        if fm["name"] != name:
            issues.append(f"C3 name={fm['name']!r} 与目录名不符")
        if not fm["description"]:
            issues.append("C3 description 缺失")
        if not fm["argument_hint"]:
            warns.append("C4 无 argument-hint（可接受）")

    # C5 line count
    lines = text.count("\n") + 1
    if lines >= 500:
        issues.append(f"C5 行数 {lines} >= 500")
    elif lines > 400:
        warns.append(f"C5 行数 {lines}（接近上限 500，仅记录）")

    # C6 relative refs resolve
    refs = []
    for ref in REF_RE.findall(text):
        refs.append(ref)
        # ignore placeholder-like paths
        if "<" in ref or "..." in ref:
            warns.append(f"C6 占位符引用（跳过检查）: {ref}")
            continue
        target = skill_dir / ref
        if not target.exists():
            issues.append(f"C6 引用不存在: {ref}")

    # C7 cross-references within known set
    cross = []
    for token in SKILL_TOKEN_RE.findall(text):
        if token in KNOWN_SKILLS and token != name:
            cross.append(token)
    for ref_name in sorted(set(cross)):
        if ref_name not in INSTALLED:
            warns.append(f"C7 引用远期技能（未安装）: {ref_name}")

    # C8 terminology residue (contexts printed for manual judgment)
    residue = []
    for label, pat in RESIDUE_PATTERNS:
        for m in pat.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            line = text.splitlines()[line_no - 1].strip()
            if any(t in line for t in EXCLUDE_LINE_TOKENS):
                continue  # proper-name noise (agent-browser CLI, AGENTS.md, .agents/, ...)
            residue.append(f"{label} @L{line_no}: {line[:100]}")
    return {"name": name, "issues": issues, "warns": warns, "lines": lines,
            "refs": refs, "cross": sorted(set(cross)), "residue": residue}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("skills_dir", nargs="?", default=str(Path(__file__).resolve().parent.parent / "skills"))
    ap.add_argument("--report", default="")
    args = ap.parse_args()

    root = Path(args.skills_dir).expanduser().resolve()
    if not root.is_dir():
        print(f"FATAL: {root} 不是目录")
        return 2

    # directory inventory
    dirs = sorted(d for d in root.iterdir() if d.is_dir())
    extra = [d.name for d in root.iterdir() if not d.is_dir() and d.name != ".DS_Store"]

    results = [check_skill(d) for d in dirs]
    unknown = [r["name"] for r in results if r["name"] not in KNOWN_SKILLS]
    missing = sorted(INSTALLED - {r["name"] for r in results})

    # summary
    n_fail = sum(1 for r in results if r["issues"])
    n_warn = sum(1 for r in results if not r["issues"] and r["warns"])

    print(f"技能目录数: {len(dirs)}（预期 33）")
    print(f"多余非目录文件: {extra or '无'}")
    print(f"未知技能: {unknown or '无'}")
    print(f"缺失技能: {missing or '无'}")
    print(f"FAIL: {n_fail} / WARN: {n_warn} / PASS: {len(results) - n_fail - n_warn}")
    print()

    for r in results:
        status = "FAIL" if r["issues"] else ("WARN" if r["warns"] else "PASS")
        print(f"[{status}] {r['name']} ({r['lines']} 行)")
        for i in r["issues"]:
            print(f"    - {i}")
        for w in r["warns"]:
            print(f"    ~ {w}")

    residue_total = [(r["name"], item) for r in results for item in r["residue"]]
    if residue_total:
        print(f"\n术语残留命中 {len(residue_total)} 条（需人工判定是否误报）:")
        for name, item in residue_total:
            print(f"  {name}: {item}")

    # report file (stage-2 test baseline)
    if args.report:
        rep = Path(args.report)
        rep.parent.mkdir(parents=True, exist_ok=True)
        lines_out = [
            "# 技能包静态校验报告（阶段 1 测试基线）",
            "",
            f"- 校验时间: （脚本运行日）",
            f"- 技能目录: `{root}`",
            f"- 目录数: {len(dirs)}（预期 33）| FAIL: {n_fail} | WARN: {n_warn} | PASS: {len(results) - n_fail - n_warn}",
            "",
            "| 技能 | 行数 | 状态 | 问题 |",
            "|---|---|---|---|",
        ]
        for r in results:
            status = "FAIL" if r["issues"] else ("WARN" if r["warns"] else "PASS")
            detail = "; ".join(r["issues"] + r["warns"]) or "-"
            lines_out.append(f"| {r['name']} | {r['lines']} | {status} | {detail} |")
        if residue_total:
            lines_out += ["", "## 术语残留命中（人工判定）", ""]
            for name, item in residue_total:
                lines_out.append(f"- `{name}`: {item}")
        rep.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
        print(f"\n报告已写入: {rep}")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
