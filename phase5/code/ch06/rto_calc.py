#!/usr/bin/env python3
"""RTO / RPO 计算与反推：先量出你现在是多少，再算「要达到目标需要什么」。

运行：
    python ch06/rto_calc.py

两个方向：
    正向：给定演练时间戳，算出实测 RTO / RPO；
    反向：给定业务能接受的上限，反推备份频率与恢复时长要求。
"""

from __future__ import annotations

from datetime import datetime

# 一次真实「删库」演练的时间戳（预发环境，2026-10-18）
T_LAST_BACKUP = datetime(2026, 10, 18, 3, 0)
T_INCIDENT = datetime(2026, 10, 18, 14, 2)
T_NOTICE = datetime(2026, 10, 18, 14, 7)
T_START_RESTORE = datetime(2026, 10, 18, 14, 9)
T_RESTORED = datetime(2026, 10, 18, 15, 31)
T_VERIFIED = datetime(2026, 10, 18, 15, 48)


def mins(a: datetime, b: datetime) -> float:
    return (b - a).total_seconds() / 60


def human(m: float) -> str:
    h, mm = divmod(int(m), 60)
    return f"{h} 小时 {mm:02d} 分" if h else f"{mm} 分"


def main() -> None:
    rpo = mins(T_LAST_BACKUP, T_INCIDENT)
    detect = mins(T_INCIDENT, T_NOTICE)
    decide = mins(T_NOTICE, T_START_RESTORE)
    restore = mins(T_START_RESTORE, T_RESTORED)
    verify = mins(T_RESTORED, T_VERIFIED)
    rto = mins(T_INCIDENT, T_RESTORED)

    print("=== 实测（一次演练，不是估算）===")
    print(f"RPO（最后一次可用备份 → 故障）　{human(rpo)}　← 这段时间的写入全丢")
    print(f"RTO（故障 → 恢复可用）　　　　　{human(rto)}")
    print(f"  其中 发现 {detect:.0f} 分 / 决策 {decide:.0f} 分 / "
          f"恢复 {restore:.0f} 分 / 验证 {verify:.0f} 分")
    print()

    print("=== 这三段里，哪一段最值得改 ===")
    parts = [("发现", detect), ("决策", decide), ("恢复", restore), ("验证", verify)]
    worst = max(parts, key=lambda p: p[1])
    print(f"最长的是「{worst[0]}」：{worst[1]:.1f} 分，占 RTO 的 {worst[1] / rto:.0%}")
    print("  发现慢 → 加告警；决策慢 → 写值班卡；恢复慢 → 换备份方式或缩小数据量；"
          "验证慢 → 固化冒烟用例")
    print()

    print("=== 反推：如果业务要求 RPO ≤ 1 小时 ===")
    for label, freq in (("每日全量备份", 24), ("每 6 小时增量", 6), ("每 1 小时增量", 1),
                        ("持续归档 / WAL 流式", 0.05)):
        ok = "满足" if freq <= 1 else "不满足"
        print(f"  {label:<18}最坏 RPO ≈ {freq:>5.2f} 小时　{ok}")

    print()
    print("=== 反推：如果业务要求 RTO ≤ 30 分钟 ===")
    need_restore = 30 - detect - decide
    print(f"  留给恢复的时间 = 30 - {detect:.0f}（发现）- {decide:.0f}（决策）"
          f" = {need_restore:.0f} 分")
    print(f"  当前恢复耗时 {restore:.0f} 分，超出 {restore - need_restore:.0f} 分。")
    print("  两条路：把数据量缩小到能在窗口内恢复，或改成「不恢复、直接切只读副本」。")
    print()
    print("=== 结论怎么写进文档 ===")
    print(f"  当前承诺：RTO {human(rto)}，RPO {human(rpo)}")
    print("  对用户的说法必须与实测一致；不一致时，要么改架构，要么改承诺——"
          "不能只改文档。")


if __name__ == "__main__":
    main()
