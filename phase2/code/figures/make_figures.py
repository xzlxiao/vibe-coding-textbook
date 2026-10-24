#!/usr/bin/env python3
"""生成《先写规格，再让 AI 动手》全书的定量示意图。

纪律：
- 所有曲线都是**教学模型示意**，不是实证数据；图内必须标注假设。
- 中文字体走 PingFang SC -> Heiti SC -> STHeiti 兜底（macOS 无 Noto Sans CJK）。
- 白底、细线、无渐变、无阴影；颜色只承担语义（青绿=规格生效，赭石=返工）。

双语机制（A1′）：--lang zh|en（默认 zh）；每图文案在模块级 T 字典；
几何代码与语言无关，语言差异只在 _t（取文案）与字体栈两处。
"""

from __future__ import annotations

import argparse
import math
import os
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # phase2/

LANG = "zh"

INK = "#1F2937"
MUTED = "#6B7280"
RULE = "#D8DEE6"
GOOD = "#0E7C66"
BAD = "#B45309"
FILL = "#F7F8FA"

FONT_STACKS = {
    "zh": ["PingFang SC", "Heiti SC", "STHeiti", "Arial Unicode MS"],
    "en": ["Arial Unicode MS", "Helvetica", "Arial", "DejaVu Sans"],
}

plt.rcParams.update(
    {
        "font.sans-serif": FONT_STACKS["zh"],
        "axes.unicode_minus": False,
        "figure.dpi": 200,
        "savefig.dpi": 240,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": RULE,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "text.color": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.grid": True,
        "grid.color": RULE,
        "grid.alpha": 0.55,
        "grid.linewidth": 0.7,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.titleweight": "medium",
        "legend.frameon": False,
    }
)

# 输出名映射（阶段 2 提交 (i) 起为终态规则）：en 落 FINAL_REL、zh 落 FINAL_REL 加 .zh 后缀
# （fig-NN-slug.zh.png）；26 处改号已并入 FINAL_REL，58 张 zh 图已 git mv 到位
# （映射依据 .omc/work/bilingual-baseline/05-renumber-map-26.md）。
FINAL_REL = {
    "fig-01-rework-cost": "assets/ch01/fig-01-rework-cost.png",
    "fig-01-batch-size": "assets/ch07/fig-01-batch-size.png",
    "fig-01-first-pass": "assets/ch09/fig-01-first-pass.png",
    "fig-01-cognitive-debt": "assets/ch12/fig-01-cognitive-debt.png",
}

# 每图双语文案（图内标注文案的单一事实源）
T = {
    "fig-01-rework-cost": {
        "zh": {
            "stages": ["写规格时", "生成后评审", "联调阶段", "灰度发布", "线上事故"],
            "label_nospec": "无规格：缺陷按默认值散落",
            "label_spec": "有规格：缺陷被拉回左侧",
            "xlabel": "缺陷被发现的阶段（越往右越晚）",
            "ylabel": "相对修复成本（对数轴，写规格时=1）",
            "title": "同一处缺陷，晚发现一个阶段，成本乘 2.5",
            "factor": "{v:g}×",
            "annotation": "规格的作用点\n不是让 AI 更聪明，\n是把 d 从 4 拉回 1",
            "note": "教学模型：C(d)=2.5^(d-1)，参数为假设值，非实测数据",
        },
        "en": {
            "stages": ["Spec writing", "Post-gen review", "Integration", "Canary", "Incident"],
            "label_nospec": "No spec: defects scatter at defaults",
            "label_spec": "With spec: defects pulled left",
            "xlabel": "Stage where the defect is found (right = later)",
            "ylabel": "Relative fix cost (log scale, spec writing = 1)",
            "title": "Same defect: found one stage later, cost × 2.5",
            "factor": "{v:g}×",
            "annotation": "A spec's leverage point\nis not a smarter AI —\nit pulls d back from 4 to 1",
            "note": "Teaching model: C(d)=2.5^(d-1); parameters assumed, not measured",
        },
    },
    "fig-01-batch-size": {
        "zh": {
            "label_context": "上下文占用（归一化）",
            "label_rework": "返工概率（示意）",
            "annotation": "2–4 个任务/批：返工最低，\n且每批都能独立验收",
            "xlabel": "单次 implement 的任务数",
            "ylabel": "归一化数值（0–1）",
            "title": "批次太小会攒集成债，太大会丢上下文",
            "note": "教学模型：占用 1-e^(-n/4.2)，返工为 U 形假设，非实测数据",
        },
        "en": {
            "label_context": "Context usage (normalized)",
            "label_rework": "Rework probability (illustrative)",
            "annotation": "2–4 tasks per batch: least rework,\nand every batch ships on its own",
            "xlabel": "Tasks per implement run",
            "ylabel": "Normalized value (0–1)",
            "title": "Too small piles up integration debt; too large loses context",
            "note": "Teaching model: usage 1-e^(-n/4.2); U-shaped rework assumed, not measured",
        },
    },
    "fig-01-first-pass": {
        "zh": {
            "label_baseline": "只看感觉（无规格基线）",
            "label_adopted": "按规格验收",
            "note_lo": "0.5 以下：规格有系统性缺口",
            "note_hi": "0.9 以上：怀疑过规格",
            "xlabel": "连续交付的周数",
            "ylabel": "首轮验收率",
            "title": "首轮验收率：规格的收益在第 3–5 周才显形",
            "note": "示例数据：固定随机种子生成，用于演示读图方式，不代表任何团队实测",
        },
        "en": {
            "label_baseline": "Gut feel only (no-spec baseline)",
            "label_adopted": "Acceptance by spec",
            "note_lo": "Below 0.5: the spec has systematic gaps",
            "note_hi": "Above 0.9: suspect over-specification",
            "xlabel": "Weeks of continuous delivery",
            "ylabel": "First-pass acceptance rate",
            "title": "First-pass rate: spec payoff shows up in weeks 3–5",
            "note": "Sample data from a fixed random seed, to teach chart reading — not any team's measurements",
        },
    },
    "fig-01-cognitive-debt": {
        "zh": {
            "label_nospec": "无规格：靠人和对话记忆",
            "label_spec": "有规格：靠可检索的判据",
            "annotation": "第 13 周：回答「为什么取消后要延迟 15 分钟」\n无规格组要翻 {y13:.0f} 分钟代码，有规格组查判据约 15 分钟",
            "xlabel": "项目已交付的周数",
            "ylabel": "回答一个「为什么」所需的分钟数",
            "title": "认知债：规格不写，债不会消失，只是转嫁给三个月后的你",
            "note": "教学模型：二次增长假设，参数为示意值，非实测数据",
        },
        "en": {
            "label_nospec": "No spec: people and chat memory",
            "label_spec": "With spec: retrievable criteria",
            "annotation": "Week 13: answering \"why delay 15 min after cancellation\"\nno-spec digs through code for {y13:.0f} min; with spec, ~15 min of criteria lookup",
            "xlabel": "Weeks since project delivery",
            "ylabel": "Minutes to answer one \"why\"",
            "title": "Cognitive debt: unwritten specs don't vanish — they bill future you",
            "note": "Teaching model: quadratic-growth assumption; illustrative values, not measured",
        },
    },
}

