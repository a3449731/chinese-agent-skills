#!/bin/bash
# T5：hooks-create 保证层测试套件（真实临时仓库，双向验证 + 故障开放 + 端到端）
# 依赖：python3、git。全部在 mktemp 目录操作，结束自动清理，不触碰任何真实仓库。
set -u

GUARD_TEMPLATE="${GUARD_TEMPLATE:-$(cd "$(dirname "$0")/.." && pwd)/skills/hooks-create/scripts/guard_template.py}"
WORKDIR="$(mktemp -d /tmp/hooks-test-XXXXXX)"
REPO="$WORKDIR/repo"
PASS=0
FAIL=0

cleanup() { rm -rf "$WORKDIR"; }
trap cleanup EXIT

check() { # check <名称> <实际退出码> <期望退出码>
  local name="$1" actual="$2" expected="$3"
  if [ "$actual" -eq "$expected" ]; then
    echo "  [PASS] $name (exit=$actual)"
    PASS=$((PASS + 1))
  else
    echo "  [FAIL] $name (exit=$actual, 期望 $expected)"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== T5-0 前置：模板存在 ==="
[ -f "$GUARD_TEMPLATE" ] && check "guard_template.py 存在" 0 0 || check "guard_template.py 存在" 1 0
# 语法检查用 ast.parse（只读，不写 __pycache__，避免沙箱写入限制干扰）
python3 -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$GUARD_TEMPLATE"
check "模板语法可解析" $? 0

echo ""
echo "=== T5-1 临时仓库准备（原生钩子方案：core.hooksPath）==="
mkdir -p "$REPO/scripts/guards" "$REPO/scripts/hooks"
cd "$REPO" || exit 1
git init -q
git config user.email "test@example.com"
git config user.name "test"
cp "$GUARD_TEMPLATE" scripts/guards/pre-commit
cp "$GUARD_TEMPLATE" scripts/guards/pre-push
cp "$GUARD_TEMPLATE" scripts/guards/commit-msg
printf '#!/bin/sh\npython3 scripts/guards/pre-commit\n' > scripts/hooks/pre-commit
printf '#!/bin/sh\npython3 scripts/guards/commit-msg "$1"\n' > scripts/hooks/commit-msg
chmod +x scripts/hooks/pre-commit scripts/hooks/commit-msg
git config core.hooksPath scripts/hooks
echo base > base.txt
git add -A
git commit -q -m "chore: init" --no-verify
check "临时仓库初始化提交成功" $? 0

echo ""
echo "=== T5-2 pre-commit 守卫双向验证 ==="
echo "secret" > .env
git add .env
python3 scripts/guards/pre-commit 2>/dev/null
check "暂存 .env 应被阻止" $? 2
git restore --staged .env && rm -f .env

echo "normal" > normal.txt
git add normal.txt
python3 scripts/guards/pre-commit 2>/dev/null
check "正常文件应放行" $? 0
git restore --staged normal.txt && rm -f normal.txt

echo ""
echo "=== T5-3 commit-msg 守卫双向验证 ==="
MSGFILE="$WORKDIR/msg"
echo "feat: add login page" > "$MSGFILE"
python3 scripts/guards/commit-msg "$MSGFILE" 2>/dev/null
check "conventional 消息应放行" $? 0
echo "随便写一句不合规的消息" > "$MSGFILE"
python3 scripts/guards/commit-msg "$MSGFILE" 2>/dev/null
check "不合规消息应拒绝" $? 2

echo ""
echo "=== T5-4 pre-push 守卫双向验证（项目命令逐字运行）==="
printf 'print("ok")\n' > check_green.py
printf 'import sys; sys.exit(1)\n' > check_red.py
git add check_green.py check_red.py && git commit -q -m "chore: add checks" --no-verify

sed 's/^TEST_COMMAND = .*/TEST_COMMAND = "python3 check_green.py"/' scripts/guards/pre-push > gp
python3 gp --mode pre-push 2>/dev/null
check "项目命令通过时应放行" $? 0
sed 's/^TEST_COMMAND = .*/TEST_COMMAND = "python3 check_red.py"/' scripts/guards/pre-push > gp
python3 gp --mode pre-push 2>/dev/null
check "项目命令失败时应阻止" $? 2
rm -f gp

echo ""
echo "=== T5-5 故障开放（非 git 环境 / 未知模式 均放行）==="
mkdir -p "$WORKDIR/not-a-repo"
(cd "$WORKDIR/not-a-repo" && python3 "$REPO/scripts/guards/pre-commit" 2>/dev/null)
check "非 git 仓库中意外错误应故障开放放行" $? 0
python3 "$GUARD_TEMPLATE" --mode no-such-mode 2>/dev/null
check "未知模式应放行" $? 0

echo ""
echo "=== T5-6 端到端：真实 git commit 触发钩子 ==="
echo "secret" > .env
git add .env
git commit -q -m "feat: add env" >/dev/null 2>&1
check "含 .env 的真实提交应被钩子阻止" $? 1
git restore --staged .env && rm -f .env

echo "clean" > clean.txt
git add clean.txt
git commit -q -m "bad message no convention" >/dev/null 2>&1
check "不合规消息的真实提交应被钩子拒绝" $? 1

git commit -q -m "feat: add clean file" >/dev/null 2>&1
check "合规的真实提交应成功" $? 0

echo ""
echo "================================"
echo "T5 结果：PASS=${PASS} FAIL=${FAIL}（共 $((PASS + FAIL))）"
[ "$FAIL" -eq 0 ]
