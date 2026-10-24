#!/usr/bin/env python3
"""《从能跑到能收钱》全书 20 张配图。

用法:
    python code/make_figures_p5.py [--lang zh|en] [chXX ...]   # 全部 / 某章

贯穿案例：会议纪要助手「纪要」——订阅 39 元/月，单次会议平均 50 分钟。
所有金额假设集中写在下方常量区，章节正文引用的数字与此处一一对应。

双语机制（A1′）：--lang zh|en（默认 zh）；每图文案在同册 fig_texts.py 的 T 字典；
几何代码与语言无关，语言差异只在 _t（取文案）与字体栈两处。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

from fig_texts import T
from _figstyle import (
    ASSETS, BAD, GOOD, GRID, INK, MUTED, PAPER, SAND, STEEL,
    apply, arrow, blank, box, clean_axes, save, stamp,
)

LANG = "zh"

ROOT = Path(__file__).resolve().parent.parent
STAGING = ROOT.parent / ".omc" / "work" / "bilingual-figures-en"  # en 同名互斥图暂存位（阶段 1）

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
    "economy": (0.8, 2.0),
    "standard": (2.0, 8.0),
    "flagship": (15.0, 60.0),
}

# 输出名映射（阶段 1：zh 走旧名原位重生成，en 走终态名；改号映射见
# .omc/work/bilingual-baseline/05-renumber-map-26.md，阶段 2 提交 (i) 与 git mv 同批切 .zh 名）
OLD_REL = {
    "fig-01-four-gates": "ch01/fig-01-four-gates.png",
    "fig-02-evidence-strength": "ch01/fig-02-evidence-strength.png",
    "fig-01-cost-waterfall": "ch02/fig-03-cost-waterfall.png",
    "fig-02-margin-curve": "ch02/fig-04-margin-curve.png",
    "fig-01-paid-loop": "ch03/fig-05-paid-loop.png",
    "fig-02-scope-quadrant": "ch03/fig-06-scope-quadrant.png",
    "fig-01-rollback-layers": "ch04/fig-07-rollback-layers.png",
    "fig-02-expand-contract": "ch04/fig-08-expand-contract.png",
    "fig-01-burn-rate": "ch05/fig-09-burn-rate.png",
    "fig-02-budget-stairs": "ch05/fig-10-budget-stairs.png",
    "fig-01-rto-rpo": "ch06/fig-11-rto-rpo.png",
    "fig-02-downgrade": "ch06/fig-12-downgrade.png",
    "fig-01-cost-gates": "ch07/fig-13-cost-gates.png",
    "fig-02-budget-guard": "ch07/fig-14-budget-guard.png",
    "fig-01-ai-act-timeline": "ch08/fig-16-ai-act-timeline.png",
    "fig-02-obligation-matrix": "ch08/fig-15-obligation-matrix.png",
    "fig-01-health-dashboard": "ch09/fig-17-health-dashboard.png",
    "fig-02-rewrite-score": "ch09/fig-18-rewrite-score.png",
    "fig-01-gantt": "ch10/fig-19-gantt.png",
    "fig-02-cashflow": "ch10/fig-20-cashflow.png",
}
FINAL_REL = {
    "fig-01-four-gates": "ch01/fig-01-four-gates.png",
    "fig-02-evidence-strength": "ch01/fig-02-evidence-strength.png",
    "fig-01-cost-waterfall": "ch02/fig-01-cost-waterfall.png",
    "fig-02-margin-curve": "ch02/fig-02-margin-curve.png",
    "fig-01-paid-loop": "ch03/fig-01-paid-loop.png",
    "fig-02-scope-quadrant": "ch03/fig-02-scope-quadrant.png",
    "fig-01-rollback-layers": "ch04/fig-01-rollback-layers.png",
    "fig-02-expand-contract": "ch04/fig-02-expand-contract.png",
    "fig-01-burn-rate": "ch05/fig-01-burn-rate.png",
    "fig-02-budget-stairs": "ch05/fig-02-budget-stairs.png",
    "fig-01-rto-rpo": "ch06/fig-01-rto-rpo.png",
    "fig-02-downgrade": "ch06/fig-02-downgrade.png",
    "fig-01-cost-gates": "ch07/fig-01-cost-gates.png",
    "fig-02-budget-guard": "ch07/fig-02-budget-guard.png",
    "fig-01-ai-act-timeline": "ch08/fig-01-ai-act-timeline.png",
    "fig-02-obligation-matrix": "ch08/fig-02-obligation-matrix.png",
    "fig-01-health-dashboard": "ch09/fig-01-health-dashboard.png",
    "fig-02-rewrite-score": "ch09/fig-02-rewrite-score.png",
    "fig-01-gantt": "ch10/fig-01-gantt.png",
    "fig-02-cashflow": "ch10/fig-02-cashflow.png",
}


def _t(fig_id: str) -> dict:
    """取文案——语言差异只允许出现在这里与字体栈。"""
    return T[fig_id][LANG]


def _out(fig_id: str):
    if LANG == "zh":
        return ASSETS / OLD_REL[fig_id]
    rel = FINAL_REL[fig_id]
    if rel == OLD_REL[fig_id]:
        # en 终态名与 zh 旧名互斥：暂存 .omc/work，阶段 2 提交 (i) zh 让名后 cp 落位
        return STAGING / "phase5" / "assets" / rel
    return ASSETS / rel


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
    t = _t("fig-01-four-gates")
    fig, ax = plt.subplots(figsize=(10.4, 5.2))
    blank(ax, (0, 10.4), (0, 5.6))

    rows = t["gates"]

    ax.text(0.35, 5.16, t["col_gate"], fontsize=9.5, color=MUTED)
    ax.text(2.95, 5.16, t["col_cond"], fontsize=9.5, color=MUTED)
    ax.text(7.35, 5.16, t["col_symptom"], fontsize=9.5, color=MUTED)
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
    ax.text(0.52, 0.42, t["bottom"],
            fontsize=10, color=INK, va="center")

    ax.set_title(t["title"],
                 fontsize=14.5, fontweight="bold", loc="left", pad=14)
    stamp(fig, t["stamp"])
    save(fig, _out("fig-01-four-gates"))


def fig01_evidence_strength() -> None:
    t = _t("fig-02-evidence-strength")
    points = list(zip(t["points"],
                      [0.2, 0.4, 3.0, 7.0, 14.0, 20.0, 30.0],
                      [1.0, 1.3, 1.8, 2.5, 3.5, 4.6, 5.0]))

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
    ax.set_xlabel(t["xlabel"], fontsize=10.2)
    ax.text(0.16, 5.14, t["strong"], fontsize=10, color=GOOD, fontweight="bold")
    ax.text(250, 0.86, t["weak"], fontsize=9.6,
            color=BAD, ha="right")

    clean_axes(ax, "x")
    ax.set_title(t["title"],
                 fontsize=14.2, fontweight="bold", loc="left", pad=14)
    stamp(fig, t["stamp"])
    save(fig, _out("fig-02-evidence-strength"))


# ============================================================ 第 02 章
def fig02_waterfall() -> None:
    t = _t("fig-01-cost-waterfall")
    costs = [
        90 * MEETING_MIN * ASR_PER_MIN,
        90 * llm_cost("standard"),
        90 * MEETING_MIN * AUDIO_MB_PER_MIN / 1024 * STORE_PER_GB,
        PRICE * PAY_RATE,
        90 * EMB_PER_MEETING,
    ]
    labels = t["labels"]

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
            txt = t["value_fmt"].format(v=v)
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
    ax.set_ylabel(t["ylabel"], fontsize=10.2)
    ax.set_ylim(0, 46)
    clean_axes(ax, "y")

    ax.annotate(t["annotate"].format(margin=level / PRICE * 100, fixed=FIXED_COST,
                                     n=np.ceil(FIXED_COST / level)),
                xy=(6, level), xytext=(3.55, 35.0), fontsize=9.6, color=GOOD,
                arrowprops=dict(arrowstyle="-|>", color=GOOD, linewidth=1.1,
                                connectionstyle="arc3,rad=-0.2"))

    ax.set_title(t["title"].format(left=level),
                 fontsize=14.2, fontweight="bold", loc="left", pad=14)
    stamp(fig, t["stamp"])
    save(fig, _out("fig-01-cost-waterfall"))


def fig02_margin_curve() -> None:
    t = _t("fig-02-margin-curve")
    n = np.arange(1, 301)
    fig, ax = plt.subplots(figsize=(9.8, 4.9))

    colors = {"economy": "#8FB8C9", "standard": STEEL, "flagship": BAD}
    for tier in ("economy", "standard", "flagship"):
        cost = n * meeting_cost(tier) + PRICE * PAY_RATE
        margin = (PRICE - cost) / PRICE * 100
        be = (PRICE - PRICE * PAY_RATE) / meeting_cost(tier)
        ax.plot(n, margin, color=colors[tier], linewidth=2.2,
                label=t["tier_label"].format(name=t["tier_names"][tier], be=be))
        ax.scatter([be], [0], color=colors[tier], s=46, zorder=4, edgecolor="white")


    ax.axhline(0, color=INK, linewidth=1.2)
    ax.axvline(30, color=MUTED, linewidth=1.0, linestyle="--")
    ax.axvline(90, color=MUTED, linewidth=1.0, linestyle="--")
    ax.text(29, -41, t["typical"], fontsize=8.2, color=MUTED, ha="right",
            va="bottom", linespacing=1.35)
    ax.text(89, -41, t["heavy"], fontsize=8.2, color=MUTED, ha="right",
            va="bottom", linespacing=1.35)

    ax.set_xlabel(t["xlabel"], fontsize=10.2)
    ax.set_ylabel(t["ylabel"], fontsize=10.2)
    ax.set_xlim(0, 300)
    ax.set_ylim(-45, 72)
    ax.legend(loc="upper right", fontsize=9.4)
    clean_axes(ax, "y")

    ax.annotate(t["annotate"],
                xy=(88, -22), xytext=(118, -39), fontsize=9.2, color=BAD,
                arrowprops=dict(arrowstyle="-|>", color=BAD, linewidth=1.1,
                                connectionstyle="arc3,rad=0.25"))

    ax.set_title(t["title"],
                 fontsize=13.6, fontweight="bold", loc="left", pad=14)
    stamp(fig, t["stamp"])
    save(fig, _out("fig-02-margin-curve"))


# ============================================================ 第 03 章
def fig03_scope_quadrant() -> None:
    t = _t("fig-02-scope-quadrant")
    features = list(zip(
        t["features"],
        [7.2, 8.8, 6.0, 2.6, 3.2, 6.8, 5.4, 8.8, 9.2, 6.2, 4.4, 7.6],
        [9.4, 9.5, 8.6, 7.8, 9.2, 6.2, 5.6, 5.0, 3.4, 3.2, 2.6, 1.4],
        [-9, 0, 7, 7, 7, 7, 7, 7, -9, 7, 7, 7],
        [4, -15, 5, 5, 5, 5, 5, 5, -4, 5, 5, 5],
        ["right", "center", "left", "left", "left", "left", "left", "left", "right", "left", "left", "left"],
    ))

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
    ax.text(0.35, 5.22, t["quad"][0], color=GOOD, **quad)
    ax.text(5.25, 5.22, t["quad"][1], color=MUTED, **quad)
    ax.text(0.35, 0.62, t["quad"][2], color=GOOD, **quad)
    ax.text(5.25, 0.62, t["quad"][3], color=MUTED, **quad)

    ax.set_xlabel(t["xlabel"], fontsize=10.2)
    ax.set_ylabel(t["ylabel"], fontsize=10.2)
    ax.set_xlim(0.2, 10.4)
    ax.set_ylim(0, 10)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    ax.set_title(t["title"],
                 fontsize=14.2, fontweight="bold", loc="left", pad=14)
    stamp(fig, t["stamp"])
    save(fig, _out("fig-02-scope-quadrant"))


def fig03_paid_loop() -> None:
    t = _t("fig-01-paid-loop")
    fig, ax = plt.subplots(figsize=(9.6, 5.0))
    blank(ax, (0, 9.6), (0, 5.4))

    nodes = [
        (t["nodes"][0][0], t["nodes"][0][1], 3.55, 4.28),
        (t["nodes"][1][0], t["nodes"][1][1], 6.45, 2.62),
        (t["nodes"][2][0], t["nodes"][2][1], 3.55, 0.96),
        (t["nodes"][3][0], t["nodes"][3][1], 0.55, 2.62),
    ]
    w, h = 2.55, 0.92
    for title, desc, x, y in nodes:
        box(ax, x, y, w, h, "", fc=PAPER, ec=STEEL)
        ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="center",
                fontsize=11.5, fontweight="bold", color=INK)
        ax.text(x + w / 2, y + 0.28, desc, ha="center", va="center",
                fontsize=8.8, color="#52606D", linespacing=1.4)

    ax.add_patch(Circle((4.8, 2.72), 0.62, facecolor=INK, edgecolor="none", zorder=4))
    ax.text(4.8, 2.72, t["center"], ha="center", va="center", fontsize=9.6,
            color="white", fontweight="bold", zorder=5, linespacing=1.3)

    arrow(ax, (5.55, 5.02), (7.85, 3.86), color=STEEL, lw=1.8, rad=-0.28)
    arrow(ax, (7.95, 2.44), (6.25, 1.32), color=STEEL, lw=1.8, rad=-0.28)
    arrow(ax, (3.42, 1.40), (1.92, 2.50), color=STEEL, lw=1.8, rad=-0.28)
    arrow(ax, (1.98, 3.62), (3.40, 4.66), color=STEEL, lw=1.8, rad=-0.28)

    ax.text(8.05, 4.62, t["breaks"][0], fontsize=9, color=BAD, ha="center", linespacing=1.4)
    ax.text(8.05, 1.06, t["breaks"][1], fontsize=9, color=BAD, ha="center", linespacing=1.4)
    ax.text(1.35, 1.02, t["breaks"][2], fontsize=9, color=BAD, ha="center", linespacing=1.4)
    ax.text(1.30, 4.66, t["breaks"][3], fontsize=9, color=BAD, ha="center", linespacing=1.4)

    ax.text(0.25, 0.30, t["note"],
            fontsize=9.8, color=INK)

    ax.set_title(t["title"],
                 fontsize=14.2, fontweight="bold", loc="left", pad=12)
    stamp(fig, t["stamp"])
    save(fig, _out("fig-01-paid-loop"))


# ============================================================ 第 04 章
def fig04_expand_contract() -> None:
    t = _t("fig-02-expand-contract")
    fig, ax = plt.subplots(figsize=(10.4, 5.0))
    blank(ax, (0, 10.4), (0, 5.4))

    cols = [
        (t["cols"][0][0], t["cols"][0][1], t["cols"][0][2], GOOD),
        (t["cols"][1][0], t["cols"][1][1], t["cols"][1][2], GOOD),
        (t["cols"][2][0], t["cols"][2][1], t["cols"][2][2], GOOD),
        (t["cols"][3][0], t["cols"][3][1], t["cols"][3][2], BAD),
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
    ax.text(0.32 + (3 * (w + gap) - gap) / 2, 1.63, t["band_ok"],
            ha="center", va="center", fontsize=9.4, color="#1B6B62")
    ax.add_patch(Rectangle((0.32 + 3 * (w + gap), 1.45), w, 0.36,
                           facecolor=BAD, alpha=0.14, edgecolor="none"))
    ax.text(0.32 + 3 * (w + gap) + w / 2, 1.63, t["band_bad"],
            ha="center", va="center", fontsize=8.8, color=BAD, linespacing=1.3)

    ax.text(0.32, 1.02, t["note1"],
            fontsize=9.6, color=INK)
    ax.text(0.32, 0.62, t["note2"],
            fontsize=9.6, color=BAD)

    ax.set_title(t["title"],
                 fontsize=14.2, fontweight="bold", loc="left", pad=12)
    stamp(fig, t["stamp"])
    save(fig, _out("fig-02-expand-contract"))


def fig04_rollback_layers() -> None:
    t = _t("fig-01-rollback-layers")
    items = [
        (t["names"][0], 30, GOOD, t["descs"][0]),
        (t["names"][1], 120, GOOD, t["descs"][1]),
        (t["names"][2], 2700, SAND, t["descs"][2]),
        (t["names"][3], 300000, BAD, t["descs"][3]),
    ]

    fig, ax = plt.subplots(figsize=(9.8, 4.4))
    y = np.arange(len(items))[::-1]
    for yi, (name, sec, color, desc) in zip(y, items):
        ax.barh(yi, sec, height=0.44, color=color, edgecolor="none", zorder=3)
        label = (t["fmt_irrev"] if sec >= 300000
                 else t["fmt_min"].format(v=sec / 60) if sec >= 60 else t["fmt_sec"].format(v=sec))
        ax.text(sec * 1.15, yi, label, va="center", fontsize=10.2,
                color=color, fontweight="bold")
        ax.text(12, yi - 0.36, desc, va="center", fontsize=8.6, color=MUTED)

    ax.set_yticks(y)
    ax.set_yticklabels([i[0] for i in items], fontsize=11)
    ax.set_xscale("log")
    ax.set_xlim(10, 3e6)
    ax.set_xlabel(t["xlabel"], fontsize=10.2)
    ax.set_ylim(-0.95, 3.55)
    clean_axes(ax, "x")

    ax.axvspan(2e5, 3e6, color=BAD, alpha=0.06, zorder=0)
    ax.text(2.05e5, 2.66, t["no_rollback"], fontsize=9, color=BAD,
            linespacing=1.4, ha="left", va="center")

    ax.set_title(t["title"],
                 fontsize=14.2, fontweight="bold", loc="left", pad=14)
    stamp(fig, t["stamp"])
    save(fig, _out("fig-01-rollback-layers"))


# ============================================================ 第 05 章
SLO = 0.995
BUDGET_MIN = (1 - SLO) * 30 * 24 * 60      # 30 天窗口下的错误预算（分钟）


def fig05_burn_rate() -> None:
    t = _t("fig-01-burn-rate")
    hours = np.linspace(0, 72, 400)
    rates = [(1, t["rates"][0], "#8FB8C9"),
             (6, t["rates"][1], SAND),
             (14.4, t["rates"][2], BAD),
             (60, t["rates"][3], "#7A2E12")]

    fig, ax = plt.subplots(figsize=(9.8, 4.7))
    for r, label, color in rates:
        used = r * hours / (30 * 24) * 100
        ax.plot(hours, np.clip(100 - used, 0, 100), color=color, linewidth=2.2, label=label)

    ax.axhline(0, color=INK, linewidth=1.0)
    ax.set_xlabel(t["xlabel"], fontsize=10.2)
    ax.set_ylabel(t["ylabel"], fontsize=10.2)
    ax.set_xlim(0, 72)
    ax.set_ylim(-3, 104)
    ax.legend(loc="upper right", fontsize=9.2)
    clean_axes(ax, "y")

    ax.annotate(t["annotate"],
                xy=(12, 0), xytext=(15.5, 26), fontsize=9.4, color="#7A2E12",
                arrowprops=dict(arrowstyle="-|>", color="#7A2E12", linewidth=1.1,
                                connectionstyle="arc3,rad=0.25"))
    ax.text(34, 5, t["budget"].format(pct=(1 - SLO) * 100, mins=BUDGET_MIN),
            fontsize=9.2, color=MUTED)

    ax.set_title(t["title"],
                 fontsize=14.2, fontweight="bold", loc="left", pad=14)
    stamp(fig, t["stamp"])
    save(fig, _out("fig-01-burn-rate"))


def fig05_budget_stairs() -> None:
    t = _t("fig-02-budget-stairs")
    # 情景推演：一个月里的四次故障，逐次累计消耗预算
    events = [
        (3.0, 20 / 60, 60, t["events"][0]),
        (11.0, 1.5, 40, t["events"][1]),
        (18.0, 0.75, 60, t["events"][2]),
        (26.0, 4.0, 20, t["events"][3]),
    ]

    fig, ax = plt.subplots(figsize=(9.8, 4.6))
    used, t_prev = 0.0, 0.0
    for day, dur, rate, label in events:
        ax.plot([t_prev, day], [used, used], color=STEEL, linewidth=2.0)
        delta = rate * dur / (30 * 24) * 100
        used += delta
        ax.plot([day, day], [used - delta, used], color=BAD, linewidth=2.0)
        ax.scatter([day], [used], color=BAD, s=30, zorder=4)
        ax.annotate(t["delta_label"].format(day=day, delta=delta), (day, used), xytext=(0, 7),
                    textcoords="offset points", fontsize=8.8, color=BAD,
                    fontweight="bold", ha="center")
        t_prev = day

    ax.plot([t_prev, 30], [used, used], color=STEEL, linewidth=2.0)
    ax.axhline(100, color=BAD, linewidth=1.2, linestyle="--")
    ax.text(0.4, 101.5, t["budget_line"], fontsize=8.8, color=BAD)

    ax.set_xlim(0, 30)
    ax.set_ylim(0, 116)
    ax.set_xlabel(t["xlabel"], fontsize=10.2)
    ax.set_ylabel(t["ylabel"], fontsize=10.2)
    clean_axes(ax, "y")

    ax.set_title(t["title"].format(used=used),
                 fontsize=13.6, fontweight="bold", loc="left", pad=14)
    stamp(fig, t["stamp"])
    save(fig, _out("fig-02-budget-stairs"))


# ============================================================ 第 06 章
def fig06_rto_rpo() -> None:
    t = _t("fig-01-rto-rpo")
    fig, ax = plt.subplots(figsize=(10.2, 4.5))
    blank(ax, (0, 10.2), (0, 4.9))

    y = 2.65
    ax.plot([0.6, 9.7], [y, y], color="#CBD2D9", linewidth=2.2, zorder=1)

    marks = [
        (1.2, t["marks"][0], GOOD),
        (5.4, t["marks"][1], BAD),
        (8.3, t["marks"][2], GOOD),
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
    ax.text(5.62, y + 0.86, t["discover"], fontsize=8.4, color="#A67C00",
            va="center", ha="right")

    # RPO
    ax.annotate("", xy=(5.4, y - 0.52), xytext=(1.2, y - 0.52),
                arrowprops=dict(arrowstyle="<->", color=BAD, linewidth=1.5))
    ax.text(3.3, y - 0.70, t["rpo"],
            ha="center", va="top", fontsize=9.6, color=BAD, fontweight="bold")

    # RTO
    ax.annotate("", xy=(8.3, y + 1.42), xytext=(5.4, y + 1.42),
                arrowprops=dict(arrowstyle="<->", color=STEEL, linewidth=1.5))
    ax.text(6.85, y + 1.54, t["rto"],
            ha="center", va="bottom", fontsize=9.6, color=STEEL, fontweight="bold")

    ax.text(0.6, 0.62, t["note1"],
            fontsize=9.2, color=MUTED, va="top")
    ax.text(0.6, 0.30, t["note2"],
            fontsize=9.8, color=INK, va="top")

    ax.set_title(t["title"],
                 fontsize=13.8, fontweight="bold", loc="left", pad=10)
    stamp(fig, t["stamp"])
    save(fig, _out("fig-01-rto-rpo"))


def fig06_downgrade() -> None:
    t = _t("fig-02-downgrade")
    strategies = list(zip(t["names"],
                          [3.0, 5.4, 2.0, 1.2],
                          [4.2, 2.2, 6.6, 8.6],
                          t["conds"]))

    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    ax.axvline(4.5, color="#B8C1CC", linewidth=1.0, linestyle="--")
    ax.axhline(5.0, color="#B8C1CC", linewidth=1.0, linestyle="--")

    for name, x, y, cond in strategies:
        ax.scatter([x], [y], s=130, color=STEEL, edgecolor="white", linewidth=1.6, zorder=4)
        ax.annotate(f"{name}\n{cond}", (x, y), xytext=(10, -4),
                    textcoords="offset points", fontsize=9.2, color=INK, linespacing=1.5)

    ax.text(0.3, 9.5, t["cost_high"], fontsize=9.4, color=MUTED)
    ax.text(0.3, 0.4, t["cost_low"], fontsize=9.4, color=MUTED)
    ax.text(7.3, 0.4, t["impl_high"], fontsize=9.4, color=MUTED, ha="right")

    ax.set_xlim(0, 7.6)
    ax.set_ylim(0, 10)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    ax.set_title(t["title"],
                 fontsize=14.0, fontweight="bold", loc="left", pad=14)
    stamp(fig, t["stamp"])
    save(fig, _out("fig-02-downgrade"))


# ============================================================ 第 07 章
def fig07_gates() -> None:
    t = _t("fig-01-cost-gates")
    base = 1000 * meeting_cost("standard")     # 1000 次请求的标准档成本
    stages = [
        (t["stages"][0], base, 1.00, STEEL),
        (t["stages"][1], base * 0.65, 0.65, "#5B8C9E"),
        (t["stages"][2], base * 0.65 * 0.78, 0.51, "#8FB8C9"),
        (t["stages"][3], base * 0.65 * 0.78 * 0.72, 0.36, GOOD),
    ]

    fig, ax = plt.subplots(figsize=(9.6, 4.6))
    y = np.arange(len(stages))[::-1]
    for yi, (name, val, frac, color) in zip(y, stages):
        ax.barh(yi, val, height=0.5, color=color, edgecolor="none", zorder=3)
        ax.text(val + 4, yi, t["value_fmt"].format(v=val), va="center", fontsize=10.5,
                color=color, fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels([s[0] for s in stages], fontsize=10.2)
    ax.set_xlabel(t["xlabel"], fontsize=10.2)
    ax.set_xlim(0, base * 1.12)
    clean_axes(ax, "x")

    ax.set_title(t["title"].format(base=base, last=stages[-1][1], drop=100 * (1 - stages[-1][2])),
                 fontsize=13.4, fontweight="bold", loc="left", pad=14)

    stamp(fig, t["stamp"])
    save(fig, _out("fig-01-cost-gates"))


def fig07_guard() -> None:
    t = _t("fig-02-budget-guard")
    hours = np.arange(0, 25)
    spend = np.full_like(hours, 8.0, dtype=float)
    spend[14:] = 60.0
    cumulative = np.minimum(np.cumsum(spend), 300.0)
    budget = 300.0

    fig, ax = plt.subplots(figsize=(9.6, 4.6))
    ax.plot(hours, cumulative, color=STEEL, linewidth=2.4, marker="o",
            markersize=3.4, label=t["label_cum"])
    ax.axhline(budget, color=BAD, linewidth=1.4, linestyle="--")
    ax.text(0.3, budget + 8, t["budget"], fontsize=9.4, color=BAD)
    ax.axhline(budget * 0.8, color=SAND, linewidth=1.2, linestyle=":")
    ax.text(0.3, budget * 0.8 + 8, t["warn80"], fontsize=9.0, color="#A67C00")

    hit = int(np.argmax(cumulative >= budget))
    ax.scatter([hours[hit]], [budget], s=90, color=BAD, zorder=5, edgecolor="white")
    ax.annotate(t["trip"],
                xy=(hours[hit], budget), xytext=(4.2, 236),
                fontsize=9.2, color=BAD,
                arrowprops=dict(arrowstyle="-|>", color=BAD, linewidth=1.1,
                                connectionstyle="arc3,rad=0.25"))

    ax.set_xlabel(t["xlabel"], fontsize=10.2)
    ax.set_ylabel(t["ylabel"], fontsize=10.2)
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 430)
    ax.legend(loc="upper left", fontsize=9.4)
    clean_axes(ax, "y")

    ax.set_title(t["title"],
                 fontsize=13.8, fontweight="bold", loc="left", pad=14)
    stamp(fig, t["stamp"])
    save(fig, _out("fig-02-budget-guard"))


# ============================================================ 第 08 章
def fig08_ai_act_timeline() -> None:
    t = _t("fig-01-ai-act-timeline")
    milestones = [
        (0, t["ms"][0][0], t["ms"][0][1], t["ms"][0][2], STEEL),
        (12, t["ms"][1][0], t["ms"][1][1], t["ms"][1][2], STEEL),
        (24, t["ms"][2][0], t["ms"][2][1], t["ms"][2][2], BAD),
        (28, t["ms"][3][0], t["ms"][3][1], t["ms"][3][2], BAD),
        (40, t["ms"][4][0], t["ms"][4][1], t["ms"][4][2], MUTED),
        (48, t["ms"][5][0], t["ms"][5][1], t["ms"][5][2], MUTED),
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
    ax.text(1.72, ypos(today), t["today"], ha="right", va="center", fontsize=8.6,
            color=GOOD, linespacing=1.35, fontweight="bold")

    for m, date, title, desc, color in milestones:
        y = ypos(m)
        ax.scatter([2.05], [y], s=86, color=color, edgecolor="white", linewidth=1.8, zorder=4)
        ax.text(2.34, y + 0.16, t["date_title"].format(date=date, title=title), fontsize=10.4, color=color,
                fontweight="bold", va="center")
        if desc:
            ax.text(2.34, y - 0.14, desc, fontsize=8.8, color="#52606D", va="center")


    ax.annotate("", xy=(2.05, ypos(24)), xytext=(2.05, ypos(40)),
                arrowprops=dict(arrowstyle="<->", color=GOOD, linewidth=1.2, linestyle="--"))
    ax.text(1.72, (ypos(24) + ypos(40)) / 2, t["buffer"], ha="right", va="center",
            fontsize=8.6, color=GOOD, linespacing=1.35)

    ax.text(0.12, 0.02, t["note"],
            fontsize=9.0, color=BAD, va="bottom")

    ax.set_title(t["title"],
                 fontsize=14.0, fontweight="bold", loc="left", pad=12)
    stamp(fig, t["stamp"])
    save(fig, _out("fig-01-ai-act-timeline"))


def fig08_obligation_matrix() -> None:
    t = _t("fig-02-obligation-matrix")
    tiers = t["tiers"]
    duties = t["duties"]
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
                face, txt, tc = "#F6E3DA", t["banned"], BAD
            elif v == 2:
                face, txt, tc = STEEL, t["full"], "white"
            elif v == 1:
                face, txt, tc = "#8FB8C9", t["partial"], "white"
            else:
                face, txt, tc = "#F4F5F6", t["none"], "#B8C1CC"
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

    ax.text(0.02, -0.86, t["legend"],
            fontsize=9.0, color=MUTED)

    ax.set_title(t["title"],
                 fontsize=14.0, fontweight="bold", loc="left", pad=14)
    stamp(fig, t["stamp"])
    save(fig, _out("fig-02-obligation-matrix"))


# ============================================================ 第 09 章
def fig09_health_dashboard() -> None:
    t = _t("fig-01-health-dashboard")
    weeks = np.arange(1, 9)
    panels = [
        (t["panels"][0][0], [72, 74, 76, 75, 71, 66, 61, 58], GOOD, t["panels"][0][1]),
        (t["panels"][1][0], [18, 17, 16, 18, 22, 27, 31, 35], BAD, t["panels"][1][1]),
        (t["panels"][2][0], [12, 11, 13, 14, 19, 24, 28, 33], STEEL, t["panels"][2][1]),
        (t["panels"][3][0], [6.2, 6.0, 6.1, 6.4, 7.3, 8.6, 9.9, 11.4], SAND, t["panels"][3][1]),
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
        ax.set_xlabel(t["xlabel"], fontsize=9.4)
    axes[0][0].text(4.6, 64.5, t["inflection"], fontsize=8.6, color=BAD)

    fig.suptitle(t["suptitle"],
                 fontsize=14.0, fontweight="bold", x=0.012, ha="left", y=1.02)
    stamp(fig, t["stamp"])
    save(fig, _out("fig-01-health-dashboard"))


def fig09_rewrite_score() -> None:
    t = _t("fig-02-rewrite-score")
    criteria = [
        (t["names"][0], 4.2, 3.5),
        (t["names"][1], 4.5, 3.5),
        (t["names"][2], 3.8, 2.5),
        (t["names"][3], 2.2, 2.5),
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
    ax.set_xlabel(t["xlabel"], fontsize=10.0)
    clean_axes(ax, "x")
    ax.text(0.15, -1.30, t["verdict"],
            fontsize=9.4, color=INK)

    ax.set_title(t["title"],
                 fontsize=13.8, fontweight="bold", loc="left", pad=14)
    stamp(fig, t["stamp"])
    save(fig, _out("fig-02-rewrite-score"))


# ============================================================ 第 10 章
def fig10_gantt() -> None:
    t = _t("fig-01-gantt")
    phases = [
        (t["phases"][0], 1, 3, STEEL),
        (t["phases"][1], 4, 7, STEEL),
        (t["phases"][2], 8, 13, "#5B8C9E"),
        (t["phases"][3], 14, 17, BAD),
        (t["phases"][4], 18, 21, "#8FB8C9"),
        (t["phases"][5], 22, 24, SAND),
        (t["phases"][6], 25, 27, "#9AA5B1"),
        (t["phases"][7], 28, 28, GOOD),
    ]

    fig, ax = plt.subplots(figsize=(10.2, 4.4))
    for i, (name, start, end, color) in enumerate(phases):
        y = len(phases) - i
        ax.barh(y, end - start + 0.8, left=start - 0.4, height=0.52,
                color=color, edgecolor="none", zorder=3)
        ax.text(end + 0.6, y,
                t["range_fmt"].format(start=start, end=end) if start != end else f"D{start}",
                va="center", fontsize=8.8, color=color, fontweight="bold")

    ax.set_yticks([len(phases) - i for i in range(len(phases))])
    ax.set_yticklabels([p[0] for p in phases], fontsize=9.6)
    ax.set_xlim(0, 32)
    ax.set_xticks([1, 7, 14, 21, 28])
    ax.set_xticklabels(["D1", "D7", "D14", "D21", "D28"], fontsize=9.4)
    ax.set_xlabel(t["xlabel"], fontsize=10.0)
    clean_axes(ax, "x")
    for d in (14, 17, 28):
        ax.axvline(d, color="#DCE2E8", linewidth=1.0, linestyle=":", zorder=0)

    ax.set_title(t["title"],
                 fontsize=14.0, fontweight="bold", loc="left", pad=14)
    stamp(fig, t["stamp"])
    save(fig, _out("fig-01-gantt"))


def fig10_cashflow() -> None:
    t = _t("fig-02-cashflow")
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
        ax.annotate(t["annotate"].format(be=be),
                    xy=(be, 0), xytext=(0.8, -600), fontsize=9.6, color=GOOD,
                    arrowprops=dict(arrowstyle="-|>", color=GOOD, linewidth=1.1,
                                    connectionstyle="arc3,rad=0.0"))

    ax.set_xlabel(t["xlabel"], fontsize=10.0)
    ax.set_ylabel(t["ylabel"], fontsize=10.0)
    ax.set_xlim(0, 12)
    clean_axes(ax, "y")

    ax.set_title(t["title"],
                 fontsize=14.0, fontweight="bold", loc="left", pad=14)
    stamp(fig, t["stamp"].format(capex=capex, price=PRICE))
    save(fig, _out("fig-02-cashflow"))


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
    global LANG
    ap = argparse.ArgumentParser(description="Generate phase5 figures.")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh", help="figure text language")
    ap.add_argument("chapters", nargs="*", help="chapter ids like ch04 (default: all)")
    args = ap.parse_args()
    LANG = args.lang
    apply(LANG)
    targets = args.chapters or list(FIGURES)
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