def _t(fig_id: str) -> dict:
    """取文案——语言差异只允许出现在这里与字体栈。"""
    return T[fig_id][LANG]

def _out(fig_id: str):
    rel = FINAL_REL[fig_id]
    if LANG == "zh":
        rel = rel[:-4] + ".zh.png"
    return ROOT / rel

def _note(fig, text: str) -> None:
    """图下方的模型示意声明，避免被当成实证数据。"""
    fig.text(0.995, -0.075, text, ha="right", va="bottom", fontsize=7.5, color=MUTED)

def _save(fig, fig_id: str) -> None:
    path = _out(fig_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.28, facecolor="white")
    plt.close(fig)
    print(f"[ok] {os.path.relpath(path, ROOT)}")

# ---------------------------------------------------------------- 图 1-2
def fig_01_rework_cost() -> None:
    t = _t("fig-01-rework-cost")
    stages = t["stages"]
    x = np.arange(1, 6)
    factor = 2.5
    no_spec = np.array([factor ** (d - 1) for d in x], dtype=float)
    with_spec = np.array([1.0, 1.6, 2.0, 2.3, 2.5])  # 规格把缺陷压在左侧两阶段

    fig, ax = plt.subplots(figsize=(7.2, 4.3), constrained_layout=True)
    ax.plot(x, no_spec, marker="o", ms=5.5, lw=2.0, color=BAD, label=t["label_nospec"])
    ax.plot(x, with_spec, marker="s", ms=5.0, lw=2.0, color=GOOD, label=t["label_spec"])

    ax.fill_between(x, with_spec, no_spec, color=BAD, alpha=0.06, linewidth=0)
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(stages)
    ax.set_xlabel(t["xlabel"])
    ax.set_ylabel(t["ylabel"])
    ax.set_title(t["title"], loc="left")

    offsets = [(9, 9), (-34, 12), (-20, 14), (-18, 13), (-36, 8)]
    for xi, yi, off in zip(x, no_spec, offsets):
        ax.annotate(t["factor"].format(v=yi), (xi, yi), textcoords="offset points", xytext=off,
                    fontsize=8.5, color=BAD)
    ax.annotate(t["annotation"],
                xy=(2.05, 2.6), xytext=(2.6, 12), fontsize=9, color=INK,
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.0,
                                connectionstyle="arc3,rad=-0.18"))
    ax.set_ylim(0.8, 34)
    ax.legend(loc="upper left", fontsize=9)
    _note(fig, t["note"])
    _save(fig, "fig-01-rework-cost")

