#!/usr/bin/env python3
"""阶段 5 教材配图的统一样式与绘图助手。

设计约束（与 README 第 8 节一致）：
  1. 白底、细线、单一强调色，不做装饰性渐变
  2. 中文字体显式回退（macOS 无 Noto Sans CJK，直接用 Hiragino Sans GB）
  3. 每张图必须标清是「实测 / 条文 / 仿真 / 结构示意」——不允许把示意画成数据
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

matplotlib.use("Agg")

FONT_STACKS = {
    "zh": [
        "Hiragino Sans GB",
        "Arial Unicode MS",
        "STHeiti",
        "PingFang SC",
        "Heiti SC",
        "DejaVu Sans",
    ],
    "en": [
        "Arial Unicode MS",
        "Helvetica",
        "Arial",
        "DejaVu Sans",
    ],
}

plt.rcParams["font.sans-serif"] = FONT_STACKS["zh"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 200
plt.rcParams["savefig.dpi"] = 240
plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["axes.edgecolor"] = "#CBD2D9"
plt.rcParams["axes.labelcolor"] = "#1F2933"
plt.rcParams["text.color"] = "#1F2933"
plt.rcParams["xtick.color"] = "#52606D"
plt.rcParams["ytick.color"] = "#52606D"
plt.rcParams["legend.frameon"] = False


def apply(lang="zh"):
    """字体栈按语言切换——语言差异只允许出现在取文案与这里。"""
    plt.rcParams["font.sans-serif"] = FONT_STACKS[lang]


# ---- 语义色（不按好看选，按含义选）----------------------------------------
INK = "#1F2933"      # 主文字
MUTED = "#7B8794"    # 图注、口径
GOOD = "#2A9D8F"     # 安全、可回滚、在预算内
BAD = "#C2571A"      # 风险、不可逆、超支
STEEL = "#3D5A80"    # 结构、流程
SAND = "#E9C46A"     # 关键数字、阈值
GRID = "#E4E7EB"
PAPER = "#F7F9FB"

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"


def save(fig, path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.3, facecolor="white")
    plt.close(fig)
    print(f"  ok  {path.name}")


def stamp(fig, text: str) -> None:
    """图注/口径声明，固定放在图下方左侧。"""
    fig.text(0.005, -0.045, text, fontsize=8.4, color=MUTED, ha="left", va="top")


def box(ax, x, y, w, h, label, fc=PAPER, ec="#B8C1CC", fs=10.0,
        bold=False, tc=INK, ls="-", lw=1.1):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.010,rounding_size=0.02",
            linewidth=lw, edgecolor=ec, facecolor=fc, linestyle=ls, zorder=2,
        )
    )
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold" if bold else "normal",
            zorder=3, linespacing=1.45)


def arrow(ax, xy_from, xy_to, color="#8A94A6", lw=1.4, rad=0.0, ls="-",
          style="-|>", scale=13):
    ax.add_patch(
        FancyArrowPatch(
            xy_from, xy_to, arrowstyle=style, mutation_scale=scale,
            linewidth=lw, color=color,
            connectionstyle=f"arc3,rad={rad}", linestyle=ls,
            zorder=1, shrinkA=2, shrinkB=2,
        )
    )


def blank(ax, xlim, ylim):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")


def clean_axes(ax, grid_axis="y"):
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.9)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
