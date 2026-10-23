#!/usr/bin/env python3
"""生成《Vibe Coding 教材·阶段 1》全部配图。

设计约束:
  1. 白底、细线、单一强调色, 不放装饰性渐变
  2. 中文字体显式回退到 Hiragino Sans GB / Arial Unicode MS
  3. 每张图都标注"实测数据"还是"定性示意"——不允许把示意画成数据

运行: python3 code/make_figures.py
输出: assets/chXX/fig-YY-*.png (240 dpi)
"""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

matplotlib.use("Agg")

plt.rcParams["font.sans-serif"] = [
    "Hiragino Sans GB",
    "Arial Unicode MS",
    "STHeiti",
    "PingFang SC",
    "DejaVu Sans",
]
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

INK = "#1F2933"
MUTED = "#7B8794"
GRID = "#E4E7EB"
FAST = "#2A9D8F"      # 变快
SLOW = "#C2571A"      # 变慢
SAND = "#E9C46A"
STEEL = "#3D5A80"
PAPER = "#F7F9FB"

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"


def save(fig, rel: str) -> None:
    path = ASSETS / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.28, facecolor="white")
    plt.close(fig)
    print(f"  ✓ {rel}")


def stamp(fig, text: str) -> None:
    fig.text(0.005, -0.035, text, fontsize=8.5, color=MUTED, ha="left", va="top")


def box(ax, x, y, w, h, label, fc=PAPER, ec="#B8C1CC", fs=10.5, bold=False, tc=INK):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.012,rounding_size=0.02",
            linewidth=1.1, edgecolor=ec, facecolor=fc, zorder=2,
        )
    )
    ax.text(
        x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs,
        color=tc, fontweight="bold" if bold else "normal", zorder=3, linespacing=1.45,
    )


def arrow(ax, xy_from, xy_to, color="#8A94A6", style="-|>", lw=1.4, rad=0.0, ls="-"):
    ax.add_patch(
        FancyArrowPatch(
            xy_from, xy_to, arrowstyle=style, mutation_scale=13,
            linewidth=lw, color=color, connectionstyle=f"arc3,rad={rad}",
            linestyle=ls, zorder=1, shrinkA=2, shrinkB=2,
        )
    )


# ---------------------------------------------------------------- ch01 · fig 01
def fig_perception_gap() -> None:
    labels = ["开发者事前预测", "开发者事后自评", "秒表实测"]
    vals = [-24, -20, 19]
    colors = [FAST, FAST, SLOW]

    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    y = np.arange(len(labels))[::-1]
    bars = ax.barh(y, vals, color=colors, height=0.46, edgecolor="none", zorder=3)

    for yi, v, c in zip(y, vals, colors):
        ax.text(
            v + (2.4 if v > 0 else -2.4), yi,
            f"{v:+d}%",
            va="center", ha="left" if v > 0 else "right",
            fontsize=13, fontweight="bold", color=c,
        )

    ax.axvline(0, color=INK, linewidth=1.2, zorder=4)
    ax.axvspan(0, 32, color=SLOW, alpha=0.05, zorder=0)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=11.5)
    ax.set_xlim(-44, 34)
    ax.set_xlabel("同一批任务、同一批人：完成时间的变化（正数 = 更慢）", fontsize=10.5)
    ax.set_title(
        "感觉与秒表的符号相反：主观上“快了”，客观上“慢了”",
        fontsize=14.5, fontweight="bold", pad=16, loc="left",
    )
    ax.grid(axis="x", color=GRID, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)

    ax.text(
        30.5, y[2] + 0.34, "真实交付变慢的区域", fontsize=9.5, color=SLOW,
        ha="right", va="bottom",
    )
    stamp(
        fig,
        "数据（实测）：METR 随机对照试验，2025-07-10，16 名资深开源开发者、246 个真实任务、平均 5 年仓库经验；"
        "「实测」为完成时间，正数表示比不用 AI 更慢。",
    )
    save(fig, "ch01/fig-01-perception-gap.png")


