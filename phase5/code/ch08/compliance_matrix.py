#!/usr/bin/env python3
"""合规判定器：按「卖到哪 + 做什么」输出一张义务清单。

运行：
    python ch08/compliance_matrix.py                 # 默认：卖到欧盟、有限风险、面向公众
    python ch08/compliance_matrix.py --market cn
    python ch08/compliance_matrix.py --tier high --no-public

它不会替你做法律判断，只做三件事：
  1. 把「你落在哪一档」的推导过程写出来，方便你复核；
  2. 把该档对应的义务逐条列出，并给出条文依据；
  3. 把「现在必须做 / 可以排期 / 不适用」分开，避免把 2027 的活提前干。
"""

from __future__ import annotations

import sys

EU_TIMELINE = [
    ("2026-08-02", "透明度义务（第 50 条）+ GPAI 义务可强制执行"),
    ("2026-12-02", "既有系统的机器可读标识宽限到期；新增禁令生效"),
    ("2027-12-02", "附件三高风险系统义务适用"),
    ("2028-08-02", "附件一嵌入型高风险系统义务适用"),
]

DUTIES = {
    "limited": [
        ("AI 交互告知：聊天界面明确说明「你在和 AI 交互」", "第 50(1) 条", "现在"),
        ("生成内容标识：图像/音频/视频/文本可识别为 AI 生成", "第 50(2) 条", "现在"),
        ("机器可读标记：水印或元数据（既有系统宽限至 2026-12-02）", "第 50(2) 条", "现在"),
        ("深伪内容显著声明", "第 50(4) 条", "现在"),
        ("记录你做过什么：一页合规说明即可", "第 50 条 / 问责原则", "现在"),
    ],
    "high": [
        ("风险管理体系（持续迭代，不是一次性文档）", "第 9 条", "2027-12-02"),
        ("技术文档与记录保存", "第 11、12 条", "2027-12-02"),
        ("人类监督机制", "第 14 条", "2027-12-02"),
        ("准确率/鲁棒性/网络安全要求", "第 15 条", "2027-12-02"),
        ("合格性评估与 CE 标记、欧盟数据库登记", "第 43、49 条", "2027-12-02"),
        ("以上之外，第 50 条透明度义务照旧", "第 50 条", "现在"),
    ],
    "minimal": [
        ("无强制义务；保留自愿性良好实践（如内容说明）", "—", "可选"),
    ],
}

CN_DUTIES = [
    ("自研模型对外提供服务 → 生成式 AI 服务备案", "《生成式人工智能服务管理暂行办法》", "上线前"),
    ("调用已备案模型的应用/功能 → 属地网信部门登记", "同上（登记通道）", "上线前"),
    ("显著位置公示模型名称、备案号或上线编号", "同上 / 属地公告要求", "上线时"),
    ("按《人工智能生成合成内容标识办法》添加标识", "标识办法", "上线时"),
    ("自动续费：接受服务前 + 续费前 5 日显著提示，可自主选择", "《网络交易监督管理办法》第 18 条", "上线前"),
    ("自动续费：服务期内提供显著、简便的随时取消入口", "同上", "上线前"),
    ("个人信息：最小收集、目的明确、可删除", "《个人信息保护法》", "上线前"),
]


def tier_from(args: dict) -> tuple[str, str]:
    if args.get("tier"):
        return args["tier"], "由参数指定"
    if args.get("high_risk_decision"):
        return "high", "系统对个人做出影响权利的决定（招聘/信贷/教育等）"
    return "limited", "AI 与用户交互或生成内容，但不做高风险决定"


def main() -> None:
    args = {"market": "eu", "tier": "", "public": True}
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == "--market":
            args["market"] = argv[i + 1]
        elif a == "--tier":
            args["tier"] = argv[i + 1]
        elif a == "--no-public":
            args["public"] = False
        elif a == "--high-risk":
            args["high_risk_decision"] = True

    tier, reason = tier_from(args)
    print("=== 第一步：定档（这一步错了，后面全错）===")
    print(f"  市场：{'欧盟' if args['market'] == 'eu' else '中国'}")
    print(f"  面向公众：{'是' if args['public'] else '否'}")
    print(f"  判定：{tier}　依据：{reason}")
    print()

    if args["market"] == "eu":
        print("=== 第二步：时间表（截至 2026-10 快照）===")
        for date, what in EU_TIMELINE:
            print(f"  {date}　{what}")
        print()
        print("=== 第三步：你这个档位要做什么 ===")
        print(f"{'义务':<52}{'依据':<18}{'时点'}")
        print("-" * 82)
        for duty, ref, when in DUTIES[tier]:
            print(f"{duty:<52}{ref:<18}{when}")
    else:
        print("=== 第二步：国内的义务清单 ===")
        print(f"{'义务':<46}{'依据':<34}{'时点'}")
        print("-" * 88)
        for duty, ref, when in CN_DUTIES:
            print(f"{duty:<46}{ref:<34}{when}")

    print()
    print("=== 第四步：一页说明怎么写（照这个骨架填）===")
    print("  1. 我卖到哪：______________")
    print(f"  2. 我在哪一档：{tier}，依据是 ______________")
    print("  3. 现在必须做：______________（做完打勾）")
    print("  4. 可以排期：______________（写明时间点）")
    print("  5. 触发动作：什么情况停机 / 什么情况告知 / 什么情况改架构")
    print()
    print("提示：本脚本输出是教学归纳，不构成法律意见；正式上线前请按当地要求复核。")


if __name__ == "__main__":
    main()
