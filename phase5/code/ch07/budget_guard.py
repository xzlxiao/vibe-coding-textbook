#!/usr/bin/env python3
"""预算守卫：单用户日预算 + 全局日预算 + 熔断。

运行：
    python ch07/budget_guard.py            # 跑一段仿真，看熔断怎么触发
    python ch07/budget_guard.py --test     # 跑一组断言，验证边界行为

设计要点（照抄到生产前请先看这三条）：
  1. 熔断必须是「拒绝新请求」，不是「让请求变便宜」——降级是另一层，别混在一起；
  2. 计数要以「用户 + 日」为键，跨日自动重置；用 UTC 还是本地时间要写死，别随环境变；
  3. 熔断触发时返回明确的错误码，前端才能给出「今天额度用完了」这种可理解的提示。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field


@dataclass
class Guard:
    per_user_daily: float = 3.0
    global_daily: float = 300.0
    warn_ratio: float = 0.8
    user_spend: dict[str, float] = field(default_factory=dict)
    total: float = 0.0
    tripped: bool = False

    def charge(self, user: str, cost: float) -> tuple[bool, str]:
        """返回 (是否放行, 原因)。调用方必须先问再花钱，不能先花再补记。"""
        if self.tripped:
            return False, "global_tripped"
        if self.user_spend.get(user, 0.0) + cost > self.per_user_daily:
            return False, "user_quota"
        if self.total + cost > self.global_daily:
            self.tripped = True
            return False, "global_budget"
        self.user_spend[user] = self.user_spend.get(user, 0.0) + cost
        self.total += cost
        return True, "ok"

    def warn(self) -> bool:
        return self.total >= self.global_daily * self.warn_ratio

    def reset_day(self) -> None:
        self.user_spend.clear()
        self.total = 0.0
        self.tripped = False


def simulate() -> None:
    g = Guard()
    print("=== 仿真：一个用户陷入重试循环 ===")
    print(f"单用户日预算 ¥{g.per_user_daily:.0f}　全局日预算 ¥{g.global_daily:.0f}")
    print()
    print(f"{'轮次':<6}{'请求成本':>8}{'该用户累计':>12}{'全局累计':>10}  结果")
    print("-" * 56)

    cost = 0.46
    for i in range(1, 12):
        ok, why = g.charge("u_1024", cost)
        mark = "放行" if ok else f"拒绝（{why}）"
        print(f"{i:<6}{cost:>8.2f}{g.user_spend.get('u_1024', 0.0):>12.2f}"
              f"{g.total:>10.2f}  {mark}")

    print()
    print(f"该用户被拦在 ¥{g.user_spend['u_1024']:.2f}，"
          f"相当于 {int(g.per_user_daily / cost)} 次请求。")
    print("没有这道闸，重试循环会把 300 元的日预算在半小时内烧完。")

    print()
    print("=== 再模拟一个全局超支日：200 个用户同时陷入异常 ===")
    g.reset_day()
    hour = 0
    while not g.tripped and hour < 24:
        hour += 1
        for u in range(200):
            g.charge(f"u_{u}", 0.46)
        if g.warn():
            print(f"  {hour:02d}:00　全局累计 ¥{g.total:.0f}　已越过 80% 预警线")
    print(f"  熔断于第 {hour} 小时触发，停在 ¥{g.total:.0f}。")
    print(f"  停在 ¥{g.total:.0f} / ¥{g.global_daily:.0f}：再下一个请求就会越过上限，所以被拒。")
    print("  这不是浪费，是边界：宁可卡在预算上，不要让账单翻倍。")


def test() -> None:
    g = Guard(per_user_daily=1.0, global_daily=10.0)
    assert g.charge("a", 0.6)[0] is True
    assert g.charge("a", 0.6)[0] is False, "单用户超额必须拒绝"
    assert g.charge("b", 0.6)[0] is True
    assert g.tripped is False
    g2 = Guard(per_user_daily=100.0, global_daily=1.0)
    assert g2.charge("a", 0.9)[0] is True
    assert g2.charge("b", 0.2)[0] is False
    assert g2.tripped is True
    ok, why = g2.charge("c", 0.1)
    assert (ok, why) == (False, "global_tripped"), "熔断后所有请求都应被拒"
    g2.reset_day()
    assert g2.charge("c", 0.1)[0] is True, "跨日重置后应恢复"
    print("6 项断言全部通过：单用户限额、全局限额、熔断后拒绝、跨日重置。")


if __name__ == "__main__":
    test() if "--test" in sys.argv else simulate()