# ---------------------------------------------------------------- ch01 · fig 02
def fig_time_accounting() -> None:
    """两种记账口径：T_first vs T_true。无数值, 只画结构。"""
    fig, ax = plt.subplots(figsize=(9.6, 3.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0.28, 3.7)
    ax.axis("off")

    segs = [
        ("理解\n需求", "#C9D6DF"),
        ("写入 /\n生成", "#8FB8C9"),
        ("返工", SLOW),
        ("审查 +\n理解 diff", SAND),
    ]
    # 传统路径
    ax.text(0.02, 2.92, "手写", fontsize=11.5, fontweight="bold", color=INK, ha="left")
    x = 1.05
    widths_a = [1.15, 3.0, 0.55, 1.5]
    for (name, color), w in zip(segs, widths_a):
        ax.add_patch(
            FancyBboxPatch(
                (x, 2.5), w, 0.62,
                boxstyle="round,pad=0.008,rounding_size=0.03",
                facecolor=color, edgecolor="white", linewidth=2, alpha=0.92,
            )
        )
        ax.text(x + w / 2, 2.81, name, ha="center", va="center", fontsize=9.2, color="white",
                fontweight="bold", linespacing=1.25)
        x += w

    # AI 路径
    ax.text(0.02, 1.42, "AI\n辅助", fontsize=11.5, fontweight="bold", color=INK, ha="left",
            linespacing=1.3)
    x = 1.05
    widths_b = [0.7, 0.95, 1.35, 3.1]
    for (name, color), w in zip(segs, widths_b):
        ax.add_patch(
            FancyBboxPatch(
                (x, 1.0), w, 0.62,
                boxstyle="round,pad=0.008,rounding_size=0.03",
                facecolor=color, edgecolor="white", linewidth=2, alpha=0.92,
            )
        )
        ax.text(x + w / 2, 1.31, name, ha="center", va="center", fontsize=9.2, color="white",
                fontweight="bold", linespacing=1.25)
        x += w

    # 括号标注
    ax.annotate(
        "", xy=(2.02, 0.78), xytext=(1.05, 0.78),
        arrowprops=dict(arrowstyle="<->", color=FAST, linewidth=1.4),
    )
    ax.text(1.53, 0.62, "首次可运行（被压缩）", fontsize=9, color=FAST, ha="center", va="top")

    ax.annotate(
        "", xy=(7.15, 0.78), xytext=(2.72, 0.78),
        arrowprops=dict(arrowstyle="<->", color=SLOW, linewidth=1.4, linestyle="--"),
    )
    ax.text(4.9, 0.62, "返工 + 审查（可能被放大）", fontsize=9, color=SLOW, ha="center", va="top")

    # 口径线
    ax.annotate(
        "", xy=(8.85, 3.34), xytext=(1.05, 3.34),
        arrowprops=dict(arrowstyle="<->", color=MUTED, linewidth=1.0),
    )
    ax.text(4.95, 3.42, "T_true = 你真正交付出去所花的时间", fontsize=9.5, color=MUTED,
            ha="center", va="bottom")
    ax.annotate(
        "", xy=(8.85, 1.86), xytext=(1.05, 1.86),
        arrowprops=dict(arrowstyle="<->", color=MUTED, linewidth=1.0),
    )
    ax.text(4.95, 1.94, "T_true（同一把尺子，长度未必更短）", fontsize=9.5, color=MUTED,
            ha="center", va="bottom")

    ax.set_title("两种记账口径：你记的是“跑起来了”，秒表记的是“交付完了”",
                 fontsize=14.5, fontweight="bold", loc="left", pad=8)
    stamp(fig, "结构示意（非实测数据）：条形长度仅表示相对关系，不表示具体分钟数。")
    save(fig, "ch01/fig-03-time-accounting.png")


# ---------------------------------------------------------------- ch01 · fig 03
def fig_context_collapse() -> None:
    turns = np.arange(0, 61)

    def decay(start, k, floor):
        return floor + (1 - floor) * np.exp(-k * np.maximum(turns - start, 0))

    early = decay(0, 0.035, 0.28)
    restated = np.minimum(0.97, decay(0, 0.012, 0.62) + 0.12)

    fig, ax = plt.subplots(figsize=(9.2, 4.5))
    ax.plot(turns, early * 100, color=SLOW, linewidth=2.4,
            label="不重述：早期指令的遵循率")
    ax.plot(turns, restated * 100, color=FAST, linewidth=2.4, linestyle="--",
            label="每 10 轮重述一次关键约束")

    ax.fill_between(turns, early * 100, restated * 100, color=SLOW, alpha=0.07)

    ax.axhline(50, color="#B8C1CC", linewidth=1, linestyle=":")
    ax.text(59, 51.5, "50% 参考线", fontsize=8.8, color=MUTED, ha="right")

    ax.annotate(
        "坍缩区：规则还在窗口里，\n但已经不再是“行为约束”",
        xy=(34, early[34] * 100), xytext=(20, 76),
        fontsize=9.5, color=SLOW,
        arrowprops=dict(arrowstyle="-|>", color=SLOW, linewidth=1.2,
                        connectionstyle="arc3,rad=-0.25"),
    )
    ax.annotate(
        "重述点",
        xy=(40, restated[40] * 100), xytext=(41.5, 45),
        fontsize=9, color=FAST,
        arrowprops=dict(arrowstyle="-|>", color=FAST, linewidth=1.1),
    )

    ax.set_xlabel("会话轮次（累计对话消息数）", fontsize=10.5)
    ax.set_ylabel("约束被实际遵守的比例", fontsize=10.5)
    ax.set_ylim(20, 104)
    ax.set_xlim(0, 60)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25%", "50%", "75%", "100%"])
    ax.grid(color=GRID, linewidth=0.9)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, fontsize=10, loc="lower left")
    ax.set_title("上下文坍缩：约束不是“写过了”就有效，它需要被周期性重新加载",
                 fontsize=14, fontweight="bold", loc="left", pad=14)
    stamp(fig, "定性示意（非实测数据）：曲线形状表达机制，横纵坐标不代表任何具体测量结果。")
    save(fig, "ch01/fig-02-context-collapse.png")


