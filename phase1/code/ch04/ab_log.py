#!/usr/bin/env python3
"""第 4 章配套工具：A/B 实测日志与汇总。

它只做三件事：
  1. 把一次任务的耗时按五段记下来（理解 / 实现 / 等待 / 返工 / 审查）
  2. 按组汇总 T_true、首轮验收率、缺陷数
  3. 给出中位数差与 bootstrap 区间——**并且明确告诉你 n 太小时不能下结论**

为什么要分段：人只记得"我写完那一刻"。等待（AI 在想）与返工（AI 想错了）
发生在两个不同的时间点，而且都不被主观计时捕获。

用法：
    python ab_log.py sample_log.csv
    python ab_log.py my_log.csv --resamples 20000

记录格式（CSV，表头必须一致）：
    task,group,understand,build,wait,rework,review,defects,first_pass
    group ∈ {hand, ai}；first_pass ∈ {0,1}；时间单位为分钟。

⚠️ sample_log.csv 里的数字是**编的**，只为演示格式。你自己的数字必须自己测。
"""

from __future__ import annotations

import argparse
import csv
import random
import statistics
from pathlib import Path

SEGMENTS = ("understand", "build", "wait", "rework", "review")


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        for k in SEGMENTS:
            r[k] = int(r[k])
        r["defects"] = int(r["defects"])
        r["first_pass"] = int(r["first_pass"])
        r["total"] = sum(r[k] for k in SEGMENTS)
        r["wait_ratio"] = r["wait"] / r["total"] if r["total"] else 0.0
    return rows


def by_group(rows: list[dict], group: str) -> list[dict]:
    return [r for r in rows if r["group"] == group]


def summarize(rows: list[dict]) -> dict:
    totals = [r["total"] for r in rows]
    return {
        "n": len(rows),
        "median": statistics.median(totals) if totals else 0,
        "mean": statistics.fmean(totals) if totals else 0,
        "fpa": statistics.fmean([r["first_pass"] for r in rows]) if rows else 0,
        "defects": statistics.fmean([r["defects"] for r in rows]) if rows else 0,
        "wait": statistics.fmean([r["wait_ratio"] for r in rows]) if rows else 0,
    }


def bootstrap_median_diff(a: list[int], b: list[int], resamples: int = 10000, seed: int = 7):
    """返回 (观测到的中位数差, 2.5 分位, 97.5 分位)。a - b。

    n 只有 3 时的区间会非常宽，这不是 bug——它诚实地告诉你"信息量不够"。
    """
    rng = random.Random(seed)
    observed = statistics.median(a) - statistics.median(b)
    diffs = []
    for _ in range(resamples):
        sa = [rng.choice(a) for _ in a]
        sb = [rng.choice(b) for _ in b]
        diffs.append(statistics.median(sa) - statistics.median(sb))
    diffs.sort()
    lo = diffs[int(0.025 * len(diffs))]
    hi = diffs[int(0.975 * len(diffs)) - 1]
    return observed, lo, hi


def main() -> int:
    ap = argparse.ArgumentParser(description="A/B 实测日志汇总")
    ap.add_argument("csv", type=Path)
    ap.add_argument("--resamples", type=int, default=10000)
    args = ap.parse_args()

    rows = load(args.csv)
    hand, ai = by_group(rows, "hand"), by_group(rows, "ai")
    if not hand or not ai:
        print("两组都必须有数据（group=hand / group=ai）")
        return 2

    s_hand, s_ai = summarize(hand), summarize(ai)

    print(f"\n记录文件：{args.csv}（共 {len(rows)} 条）\n")
    head = f"{'组别':<6}{'n':>3}{'T_true 中位数':>14}{'均值':>9}{'首轮验收率':>11}{'缺陷/任务':>10}{'等待占比':>10}"
    print(head)
    print("-" * len(head.encode("gbk", errors="ignore")))
    for label, s in (("手写", s_hand), ("AI", s_ai)):
        print(f"{label:<6}{s['n']:>3}{s['median']:>12.0f} 分{s['mean']:>7.0f}{s['fpa']:>10.0%}"
              f"{s['defects']:>10.2f}{s['wait']:>10.0%}")

    # 段位构成
    print("\n时间构成（均值，分钟）：")
    for label, group in (("手写", hand), ("AI", ai)):
        parts = "  ".join(
            f"{k} {statistics.fmean([r[k] for r in group]):.0f}" for k in SEGMENTS
        )
        print(f"  {label:<4}{parts}")

    diff, lo, hi = bootstrap_median_diff(
        [r["total"] for r in ai], [r["total"] for r in hand], args.resamples
    )
    print(f"\n中位数差（AI − 手写）= {diff:+.0f} 分钟")
    print(f"95% bootstrap 区间 = [{lo:+.0f}, {hi:+.0f}]  （重采样 {args.resamples} 次）")

    print()
    if lo <= 0 <= hi:
        print("结论：区间跨 0 → 这组数据**不足以支持任何一个方向**的结论。")
        print("      正确动作是继续攒数据（或加任务数），不是把这条写进复盘当结论。")
    else:
        print("结论：区间不跨 0 → 方向可信，但幅度仍受任务选择影响，别外推到别的项目。")
    if s_ai["n"] < 10:
        print(f"提醒：AI 组只有 {s_ai['n']} 条记录。n < 10 时，这是个案基线，不是统计结论。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
