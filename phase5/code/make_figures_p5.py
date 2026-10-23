#!/usr/bin/env python3
"""《从能跑到能收钱》全书 20 张配图。

用法:
    python code/make_figures_p5.py            # 全部
    python code/make_figures_p5.py ch04       # 只画某一章

贯穿案例：会议纪要助手「纪要」——订阅 39 元/月，单次会议平均 50 分钟。
所有金额假设集中写在下方常量区，章节正文引用的数字与此处一一对应。
"""

from __future__ import annotations

import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

from _figstyle import (
    ASSETS, BAD, GOOD, GRID, INK, MUTED, PAPER, SAND, STEEL,
    arrow, blank, box, clean_axes, save, stamp,
)

# ---------------------------------------------------------------- 贯穿案例参数
PRICE = 39.0              # 订阅价，元/月
MEETING_MIN = 50          # 单次会议平均时长，分钟
ASR_PER_MIN = 0.002       # 语音转写，元/分钟（快照假设）
AUDIO_MB_PER_MIN = 1.0    # 音频体积，MB/分钟
STORE_PER_GB = 0.30       # 对象存储，元/GB/月（快照假设）
PAY_RATE = 0.006          # 支付通道费率
TOK_IN = 15_000           # 单次会议输入 token
TOK_OUT = 2_000           # 单次会议输出 token
EMB_PER_MEETING = 0.0017  # 单次会议的向量检索摊销
FIXED_COST = 120.0        # 域名 + 数据库 + 监控 + 邮件，元/月

# 三档模型单价：(输入 元/百万 token, 输出 元/百万 token)
TIERS = {
    "经济档": (0.8, 2.0),
    "标准档": (2.0, 8.0),
    "旗舰档": (15.0, 60.0),
}


def llm_cost(tier: str) -> float:
    pin, pout = TIERS[tier]
    return TOK_IN * pin / 1e6 + TOK_OUT * pout / 1e6


def meeting_cost(tier: str) -> float:
    """单次会议的可变成本（不含支付通道费）。"""
    asr = MEETING_MIN * ASR_PER_MIN
    storage = MEETING_MIN * AUDIO_MB_PER_MIN / 1024 * STORE_PER_GB
    return asr + storage + llm_cost(tier) + EMB_PER_MEETING


# ============================================================ 第 01 章
def fig01_four_gates() -> None:
    fig, ax = plt.subplots(figsize=(10.4, 5.2))
    blank(ax, (0, 10.4), (0, 5.6))

    rows = [
        ("① 有人愿意付", "能说出「谁、在什么场景、为了省掉什么」愿意掏钱",
         "朋友都说好，但没人问「多少钱」"),
        ("② 有可计价的单位", "能把它切成一个可重复计费的单元（次/月/席位）",
         "只能按「项目」报价，每单都要重新谈"),
        ("③ 交付得出去", "用户自己就能完成，不需要你在旁边操作",
         "每个新用户都要你陪着跑一遍"),
        ("④ 担得起责任", "出事时你知道该退钱、该告知、该停机",
         "用户问「数据会不会泄露」，你答不上来"),
    ]

    ax.text(0.35, 5.16, "门", fontsize=9.5, color=MUTED)
    ax.text(2.95, 5.16, "通过条件（缺了这一条，门就是关的）", fontsize=9.5, color=MUTED)
    ax.text(7.35, 5.16, "卡住时的典型症状", fontsize=9.5, color=MUTED)
    ax.plot([0.35, 10.05], [5.02, 5.02], color="#CBD2D9", linewidth=1.0)

    for i, (name, cond, symptom) in enumerate(rows):
        y = 4.26 - i * 1.06
        ax.add_patch(FancyBboxPatch((0.35, y - 0.34), 9.7, 0.82,
                                    boxstyle="round,pad=0.008,rounding_size=0.03",
                                    facecolor=PAPER, edgecolor="#DCE2E8", linewidth=1.0))
        ax.text(0.62, y + 0.07, name, fontsize=12, fontweight="bold", color=INK, va="center")
        ax.text(2.95, y + 0.07, cond, fontsize=9.6, color="#3E4C59", va="center")
        ax.text(7.35, y + 0.07, symptom, fontsize=9.6, color=BAD, va="center")

    ax.annotate("", xy=(0.35, 0.22), xytext=(0.35, 0.62),
                arrowprops=dict(arrowstyle="-|>", color=INK, linewidth=1.6))
    ax.text(0.52, 0.42, "四门全过才叫验证；任何一门未测，都只能算「能跑」。",
            fontsize=10, color=INK, va="center")

    ax.set_title("收钱的四道门：它们不是难度递增的四关，而是四个独立的开关",
                 fontsize=14.5, fontweight="bold", loc="left", pad=14)
    stamp(fig, "结构示意：门的划分与症状来自作者对独立产品上线失败的归纳，不是统计结果。")
    save(fig, "ch01/fig-01-four-gates.png")


def fig01_evidence_strength() -> None:
    points = [
        ("朋友口头称赞", 0.2, 1.0),
        ("Demo 现场演示", 0.4, 1.3),
        ("免费注册人数", 3.0, 1.8),
        ("留邮箱的意向名单", 7.0, 2.5),
        ("预付定金", 14.0, 3.5),
        ("第一笔真实付款", 20.0, 4.6),
        ("第二个月仍然续费", 30.0, 5.0),
    ]

    fig, ax = plt.subplots(figsize=(9.6, 4.9))
    ax.axhspan(0.6, 2.6, color=BAD, alpha=0.05, zorder=0)
    ax.axhspan(3.2, 5.4, color=GOOD, alpha=0.06, zorder=0)

    for label, x, y in points:
        strong = y >= 3.2
        ax.scatter([x], [y], s=110, color=GOOD if strong else BAD,
                   edgecolor="white", linewidth=1.6, zorder=3)
        ax.annotate(label, (x, y), xytext=(9, 0), textcoords="offset points",
                    fontsize=9.6, va="center",
                    color=GOOD if strong else BAD, fontweight="bold" if strong else "normal")

    ax.set_xscale("log")
    ax.set_xlim(0.13, 260)
    ax.set_ylim(0.6, 5.5)
    ax.set_yticks([])
    ax.set_xlabel("拿到这个证据要花的时间（天，对数轴）", fontsize=10.2)
    ax.text(0.16, 5.14, "证据强度高", fontsize=10, color=GOOD, fontweight="bold")
    ax.text(250, 0.86, "下半区只能证明「不讨厌」，不能证明「要买」", fontsize=9.6,
            color=BAD, ha="right")

    clean_axes(ax, "x")
    ax.set_title("验证动作的性价比：越靠右下，越省钱也越没用",
                 fontsize=14.2, fontweight="bold", loc="left", pad=14)
    stamp(fig, "作者判断（非实测）：纵轴为证据强度评分，横轴为完成该动作的典型耗时；"
               "位置用于比较排序，不代表任何测量值。")
    save(fig, "ch01/fig-02-evidence-strength.png")


