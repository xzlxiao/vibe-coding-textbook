#!/usr/bin/env python3
"""回滚演练记录器：把一次演练拆成五个时刻，算出四段耗时并判定是否达标。

运行：
    python ch04/rollback_drill.py            # 打印本书的演练样例
    python ch04/rollback_drill.py --blank    # 打印一张空白记录表，演练时手填

真实演练时请按后面四个常量改时间，别改程序逻辑——演练最怕的就是「为了好看而调数」。
"""

from __future__ import annotations

from datetime import datetime, timedelta

# 一次真实演练的五个时刻（2026-10-17，预发环境）
T_DEPLOY = datetime(2026, 10, 17, 14, 2)    # 带缺陷版本上线
T_NOTICE = datetime(2026, 10, 17, 14, 11)   # 告警触发 / 人发现
T_DECIDE = datetime(2026, 10, 17, 14, 14)   # 决定回滚
T_ROLLED = datetime(2026, 10, 17, 14, 19)   # 上一版重新可用
T_VERIFY = datetime(2026, 10, 17, 14, 24)   # 关键路径验证通过

# 目标值：来自上线判据，不是行业标准
TARGETS = {
    "发现": 5,      # 分钟
    "决策": 5,
    "执行": 3,
    "验证": 10,
}


def minutes(a: datetime, b: datetime) -> float:
    return (b - a).total_seconds() / 60


def main() -> None:
    segs = [
        ("发现（故障 → 知道）", minutes(T_DEPLOY, T_NOTICE), TARGETS["发现"]),
        ("决策（知道 → 决定）", minutes(T_NOTICE, T_DECIDE), TARGETS["决策"]),
        ("执行（决定 → 上一版可用）", minutes(T_DECIDE, T_ROLLED), TARGETS["执行"]),
        ("验证（可用 → 确认没事）", minutes(T_ROLLED, T_VERIFY), TARGETS["验证"]),
    ]

    print("=== 回滚演练记录 ===")
    print(f"{'阶段':<26}{'实测':>8}{'目标':>8}  判定")
    print("-" * 56)
    total = 0.0
    for name, actual, target in segs:
        total += actual
        ok = "达标" if actual <= target else "超时"
        print(f"{name:<26}{actual:>6.0f} 分{target:>6} 分  {ok}")

    print("-" * 56)
    print(f"{'故障到确认恢复':<26}{total:>6.0f} 分")

    fail = [(n, a, t) for n, a, t in segs if a > t]
    print()
    if not fail:
        print("结论：五段全部达标，这套流程可以写进上线检查单。")
    else:
        print(f"结论：{len(fail)} 段超时，不能写进检查单。逐条改法：")
        for name, actual, target in fail:
            print(f"  - {name}：实测 {actual:.0f} 分 / 目标 {target} 分 → {_fix(name)}")

    print()
    print("=== 这次演练暴露的一个真问题 ===")
    print("回滚脚本能跑，但它假设「上一版镜像还在」。若镜像保留策略是 3 天，"
          "而故障发生在上线第 4 天，脚本会静默失败。")
    print("改法：把镜像保留期写进部署配置并与回滚脚本同源，演练时顺带验证一次。")


def _fix(name: str) -> str:
    return {
        "发现（故障 → 知道）": "补一条症状告警（错误率 5 分钟窗口），不要等用户反馈",
        "决策（知道 → 决定）": "把「谁有权决定回滚」写进值班卡，必要时先回滚再定位",
        "执行（决定 → 上一版可用）": "回滚命令一条化，镜像保留期 ≥ 7 天并纳入演练",
        "验证（可用 → 确认没事）": "固化 5 条冒烟用例，跑完即出结论",
    }.get(name, "按记录逐项排查")


def blank() -> None:
    print("=== 回滚演练空白记录表（演练时手填）===")
    for field in ("版本号 / 变更内容", "T1 发布完成", "T2 发现时间", "T3 决定回滚",
                  "T4 上一版可用", "T5 验证通过", "失败环节与改法"):
        print(f"  {field}：______________________")


if __name__ == "__main__":
    import sys
    blank() if "--blank" in sys.argv else main()
