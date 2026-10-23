#!/usr/bin/env python3
"""健康度看板：四个指标 + 趋势判定，回答「该补还是该推倒」。

运行：
    python ch09/health_dashboard.py

判定规则（写在代码里，避免每次凭感觉）：
    连续 4 周朝坏方向走 → 该指标「转向」
    至少 3 个指标同时转向 → 触发重写讨论
    只有 1 个转向 → 先补那一条，不谈重写
"""

from __future__ import annotations

WEEKS = [1, 2, 3, 4, 5, 6, 7, 8]

METRICS = {
    "首轮验收率（%）": ([72, 74, 76, 75, 71, 66, 61, 58], "up"),
    "返工率（%）": ([18, 17, 16, 18, 22, 27, 31, 35], "down"),
    "门禁拦截（次/周）": ([12, 11, 13, 14, 19, 24, 28, 33], "down"),
    "单任务成本（元）": ([6.2, 6.0, 6.1, 6.4, 7.3, 8.6, 9.9, 11.4], "down"),
}

# "up" = 数值越大越好；"down" = 数值越小越好


def slope(values: list[float]) -> float:
    """最小二乘斜率，用来判断趋势而不被单周波动带偏。"""
    n = len(values)
    xs = list(range(n))
    mx = sum(xs) / n
    my = sum(values) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, values))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den


def worsening(values: list[float], good: str) -> bool:
    s = slope(values)
    return s < 0 if good == "up" else s > 0


def consecutive_worse(values: list[float], good: str, span: int = 4) -> bool:
    tail = values[-span:]
    pairs = list(zip(tail, tail[1:]))
    if good == "up":
        return all(b < a for a, b in pairs)
    return all(b > a for a, b in pairs)


def main() -> None:
    print("=== 八周健康度（模拟数据，用于演示判据）===")
    print(f"{'指标':<20}{'第1周':>8}{'第8周':>8}{'斜率/周':>10}  判定")
    print("-" * 60)

    turned = 0
    for name, (values, good) in METRICS.items():
        s = slope(values)
        bad = worsening(values, good) and consecutive_worse(values, good)
        turned += 1 if bad else 0
        verdict = "转向" if bad else "平稳"
        print(f"{name:<20}{values[0]:>8.1f}{values[-1]:>8.1f}{s:>+10.2f}  {verdict}")

    print()
    print(f"转向指标数：{turned} / {len(METRICS)}")
    if turned >= 3:
        print("判定：触发重写讨论。但先回答一个问题——")
        print("  是「结构撑不住了」，还是「需求变了、旧结构在为新需求买单」？")
        print("  前者重写，后者只该补一层适配。")
    elif turned == 1:
        print("判定：先补那一条。单项恶化通常是局部问题，不构成重写理由。")
    else:
        print("判定：继续观察，不动结构。")

    print()
    print("=== 打分卡：四条重写判据（0—5 分，越线即触发）===")
    card = [
        ("改动半径（改一个需求要动几个文件）", 4.2, 3.5),
        ("理解成本（三个月后的你要多久能改）", 4.5, 3.5),
        ("缺陷密度趋势（连续四周是否上升）", 3.8, 2.5),
        ("门禁通过率趋势（补测试后是否仍下降）", 2.2, 2.5),
    ]
    for name, score, line in card:
        flag = "越线" if score > line else "未越线"
        print(f"  {name:<34}{score:>4.1f} / 阈值 {line:.1f}　{flag}")

    over = sum(1 for _, s, l in card if s > l)
    print()
    print(f"越线 {over} 条 → " + ("可以谈重写，且必须同时给出「不重写」的替代方案。"
                                 if over >= 3 else "不满足重写条件，先补最差的那条。"))

    print()
    print("=== 如果决定不重写，最小动作是什么 ===")
    print("  1. 把改动半径最大的那个模块抽出一个接口层，先隔离，不重写；")
    print("  2. 给最常改的两条路径补上端到端用例，把门禁通过率拉回来；")
    print("  3. 四周后重跑这张看板：斜率变平 = 补对了；继续恶化 = 再谈推倒。")


if __name__ == "__main__":
    main()