# ============================================================ 第 02 章
def fig02_waterfall() -> None:
    costs = [
        90 * MEETING_MIN * ASR_PER_MIN,
        90 * llm_cost("标准档"),
        90 * MEETING_MIN * AUDIO_MB_PER_MIN / 1024 * STORE_PER_GB,
        PRICE * PAY_RATE,
        90 * EMB_PER_MEETING,
    ]
    labels = ["订阅收入", "语音转写", "模型调用", "对象存储", "支付通道", "向量检索", "贡献毛利"]

    bottoms, heights, colors, tops = [], [], [], []
    level = PRICE
    # 第一根：收入
    bottoms.append(0.0)
    heights.append(PRICE)
    colors.append(STEEL)
    tops.append(PRICE)
    # 中间五根：成本
    for c in costs:
        bottoms.append(level - c)
        heights.append(c)
        colors.append(BAD)
        level -= c
        tops.append(level)
    # 最后一根：贡献毛利
    bottoms.append(0.0)
    heights.append(level)
    colors.append(GOOD)
    tops.append(level)

    values = [PRICE] + [-c for c in costs] + [level]

    fig, ax = plt.subplots(figsize=(9.8, 4.9))
    x = np.arange(len(labels))
    ax.bar(x, heights, bottom=bottoms, color=colors, width=0.56,
           edgecolor="none", zorder=3)

    for i, (b, h, v) in enumerate(zip(bottoms, heights, values)):
        if i in (0, len(labels) - 1):
            txt = f"¥{v:.2f}"
        else:
            txt = f"-{h:.2f}"
        ax.text(i, b + h + 0.9, txt, ha="center", fontsize=10.5,
                color=colors[i], fontweight="bold")

    # 连接线：让瀑布的"接续"关系看得见
    for i in range(len(labels) - 1):
        y = tops[i]
        ax.plot([i + 0.28, i + 0.72], [y, y], color="#B8C1CC",
                linewidth=1.0, linestyle=":", zorder=2)

    ax.axhline(0, color=INK, linewidth=1.0)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.8)
    ax.set_ylabel("元 / 用户 / 月", fontsize=10.2)
    ax.set_ylim(0, 46)
    clean_axes(ax, "y")

    ax.annotate(f"毛利率 {level / PRICE * 100:.1f}%\n"
                f"覆盖 ¥{FIXED_COST:.0f} 固定成本需 {np.ceil(FIXED_COST / level):.0f} 个付费用户",
                xy=(6, level), xytext=(3.55, 35.0), fontsize=9.6, color=GOOD,
                arrowprops=dict(arrowstyle="-|>", color=GOOD, linewidth=1.1,
                                connectionstyle="arc3,rad=-0.2"))

    ax.set_title(f"一个重度用户的月度账本：39 元收入，最后剩下 {level:.2f} 元",
                 fontsize=14.2, fontweight="bold", loc="left", pad=14)
    stamp(fig, "实测算法（假设值代入）：订阅 39 元/月、90 次会议、单次 50 分钟、"
               "转写 0.002 元/分钟、标准档模型 2/8 元每百万 token。单价为 2026-10 快照，以你签约为准。")
    save(fig, "ch02/fig-03-cost-waterfall.png")


def fig02_margin_curve() -> None:
    n = np.arange(1, 301)
    fig, ax = plt.subplots(figsize=(9.8, 4.9))

    colors = {"经济档": "#8FB8C9", "标准档": STEEL, "旗舰档": BAD}
    for tier in ("经济档", "标准档", "旗舰档"):
        cost = n * meeting_cost(tier) + PRICE * PAY_RATE
        margin = (PRICE - cost) / PRICE * 100
        be = (PRICE - PRICE * PAY_RATE) / meeting_cost(tier)
        ax.plot(n, margin, color=colors[tier], linewidth=2.2,
                label=f"{tier}（平衡 {be:.0f} 次/月）")
        ax.scatter([be], [0], color=colors[tier], s=46, zorder=4, edgecolor="white")


    ax.axhline(0, color=INK, linewidth=1.2)
    ax.axvline(30, color=MUTED, linewidth=1.0, linestyle="--")
    ax.axvline(90, color=MUTED, linewidth=1.0, linestyle="--")
    ax.text(29, -41, "典型用户\n30 次", fontsize=8.2, color=MUTED, ha="right",
            va="bottom", linespacing=1.35)
    ax.text(89, -41, "重度用户\n90 次", fontsize=8.2, color=MUTED, ha="right",
            va="bottom", linespacing=1.35)

    ax.set_xlabel("每月会议次数", fontsize=10.2)
    ax.set_ylabel("毛利率（%）", fontsize=10.2)
    ax.set_xlim(0, 300)
    ax.set_ylim(-45, 72)
    ax.legend(loc="upper right", fontsize=9.4)
    clean_axes(ax, "y")

    ax.annotate("同一功能，只换模型档位：\n这条线在 90 次时已经亏了",
                xy=(88, -22), xytext=(118, -39), fontsize=9.2, color=BAD,
                arrowprops=dict(arrowstyle="-|>", color=BAD, linewidth=1.1,
                                connectionstyle="arc3,rad=0.25"))

    ax.set_title("毛利率不是定价决定的，是「单价 × 用量 × 模型档位」三个数一起决定的",
                 fontsize=13.6, fontweight="bold", loc="left", pad=14)
    stamp(fig, "实测算法（假设值代入）：三档模型输入/输出单价分别为 0.8/2、2/8、15/60 元每百万 token；"
               "其余成本见 code/_figstyle.py 常量区。")
    save(fig, "ch02/fig-04-margin-curve.png")