# ---------------------------------------------------------------- ch02 · fig 04
def fig_context_layers() -> None:
    fig, ax = plt.subplots(figsize=(9.8, 4.6))
    ax.set_xlim(0, 10.4)
    ax.set_ylim(0.1, 5.0)
    ax.axis("off")

    layers = [
        ("L0 · 索引层", "文件树 + 每个目录一句话职责 + 入口点", "常驻 · ≤ 300 tokens",
         "#3D5A80", 3.55),
        ("L1 · 契约层", "模块边界、数据结构、不变量、命令清单", "命中模块才载入 · ≤ 1500 tokens",
         "#5B8C9E", 2.25),
        ("L2 · 全文层", "真正要改的那 1—3 个文件", "按需 · 一次不超过 3 个文件",
         "#8FB8C9", 0.95),
    ]
    for title, desc, budget, color, y in layers:
        ax.add_patch(
            FancyBboxPatch((1.05, y), 6.15, 1.05,
                           boxstyle="round,pad=0.01,rounding_size=0.04",
                           facecolor=color, edgecolor="none", alpha=0.94)
        )
        ax.text(1.35, y + 0.68, title, fontsize=12.5, fontweight="bold", color="white", va="center")
        ax.text(1.35, y + 0.28, desc, fontsize=9.3, color="#EAF0F4", va="center")
        ax.text(6.9, y + 0.52, budget, fontsize=9.0, color="#EAF0F4",
                va="center", ha="right")

    # 左侧：命中才展开
    ax.annotate("", xy=(0.72, 1.0), xytext=(0.72, 4.55),
                arrowprops=dict(arrowstyle="-|>", color=INK, linewidth=1.5))
    ax.text(0.52, 2.75, "命 中 才 展 开", fontsize=9.6, color=INK,
            rotation=90, ha="center", va="center", fontweight="bold")

    # 右侧：全塞对照
    ax.add_patch(
        FancyBboxPatch((8.05, 0.95), 1.55, 3.65,
                       boxstyle="round,pad=0.01,rounding_size=0.04",
                       facecolor=PAPER, edgecolor=SLOW, linewidth=1.3, linestyle="--")
    )
    ax.text(8.82, 4.72, "反例：全塞", fontsize=10.5, fontweight="bold", color=SLOW, ha="center")
    ax.text(8.82, 2.75,
            "整 仓 库  ≈  20 万 tokens\n有 效 注 意 力 被 稀 释",
            fontsize=8.8, color=MUTED, ha="center", va="center",
            rotation=90, linespacing=2.0)

    ax.text(1.05, 0.36,
            "顺序不能反：先给地图，再给图纸，最后给墙面。反过来，就是让模型在二十万字里自己找重点。",
            fontsize=9.6, color=MUTED)
    ax.set_title("渐进披露的三层：预算按“命中概率”分配，不按“完整度”分配",
                 fontsize=14, fontweight="bold", loc="left", pad=12)
    stamp(fig, "结构示意：token 预算为本书建议的经验值，可按模型窗口调整，不必照抄。")
    save(fig, "ch02/fig-04-context-layers.png")


