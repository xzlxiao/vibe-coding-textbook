#!/usr/bin/env python3
"""重试预算与断路演示：让失败变便宜。

它不连接任何上游，只做一件事：把「无预算重试」与「带断路」两种策略
在同一串故障下的行为差异算出来给你看。数字是模拟的，机制是真的。

用法：
  python3 retry_budget.py                 # 默认：一次 429，比较三种策略
  python3 retry_budget.py --fail 2        # 连续两次故障
  python3 retry_budget.py --threshold 2   # 断路阈值改为 2 次失败

输出：三种策略下发往上游的请求数（越少越省钱，也越不放大故障）。
"""

from __future__ import annotations

import argparse


def strategy_no_budget(failures: int, retries: int = 3) -> int:
    """无预算重试：每次失败都立刻重试 retries 次，每次重试又可能再失败。"""
    total = 0
    pending = 1
    for _ in range(failures):
        total += pending                      # 这一次调用本身
        total += pending * retries            # 立刻重试
        pending = pending * retries           # 重试本身也会失败 → 下一轮放大
    return total + pending


def strategy_budget(failures: int, budget: int = 3) -> int:
    """有预算：整个链路最多发 budget 次。"""
    total = 0
    spent = 0
    for _ in range(failures + 1):
        if spent >= budget:
            break
        total += 1
        spent += 1
    return total


def strategy_circuit(failures: int, threshold: int = 2) -> int:
    """断路：失败累计到阈值就打开，不再发请求。"""
    total = 0
    fails_seen = 0
    for _ in range(failures + 1):
        if fails_seen >= threshold:
            break                             # 打开：快速失败，不发请求
        total += 1
        fails_seen += 1
    return total


def main() -> int:
    ap = argparse.ArgumentParser(description="重试预算与断路对比（模拟）")
    ap.add_argument("--fail", type=int, default=1, help="连续故障次数")
    ap.add_argument("--retries", type=int, default=3, help="无预算策略的每次重试次数")
    ap.add_argument("--threshold", type=int, default=2, help="断路阈值")
    args = ap.parse_args()

    rows = [
        ("无预算重试", strategy_no_budget(args.fail, args.retries),
         "每层 ×%d，乘法放大" % args.retries),
        ("有预算（上限 3）", strategy_budget(args.fail, 3),
         "发满就停，剩下的快速失败"),
        ("断路（阈值 %d）" % args.threshold, strategy_circuit(args.fail, args.threshold),
         "到阈值就打开，不发请求"),
    ]

    print("=" * 70)
    print("重试策略对比（模拟，%d 次连续故障）" % args.fail)
    print("=" * 70)
    for name, n, note in rows:
        print("  %-18s 发往上游 %3d 次   %s" % (name, n, note))

    base = rows[0][1]
    print("\n相对无预算重试：")
    for name, n, _ in rows[1:]:
        print("  %-18s 少发 %3d 次（%.0f%%）" % (name, base - n, 100 * (base - n) / base))

    print("\n结论：断路不是让服务更快，是让失败变便宜。")
    print("配套纪律：重试要有预算（次数 + 总时长），且必须指数退避。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