# ============================================================ 第 03 章
def fig03_scope_quadrant() -> None:
    features = [
        ("录音上传与转写", 7.2, 9.4, -9, 4, "right"),
        ("结构化纪要生成", 8.8, 9.5, 0, -15, "center"),
        ("行动项提取", 6.0, 8.6, 7, 5, "left"),
        ("导出 Word / PDF", 2.6, 7.8, 7, 5, "left"),
        ("订阅与支付", 3.2, 9.2, 7, 5, "left"),
        ("说话人分离", 6.8, 6.2, 7, 5, "left"),
        ("自定义模板", 5.4, 5.6, 7, 5, "left"),
        ("团队共享空间", 8.8, 5.0, 7, 5, "left"),
        ("移动端 App", 9.2, 3.4, -9, -4, "right"),
        ("日历自动入会", 6.2, 3.2, 7, 5, "left"),
        ("多语言界面", 4.4, 2.6, 7, 5, "left"),
        ("情绪与语气分析", 7.6, 1.4, 7, 5, "left"),
    ]

    fig, ax = plt.subplots(figsize=(9.4, 5.4))
    ax.axvspan(0, 5, ymin=0.5, ymax=1.0, color=GOOD, alpha=0.07, zorder=0)
    ax.axvspan(5, 10, ymin=0.0, ymax=0.5, color=MUTED, alpha=0.06, zorder=0)

    ax.axvline(5, color="#B8C1CC", linewidth=1.0, linestyle="--")
    ax.axhline(5, color="#B8C1CC", linewidth=1.0, linestyle="--")

    for name, x, y, dx, dy, ha in features:
        first = x < 5 and y > 5
        ax.scatter([x], [y], s=90, color=GOOD if first else MUTED,
                   edgecolor="white", linewidth=1.4, zorder=3)
        ax.annotate(name, (x, y), xytext=(dx, dy), textcoords="offset points",
                    fontsize=8.8, color=INK if first else "#52606D", ha=ha)

    quad = dict(fontsize=9.6, fontweight="bold",
                bbox=dict(facecolor="white", edgecolor="none", pad=2.0, alpha=0.92))
    ax.text(0.35, 5.22, "先做：撑起付费闭环", color=GOOD, **quad)
    ax.text(5.25, 5.22, "想清楚再做：贵，但值不值要算", color=MUTED, **quad)
    ax.text(0.35, 0.62, "顺手就做：便宜且加分", color=GOOD, **quad)
    ax.text(5.25, 0.62, "这一版不做", color=MUTED, **quad)

    ax.set_xlabel("实现成本（含持续的维护成本）  →", fontsize=10.2)
    ax.set_ylabel("对「能收钱」的贡献  →", fontsize=10.2)
    ax.set_xlim(0.2, 10.4)
    ax.set_ylim(0, 10)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    ax.set_title("把需求池摊在两张尺子上：贵不贵，和有没有用，是两件事",
                 fontsize=14.2, fontweight="bold", loc="left", pad=14)
    stamp(fig, "作者评分（结构示意）：两轴为 0-10 的主观打分，用于排序而非测量；"
               "换成你自己的项目时请重新打分，不要照搬位置。")
    save(fig, "ch03/fig-06-scope-quadrant.png")


def fig03_paid_loop() -> None:
    fig, ax = plt.subplots(figsize=(9.6, 5.0))
    blank(ax, (0, 9.6), (0, 5.4))

    nodes = [
        ("看见价值", "3 分钟内看懂\n自己能省什么", 3.55, 4.28),
        ("完成支付", "一步到位\n不要求先注册", 6.45, 2.62),
        ("拿到结果", "失败可见\n可重试", 3.55, 0.96),
        ("出事能找到人", "退款 / 支持\n有明确入口", 0.55, 2.62),
    ]
    w, h = 2.55, 0.92
    for title, desc, x, y in nodes:
        box(ax, x, y, w, h, "", fc=PAPER, ec=STEEL)
        ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="center",
                fontsize=11.5, fontweight="bold", color=INK)
        ax.text(x + w / 2, y + 0.28, desc, ha="center", va="center",
                fontsize=8.8, color="#52606D", linespacing=1.4)

    ax.add_patch(Circle((4.8, 2.72), 0.62, facecolor=INK, edgecolor="none", zorder=4))
    ax.text(4.8, 2.72, "付费\n闭环", ha="center", va="center", fontsize=9.6,
            color="white", fontweight="bold", zorder=5, linespacing=1.3)

    arrow(ax, (5.55, 5.02), (7.85, 3.86), color=STEEL, lw=1.8, rad=-0.28)
    arrow(ax, (7.95, 2.44), (6.25, 1.32), color=STEEL, lw=1.8, rad=-0.28)
    arrow(ax, (3.42, 1.40), (1.92, 2.50), color=STEEL, lw=1.8, rad=-0.28)
    arrow(ax, (1.98, 3.62), (3.40, 4.66), color=STEEL, lw=1.8, rad=-0.28)

    ax.text(8.05, 4.62, "断这里：\n注册了但没付", fontsize=9, color=BAD, ha="center", linespacing=1.4)
    ax.text(8.05, 1.06, "断这里：\n付了但拿不到结果", fontsize=9, color=BAD, ha="center", linespacing=1.4)
    ax.text(1.35, 1.02, "断这里：\n出事没人管，口碑归零", fontsize=9, color=BAD, ha="center", linespacing=1.4)
    ax.text(1.30, 4.66, "断这里：\n看不懂，直接关掉", fontsize=9, color=BAD, ha="center", linespacing=1.4)

    ax.text(0.25, 0.30,
            "四个环里最短的那一段决定上限。补最长的环不会让水变多，只会让你更累。",
            fontsize=9.8, color=INK)

    ax.set_title("付费闭环的四个环：MVP 的任务不是「功能多」，是「环不断」",
                 fontsize=14.2, fontweight="bold", loc="left", pad=12)
    stamp(fig, "结构示意：环的划分用于诊断断点，不含任何时间或转化率数据。")
    save(fig, "ch03/fig-05-paid-loop.png")


