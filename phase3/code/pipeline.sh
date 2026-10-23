#!/usr/bin/env bash
# 第 12 章：一条最小的门禁流水线
#
# 排序原则：按"单位拦截成本"从低到高。任何一道失败，立刻停——
# 后面的闸不必再跑，因为你已经知道这次提交要回去改了。
#
# 用法：
#   bash pipeline.sh                         # 默认校验修好的实现
#   bash pipeline.sh coupon_service.py       # 校验有缺陷的实现（会红）

set -u
PY="${PY:-python3}"
IMPL_RAW="${1:-coupon_service_fixed}"
IMPL="${IMPL_RAW%.py}"      # 允许传 coupon_service.py 或 coupon_service
FILE="${IMPL}.py"
ROOT="$(cd "$(dirname "$0")" && pwd)"
CASE="$ROOT/case_coupon"
export COUPON_IMPL="$IMPL"
FAILED=0

hint() { printf '\n\033[1m%s\033[0m\n' "$1"; }
ok()   { printf '  \033[32mok\033[0m  %s (%s)\n' "$1" "$2"; }
bad()  { printf '  \033[31mFAIL\033[0m %s (%s)\n' "$1" "$2"; }

run_gate() {
  local label="$1"; shift
  local start end dur
  start=$(date +%s%N)
  if "$@" >/tmp/gate.log 2>&1; then
    end=$(date +%s%N); dur=$(( (end - start) / 1000000 ))
    ok "$label" "${dur}ms"
  else
    end=$(date +%s%N); dur=$(( (end - start) / 1000000 ))
    bad "$label" "${dur}ms"
    sed 's/^/      /' /tmp/gate.log | tail -6
    FAILED=1
  fi
}

hint "门禁流水线 · 被测实现：${IMPL}"
cd "$CASE" || exit 2

run_gate "1 依赖允许清单" "$PY" dependency_gate.py "$FILE"
if [ "$FAILED" -eq 1 ]; then hint "在依赖层停住——后面的闸不必跑。"; exit 1; fi

run_gate "2 静态检查"     "$PY" "$ROOT/ch05/static_sweep.py"
run_gate "3 行为测试"     "$PY" -m unittest test_coupon_behavior -q
run_gate "4 覆盖率门槛"   "$PY" -m coverage run --branch --include=coupon_service.py \
                            -m unittest test_coupon_behavior -q
run_gate "5 变异测试"     env -u COUPON_IMPL "$PY" mutation_demo.py "$FILE"

# 变异测试必须跑在"测试默认导入 coupon_service"的形态下，否则变异体根本没被加载
SCORE=$(env -u COUPON_IMPL "$PY" mutation_demo.py "$FILE" 2>/dev/null | grep -oE "[0-9]+/[0-9]+" | tail -1)
C_NUM=${SCORE%%/*}
if [ -n "$SCORE" ] && [ "${C_NUM:-0}" -ge 3 ]; then
  ok "6 变异分数门槛" "$SCORE"
else
  bad "6 变异分数门槛" "${SCORE:-未取到}"
  FAILED=1
fi

cd "$ROOT/ch08" || exit 2
run_gate "7 约束存在性"   "$PY" constraint_check.py "$FILE"

if [ "$FAILED" -ne 0 ]; then
  hint "流水线失败：标红的那道闸拦住了这次提交。"
  exit 1
fi
hint "全部通过。"
exit 0
