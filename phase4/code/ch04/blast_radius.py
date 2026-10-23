#!/usr/bin/env python3
"""把一个智能体的工具清单换算成「权限矩阵 + 复核档」。

做法：对每个工具问三个问题（第 01 章 2.2 / 3.4 节的三判据）
    1. 影响半径  1 = 单个对象 / 2 = 一个服务或千行级 / 3 = 全库、全租户、已对外发生
    2. 可逆性    1 = 可回滚 / 2 = 需快照恢复 / 3 = 不可逆
    3. 可观测性  1 = 有日志且会告警 / 2 = 只有日志 / 3 = 看不见
然后用固定矩阵查复核档；可观测性 ≥ 2 时升一档（看不见 = 没有判断，只有赌）。

输出是可直接贴进威胁模型的 Markdown 表格。默认内置第 01 章的 LessonVault 客服智能体。

用法：
  python3 blast_radius.py                 # 打印内置案例
  python3 blast_radius.py --json my.json  # 换成你自己的工具清单
"""

from __future__ import annotations

import argparse
import json
import sys

TIERS = ["自动放行", "自动 + 事后审", "单人在环", "双人 + 预演", "默认禁止"]

# matrix[可逆性][影响半径]，值 = TIERS 的下标
MATRIX = {
    1: {1: 0, 2: 1, 3: 2},
    2: {1: 1, 2: 2, 3: 3},
    3: {1: 2, 2: 3, 3: 4},
}

RADIUS_LABEL = {1: "1 个对象", 2: "1 个服务 / 千行级", 3: "全库 / 全租户 / 已对外"}
REV_LABEL = {1: "可回滚", 2: "需快照恢复", 3: "不可逆"}

DEFAULT_SPEC = {
    "agent": "LessonVault 客服智能体",
    "tools": [
        {
            "name": "lookup_order(order_id)",
            "scope": "读：orders 单行",
            "radius": 1,
            "reversibility": 1,
            "observability": 1,
            "kill_switch": "关掉该 MCP 服务器即可",
        },
        {
            "name": "search_notes(query)",
            "scope": "读：notes 全表（limit 1000）",
            "radius": 2,
            "reversibility": 1,
            "observability": 2,
            "kill_switch": "同上；并把 limit 收到 20",
        },
        {
            "name": "issue_refund(order_id, cents)",
            "scope": "写：Stripe 退款，单笔上限 50 元",
            "radius": 1,
            "reversibility": 3,
            "observability": 1,
            "kill_switch": "撤下 Stripe 密钥 + 冻结该工具",
        },
        {
            "name": "bulk_refund(filter, cents)",
            "scope": "写：按筛选条件批量退款，无上限",
            "radius": 3,
            "reversibility": 3,
            "observability": 2,
            "kill_switch": "不提供该工具（默认禁止 = 不实现）",
        },
        {
            "name": "send_email(to, subject, body)",
            "scope": "外发：任意收件人",
            "radius": 3,
            "reversibility": 3,
            "observability": 3,
            "kill_switch": "邮件网关侧封域名 + 关闭工具",
        },
        {
            "name": "update_subscription(user_id, plan)",
            "scope": "写：subscriptions 单行",
            "radius": 1,
            "reversibility": 2,
            "observability": 1,
            "kill_switch": "回滚到上一 plan（有快照）",
        },
    ],
}


def tier_for(radius: int, reversibility: int, observability: int) -> tuple[str, str]:
    base = MATRIX[reversibility][radius]
    note = ""
    if observability >= 2 and base < 4:
        base += 1
        note = "可观测性不足，升一档"
    return TIERS[base], note


def to_markdown(spec: dict) -> tuple[str, list[str]]:
    lines = [
        f"### {spec['agent']} · 权限矩阵",
        "",
        "| 工具 | 作用域 | 影响半径 | 可逆性 | 可观测性 | 复核档 | kill switch |",
        "|---|---|---|---|---|---|---|",
    ]
    warnings: list[str] = []
    for t in spec["tools"]:
        tier, note = tier_for(t["radius"], t["reversibility"], t["observability"])
        obs = {1: "有日志+告警", 2: "只有日志", 3: "看不见"}[t["observability"]]
        lines.append(
            f"| `{t['name']}` | {t['scope']} | {RADIUS_LABEL[t['radius']]} | "
            f"{REV_LABEL[t['reversibility']]} | {obs} | **{tier}** | {t['kill_switch']} |"
        )
        if note:
            warnings.append(f"{t['name']}：{note}")
        if tier == TIERS[-1]:
            warnings.append(
                f"{t['name']}：落在「默认禁止」档——正确做法是**不实现**，而不是加个确认框"
            )
    return "\n".join(lines), warnings


def main() -> int:
    ap = argparse.ArgumentParser(description="工具清单 → 权限矩阵 + 复核档")
    ap.add_argument("--json", help="自定义清单的 JSON 路径；缺省用内置案例")
    args = ap.parse_args()

    if args.json:
        with open(args.json, encoding="utf-8") as fh:
            spec = json.load(fh)
    else:
        spec = DEFAULT_SPEC

    md, warnings = to_markdown(spec)
    print(md)

    graded = [
        (TIERS.index(tier_for(t["radius"], t["reversibility"], t["observability"])[0]), t["name"])
        for t in spec["tools"]
    ]
    allowed = [(i, n) for i, n in graded if i < TIERS.index(TIERS[-1])]
    banned = [n for i, n in graded if i == TIERS.index(TIERS[-1])]

    if allowed:
        top_idx, top_name = max(allowed)
        print(f"\n已实现工具的复核档取最高项：**{TIERS[top_idx]}**（由 `{top_name}` 决定）")
        print("理由：档位不能线性平均。链路里只要有一个不可撤的出口，整条链就是不可撤的。")
    if banned:
        print(f"\n不该实现（应删掉工具定义，而不是加确认框）：{'、'.join(f'`{n}`' for n in banned)}")

    if warnings:
        print("\n需要盯的三处：")
        for w in warnings:
            print(f"  - {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
