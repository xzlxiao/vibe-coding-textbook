#!/usr/bin/env python3
"""SLO 与错误预算：把「稳不稳」换算成分钟，再把分钟换算成告警阈值。

运行：
    python ch05/slo_burn.py

输出三张东西：
  1. 预算换算表（不同 SLO → 每月可用的故障分钟）
  2. 燃烧率 → 烧穿时间（决定「多久必须响应」）
  3. 多窗口告警阈值（既不过度打扰，也不漏掉慢性泄漏）
"""

from __future__ import annotations

WINDOW_DAYS = 30
WINDOW_MIN = WINDOW_DAYS * 24 * 60


def budget_min(slo: float) -> float:
    return (1 - slo) * WINDOW_MIN


def burn_to_zero_hours(rate: float) -> float:
    """燃烧率是「相对允许错误率的倍数」，所以烧穿时间 = 窗口 / 倍数。

    注意别写成「预算分钟数 / 倍数」——那会把 1× 算成 3.6 小时，
    而 1× 的真实含义是「刚好用完整个 30 天」。
    """
    return WINDOW_MIN / 60 / rate


def main() -> None:
    print("=== 1. 预算换算（30 天窗口）===")
    print(f"{'SLO':<8}{'允许失败比例':>14}{'每月可用故障':>14}{'每周':>10}")
    print("-" * 48)
    for slo in (0.99, 0.995, 0.999):
        b = budget_min(slo)
        print(f"{slo:<8.1%}{(1 - slo):>13.2%}{b:>12.0f} 分{b / 4.3:>9.0f} 分")

    slo = 0.995
    b = budget_min(slo)
    print()
    print(f"本书取 SLO = {slo:.1%}，即每月 {b:.0f} 分钟（约 {b / 60:.1f} 小时）")

    print()
    print("=== 2. 燃烧率：这个速度下，多久烧光一个月预算 ===")
    print(f"{'燃烧率':<10}{'含义':<22}{'烧穿时间':>12}")
    print("-" * 46)
    rows = [
        (1.0, "刚好贴着 SLO 走", ""),
        (6.0, "慢性泄漏", ""),
        (14.4, "一天内必须处理", ""),
        (60.0, "全站不可用", ""),
    ]
    for rate, meaning, _ in rows:
        h = burn_to_zero_hours(rate)
        show = f"{h:.0f} 小时" if h < 72 else f"{h / 24:.0f} 天"
        print(f"{rate:<10.1f}{meaning:<22}{show:>12}")

    print()
    print("=== 3. 多窗口告警阈值（Google SRE 的常用组合，按你的 SLO 重算）===")
    print("长窗口负责「确认这是真问题」，短窗口负责「确认它还在继续」，两者同时满足才报警。")
    print()
    print(f"{'级别':<6}{'长窗口':<8}{'短窗口':<8}{'阈值':<10}{'含义'}")
    print("-" * 62)
    print(f"{'P1':<6}{'1 小时':<8}{'5 分钟':<8}{'14.4×':<10}1 小时烧掉 2% 月预算")
    print(f"{'P2':<6}{'6 小时':<8}{'30 分钟':<8}{'6×':<10}6 小时烧掉 5% 月预算")
    print(f"{'P3':<6}{'3 天':<8}{'6 小时':<8}{'1×':<10}已在持续泄漏，工作日处理")

    print()
    print("算一下 P1 为什么是 14.4：")
    print(f"  1 小时 = {1 / (WINDOW_DAYS * 24):.4%} 的月时长；"
          f"想在 1 小时内烧掉 2% 预算，需要 {0.02 / (1 / (WINDOW_DAYS * 24)):.1f}× 的速率")

    print()
    print("=== 4. 本月四次故障的累计消耗 ===")
    events = [
        ("D3", 20 / 60, 60, "全站不可用"),
        ("D11", 1.5, 40, "转写队列积压，20% 请求失败"),
        ("D18", 0.75, 60, "登录故障"),
        ("D26", 4.0, 20, "单模型降级，10% 请求失败"),
    ]
    used = 0.0
    for day, hours, rate, desc in events:
        delta = rate * hours / (WINDOW_DAYS * 24) * 100
        used += delta
        print(f"  {day:<4}{desc:<28}+{delta:5.1f}%　累计 {used:5.1f}%")
    print(f"\n  合计 {used:.1f}% —— 还在预算内，但已经用掉四分之一。")
    print("  预算没用完不等于没事：它说明这个月没有余量再做「有风险的发布」。")


if __name__ == "__main__":
    main()
