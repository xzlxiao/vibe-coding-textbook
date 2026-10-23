#!/usr/bin/env python3
"""读 metrics.csv，算三个规格质量指标。

用法：
    python summarize.py metrics.csv
    python summarize.py metrics.csv --by-week

指标口径（与第 09 章正文一致，必须固定，换口径就没有可比性）：
- 首轮验收率 first-pass acceptance rate
    = first_pass=1 的任务数 / 任务总数
    分母是"任务"，不是 PR，也不是"需求"。
- 返工率 rework ratio
    = 合并后 7 天内跟进提交数 / 任务数
    只统计"为修这个任务而产生的提交"，重构与格式化不算。
- 规格漂移捕获 drift catches
    = 评审意见中"违反规格 / 超出范围外"的条数（累计）
    它是规格"承重"的证据，不是坏事。
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig") as f:  # 兼容 Excel 导出的 BOM
        rows = list(csv.DictReader(f))
    for r in rows:
        r["gen_rounds"] = int(r["gen_rounds"])
        r["first_pass"] = int(r["first_pass"])
        r["rework_commits"] = int(r["rework_commits"])
        r["review_minutes"] = int(r["review_minutes"])
        r["drift_hits"] = int(r["drift_hits"])
    return rows


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    if n == 0:
        raise SystemExit("csv 里没有数据行")
    first = sum(r["first_pass"] for r in rows)
    rework = sum(r["rework_commits"] for r in rows)
    drift = sum(r["drift_hits"] for r in rows)
    return {
        "tasks": n,
        "first_pass_tasks": first,
        "fpr": first / n,
        "rework_commits": rework,
        "rework_ratio": rework / n,
        "drift_catches": drift,
        "avg_review_minutes": sum(r["review_minutes"] for r in rows) / n,
        "avg_gen_rounds": sum(r["gen_rounds"] for r in rows) / n,
    }


def reading(fpr: float) -> str:
    if fpr < 0.5:
        return "低于 0.5：规格有系统性缺口，先别提高生成速度"
    if fpr > 0.9:
        return "高于 0.9：检查是否过规格（判据是否写到了风险不需要的细度）"
    return "落在 0.5–0.9：可继续，观察趋势而不是绝对值"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", type=Path)
    ap.add_argument("--by-week", action="store_true", help="按周拆分")
    args = ap.parse_args()

    rows = load(args.csv)
    s = summarize(rows)

    print("=== 规格质量指标 ===")
    print(f"任务数              : {s['tasks']}")
    print(f"首轮通过任务数      : {s['first_pass_tasks']}")
    print(f"首轮验收率          : {s['fpr']:.1%}   （{reading(s['fpr'])}）")
    print(f"跟进提交总数        : {s['rework_commits']}")
    print(f"返工率（提交/任务） : {s['rework_ratio']:.2f}")
    print(f"规格漂移捕获        : {s['drift_catches']} 次")
    print(f"平均评审时长        : {s['avg_review_minutes']:.0f} 分钟/任务")
    print(f"平均生成轮次        : {s['avg_gen_rounds']:.2f} 轮/任务")

    if args.by_week:
        buckets: dict[str, list[dict]] = defaultdict(list)
        for r in rows:
            iso = r["date"].split("-")
            buckets[f"{iso[0]}-{iso[1]}"].append(r)
        print("\n=== 按月 ===")
        print(f"{'月份':<10}{'任务':>4}{'首轮率':>8}{'返工率':>8}{'漂移':>6}")
        for k in sorted(buckets):
            b = summarize(buckets[k])
            print(f"{k:<10}{b['tasks']:>4}{b['fpr']:>8.0%}{b['rework_ratio']:>8.2f}{b['drift_catches']:>6}")


if __name__ == "__main__":
    main()