# ============================================================ 第 04 章
def fig04_expand_contract() -> None:
    fig, ax = plt.subplots(figsize=(10.4, 5.0))
    blank(ax, (0, 10.4), (0, 5.4))

    cols = [
        ("R1", "加列 + 双写", "写入：旧列 + 新列\n读取：旧列\n回滚：直接回退", GOOD),
        ("R2", "回填历史", "写入：旧列 + 新列\n读取：旧列\n回滚：仍安全", GOOD),
        ("R3", "切读新列", "写入：旧列 + 新列\n读取：新列\n回滚：改读旧列", GOOD),
        ("R4", "停双写 + 删旧列", "写入：新列\n读取：新列\n回滚：不可逆", BAD),
    ]

    w, gap = 2.28, 0.22
    for i, (tag, title, body, color) in enumerate(cols):
        x = 0.32 + i * (w + gap)
        ax.add_patch(FancyBboxPatch((x, 2.08), w, 2.62,
                                    boxstyle="round,pad=0.012,rounding_size=0.03",
                                    facecolor="white", edgecolor=color, linewidth=1.5))
        ax.add_patch(Rectangle((x, 4.02), w, 0.68, facecolor=color, edgecolor="none", zorder=3))
        ax.text(x + w / 2, 4.36, tag, ha="center", va="center", fontsize=11.5,
                color="white", fontweight="bold", zorder=4)
        ax.text(x + w / 2, 3.70, title, ha="center", va="center", fontsize=9.8,
                color=INK, fontweight="bold")
        ax.text(x + 0.18, 3.34, body, ha="left", va="top", fontsize=8.8,
                color="#3E4C59", linespacing=1.55)

        if i < 3:
            arrow(ax, (x + w + 0.02, 3.36), (x + w + gap - 0.02, 3.36),
                  color="#8A94A6", lw=1.4, scale=11)

    ax.add_patch(Rectangle((0.32, 1.45), 3 * (w + gap) - gap, 0.36,
                           facecolor=GOOD, alpha=0.14, edgecolor="none"))
    ax.text(0.32 + (3 * (w + gap) - gap) / 2, 1.63,
            "这三次发布之间，任何一次都能在分钟级退回上一版",
            ha="center", va="center", fontsize=9.4, color="#1B6B62")
    ax.add_patch(Rectangle((0.32 + 3 * (w + gap), 1.45), w, 0.36,
                           facecolor=BAD, alpha=0.14, edgecolor="none"))
    ax.text(0.32 + 3 * (w + gap) + w / 2, 1.63, "删掉旧列之后\n没有退路",
            ha="center", va="center", fontsize=8.8, color=BAD, linespacing=1.3)

    ax.text(0.32, 1.02,
            "关键不在「分四次发」，而在每一步的读写都同时兼容新旧两种状态——"
            "这样回滚才只需要改代码，不需要改数据。",
            fontsize=9.6, color=INK)
    ax.text(0.32, 0.62,
            "把四步压成一次发布，等于把「分钟级回滚」换成「祈祷它别出错」。",
            fontsize=9.6, color=BAD)

    ax.set_title("expand-contract：让数据库迁移也变成可回滚的操作",
                 fontsize=14.2, fontweight="bold", loc="left", pad=12)
    stamp(fig, "结构示意：四个发布批次为本书推荐的最小拆分，实际批次数可按变更规模增减。")
    save(fig, "ch04/fig-08-expand-contract.png")


def fig04_rollback_layers() -> None:
    items = [
        ("代码回滚", 30, GOOD, "重新部署上一版镜像"),
        ("配置回滚", 120, GOOD, "特性开关 / 环境变量"),
        ("数据恢复", 2700, SAND, "从备份还原，会丢中间写入"),
        ("已删列 / 已改类型", 300000, BAD, "没有回滚路径，只能向前修"),
    ]

    fig, ax = plt.subplots(figsize=(9.8, 4.4))
    y = np.arange(len(items))[::-1]
    for yi, (name, sec, color, desc) in zip(y, items):
        ax.barh(yi, sec, height=0.44, color=color, edgecolor="none", zorder=3)
        label = ("不可逆" if sec >= 300000
                 else f"{sec / 60:.0f} 分钟" if sec >= 60 else f"{sec} 秒")
        ax.text(sec * 1.15, yi, label, va="center", fontsize=10.2,
                color=color, fontweight="bold")
        ax.text(12, yi - 0.36, desc, va="center", fontsize=8.6, color=MUTED)

    ax.set_yticks(y)
    ax.set_yticklabels([i[0] for i in items], fontsize=11)
    ax.set_xscale("log")
    ax.set_xlim(10, 3e6)
    ax.set_xlabel("回到上一个可用状态所需时间（秒，对数轴）", fontsize=10.2)
    ax.set_ylim(-0.95, 3.55)
    clean_axes(ax, "x")

    ax.axvspan(2e5, 3e6, color=BAD, alpha=0.06, zorder=0)
    ax.text(2.05e5, 2.66, "这一格没有回滚\n只有「向前修复」", fontsize=9, color=BAD,
            linespacing=1.4, ha="left", va="center")

    ax.set_title("回滚不是一件事，是三层；每往下一层，时间就多一个数量级",
                 fontsize=14.2, fontweight="bold", loc="left", pad=14)
    stamp(fig, "量级示意：秒/分钟取自常规部署与配置系统的典型操作耗时，"
               "45 分钟取自第 06 章的演练记录；实际值以你自己的演练为准。")
    save(fig, "ch04/fig-07-rollback-layers.png")


# ============================================================ 第 05 章
SLO = 0.995
BUDGET_MIN = (1 - SLO) * 30 * 24 * 60      # 30 天窗口下的错误预算（分钟）


def fig05_burn_rate() -> None:
    hours = np.linspace(0, 72, 400)
    rates = [(1, "1×：刚好贴着 SLO 走", "#8FB8C9"),
             (6, "6×：慢性泄漏", SAND),
             (14.4, "14.4×：需要当天处理", BAD),
             (60, "60×：全站不可用", "#7A2E12")]

    fig, ax = plt.subplots(figsize=(9.8, 4.7))
    for r, label, color in rates:
        used = r * hours / (30 * 24) * 100
        ax.plot(hours, np.clip(100 - used, 0, 100), color=color, linewidth=2.2, label=label)

    ax.axhline(0, color=INK, linewidth=1.0)
    ax.set_xlabel("事故持续时长（小时）", fontsize=10.2)
    ax.set_ylabel("30 天错误预算剩余（%）", fontsize=10.2)
    ax.set_xlim(0, 72)
    ax.set_ylim(-3, 104)
    ax.legend(loc="upper right", fontsize=9.2)
    clean_axes(ax, "y")

    ax.annotate("全站挂 12 小时\n= 烧掉一整个月的预算",
                xy=(12, 0), xytext=(15.5, 26), fontsize=9.4, color="#7A2E12",
                arrowprops=dict(arrowstyle="-|>", color="#7A2E12", linewidth=1.1,
                                connectionstyle="arc3,rad=0.25"))
    ax.text(34, 5, f"预算总量 = {(1 - SLO) * 100:.1f}% × 30 天 = {BUDGET_MIN:.0f} 分钟",
            fontsize=9.2, color=MUTED)

    ax.set_title("错误预算把「稳不稳」变成一道除法：烧得多快，决定你多急",
                 fontsize=14.2, fontweight="bold", loc="left", pad=14)
    stamp(fig, "实测算法：SLO = 99.5%、30 天窗口；曲线为消耗速率的线性推演，不含自动恢复。")
    save(fig, "ch05/fig-09-burn-rate.png")


