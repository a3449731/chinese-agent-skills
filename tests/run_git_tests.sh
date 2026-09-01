#!/bin/bash
# T3: real git drill — worktree-create / worktree-merge mechanics + ablation dry-run.
# Exercises the core git operations the two worktree skills prescribe, on a real
# throwaway repo in /tmp. Never touches the workspace or the skills root
# (SKILLS_DIR env overrides the skills root).
set -u

SKILLS="${SKILLS_DIR:-$(cd "$(dirname "$0")/.." && pwd)/skills}"
WORK="$(mktemp -d /tmp/skill-test-git.XXXXXX)"
REPO="$WORK/repo"
PASS=0
FAIL=0

cleanup() {
  if [ -d "$REPO/.git" ]; then
    git -C "$REPO" worktree remove --force worktrees/feat-a 2>/dev/null
    git -C "$REPO" worktree remove --force worktrees/feat-b 2>/dev/null
    git -C "$REPO" worktree prune 2>/dev/null
  fi
  rm -rf "$WORK"
}
trap cleanup EXIT

ok()   { PASS=$((PASS+1)); echo "  [PASS] $1"; }
bad()  { FAIL=$((FAIL+1)); echo "  [FAIL] $1"; }

echo "== T3 git drill — worktree-create / worktree-merge mechanics =="

# ---- fixture: repo with a gitignored secret + one tracked file ----
mkdir -p "$REPO"
cd "$REPO" || exit 1
git init -q
git config user.name test && git config user.email test@test
printf 'secret=abc\n' > .env
printf '.env\n' > .gitignore
printf 'v1\n' > app.txt
printf '# Repo rules\n- keep it simple\n' > CLAUDE.md
git add -A && git commit -qm init
BASE="$(git rev-parse --short HEAD)"

# ---- drill 1: worktree-create mechanics ----
echo "--- 1) create two parallel worktrees (worktree-create) ---"
git worktree add -q -b feat-a worktrees/feat-a
git worktree add -q -b feat-b worktrees/feat-b
[ "$(git worktree list | wc -l | tr -d ' ')" -eq 3 ] \
  && ok "two worktrees registered (3 entries)" || bad "worktree count: $(git worktree list | wc -l)"

# gitignored config copied into each worktree (the skill's step 2)
for wt in worktrees/feat-a worktrees/feat-b; do
  cp .env "$wt/.env"
done
[ -f worktrees/feat-a/.env ] && [ -f worktrees/feat-b/.env ] \
  && ok "gitignored .env copied into both worktrees" || bad ".env not copied"

# health check: each worktree clean
clean_a="$(git -C worktrees/feat-a status --porcelain)"
clean_b="$(git -C worktrees/feat-b status --porcelain)"
[ -z "$clean_a" ] && [ -z "$clean_b" ] \
  && ok "both worktrees healthy (clean status)" || bad "dirty worktree: $clean_a $clean_b"

# branches isolated
[ "$(git -C worktrees/feat-a symbolic-ref --short HEAD)" = "feat-a" ] \
  && [ "$(git -C worktrees/feat-b symbolic-ref --short HEAD)" = "feat-b" ] \
  && ok "each worktree on its own branch" || bad "branch isolation failed"

# ---- drill 2: parallel work — both feature branches (different files) ----
echo "--- 2) parallel work on both branches ---"
echo 'v2-a' > worktrees/feat-a/app.txt
git -C worktrees/feat-a add -A && git -C worktrees/feat-a commit -qm "feat-a: bump to v2-a"
printf 'lib-v1\n' > worktrees/feat-b/lib.txt
git -C worktrees/feat-b add -A && git -C worktrees/feat-b commit -qm "feat-b: add lib.txt"
[ "$(git -C worktrees/feat-a rev-parse HEAD)" != "$(git -C worktrees/feat-b rev-parse HEAD)" ] \
  && ok "independent commits on both branches" || bad "commits not independent"
[ "$(cat worktrees/feat-a/app.txt)" = "v2-a" ] && [ -f worktrees/feat-b/lib.txt ] \
  && ok "isolated filesystem states" || bad "worktree isolation broken"

# ---- drill 3: worktree-merge mechanics (integration branch) ----
echo "--- 3) integrate via integration branch (worktree-merge) ---"
git checkout -q main
git checkout -q -b integration
git merge -q --no-ff feat-a -m "integrate feat-a" \
  && ok "merge feat-a into integration" || bad "merge feat-a failed"
git merge -q --no-ff feat-b -m "integrate feat-b" \
  && ok "merge feat-b into integration (no conflict)" || bad "merge feat-b failed"
grep -q 'v2-a' app.txt && grep -q 'lib-v1' lib.txt \
  && ok "integration contains both changes" \
  || bad "integration content wrong: $(cat app.txt) $(ls lib.txt 2>/dev/null || echo MISSING)"

# every merge verified before touching main (skill: "每次合并后都验证")
# in-repo worktrees/ dir is untracked by design; only tracked-file changes count
DIRTY_TRACKED="$(git -C "$REPO" status --porcelain | grep -v '^??')"
[ -n "$DIRTY_TRACKED" ] \
  && bad "integration dirty after merges: $DIRTY_TRACKED" || ok "integration clean after merges"

# ---- drill 4: merge back to main + cleanup ----
echo "--- 4) merge back to main, cleanup ---"
git checkout -q main
git merge -q --no-ff integration -m "ship integrated work"
[ "$(git -C "$REPO" rev-parse --short HEAD)" != "$BASE" ] \
  && ok "main advanced past base" || bad "main unchanged"
grep -q 'v2-a' app.txt && [ -f lib.txt ] && ok "main has final content" || bad "main content wrong"

git worktree remove --force worktrees/feat-a
git worktree remove --force worktrees/feat-b
git worktree prune
git branch -q -D feat-a feat-b integration
[ "$(git worktree list | wc -l | tr -d ' ')" -eq 1 ] \
  && ok "worktrees cleaned up (1 entry)" || bad "leftover worktrees"
[ -z "$(git branch | grep -E 'feat-a|feat-b|integration')" ] \
  && ok "feature branches removed" || bad "leftover branches: $(git branch)"

# ---- drill 5: run_ablation.py --dry-run on this repo ----
echo "--- 5) ablation dry-run must not touch the worktree ---"
printf 'Change app.txt to v3\n' > task.md
BEFORE="$(git rev-parse HEAD)"
python3 "$SKILLS/ablate-ai-layer/scripts/run_ablation.py" "$REPO" --task-file task.md --dry-run > /dev/null 2>&1
rc=$?
AFTER="$(git rev-parse HEAD)"
DIRTY="$(git status --porcelain | grep -v '^??' | wc -l | tr -d ' ')"
[ "$rc" -eq 0 ] && [ "$BEFORE" = "$AFTER" ] && [ "$DIRTY" -eq 0 ] \
  && ok "ablation dry-run: exit $rc, HEAD unchanged, worktree clean" \
  || bad "ablation dry-run touched repo: rc=$rc HEAD=$BEFORE->$AFTER dirty=$DIRTY"

echo ""
echo "T3 summary: $PASS passed / $FAIL failed"
[ "$FAIL" -eq 0 ]
