#!/usr/bin/env python3
"""生成《先写规格，再让 AI 动手》全书的定量示意图。

纪律：
- 所有曲线都是**教学模型示意**，不是实证数据；图内必须标注假设。
- 中文字体走 PingFang SC -> Heiti SC -> STHeiti 兜底（macOS 无 Noto Sans CJK）。
- 白底、细线、无渐变、无阴影；颜色只承担语义（青绿=规格生效，赭石=返工）。
"""

from __future__ import annotations

import math
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # phase2/

INK = "#1F2937"
MUTED = "#6B7280"
RULE = "#D8DEE6"
GOOD = "#0E7C66"
BAD = "#B45309"
FILL = "#F7F8FA"

plt.rcParams.update(
    {
        "font.sans-serif": ["PingFang SC", "Heiti SC", "STHeiti", "Arial Unicode MS"],
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


def _note(fig, text: str) -> None:
    """图下方的模型示意声明，避免被当成实证数据。"""
    fig.text(0.995, -0.075, text, ha="right", va="bottom", fontsize=7.5, color=MUTED)


def _save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.28, facecolor="white")
    plt.close(fig)
    print(f"[ok] {path.relative_to(ROOT)}")


# ---------------------------------------------------------------- 图 1-2
def fig_01_rework_cost() -> None:
    stages = ["写规格时", "生成后评审", "联调阶段", "灰度发布", "线上事故"]
    x = np.arange(1, 6)
    factor = 2.5
    no_spec = np.array([factor ** (d - 1) for d in x], dtype=float)
    with_spec = np.array([1.0, 1.6, 2.0, 2.3, 2.5])  # 规格把缺陷压在左侧两阶段

    fig, ax = plt.subplots(figsize=(7.2, 4.3), constrained_layout=True)
    ax.plot(x, no_spec, marker="o", ms=5.5, lw=2.0, color=BAD, label="无规格：缺陷按默认值散落")
    ax.plot(x, with_spec, marker="s", ms=5.0, lw=2.0, color=GOOD, label="有规格：缺陷被拉回左侧")

    ax.fill_between(x, with_spec, no_spec, color=BAD, alpha=0.06, linewidth=0)
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(stages)
    ax.set_xlabel("缺陷被发现的阶段（越往右越晚）")
    ax.set_ylabel("相对修复成本（对数轴，写规格时=1）")
    ax.set_title("同一处缺陷，晚发现一个阶段，成本乘 2.5", loc="left")

    offsets = [(9, 9), (-34, 12), (-20, 14), (-18, 13), (-36, 8)]
    for xi, yi, off in zip(x, no_spec, offsets):
        ax.annotate(f"{yi:g}×", (xi, yi), textcoords="offset points", xytext=off,
                    fontsize=8.5, color=BAD)
    ax.annotate("规格的作用点\n不是让 AI 更聪明，\n是把 d 从 4 拉回 1",
                xy=(2.05, 2.6), xytext=(2.6, 12), fontsize=9, color=INK,
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.0,
                                connectionstyle="arc3,rad=-0.18"))
    ax.set_ylim(0.8, 34)
    ax.legend(loc="upper left", fontsize=9)
    _note(fig, "教学模型：C(d)=2.5^(d-1)，参数为假设值，非实测数据")
    _save(fig, ROOT / "assets/ch01/fig-02-rework-cost.png")


# ---------------------------------------------------------------- 图 7-2
def fig_07_batch_size() -> None:
    n = np.arange(1, 13)
    context = 1 - np.exp(-n / 4.2)          # 上下文占用：先陡后饱和
    # U 形：太小攒集成债，太大撑爆上下文；不对称，右侧更陡
    rework = np.where(n <= 3, 0.24 + 0.055 * (n - 3) ** 2, 0.24 + 0.0075 * (n - 3) ** 2)

    fig, ax = plt.subplots(figsize=(7.2, 4.3), constrained_layout=True)
    ax.plot(n, context, marker="o", ms=4.5, lw=2.0, color=GOOD, label="上下文占用（归一化）")
    ax.plot(n, rework, marker="s", ms=4.0, lw=2.0, color=BAD, label="返工概率（示意）")

    ax.axvspan(2, 4, color=GOOD, alpha=0.07, linewidth=0)
    ax.annotate("2–4 个任务/批：返工最低，\n且每批都能独立验收",
                xy=(3.0, 0.245), xytext=(1.05, 0.075), fontsize=9, color=INK,
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.0,
                                connectionstyle="arc3,rad=0.15"))

    ax.set_xticks(n)
    ax.set_xlabel("单次 implement 的任务数")
    ax.set_ylabel("归一化数值（0–1）")
    ax.set_ylim(0, 1.05)
    ax.set_title("批次太小会攒集成债，太大会丢上下文", loc="left")
    ax.legend(loc="upper left", fontsize=9)
    _note(fig, "教学模型：占用 1-e^(-n/4.2)，返工为 U 形假设，非实测数据")
    _save(fig, ROOT / "assets/ch07/fig-02-batch-size.png")