def fig05_budget_stairs() -> None:
    # 情景推演：一个月里的四次故障，逐次累计消耗预算
    events = [
        (3.0, 20 / 60, 60, "D3 全站不可用 20 分钟"),
        (11.0, 1.5, 40, "D11 转写队列积压，20% 请求失败 90 分钟"),
        (18.0, 0.75, 60, "D18 登录故障 45 分钟"),
        (26.0, 4.0, 20, "D26 单模型降级，10% 请求失败 4 小时"),
    ]

    fig, ax = plt.subplots(figsize=(9.8, 4.6))
    used, t_prev = 0.0, 0.0
    for day, dur, rate, label in events:
        ax.plot([t_prev, day], [used, used], color=STEEL, linewidth=2.0)
        delta = rate * dur / (30 * 24) * 100
        used += delta
        ax.plot([day, day], [used - delta, used], color=BAD, linewidth=2.0)
        ax.scatter([day], [used], color=BAD, s=30, zorder=4)
        ax.annotate(f"D{day:.0f}　+{delta:.1f}%", (day, used), xytext=(0, 7),
                    textcoords="offset points", fontsize=8.8, color=BAD,
                    fontweight="bold", ha="center")
        t_prev = day

    ax.plot([t_prev, 30], [used, used], color=STEEL, linewidth=2.0)
    ax.axhline(100, color=BAD, linewidth=1.2, linestyle="--")
    ax.text(0.4, 101.5, "预算耗尽线：到这里之后，任何新故障都必须冻结发布", fontsize=8.8, color=BAD)

    ax.set_xlim(0, 30)
    ax.set_ylim(0, 116)
    ax.set_xlabel("当月日期", fontsize=10.2)
    ax.set_ylabel("累计消耗的错误预算（%）", fontsize=10.2)
    clean_axes(ax, "y")

    ax.set_title(f"四次小故障加起来 {used:.1f}%：真正的风险不是单次事故，是它一直在来",
                 fontsize=13.6, fontweight="bold", loc="left", pad=14)
    stamp(fig, "情景推演（非实测）：故障时长与失败比例为设定值，消耗量按 burn rate 公式计算；"
               "可用于你自己的月度复盘表。")
    save(fig, "ch05/fig-10-budget-stairs.png")


# ============================================================ 第 06 章
def fig06_rto_rpo() -> None:
    fig, ax = plt.subplots(figsize=(10.2, 4.5))
    blank(ax, (0, 10.2), (0, 4.9))

    y = 2.65
    ax.plot([0.6, 9.7], [y, y], color="#CBD2D9", linewidth=2.2, zorder=1)

    marks = [
        (1.2, "03:00\n最后一次可用备份", GOOD),
        (5.4, "14:02\n故障发生", BAD),
        (8.3, "15:31\n恢复完成", GOOD),
    ]
    for x, label, color in marks:
        ax.plot([x, x], [y - 0.16, y + 0.16], color=color, linewidth=2.6, zorder=3)
        ax.scatter([x], [y], s=70, color=color, edgecolor="white", linewidth=1.5, zorder=4)
        ax.text(x, y + 0.34, label, ha="center", va="bottom", fontsize=9.0,
                color=color, linespacing=1.45)

    # 中间两个未标注刻度：发现与决定
    for x in (5.78, 6.06):
        ax.plot([x, x], [y - 0.10, y + 0.10], color=SAND, linewidth=2.0, zorder=3)
    ax.annotate("", xy=(6.06, y + 0.86), xytext=(5.78, y + 0.86),
                arrowprops=dict(arrowstyle="<->", color=SAND, linewidth=1.3))
    ax.text(5.62, y + 0.86, "发现 14:07 → 决定 14:09", fontsize=8.4, color="#A67C00",
            va="center", ha="right")

    # RPO
    ax.annotate("", xy=(5.4, y - 0.52), xytext=(1.2, y - 0.52),
                arrowprops=dict(arrowstyle="<->", color=BAD, linewidth=1.5))
    ax.text(3.3, y - 0.70, "RPO = 11 小时 02 分（这段时间的写入，全部丢失）",
            ha="center", va="top", fontsize=9.6, color=BAD, fontweight="bold")

    # RTO
    ax.annotate("", xy=(8.3, y + 1.42), xytext=(5.4, y + 1.42),
                arrowprops=dict(arrowstyle="<->", color=STEEL, linewidth=1.5))
    ax.text(6.85, y + 1.54, "RTO = 89 分钟（从故障到可用）",
            ha="center", va="bottom", fontsize=9.6, color=STEEL, fontweight="bold")

    ax.text(0.6, 0.62,
            "「发现 + 决定」这 7 分钟靠告警和预案，不靠运气；多数团队只优化了最后一段「恢复」。",
            fontsize=9.2, color=MUTED, va="top")
    ax.text(0.6, 0.30,
            "RPO 由备份频率决定，RTO 由「发现 + 决策 + 恢复」三者相加决定。",
            fontsize=9.8, color=INK, va="top")

    ax.set_title("一次删库演练的时间轴：RTO 和 RPO 不是形容词，是两个可以量出来的数",
                 fontsize=13.8, fontweight="bold", loc="left", pad=10)
    stamp(fig, "实测结构（值取自第 06 章演练记录）：日备一次、恢复耗时 82 分钟；你自己的数字会不同。")
    save(fig, "ch06/fig-11-rto-rpo.png")