# ---------------------------------------------------------------- ch03 · fig 05
def fig_harness_flow() -> None:
    fig, ax = plt.subplots(figsize=(10.2, 4.6))
    ax.set_xlim(0, 10.2)
    ax.set_ylim(0, 4.6)
    ax.axis("off")

    ax.text(1.55, 4.24, "前馈控制（生成前）", fontsize=10.5, fontweight="bold",
            color=STEEL, ha="center")
    ax.text(8.55, 4.24, "反馈控制（生成后）", fontsize=10.5, fontweight="bold",
            color=SLOW, ha="center")

    ff = ["规则文件\nAGENTS.md", "Agent Skills\n可复用工序", "规格 / 验收判据", "示例与模板\n“照着这个写”"]
    for i, t in enumerate(ff):
        box(ax, 0.25, 3.32 - i * 0.82, 2.55, 0.62, t, fc="#EDF2F6", ec=STEEL, fs=8.8)

    fb = ["编译 / 类型检查", "lint + 格式化", "单元测试 / 变异测试", "SAST / 依赖与密钥扫描", "预发布环境（人眼看）"]
    for i, t in enumerate(fb):
        box(ax, 7.35, 3.42 - i * 0.66, 2.6, 0.5, t, fc="#FBEDE6", ec=SLOW, fs=8.6)

    box(ax, 3.35, 2.35, 3.4, 0.95, "生成\n（智能体 / 补全 / 构建器）", fc="#1F2933", ec="#1F2933",
        fs=11, bold=True, tc="white")
    box(ax, 3.35, 0.85, 3.4, 0.75, "人\n（只裁决，不逐行读）", fc="#F2EFE4", ec=SAND, fs=10.5, bold=True)

    for i in range(4):
        arrow(ax, (2.85, 3.63 - i * 0.82), (3.32, 2.95), color=STEEL, lw=1.0, rad=0.12)
    for i in range(5):
        arrow(ax, (6.8, 2.85), (7.32, 3.67 - i * 0.66), color=SLOW, lw=1.0, rad=-0.12)

    arrow(ax, (5.05, 2.3), (5.05, 1.65), color=INK, lw=1.6)
    ax.text(5.15, 1.98, "通过 / 打回", fontsize=8.8, color=INK, va="center")

    ax.add_patch(
        FancyBboxPatch((0.25, 0.12), 2.55, 0.5,
                       boxstyle="round,pad=0.01,rounding_size=0.03",
                       facecolor="white", edgecolor="#B8C1CC", linestyle="--", linewidth=1.1)
    )
    ax.text(1.52, 0.37, "横切：沙箱 · 权限 · 预算上限", fontsize=8.4, color=MUTED,
            ha="center", va="center")

    ax.text(3.35, 0.42,
            "判据只有一条：能用确定性工具判定的，不要用提示词去“要求”。",
            fontsize=9.6, color=MUTED, va="center")
    ax.set_title("夹具的两半：一半负责让它“照着做”，一半负责证明它“做对了”",
                 fontsize=14, fontweight="bold", loc="left", pad=8)
    stamp(fig, "结构示意：层数与顺序可按项目裁剪，但“前馈在前、反馈在后、人来裁决”这三段不能省。")
    save(fig, "ch03/fig-05-harness-flow.png")


