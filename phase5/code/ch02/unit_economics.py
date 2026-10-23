#!/usr/bin/env python3
"""单位经济计算器：三档模型 × 三个用量档，外加一次敏感性分析。

运行：
    python ch02/unit_economics.py

所有单价都是「假设值」，请换成你签约时的实际价目。程序只负责算，不替你判断。
"""

from __future__ import annotations

PRICE = 39.0              # 订阅价，元/月
MEETING_MIN = 50          # 单次会议时长
ASR_PER_MIN = 0.002       # 语音转写，元/分钟
AUDIO_MB_PER_MIN = 1.0
STORE_PER_GB = 0.30
PAY_RATE = 0.006
TOK_IN, TOK_OUT = 15_000, 2_000
EMB = 0.0017
FIXED = 120.0

TIERS = {"经济档": (0.8, 2.0), "标准档": (2.0, 8.0), "旗舰档": (15.0, 60.0)}
USAGE = {"轻度": 10, "典型": 30, "重度": 90}


def cost_per_meeting(tier: str) -> float:
    pin, pout = TIERS[tier]
    llm = TOK_IN * pin / 1e6 + TOK_OUT * pout / 1e6
    asr = MEETING_MIN * ASR_PER_MIN
    storage = MEETING_MIN * AUDIO_MB_PER_MIN / 1024 * STORE_PER_GB
    return asr + storage + llm + EMB


def monthly(n: int, tier: str) -> dict:
    variable = n * cost_per_meeting(tier) + PRICE * PAY_RATE
    margin = PRICE - variable
    return {
        "n": n,
        "variable": variable,
        "margin": margin,
        "rate": margin / PRICE * 100,
        "per_meeting": variable / n,
    }


def break_even(tier: str) -> float:
    return (PRICE - PRICE * PAY_RATE) / cost_per_meeting(tier)


def main() -> None:
    print("=== 单位经济：三档模型 × 三个用量档 ===")
    print(f"订阅 ¥{PRICE}/月　单次 {MEETING_MIN} 分钟　转写 ¥{ASR_PER_MIN}/分钟　"
          f"存储 ¥{STORE_PER_GB}/GB/月　支付 {PAY_RATE:.1%}")
    print("模型单价（元/百万 token）：" + "　".join(
        f"{k} {v[0]}/{v[1]}" for k, v in TIERS.items()))
    print()

    header = f"{'档位':<6}{'用量':<6}{'次数':>4}{'变动成本':>10}{'贡献毛利':>10}{'毛利率':>9}{'单次成本':>10}"
    print(header)
    print("-" * len(header) * 2)
    for tier in TIERS:
        for label, n in USAGE.items():
            r = monthly(n, tier)
            print(f"{tier:<6}{label:<6}{r['n']:>4}{r['variable']:>10.2f}"
                  f"{r['margin']:>10.2f}{r['rate']:>8.1f}%{r['per_meeting']:>10.3f}")
        print()

    print("=== 盈亏平衡（每月多少次会议开始亏） ===")
    for tier in TIERS:
        be = break_even(tier)
        print(f"{tier}：{be:6.1f} 次/月" + ("　→ 重度用户已经越线" if be < 90 else ""))

    print()
    print("=== 覆盖固定成本需要多少付费用户（标准档 · 重度 90 次） ===")
    r = monthly(90, "标准档")
    print(f"单用户贡献毛利 ¥{r['margin']:.2f}　固定成本 ¥{FIXED:.0f}/月　"
          f"需要 {FIXED / r['margin']:.1f} 个 → 取整 {int(-(-FIXED // r['margin']))} 个")

    print()
    print("=== 敏感性：标准档 · 重度 90 次，各变量单独恶化 ===")
    base = r["rate"]
    cases = [
        ("模型单价 +20%", lambda: _with_price(1.2)),
        ("缓存命中率归零（输入 token +30%）", lambda: _with_input(1.3)),
        ("单用户用量 +50%", lambda: _with_n(135)),
    ]
    for name, fn in cases:
        rate = fn()
        print(f"{name:<34}毛利率 {rate:5.1f}%　（变化 {rate - base:+.1f} 个百分点）")


def _with_price(k: float) -> float:
    pin, pout = TIERS["标准档"]
    llm = k * (TOK_IN * pin / 1e6 + TOK_OUT * pout / 1e6)
    per = llm + MEETING_MIN * ASR_PER_MIN + MEETING_MIN / 1024 * STORE_PER_GB + EMB
    return (PRICE - (90 * per + PRICE * PAY_RATE)) / PRICE * 100


def _with_input(k: float) -> float:
    pin, pout = TIERS["标准档"]
    llm = k * TOK_IN * pin / 1e6 + TOK_OUT * pout / 1e6
    per = llm + MEETING_MIN * ASR_PER_MIN + MEETING_MIN / 1024 * STORE_PER_GB + EMB
    return (PRICE - (90 * per + PRICE * PAY_RATE)) / PRICE * 100


def _with_n(n: int) -> float:
    return monthly(n, "标准档")["rate"]


if __name__ == "__main__":
    main()