def fig06_downgrade() -> None:
    strategies = [
        ("排队重试", 3.0, 4.2, "上游超时但用户能等"),
        ("降级到小模型", 5.4, 2.2, "质量可降，结果仍要给"),
        ("兜底文案 + 标记", 2.0, 6.6, "宁可不答，也不能答错"),
        ("明确失败 + 退款", 1.2, 8.6, "涉及钱或责任"),
    ]

    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    ax.axvline(4.5, color="#B8C1CC", linewidth=1.0, linestyle="--")
    ax.axhline(5.0, color="#B8C1CC", linewidth=1.0, linestyle="--")

    for name, x, y, cond in strategies:
        ax.scatter([x], [y], s=130, color=STEEL, edgecolor="white", linewidth=1.6, zorder=4)
        ax.annotate(f"{name}\n{cond}", (x, y), xytext=(10, -4),
                    textcoords="offset points", fontsize=9.2, color=INK, linespacing=1.5)

    ax.text(0.3, 9.5, "体验代价高", fontsize=9.4, color=MUTED)
    ax.text(0.3, 0.4, "体验代价低", fontsize=9.4, color=MUTED)
    ax.text(7.3, 0.4, "实现成本高 →", fontsize=9.4, color=MUTED, ha="right")

    ax.set_xlim(0, 7.6)
    ax.set_ylim(0, 10)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    ax.set_title("上游挂了，四种降级方式：先问「这次请求允不允许答错」",
                 fontsize=14.0, fontweight="bold", loc="left", pad=14)
    stamp(fig, "作者判断（非实测）：两轴为主观评分，用于选型讨论；实际选择应以你的责任边界为准。")
    save(fig, "ch06/fig-12-downgrade.png")


# ============================================================ 第 07 章
def fig07_gates() -> None:
    base = 1000 * meeting_cost("标准档")     # 1000 次请求的标准档成本
    stages = [
        ("基线：1000 次请求", base, 1.00, STEEL),
        ("① 输入裁剪 -35%", base * 0.65, 0.65, "#5B8C9E"),
        ("② 缓存命中 22%", base * 0.65 * 0.78, 0.51, "#8FB8C9"),
        ("③ 简单任务路由 -28%", base * 0.65 * 0.78 * 0.72, 0.36, GOOD),
    ]

    fig, ax = plt.subplots(figsize=(9.6, 4.6))
    y = np.arange(len(stages))[::-1]
    for yi, (name, val, frac, color) in zip(y, stages):
        ax.barh(yi, val, height=0.5, color=color, edgecolor="none", zorder=3)
        ax.text(val + 4, yi, f"¥{val:.1f}", va="center", fontsize=10.5,
                color=color, fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels([s[0] for s in stages], fontsize=10.2)
    ax.set_xlabel("1000 次请求的模型成本（元）", fontsize=10.2)
    ax.set_xlim(0, base * 1.12)
    clean_axes(ax, "x")

    ax.set_title(f"成本四道闸：前三道把均值从 ¥{base:.0f} 压到 ¥{stages[-1][1]:.0f}"
                 f"（-{100 * (1 - stages[-1][2]):.0f}%），第四道改的是方差",
                 fontsize=13.4, fontweight="bold", loc="left", pad=14)

    stamp(fig, "实测算法（假设值代入）：单次请求标准档 ¥0.163；裁剪比例按经验区间设定，换你的场景需重新标定。"
               "第四道闸不在这张图里：它不改均值，只截断尾部——而那 1% 的尾部常占三成账单。")
    save(fig, "ch07/fig-13-cost-gates.png")


def fig07_guard() -> None:
    hours = np.arange(0, 25)
    spend = np.full_like(hours, 8.0, dtype=float)
    spend[14:] = 60.0
    cumulative = np.minimum(np.cumsum(spend), 300.0)
    budget = 300.0

    fig, ax = plt.subplots(figsize=(9.6, 4.6))
    ax.plot(hours, cumulative, color=STEEL, linewidth=2.4, marker="o",
            markersize=3.4, label="累计花费")
    ax.axhline(budget, color=BAD, linewidth=1.4, linestyle="--")
    ax.text(0.3, budget + 8, "日预算上限 ¥300", fontsize=9.4, color=BAD)
    ax.axhline(budget * 0.8, color=SAND, linewidth=1.2, linestyle=":")
    ax.text(0.3, budget * 0.8 + 8, "80% 预警线", fontsize=9.0, color="#A67C00")

    hit = int(np.argmax(cumulative >= budget))
    ax.scatter([hours[hit]], [budget], s=90, color=BAD, zorder=5, edgecolor="white")
    ax.annotate("熔断生效：拒绝新请求，保留进行中的",
                xy=(hours[hit], budget), xytext=(4.2, 236),
                fontsize=9.2, color=BAD,
                arrowprops=dict(arrowstyle="-|>", color=BAD, linewidth=1.1,
                                connectionstyle="arc3,rad=0.25"))

    ax.set_xlabel("当日小时", fontsize=10.2)
    ax.set_ylabel("累计花费（元）", fontsize=10.2)
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 430)
    ax.legend(loc="upper left", fontsize=9.4)
    clean_axes(ax, "y")

    ax.set_title("预算熔断不是「省钱」，是把一次无限额的意外变成一次有上限的故障",
                 fontsize=13.8, fontweight="bold", loc="left", pad=14)
    stamp(fig, "仿真（非实测）：前 14 小时 ¥8/小时，第 14 小时起出现死循环导致 ¥60/小时；"
               "熔断在累计达到日预算时触发。")
    save(fig, "ch07/fig-14-budget-guard.png")