# ---------------------------------------------------------------- ch03 · fig 06
def fig_gate_cost() -> None:
    stages = ["本地编辑器", "pre-commit", "CI / PR", "预发布", "生产"]
    catches = [
        "语法、类型、一眼可见的蠢错",
        "lint、格式、密钥误提交",
        "测试失败、依赖与安全扫描",
        "交互与真实数据下的崩溃",
        "用户替你发现（最贵的一种）",
    ]
    relative_cost = [1, 2.5, 7, 22, 60]
    colors = ["#8FB8C9", "#6E9DB0", "#5B8C9E", "#C98B5E", SLOW]

    fig, ax = plt.subplots(figsize=(9.8, 4.6))
    y = np.arange(len(stages))[::-1]
    ax.barh(y, relative_cost, height=0.5, color=colors, edgecolor="none", zorder=3)

    for yi, c in zip(y, relative_cost):
        ax.text(c * 1.09, yi, f"≈ {c:g}×", fontsize=10.5, color=INK, fontweight="bold",
                va="center")

    ax.set_yticks(y)
    ax.set_yticklabels(
        [f"{s}\n{c}" for s, c in zip(stages, catches)],
        fontsize=9.6, linespacing=1.9,
    )
    ax.set_xscale("log")
    ax.set_xlim(0.7, 260)
    ax.set_xlabel("发现同一个缺陷时的相对修复成本（对数轴）", fontsize=10.2)
    ax.grid(axis="x", color=GRID, linewidth=0.9)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.set_title("门禁要往左放：越晚发现，代价涨得越快",
                 fontsize=14, fontweight="bold", loc="left", pad=14)
    stamp(fig, "量级示意：倍数取自业界长期引用的“缺陷左移成本”经验法则（常表述为 1:10:100），"
               "用于表达趋势而非精确测量。三条最小门禁（lint / 类型 / 单测）装在 pre-commit 与 CI / PR 两格。")
    save(fig, "ch03/fig-06-gate-cost.png")


# ---------------------------------------------------------------- ch04 · fig 07
def fig_ab_timeline() -> None:
    fig, ax = plt.subplots(figsize=(9.8, 3.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0.18, 3.24)
    ax.axis("off")

    segs = [
        ("需求理解", "#C9D6DF"),
        ("实现 / 生成", "#8FB8C9"),
        ("等待", SAND),
        ("返工", SLOW),
        ("审查 + 理解", "#5B8C9E"),
    ]
    rows = [("手写组", [1.3, 3.2, 0.0, 0.7, 1.4], 2.32),
            ("AI 组", [0.9, 1.1, 1.2, 2.3, 2.0], 1.18)]

    for label, widths, ytop in rows:
        ax.text(0.05, ytop + 0.42, label, fontsize=11.5, fontweight="bold", color=INK)
        x = 1.6
        for (name, color), w in zip(segs, widths):
            if w <= 0:
                continue
            ax.add_patch(
                FancyBboxPatch((x, ytop), w, 0.66,
                               boxstyle="round,pad=0.008,rounding_size=0.03",
                               facecolor=color, edgecolor="white", linewidth=2, alpha=0.92)
            )
            if w > 0.55:
                ax.text(x + w / 2, ytop + 0.33, name, ha="center", va="center",
                        fontsize=8.4 if w < 1.0 else 9.0, color="white", fontweight="bold")
            x += w
        ax.annotate("", xy=(x + 0.12, ytop + 0.33), xytext=(x + 0.02, ytop + 0.33),
                    arrowprops=dict(arrowstyle="-|>", color=MUTED, linewidth=1.2))
        ax.text(x + 0.2, ytop + 0.33, "T_true", fontsize=9, color=MUTED, va="center")

    ax.text(1.6, 0.62,
            "五个格子，五条秒表读数。缺任何一格，你的结论就会偏——多数人只记第二格。",
            fontsize=9.4, color=MUTED)
    ax.text(1.6, 0.34,
            "注意“等待”这一格：AI 组会凭空多出它，而它极易被记忆抹掉（你去倒了杯水）。",
            fontsize=9.4, color=SLOW)

    ax.set_title("A/B 实验的记录模板：把一次任务切成五段，别只记“写完那一刻”",
                 fontsize=14, fontweight="bold", loc="left", pad=8)
    stamp(fig, "模板示意：宽度不代表任何实测结果，实际填数请用 code/ch04/ab_log.py。")
    save(fig, "ch04/fig-07-ab-timeline.png")


def main() -> None:
    print("生成配图：")
    fig_perception_gap()
    fig_time_accounting()
    fig_context_collapse()
    fig_context_layers()
    fig_harness_flow()
    fig_gate_cost()
    fig_ab_timeline()
    print("完成。")


if __name__ == "__main__":
    main()
