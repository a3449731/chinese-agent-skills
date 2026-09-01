#!/usr/bin/env python3
"""T2: run the py scripts shipped with the installed skills, for real.

Covers the 3 python scripts under the repo's skills/ directory
(SKILLS_DIR env overrides the skills root; REAL_REPO env overrides the read-only target repo):
  - ablate-ai-layer/scripts/map_layer.py   (read-only AI-layer mapper)
  - second-brain-audit/scripts/audit.py    (read-only contradiction auditor)
  - ablate-ai-layer/scripts/run_ablation.py(--dry-run; must not touch the worktree)

Every test runs in a throwaway temp dir (or read-only against the real repo).
Pure stdlib. Exit code 0 = all tests passed.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SKILLS = Path(os.environ["SKILLS_DIR"]) if os.environ.get("SKILLS_DIR") \
    else Path(__file__).resolve().parent.parent / "skills"
REAL_REPO = Path(os.environ["REAL_REPO"]) if os.environ.get("REAL_REPO") \
    else Path(__file__).resolve().parent.parent

PASS, FAIL = 0, 0
RESULTS: list[tuple[str, str, str]] = []


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=120)


def check(name: str, ok: bool, detail: str) -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        RESULTS.append((name, "PASS", detail))
        print(f"  [PASS] {name} — {detail}")
    else:
        FAIL += 1
        RESULTS.append((name, "FAIL", detail))
        print(f"  [FAIL] {name} — {detail}")


def make_mini_repo(root: Path) -> None:
    """Minimal repo: CLAUDE.md + AGENTS.md + .claude/skills/ + one source file."""
    (root / "CLAUDE.md").write_text("# Mini repo rules\n- always load this\n", encoding="utf-8")
    (root / "AGENTS.md").write_text("# Open standard\n", encoding="utf-8")
    sk = root / ".claude" / "skills" / "demo"
    sk.mkdir(parents=True)
    (sk / "SKILL.md").write_text("---\nname: demo\n---\nDemo skill.\n", encoding="utf-8")
    (root / "app.py").write_text("print('hello')\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=str(root), check=True)
    subprocess.run(["git", "add", "-A"], cwd=str(root), check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "-qm", "init"], cwd=str(root), check=True)


def test_map_layer() -> None:
    print("\n== map_layer.py ==")
    script = SKILLS / "ablate-ai-layer" / "scripts" / "map_layer.py"

    # 1) real repo, text mode (read-only; this repo has no CLAUDE.md/AGENTS.md,
    #    so no classification is expected — assert it runs and reports something)
    p = run(["python3", str(script), str(REAL_REPO)])
    check("map_layer real-repo exit 0", p.returncode == 0, p.stderr.strip()[:120] or "ok")
    check("map_layer real-repo produces output",
          len(p.stdout.strip()) > 0,
          f"stdout {len(p.stdout)} chars")

    # 2) mini repo (has CLAUDE.md + AGENTS.md + .claude/skills/), text + json
    with tempfile.TemporaryDirectory(prefix="skill-test-map-") as td:
        mini = Path(td) / "mini"
        mini.mkdir()
        make_mini_repo(mini)
        p = run(["python3", str(script), str(mini)])
        check("map_layer mini classifications",
              "always-loaded" in p.stdout and "on-demand" in p.stdout,
              f"stdout {len(p.stdout)} chars")
        p = run(["python3", str(script), str(mini), "--json"])
        check("map_layer mini exit 0", p.returncode == 0, p.stderr.strip()[:120] or "ok")
        try:
            data = json.loads(p.stdout)
            arts = data.get("artifacts", []) if isinstance(data, dict) else data
            kinds = {e.get("kind") for e in arts}
            check("map_layer json valid + classes",
                  "always-loaded" in kinds and "on-demand" in kinds,
                  f"{len(arts)} artifacts, kinds={sorted(k for k in kinds if k)}")
        except json.JSONDecodeError as e:
            check("map_layer json valid", False, f"invalid json: {e}")

        # read-only: repo must be untouched
        st = subprocess.run(["git", "status", "--porcelain"], cwd=str(mini),
                            capture_output=True, text=True).stdout.strip()
        check("map_layer read-only", st == "", f"git status: {st or 'clean'}")


def test_audit() -> None:
    print("\n== audit.py ==")
    script = SKILLS / "second-brain-audit" / "scripts" / "audit.py"

    with tempfile.TemporaryDirectory(prefix="skill-test-audit-") as td:
        notes = Path(td) / "notes"
        notes.mkdir()
        # Subject attribution: page name (acme-corp.md -> "acme corp") plus the
        # bolded key in billing.md must resolve to the SAME subject in two files.
        (notes / "acme-corp.md").write_text(
            "# Acme Corp\n- Retainer is **$2,800/mo**\n", encoding="utf-8")
        (notes / "billing.md").write_text(
            "# Billing\n- **Acme Corp** retainer is **$3,200/mo**\n", encoding="utf-8")
        (notes / "misc.md").write_text("# Other\n- team size: 4 people\n", encoding="utf-8")

        p = run(["python3", str(script), str(notes)])
        check("audit exit 0", p.returncode == 0, p.stderr.strip()[:120] or "ok")
        out = p.stdout
        check("audit finds cross-file contradiction",
              "answered differently" in out and "1 subject" in out.replace("1 subject(s)", "1 subject"),
              f"stdout {len(out)} chars")

        pj = run(["python3", str(script), str(notes), "--json"])
        try:
            data = json.loads(pj.stdout)
            n = data.get("contradicted_subjects", 0) if isinstance(data, dict) else 0
            check("audit json contradicted_subjects >= 1", n >= 1,
                  f"contradicted_subjects={n}")
        except json.JSONDecodeError as e:
            check("audit json valid", False, f"invalid json: {e}")


def test_run_ablation_dry_run() -> None:
    print("\n== run_ablation.py --dry-run ==")
    script = SKILLS / "ablate-ai-layer" / "scripts" / "run_ablation.py"

    with tempfile.TemporaryDirectory(prefix="skill-test-abl-") as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        make_mini_repo(repo)
        (repo / "task.md").write_text("Add a --version flag to app.py\n", encoding="utf-8")

        before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo),
                                capture_output=True, text=True).stdout.strip()
        p = run(["python3", str(script), str(repo), "--task-file", str(repo / "task.md"),
                 "--dry-run"])
        check("ablation --dry-run exit 0", p.returncode == 0, p.stderr.strip()[:120] or "ok")
        check("ablation prints plan",
              "--dry-run: nothing executed" in p.stdout,
              f"stdout tail: {p.stdout.strip()[-80:]!r}")

        after = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo),
                               capture_output=True, text=True).stdout.strip()
        # task.md is intentionally untracked; only tracked changes count
        st = subprocess.run(["git", "status", "--porcelain"], cwd=str(repo),
                            capture_output=True, text=True).stdout.strip()
        tracked = [l for l in st.splitlines() if not l.startswith("??")]
        check("ablation worktree untouched",
              before == after and not tracked,
              f"head {'same' if before == after else 'CHANGED'}; tracked changes: {tracked or 'none'}")
        wts = subprocess.run(["git", "worktree", "list"], cwd=str(repo),
                             capture_output=True, text=True).stdout
        check("ablation no leftover worktree",
              len([l for l in wts.strip().splitlines() if l.strip()]) == 1,
              f"worktrees: {wts.strip()}")


def main() -> None:
    if not SKILLS.exists():
        print(f"skills dir not found: {SKILLS}", file=sys.stderr)
        sys.exit(2)
    print(f"T2 py-script tests — skills: {SKILLS}")
    test_map_layer()
    test_audit()
    test_run_ablation_dry_run()
    print(f"\nT2 summary: {PASS} passed / {FAIL} failed")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
