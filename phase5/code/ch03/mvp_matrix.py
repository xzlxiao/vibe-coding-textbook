#!/usr/bin/env python3
"""MVP 范围打分器：把需求池按「闭环要件 × 贡献 × 成本」摊开。

运行：
    python ch03/mvp_matrix.py

评分是主观的——这件事无法自动化。程序只做三件事：
  1. 先摘出「闭环要件」：缺了它就没有产品，成本再高也得做；
  2. 剩下的按贡献 × 真实成本摆进四象限；
  3. 强制每条「不做」的功能写一句触发条件，避免以后凭感觉翻案。
"""

from __future__ import annotations

# name, 闭环要件?, 付费闭环贡献 0-10, 实现成本 0-10, 上线后维护成本 0-10
FEATURES = [
    ("录音上传与转写", True, 9.4, 7.5, 5.0),
    ("结构化纪要生成", True, 9.6, 8.4, 6.0),
    ("订阅与支付", True, 9.2, 3.2, 2.0),
    ("行动项提取", False, 8.6, 6.0, 4.0),
    ("导出 Word / PDF", False, 7.8, 2.6, 1.0),
    ("说话人分离", False, 6.2, 6.8, 4.0),
    ("自定义模板", False, 5.6, 5.4, 3.0),
    ("团队共享空间", False, 5.0, 8.8, 7.0),
    ("移动端 App", False, 3.4, 9.2, 9.0),
    ("日历自动入会", False, 3.2, 6.2, 3.0),
    ("多语言界面", False, 2.6, 4.4, 4.0),
    ("情绪与语气分析", False, 1.4, 7.6, 5.0),
]

VALUE_LINE = 5.0
COST_LINE = 5.0
# 维护成本按 0.4 折算：上线是一次性支出，维护是每月都要付的
MAINT_WEIGHT = 0.4


def real_cost(base: float, maint: float) -> float:
    return base + MAINT_WEIGHT * maint


def bucket(essential: bool, contribution: float, cost: float) -> str:
    if essential:
        return "现在做（闭环要件）"
    if contribution >= VALUE_LINE and cost < COST_LINE:
        return "现在做"
    if contribution >= VALUE_LINE:
        return "想清楚再做"
    if cost < COST_LINE:
        return "顺手就做"
    return "永远不做"


def main() -> None:
    rows = []
    for name, essential, value, cost, maint in FEATURES:
        c = real_cost(cost, maint)
        rows.append((name, essential, value, c, bucket(essential, value, c)))

    print("=== 功能清单（成本已按 0.4 权重折入维护成本）===")
    print(f"{'功能':<18}{'要件':<6}{'贡献':>6}{'真实成本':>10}  结论")
    print("-" * 58)
    for name, essential, value, cost, b in sorted(rows, key=lambda r: -r[2]):
        tag = "是" if essential else "—"
        print(f"{name:<18}{tag:<6}{value:>6.1f}{cost:>10.1f}  {b}")

    print()
    for b in ("现在做（闭环要件）", "现在做", "想清楚再做", "顺手就做", "永远不做"):
        names = [r[0] for r in rows if r[4] == b]
        if names:
            print(f"{b}（{len(names)} 项）：{'、'.join(names)}")

    now = [r for r in rows if r[4].startswith("现在做")]
    heavy = [r[0] for r in now if r[1] and r[3] >= 9]
    print()
    print(f"第一版范围：{len(now)} 项；其中闭环要件 {sum(1 for r in now if r[1])} 项")
    print(f"要件里有 {len(heavy)} 项成本 ≥ 9：{'、'.join(heavy)}"
          "　—— 这就是为什么第一版必须砍掉一切非要件。")
    print("注意：要件这一列不看成本。缺了它就没有产品，再贵也得做——"
          "象限只对「锦上添花」的东西有否决权。")

    print()
    print("=== 故意不做清单（必须带触发条件）===")
    for name, essential, value, cost, b in rows:
        if b in ("想清楚再做", "永远不做"):
            print(f"  - {name}：{b}；触发条件：{_trigger(name)}")


def _trigger(name: str) -> str:
    table = {
        "行动项提取": "用户访谈里出现 3 次以上「找不到谁负责什么」",
        "说话人分离": "付费用户中三人以上会议的占比超过 30%",
        "自定义模板": "同一用户连续三周手动修改输出格式",
        "团队共享空间": "出现第一个 5 人以上的付费团队",
        "移动端 App": "移动端访问占比超过 40% 且留存明显更高",
        "日历自动入会": "用户平均每周手动上传超过 5 次",
        "多语言界面": "非中文用户占注册量 20% 以上",
        "情绪与语气分析": "有客户为此单独询价",
    }
    return table.get(name, "有付费用户明确提出并愿意为此加价")


if __name__ == "__main__":
    main()