# ============================================================ 第 08 章
def fig08_ai_act_timeline() -> None:
    milestones = [
        (0, "2024-08-01", "法案生效", "分级框架确立，义务尚未适用", STEEL),
        (12, "2025-08-02", "通用模型（GPAI）义务", "模型提供方开始承担文档与治理义务", STEEL),
        (24, "2026-08-02", "透明度 + GPAI 可强制执行", "", BAD),
        (28, "2026-12-02", "标识宽限到期 + 新增禁令", "既有系统须完成机器可读标识", BAD),
        (40, "2027-12-02", "附件三高风险系统", "招聘、信用、教育、执法辅助等场景", MUTED),
        (48, "2028-08-02", "附件一嵌入型高风险", "医疗器械、机械等受监管产品内的 AI", MUTED),
    ]

    fig, ax = plt.subplots(figsize=(9.8, 5.4))
    blank(ax, (0, 9.8), (0, 6.2))

    top, bottom = 5.55, 0.62
    span = milestones[-1][0]
    def ypos(m: float) -> float:
        return top - (m / span) * (top - bottom)

    ax.plot([2.05, 2.05], [bottom, top], color="#CBD2D9", linewidth=2.0, zorder=1)

    today = 26
    ax.plot([1.86, 2.24], [ypos(today)] * 2, color=GOOD, linewidth=2.2, zorder=3)
    ax.text(1.72, ypos(today), "今天\n2026-10", ha="right", va="center", fontsize=8.6,
            color=GOOD, linespacing=1.35, fontweight="bold")

    for m, date, title, desc, color in milestones:
        y = ypos(m)
        ax.scatter([2.05], [y], s=86, color=color, edgecolor="white", linewidth=1.8, zorder=4)
        ax.text(2.34, y + 0.16, f"{date}　{title}", fontsize=10.4, color=color,
                fontweight="bold", va="center")
        if desc:
            ax.text(2.34, y - 0.14, desc, fontsize=8.8, color="#52606D", va="center")


    ax.annotate("", xy=(2.05, ypos(24)), xytext=(2.05, ypos(40)),
                arrowprops=dict(arrowstyle="<->", color=GOOD, linewidth=1.2, linestyle="--"))
    ax.text(1.72, (ypos(24) + ypos(40)) / 2, "16 个月\n缓冲", ha="right", va="center",
            fontsize=8.6, color=GOOD, linespacing=1.35)

    ax.text(0.12, 0.02,
            "多数独立产品在这两道之间：透明度要做，技术文档可以排到 2027。把 2027 的活提前干，"
            "和把 2026 的活漏掉，是同一种错误。",
            fontsize=9.0, color=BAD, va="bottom")

    ax.set_title("EU AI Act 的真实时间表：延期的是高风险文档，不是透明度",
                 fontsize=14.0, fontweight="bold", loc="left", pad=12)
    stamp(fig, "条文（截至 2026-10 快照）：Regulation (EU) 2024/1689 经 Digital Omnibus 修订后的适用节点；"
               "详见第 08 章表 8-1。非法律意见。")
    save(fig, "ch08/fig-16-ai-act-timeline.png")


def fig08_obligation_matrix() -> None:
    tiers = ["禁止类", "高风险", "有限风险", "最小风险"]
    duties = ["风险管理\n体系", "技术文档\n与记录", "人类\n监督", "透明度\n告知", "内容\n标识", "登记 /\n公示"]
    # 2 = 完整适用, 1 = 部分适用, 0 = 不适用
    grid = [
        [0, 0, 0, 0, 0, 0],
        [2, 2, 2, 2, 2, 1],
        [0, 0, 0, 2, 2, 1],
        [0, 0, 0, 0, 0, 0],
    ]

    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    for i, tier in enumerate(tiers):
        for j, duty in enumerate(duties):
            v = grid[i][j]
            if i == 0:
                face, txt, tc = "#F6E3DA", "禁止投放", BAD
            elif v == 2:
                face, txt, tc = STEEL, "●", "white"
            elif v == 1:
                face, txt, tc = "#8FB8C9", "○", "white"
            else:
                face, txt, tc = "#F4F5F6", "—", "#B8C1CC"
            ax.add_patch(Rectangle((j, 3 - i), 1, 1, facecolor=face, edgecolor="white", linewidth=2.4))
            ax.text(j + 0.5, 3 - i + 0.5, txt, ha="center", va="center",
                    fontsize=10.5, color=tc,
                    fontweight="bold" if i == 0 else "normal")

    ax.set_xlim(0, len(duties))
    ax.set_ylim(0, len(tiers))
    ax.set_xticks(np.arange(len(duties)) + 0.5)
    ax.set_xticklabels(duties, fontsize=9.2, linespacing=1.4)
    ax.set_yticks(np.arange(len(tiers)) + 0.5)
    ax.set_yticklabels(tiers[::-1], fontsize=10)
    ax.tick_params(length=0)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)

    ax.text(0.02, -0.86, "● 完整适用　○ 部分适用　— 不适用。"
                         "多数独立产品落在「有限风险」行：真正必须先做的只有后三列。",
            fontsize=9.0, color=MUTED)

    ax.set_title("按风险档拆义务：你要做的是「一行」，不是「一整列」",
                 fontsize=14.0, fontweight="bold", loc="left", pad=14)
    stamp(fig, "依据 Regulation (EU) 2024/1689 第 5、6、43、50、113 条整理（2026-10 快照）；"
               "本图为教学归纳，不构成法律意见。")
    save(fig, "ch08/fig-15-obligation-matrix.png")