# ---------------------------------------------------------------- 图 9-2
def fig_09_first_pass() -> None:
    rng = np.random.default_rng(20261019)
    weeks = np.arange(1, 13)
    baseline = 0.38 + 0.012 * weeks + rng.normal(0, 0.035, weeks.size)
    adopted = 0.52 + 0.26 * (1 - np.exp(-weeks / 3.2)) + rng.normal(0, 0.028, weeks.size)

    fig, ax = plt.subplots(figsize=(7.2, 4.3), constrained_layout=True)
    ax.plot(weeks, baseline, marker="o", ms=4.5, lw=1.8, color=BAD, label="只看感觉（无规格基线）")
    ax.plot(weeks, adopted, marker="s", ms=4.2, lw=2.0, color=GOOD, label="按规格验收")

    ax.axhline(0.5, color=MUTED, lw=1.0, ls=(0, (4, 3)))
    ax.text(12.35, 0.5, "0.5 以下：规格有系统性缺口", fontsize=7.8, color=MUTED,
            va="center", ha="left", bbox=dict(fc="white", ec="none", pad=1.5))
    ax.axhline(0.9, color=MUTED, lw=1.0, ls=(0, (1, 3)))
    ax.text(12.35, 0.9, "0.9 以上：怀疑过规格", fontsize=7.8, color=MUTED,
            va="center", ha="left", bbox=dict(fc="white", ec="none", pad=1.5))

    ax.set_xticks(weeks)
    ax.set_xlabel("连续交付的周数")
    ax.set_ylabel("首轮验收率")
    ax.set_ylim(0.2, 1.0)
    ax.set_xlim(0.3, 14.6)
    ax.set_yticks(np.arange(0.2, 1.01, 0.1))
    ax.set_yticklabels([f"{v:.0%}" for v in np.arange(0.2, 1.01, 0.1)])
    ax.set_title("首轮验收率：规格的收益在第 3–5 周才显形", loc="left")
    ax.legend(loc="lower right", fontsize=9)
    _note(fig, "示例数据：固定随机种子生成，用于演示读图方式，不代表任何团队实测")
    _save(fig, ROOT / "assets/ch09/fig-02-first-pass.png")


# ---------------------------------------------------------------- 图 12-2
def fig_12_cognitive_debt() -> None:
    weeks = np.arange(0, 27)
    no_spec = 8 + 1.1 * weeks + 0.055 * weeks ** 2
    with_spec = 8 + 0.55 * weeks + 0.008 * weeks ** 2

    fig, ax = plt.subplots(figsize=(7.2, 4.3), constrained_layout=True)
    ax.plot(weeks, no_spec, lw=2.0, color=BAD, label="无规格：靠人和对话记忆")
    ax.plot(weeks, with_spec, lw=2.0, color=GOOD, label="有规格：靠可检索的判据")

    y13 = 8 + 1.1 * 13 + 0.055 * 13 ** 2
    ax.annotate(f"第 13 周：回答「为什么取消后要延迟 15 分钟」\n无规格组要翻 {y13:.0f} 分钟代码，有规格组查判据约 15 分钟",
                xy=(13, y13), xytext=(1.4, 52), fontsize=8.4,
                color=INK, arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.0))

    ax.set_xlabel("项目已交付的周数")
    ax.set_ylabel("回答一个「为什么」所需的分钟数")
    ax.set_title("认知债：规格不写，债不会消失，只是转嫁给三个月后的你", loc="left")
    ax.legend(loc="upper left", fontsize=9)
    _note(fig, "教学模型：二次增长假设，参数为示意值，非实测数据")
    _save(fig, ROOT / "assets/ch12/fig-02-cognitive-debt.png")


if __name__ == "__main__":
    fig_01_rework_cost()
    fig_07_batch_size()
    fig_09_first_pass()
    fig_12_cognitive_debt()