# ---------------------------------------------------------------- 图 7-2
def fig_07_batch_size() -> None:
    t = _t("fig-01-batch-size")
    n = np.arange(1, 13)
    context = 1 - np.exp(-n / 4.2)          # 上下文占用：先陡后饱和
    # U 形：太小攒集成债，太大撑爆上下文；不对称，右侧更陡
    rework = np.where(n <= 3, 0.24 + 0.055 * (n - 3) ** 2, 0.24 + 0.0075 * (n - 3) ** 2)

    fig, ax = plt.subplots(figsize=(7.2, 4.3), constrained_layout=True)
    ax.plot(n, context, marker="o", ms=4.5, lw=2.0, color=GOOD, label=t["label_context"])
    ax.plot(n, rework, marker="s", ms=4.0, lw=2.0, color=BAD, label=t["label_rework"])

    ax.axvspan(2, 4, color=GOOD, alpha=0.07, linewidth=0)
    ax.annotate(t["annotation"],
                xy=(3.0, 0.245), xytext=(1.05, 0.075), fontsize=9, color=INK,
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.0,
                                connectionstyle="arc3,rad=0.15"))

    ax.set_xticks(n)
    ax.set_xlabel(t["xlabel"])
    ax.set_ylabel(t["ylabel"])
    ax.set_ylim(0, 1.05)
    ax.set_title(t["title"], loc="left")
    ax.legend(loc="upper left", fontsize=9)
    _note(fig, t["note"])
    _save(fig, "fig-01-batch-size")

# ---------------------------------------------------------------- 图 9-2
def fig_09_first_pass() -> None:
    t = _t("fig-01-first-pass")
    rng = np.random.default_rng(20261019)
    weeks = np.arange(1, 13)
    baseline = 0.38 + 0.012 * weeks + rng.normal(0, 0.035, weeks.size)
    adopted = 0.52 + 0.26 * (1 - np.exp(-weeks / 3.2)) + rng.normal(0, 0.028, weeks.size)

    fig, ax = plt.subplots(figsize=(7.2, 4.3), constrained_layout=True)
    ax.plot(weeks, baseline, marker="o", ms=4.5, lw=1.8, color=BAD, label=t["label_baseline"])
    ax.plot(weeks, adopted, marker="s", ms=4.2, lw=2.0, color=GOOD, label=t["label_adopted"])

    ax.axhline(0.5, color=MUTED, lw=1.0, ls=(0, (4, 3)))
    ax.text(12.35, 0.5, t["note_lo"], fontsize=7.8, color=MUTED,
            va="center", ha="left", bbox=dict(fc="white", ec="none", pad=1.5))
    ax.axhline(0.9, color=MUTED, lw=1.0, ls=(0, (1, 3)))
    ax.text(12.35, 0.9, t["note_hi"], fontsize=7.8, color=MUTED,
            va="center", ha="left", bbox=dict(fc="white", ec="none", pad=1.5))

    ax.set_xticks(weeks)
    ax.set_xlabel(t["xlabel"])
    ax.set_ylabel(t["ylabel"])
    ax.set_ylim(0.2, 1.0)
    ax.set_xlim(0.3, 14.6)
    ax.set_yticks(np.arange(0.2, 1.01, 0.1))
    ax.set_yticklabels([f"{v:.0%}" for v in np.arange(0.2, 1.01, 0.1)])
    ax.set_title(t["title"], loc="left")
    ax.legend(loc="lower right", fontsize=9)
    _note(fig, t["note"])
    _save(fig, "fig-01-first-pass")

# ---------------------------------------------------------------- 图 12-2
def fig_12_cognitive_debt() -> None:
    t = _t("fig-01-cognitive-debt")
    weeks = np.arange(0, 27)
    no_spec = 8 + 1.1 * weeks + 0.055 * weeks ** 2
    with_spec = 8 + 0.55 * weeks + 0.008 * weeks ** 2

    fig, ax = plt.subplots(figsize=(7.2, 4.3), constrained_layout=True)
    ax.plot(weeks, no_spec, lw=2.0, color=BAD, label=t["label_nospec"])
    ax.plot(weeks, with_spec, lw=2.0, color=GOOD, label=t["label_spec"])

    y13 = 8 + 1.1 * 13 + 0.055 * 13 ** 2
    ax.annotate(t["annotation"].format(y13=y13),
                xy=(13, y13), xytext=(1.4, 52), fontsize=8.4,
                color=INK, arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.0))

    ax.set_xlabel(t["xlabel"])
    ax.set_ylabel(t["ylabel"])
    ax.set_title(t["title"], loc="left")
    ax.legend(loc="upper left", fontsize=9)
    _note(fig, t["note"])
    _save(fig, "fig-01-cognitive-debt")

def main() -> None:
    global LANG
    ap = argparse.ArgumentParser(description="Generate phase2 figures.")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh", help="figure text language")
    args = ap.parse_args()
    LANG = args.lang
    plt.rcParams["font.sans-serif"] = FONT_STACKS[LANG]
    fig_01_rework_cost()
    fig_07_batch_size()
    fig_09_first_pass()
    fig_12_cognitive_debt()

if __name__ == "__main__":
    main()