# ============================================================ 第 09 章
def fig09_health_dashboard() -> None:
    weeks = np.arange(1, 9)
    panels = [
        ("首轮验收率（%）", [72, 74, 76, 75, 71, 66, 61, 58], GOOD, "越高越好"),
        ("返工率（%）", [18, 17, 16, 18, 22, 27, 31, 35], BAD, "越低越好"),
        ("门禁拦截（次/周）", [12, 11, 13, 14, 19, 24, 28, 33], STEEL, "突然变多＝改动越来越难一次通过"),
        ("单任务成本（元）", [6.2, 6.0, 6.1, 6.4, 7.3, 8.6, 9.9, 11.4], SAND, "含模型与人工返工"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(9.8, 5.6), sharex=True)
    for ax, (title, data, color, note) in zip(axes.flat, panels):
        ax.plot(weeks, data, color=color, linewidth=2.2, marker="o", markersize=4)
        ax.axvspan(4.5, 8.5, color=BAD, alpha=0.05, zorder=0)
        ax.set_title(title, fontsize=10.6, loc="left", pad=6)
        ax.text(0.03, 0.94, note, transform=ax.transAxes, fontsize=8.2,
                color=MUTED, va="top")
        ax.grid(color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)

    for ax in axes[1]:
        ax.set_xlabel("上线后第 N 周", fontsize=9.4)
    axes[0][0].text(4.6, 64.5, "拐点", fontsize=8.6, color=BAD)

    fig.suptitle("四个指标同时转向，才是信号；只有一项变差，通常只是噪声",
                 fontsize=14.0, fontweight="bold", x=0.012, ha="left", y=1.02)
    stamp(fig, "模拟数据（非实测）：形状取自常见的认知债累积模式，用于教学；"
               "你自己填数时请连续记录至少四周再判断趋势。")
    save(fig, "ch09/fig-17-health-dashboard.png")


def fig09_rewrite_score() -> None:
    criteria = [
        ("改动半径\n改一个需求要动几个文件", 4.2, 3.5),
        ("理解成本\n三个月后的你要多久能改", 4.5, 3.5),
        ("缺陷密度趋势\n连续四周是否上升", 3.8, 2.5),
        ("门禁通过率趋势\n补测试后是否仍下降", 2.2, 2.5),
    ]

    fig, ax = plt.subplots(figsize=(9.4, 4.0))
    y = np.arange(len(criteria))[::-1]
    for yi, (name, score, threshold) in zip(y, criteria):
        color = BAD if score > threshold else GOOD
        ax.barh(yi, score, height=0.44, color=color, alpha=0.85, edgecolor="none", zorder=3)
        ax.plot([threshold, threshold], [yi - 0.3, yi + 0.3], color=INK, linewidth=1.8, zorder=4)
        ax.text(score + 0.12, yi, f"{score:.1f}", va="center", fontsize=10.2,
                color=color, fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels([c[0] for c in criteria], fontsize=9.2, linespacing=1.4)
    ax.set_xlim(0, 5.4)
    ax.set_xlabel("评分（0—5，黑线为该判据的触发阈值）", fontsize=10.0)
    clean_axes(ax, "x")
    ax.text(0.15, -1.30, "三条越线 → 该谈重写；只有一条越线 → 先补那一条。",
            fontsize=9.4, color=INK)

    ax.set_title("重写判据打分卡：让「该不该推倒」变成四个可打分的题",
                 fontsize=13.8, fontweight="bold", loc="left", pad=14)
    stamp(fig, "评分为本书对贯穿案例的判断（非实测）：用于演示打分方式，阈值需按项目调整。")
    save(fig, "ch09/fig-18-rewrite-score.png")


# ============================================================ 第 10 章
def fig10_gantt() -> None:
    phases = [
        ("范围锁定 + 四门体检", 1, 3, STEEL),
        ("计价与单位经济", 4, 7, STEEL),
        ("上线工程：发布 / 监控 / 备份", 8, 13, "#5B8C9E"),
        ("三次演练：回滚 / 恢复 / 熔断", 14, 17, BAD),
        ("灰度放量与修文案", 18, 21, "#8FB8C9"),
        ("合规与对外材料", 22, 24, SAND),
        ("缓冲", 25, 27, "#9AA5B1"),
        ("公开上线", 28, 28, GOOD),
    ]

    fig, ax = plt.subplots(figsize=(10.2, 4.4))
    for i, (name, start, end, color) in enumerate(phases):
        y = len(phases) - i
        ax.barh(y, end - start + 0.8, left=start - 0.4, height=0.52,
                color=color, edgecolor="none", zorder=3)
        ax.text(end + 0.6, y, f"D{start}–D{end}" if start != end else f"D{start}",
                va="center", fontsize=8.8, color=color, fontweight="bold")

    ax.set_yticks([len(phases) - i for i in range(len(phases))])
    ax.set_yticklabels([p[0] for p in phases], fontsize=9.6)
    ax.set_xlim(0, 32)
    ax.set_xticks([1, 7, 14, 21, 28])
    ax.set_xticklabels(["D1", "D7", "D14", "D21", "D28"], fontsize=9.4)
    ax.set_xlabel("第 N 天", fontsize=10.0)
    clean_axes(ax, "x")
    for d in (14, 17, 28):
        ax.axvline(d, color="#DCE2E8", linewidth=1.0, linestyle=":", zorder=0)

    ax.set_title("28 天：演练排在灰度之前，灰度排在合规之前",
                 fontsize=14.0, fontweight="bold", loc="left", pad=14)
    stamp(fig, "排期模板（非实测）：假设每天可投入 4—6 小时；若为全职投入，可整体压缩约 1/3。")
    save(fig, "ch10/fig-19-gantt.png")


def fig10_cashflow() -> None:
    months = np.arange(0, 13)
    new_users, churn, fixed, capex = 6, 0.03, 120.0, 3000.0
    users, cash, series = 0.0, -capex, []
    for _ in months:
        users = users * (1 - churn) + new_users
        net = users * (PRICE - 15.1) - fixed
        cash += net
        series.append(cash)

    fig, ax = plt.subplots(figsize=(9.6, 4.4))
    ax.plot(months, series, color=STEEL, linewidth=2.4, marker="o", markersize=4)
    ax.axhline(0, color=INK, linewidth=1.2)
    ax.fill_between(months, series, 0, where=np.array(series) < 0, color=BAD, alpha=0.08)
    ax.fill_between(months, series, 0, where=np.array(series) >= 0, color=GOOD, alpha=0.10)

    be = next((m for m, v in zip(months, series) if v >= 0), None)
    if be is not None:
        ax.scatter([be], [0], s=90, color=GOOD, zorder=5, edgecolor="white", linewidth=1.6)
        ax.annotate(f"累计现金流转正：第 {be} 个月",
                    xy=(be, 0), xytext=(0.8, -600), fontsize=9.6, color=GOOD,
                    arrowprops=dict(arrowstyle="-|>", color=GOOD, linewidth=1.1,
                                    connectionstyle="arc3,rad=0.0"))

    ax.set_xlabel("上线后第 N 个月", fontsize=10.0)
    ax.set_ylabel("累计现金流（元）", fontsize=10.0)
    ax.set_xlim(0, 12)
    clean_axes(ax, "y")

    ax.set_title("回本点不是「第一个月赚钱」，是「累计现金流转正」",
                 fontsize=14.0, fontweight="bold", loc="left", pad=14)
    stamp(fig, f"仿真（非实测）：初始投入 ¥{capex:.0f}（合规、设计与工具）、月增 6 个付费用户、"
               f"月流失 3%、ARPU ¥{PRICE:.0f}、单用户变动成本 ¥15.1。")
    save(fig, "ch10/fig-20-cashflow.png")


# ============================================================ 调度
FIGURES = {
    "ch01": [fig01_four_gates, fig01_evidence_strength],
    "ch02": [fig02_waterfall, fig02_margin_curve],
    "ch03": [fig03_scope_quadrant, fig03_paid_loop],
    "ch04": [fig04_expand_contract, fig04_rollback_layers],
    "ch05": [fig05_burn_rate, fig05_budget_stairs],
    "ch06": [fig06_rto_rpo, fig06_downgrade],
    "ch07": [fig07_gates, fig07_guard],
    "ch08": [fig08_ai_act_timeline, fig08_obligation_matrix],
    "ch09": [fig09_health_dashboard, fig09_rewrite_score],
    "ch10": [fig10_gantt, fig10_cashflow],
}


def main() -> None:
    targets = sys.argv[1:] or list(FIGURES)
    unknown = [t for t in targets if t not in FIGURES]
    if unknown:
        print(f"未知章节：{unknown}；可选：{list(FIGURES)}")
        raise SystemExit(2)
    for chapter in targets:
        print(f"[{chapter}]")
        for fn in FIGURES[chapter]:
            fn()
    print("完成。")


if __name__ == "__main__":
    main()
