"""共享绘图样式 —— 全书统一，改一处全本生效。

配色纪律：白底、无渐变、无阴影；警示红只用于"这里有坑"，
通过绿只用于"这一层真的守住了"，中性灰用于对照项。
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent

INK = "#1F2937"
MUTED = "#6B7280"
RULE = "#D1D5DB"
ACCENT = "#B3261E"
NEUTRAL = "#94A3B8"
GOOD = "#0F6B5C"
WASH = "#F9FAFB"

FONT_STACKS = {
    "zh": [
        "Hiragino Sans GB",
        "Arial Unicode MS",
        "Heiti SC",
        "Songti SC",
        "Noto Sans CJK SC",
        "DejaVu Sans",
    ],
    "en": [
        "Arial Unicode MS",
        "Helvetica",
        "Arial",
        "DejaVu Sans",
    ],
}


def apply(lang="zh"):
    plt.rcParams["font.sans-serif"] = FONT_STACKS[lang]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 200
    plt.rcParams["savefig.dpi"] = 240
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"


def clean(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(RULE)
    ax.tick_params(colors=MUTED, labelsize=9, length=0)


def titles(ax, main, sub):
    ax.set_title(main, loc="left", fontsize=12.5, color=INK, pad=20, fontweight="bold")
    ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=9.5, color=MUTED, va="bottom")


def footnote(fig, text, note=None):
    fig.text(0.012, 0.005, text, fontsize=8, color=MUTED)
    if note:
        fig.text(0.012, -0.028, note, fontsize=8, color=ACCENT)
