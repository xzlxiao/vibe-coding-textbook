#!/usr/bin/env python3
"""上线日检查单：20 项，分四组，可打勾、可导出 Markdown。

运行：
    python ch10/launch_checklist.py               # 打印清单与示例进度
    python ch10/launch_checklist.py --export      # 导出可直接贴进仓库的 Markdown
    python ch10/launch_checklist.py --blockers    # 只看「不通过就必须推迟」的项

设计原则：每一项都要能被第三方在 5 分钟内验证。写不出验证方法的，不算检查项。
"""

from __future__ import annotations

import sys

# (分组, 编号, 条目, 验证方法, 是否阻断上线)
ITEMS = [
    ("能退回去", "R1", "上一次发布可一键回滚", "在预发执行一次回滚命令，计时", True),
    ("能退回去", "R2", "数据库迁移可回滚或已前向兼容", "查看迁移脚本，确认没有 DROP/改类型", True),
    ("能退回去", "R3", "上一版镜像保留 ≥ 7 天", "查看镜像仓库保留策略", True),
    ("能退回去", "R4", "特性开关可关闭新功能而不发版", "关掉开关，确认功能消失且旧路径正常", False),

    ("看得见", "O1", "四个黄金信号已上仪表盘", "打开面板，四个图都有数据", True),
    ("看得见", "O2", "错误率告警 5 分钟内可达", "造一次 5xx，计时等告警", True),
    ("看得见", "O3", "单请求成本可在日志里查到", "抽一条请求，看到 token 与费用", False),
    ("看得见", "O4", "上游超时有独立告警", "模拟上游超时，确认告警", False),
    ("看得见", "O5", "有一条「今天花了多少」的日汇总", "查看日报或查询语句", False),

    ("有后路", "B1", "备份任务最近 24 小时成功", "查看备份日志", True),
    ("有后路", "B2", "做过一次恢复演练并记录 RTO", "翻演练记录，有具体分钟数", True),
    ("有后路", "B3", "模型 API 不可用时有降级策略", "拔掉上游，看用户看到什么", True),
    ("有后路", "B4", "支付失败有明确提示与重试", "用测试卡触发失败", False),

    ("说得清", "L1", "价格页写明计费单位与周期", "自己读一遍，能否算出一个月多少钱", True),
    ("说得清", "L2", "自动续费在扣费前 5 日显著提示", "走一遍订阅流程，看提示在哪一步", True),
    ("说得清", "L3", "取消订阅入口不超过两层", "从首页点到取消，数点击次数", True),
    ("说得清", "L4", "有退款政策与联系方式", "页脚能找到，且邮箱能收信", True),
    ("说得清", "L5", "AI 交互处有「这是 AI」的告知", "打开对话界面，第一屏可见", True),
    ("说得清", "L6", "生成内容带标识", "导出一次结果，看是否带标识", True),
    ("说得清", "L7", "公示所用模型名称与备案号/上线编号", "在关于页或详情页可见", True),
]

# 示例进度：假设今天是上线前一天，R4 与 O3 还没做
DONE = {i[1] for i in ITEMS} - {"R4", "O3"}


def main() -> None:
    total = len(ITEMS)
    done = len(DONE)
    blockers = [i for i in ITEMS if i[4] and i[1] not in DONE]

    print("=== 上线日检查单 ===")
    group = ""
    for g, code, item, how, block in ITEMS:
        if g != group:
            print(f"\n[{g}]")
            group = g
        mark = "x" if code in DONE else " "
        flag = " ← 阻断" if block and code not in DONE else ""
        print(f"  [{mark}] {code}  {item}{flag}")
        print(f"        验证：{how}")

    print()
    print(f"进度：{done}/{total}　未完成阻断项：{len(blockers)}")
    if blockers:
        print("结论：不能上线。先处理：" + "、".join(b[2] for b in blockers))
        print("把「明天上线」改成「这几项做完就上线」——日期是承诺，条件是门槛。")
    else:
        print("结论：可以上线。上线后 24 小时内不要做任何非必要变更。")


def export() -> None:
    print("# 上线日检查单\n")
    group = ""
    for g, code, item, how, block in ITEMS:
        if g != group:
            print(f"\n## {g}\n")
            group = g
        suffix = "（阻断）" if block else ""
        print(f"- [ ] **{code}** {item}{suffix}  \n      验证：{how}")


if __name__ == "__main__":
    if "--export" in sys.argv:
        export()
    elif "--blockers" in sys.argv:
        for g, code, item, how, block in ITEMS:
            if block:
                print(f"{code}  {item}　验证：{how}")
    else:
        main()
