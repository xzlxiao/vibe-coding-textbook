#!/usr/bin/env python3
"""生成《Vibe Coding 教材·阶段 1》全部配图。

设计约束:
  1. 白底、细线、单一强调色, 不放装饰性渐变
  2. 中文字体显式回退到 Hiragino Sans GB / Arial Unicode MS
  3. 每张图都标注"实测数据"还是"定性示意"——不允许把示意画成数据

运行: python3 code/make_figures.py [--lang zh|en]
输出: assets/chXX/fig-YY-*.png (240 dpi)

双语机制（A1′）：--lang zh|en（默认 zh）；每图文案在模块级 T 字典；
几何代码与语言无关，语言差异只在 _t（取文案）与字体栈两处。
"""

import argparse
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

matplotlib.use("Agg")

LANG = "zh"

FONT_STACKS = {
    "zh": [
        "Hiragino Sans GB",
        "Arial Unicode MS",
        "STHeiti",
        "PingFang SC",
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
STAGING = ROOT.parent / ".omc" / "work" / "bilingual-figures-en"  # en 同名互斥图暂存位（阶段 1）

# 输出名映射（阶段 1：zh 走旧名原位重生成，en 走终态名；改号映射见
# .omc/work/bilingual-baseline/05-renumber-map-26.md，阶段 2 提交 (i) 与 git mv 同批切 .zh 名）
OLD_REL = {
    "fig-01-perception-gap": "ch01/fig-01-perception-gap.png",
    "fig-02-context-collapse": "ch01/fig-02-context-collapse.png",
    "fig-03-time-accounting": "ch01/fig-03-time-accounting.png",
    "fig-01-context-layers": "ch02/fig-04-context-layers.png",
    "fig-01-harness-flow": "ch03/fig-05-harness-flow.png",
    "fig-02-gate-cost": "ch03/fig-06-gate-cost.png",
    "fig-01-ab-timeline": "ch04/fig-07-ab-timeline.png",
}
FINAL_REL = {
    "fig-01-perception-gap": "ch01/fig-01-perception-gap.png",
    "fig-02-context-collapse": "ch01/fig-02-context-collapse.png",
    "fig-03-time-accounting": "ch01/fig-03-time-accounting.png",
    "fig-01-context-layers": "ch02/fig-01-context-layers.png",
    "fig-01-harness-flow": "ch03/fig-01-harness-flow.png",
    "fig-02-gate-cost": "ch03/fig-02-gate-cost.png",
    "fig-01-ab-timeline": "ch04/fig-01-ab-timeline.png",
}

# 每图双语文案（图内标注文案的单一事实源）
T = {
    "fig-01-perception-gap": {
        "zh": {
            "labels": ["开发者事前预测", "开发者事后自评", "秒表实测"],
            "xlabel": "同一批任务、同一批人：完成时间的变化（正数 = 更慢）",
            "title": "感觉与秒表的符号相反：主观上“快了”，客观上“慢了”",
            "region": "真实交付变慢的区域",
            "stamp": "数据（实测）：METR 随机对照试验，2025-07-10，16 名资深开源开发者、246 个真实任务、平均 5 年仓库经验；"
                     "「实测」为完成时间，正数表示比不用 AI 更慢。",
        },
        "en": {
            "labels": ["Developers' upfront prediction", "Developers' after-the-fact rating", "Stopwatch measurement"],
            "xlabel": "Same tasks, same people: change in completion time (positive = slower)",
            "title": "Feeling and stopwatch disagree: subjectively faster, objectively slower",
            "region": "Region where delivery truly got slower",
            "stamp": "Data (measured): METR randomized controlled trial, 2025-07-10; 16 senior OSS developers, "
                     "246 real tasks, avg 5 years of repo experience; measured = completion time, positive means slower than without AI.",
        },
    },
    "fig-03-time-accounting": {
        "zh": {
            "segs": ["理解\n需求", "写入 /\n生成", "返工", "审查 +\n理解 diff"],
            "row_hand": "手写",
            "row_ai": "AI\n辅助",
            "bracket_first": "首次可运行（被压缩）",
            "bracket_rest": "返工 + 审查（可能被放大）",
            "rule_true": "T_true = 你真正交付出去所花的时间",
            "rule_note": "T_true（同一把尺子，长度未必更短）",
            "title": "两种记账口径：你记的是“跑起来了”，秒表记的是“交付完了”",
            "stamp": "结构示意（非实测数据）：条形长度仅表示相对关系，不表示具体分钟数。",
        },
        "en": {
            "segs": ["Understand\nrequirements", "Write /\ngenerate", "Rework", "Review +\nunderstand diff"],
            "row_hand": "Hand-\nwritten",
            "row_ai": "AI-\nassisted",
            "bracket_first": "First runnable (compressed)",
            "bracket_rest": "Rework + review (possibly amplified)",
            "rule_true": "T_true = the time you actually spend delivering",
            "rule_note": "T_true (same yardstick, not necessarily shorter)",
            "title": "Two ways to keep the books: you count \"it runs\", the stopwatch counts \"delivered\"",
            "stamp": "Structural illustration (not measured data): bar lengths show relative relations only, not minutes.",
        },
    },
    "fig-02-context-collapse": {
        "zh": {
            "label_early": "不重述：早期指令的遵循率",
            "label_restate": "每 10 轮重述一次关键约束",
            "ref50": "50% 参考线",
            "collapse": "坍缩区：规则还在窗口里，\n但已经不再是“行为约束”",
            "point": "重述点",
            "xlabel": "会话轮次（累计对话消息数）",
            "ylabel": "约束被实际遵守的比例",
            "title": "上下文坍缩：约束不是“写过了”就有效，它需要被周期性重新加载",
            "stamp": "定性示意（非实测数据）：曲线形状表达机制，横纵坐标不代表任何具体测量结果。",
        },
        "en": {
            "label_early": "No restatement: adherence to early instructions",
            "label_restate": "Restate key constraints every 10 turns",
            "ref50": "50% reference line",
            "collapse": "Collapse zone: the rule is still in the window,\nbut no longer a behavioral constraint",
            "point": "Restatement point",
            "xlabel": "Conversation turns (cumulative messages)",
            "ylabel": "Share of constraints actually followed",
            "title": "Context collapse: \"written once\" is not \"in effect\" — constraints need periodic reloading",
            "stamp": "Qualitative illustration (not measured data): curve shape expresses the mechanism; axes carry no measurements.",
        },
    },
    "fig-01-context-layers": {
        "zh": {
            "layers": [
                ("L0 · 索引层", "文件树 + 每个目录一句话职责 + 入口点", "常驻 · ≤ 300 tokens"),
                ("L1 · 契约层", "模块边界、数据结构、不变量、命令清单", "命中模块才载入 · ≤ 1500 tokens"),
                ("L2 · 全文层", "真正要改的那 1—3 个文件", "按需 · 一次不超过 3 个文件"),
            ],
            "expand": "命 中 才 展 开",
            "counter": "反例：全塞",
            "counter_note": "整 仓 库  ≈  20 万 tokens\n有 效 注 意 力 被 稀 释",
            "order": "顺序不能反：先给地图，再给图纸，最后给墙面。反过来，就是让模型在二十万字里自己找重点。",
            "title": "渐进披露的三层：预算按“命中概率”分配，不按“完整度”分配",
            "stamp": "结构示意：token 预算为本书建议的经验值，可按模型窗口调整，不必照抄。",
        },
        "en": {
            "layers": [
                ("L0 · Index layer", "File tree + one-line duty per directory + entry points", "Resident · ≤ 300 tokens"),
                ("L1 · Contract layer", "Module boundaries, data structures, invariants, command list", "Loaded on hit · ≤ 1500 tokens"),
                ("L2 · Full-text layer", "The 1–3 files you actually change", "On demand · at most 3 files at once"),
            ],
            "expand": "E X P A N D   O N   H I T",
            "counter": "Counter-example: stuff it all in",
            "counter_note": "W H O L E   R E P O  ≈  200k tokens\nA T T E N T I O N   G E T S   D I L U T E D",
            "order": "Order matters: map first, then blueprints, then the walls. Reverse it and the model hunts for focus in 200k tokens.",
            "title": "Progressive disclosure: budget by hit probability, not by completeness",
            "stamp": "Structural illustration: token budgets are this book's suggested heuristics; adjust to your model window, don't copy blindly.",
        },
    },
    "fig-01-harness-flow": {
        "zh": {
            "feedforward": "前馈控制（生成前）",
            "feedback": "反馈控制（生成后）",
            "ff": ["规则文件\nAGENTS.md", "Agent Skills\n可复用工序", "规格 / 验收判据", "示例与模板\n“照着这个写”"],
            "fb": ["编译 / 类型检查", "lint + 格式化", "单元测试 / 变异测试", "SAST / 依赖与密钥扫描", "预发布环境（人眼看）"],
            "generation": "生成\n（智能体 / 补全 / 构建器）",
            "human": "人\n（只裁决，不逐行读）",
            "verdict": "通过 / 打回",
            "crosscut": "横切：沙箱 · 权限 · 预算上限",
            "criterion": "判据只有一条：能用确定性工具判定的，不要用提示词去“要求”。",
            "title": "夹具的两半：一半负责让它“照着做”，一半负责证明它“做对了”",
            "stamp": "结构示意：层数与顺序可按项目裁剪，但“前馈在前、反馈在后、人来裁决”这三段不能省。",
        },
        "en": {
            "feedforward": "Feedforward control (before generation)",
            "feedback": "Feedback control (after generation)",
            "ff": ["Rules file\nAGENTS.md", "Agent Skills\nreusable procedures", "Spec / acceptance criteria", "Examples & templates\n\"write it like this\""],
            "fb": ["Compile / type-check", "lint + formatting", "Unit tests / mutation tests", "SAST / dependency & secret scans", "Pre-release env (human eyes)"],
            "generation": "Generation\n(agent / completion / builder)",
            "human": "Human\n(judges only, no line-by-line reading)",
            "verdict": "Pass / send back",
            "crosscut": "Cross-cutting: sandbox · permissions · budget caps",
            "criterion": "One criterion only: what deterministic tools can judge, never \"ask\" for it in a prompt.",
            "title": "The harness has two halves: one makes it follow, one proves it right",
            "stamp": "Structural illustration: layers and order can be trimmed per project, but \"feedforward first, feedback after, human decides\" cannot be cut.",
        },
    },
    "fig-02-gate-cost": {
        "zh": {
            "stages": ["本地编辑器", "pre-commit", "CI / PR", "预发布", "生产"],
            "catches": ["语法、类型、一眼可见的蠢错", "lint、格式、密钥误提交", "测试失败、依赖与安全扫描",
                        "交互与真实数据下的崩溃", "用户替你发现（最贵的一种）"],
            "factor": "≈ {v:g}×",
            "xlabel": "发现同一个缺陷时的相对修复成本（对数轴）",
            "title": "门禁要往左放：越晚发现，代价涨得越快",
            "stamp": "量级示意：倍数取自业界长期引用的“缺陷左移成本”经验法则（常表述为 1:10:100），"
                     "用于表达趋势而非精确测量。三条最小门禁（lint / 类型 / 单测）装在 pre-commit 与 CI / PR 两格。",
        },
        "en": {
            "stages": ["Local editor", "pre-commit", "CI / PR", "Pre-release", "Production"],
            "catches": ["Syntax, types, obvious blunders", "lint, formatting, committed secrets",
                        "Test failures, dependency & security scans", "Crashes under real interaction and data",
                        "Users find it (the most expensive kind)"],
            "factor": "≈ {v:g}×",
            "xlabel": "Relative fix cost for the same defect (log scale)",
            "title": "Put gates left: the later the discovery, the faster the cost explodes",
            "stamp": "Order-of-magnitude illustration: multipliers from the long-cited shift-left cost rule of thumb (often 1:10:100), "
                     "expressing trend, not precise measurement. The three minimal gates (lint / types / unit tests) sit in pre-commit and CI / PR.",
        },
    },
    "fig-01-ab-timeline": {
        "zh": {
            "segs": ["需求理解", "实现 / 生成", "等待", "返工", "审查 + 理解"],
            "row_hand": "手写组",
            "row_ai": "AI 组",
            "note1": "五个格子，五条秒表读数。缺任何一格，你的结论就会偏——多数人只记第二格。",
            "note2": "注意“等待”这一格：AI 组会凭空多出它，而它极易被记忆抹掉（你去倒了杯水）。",
            "title": "A/B 实验的记录模板：把一次任务切成五段，别只记“写完那一刻”",
            "stamp": "模板示意：宽度不代表任何实测结果，实际填数请用 code/ch04/ab_log.py。",
        },
        "en": {
            "segs": ["Understand\nrequirements", "Implement /\ngenerate", "Waiting", "Rework", "Review +\nunderstand"],
            "row_hand": "Hand-written group",
            "row_ai": "AI group",
            "note1": "Five cells, five stopwatch readings. Miss any one and your conclusion drifts — most people only log the second.",
            "note2": "Watch the waiting cell: the AI group grows it out of thin air, and memory erases it (you went for water).",
            "title": "A/B experiment log template: cut one task into five segments, don't just log \"done\"",
            "stamp": "Template illustration: widths carry no measurements; fill real numbers with code/ch04/ab_log.py.",
        },
    },
}


def _t(fig_id: str) -> dict:
    """取文案——语言差异只允许出现在这里与字体栈。"""
    return T[fig_id][LANG]


def _out(fig_id: str) -> Path:
    if LANG == "zh":
        path = ASSETS / OLD_REL[fig_id]
    else:
        rel = FINAL_REL[fig_id]
        if rel == OLD_REL[fig_id]:
            # en 终态名与 zh 旧名互斥：暂存 .omc/work，阶段 2 提交 (i) zh 让名后 cp 落位
            path = STAGING / "phase1" / "assets" / rel
        else:
            path = ASSETS / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def save(fig, fig_id: str) -> None:
    path = _out(fig_id)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.28, facecolor="white")
    plt.close(fig)
    print(f"  ✓ {path.name}")


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
    t = _t("fig-01-perception-gap")
    labels = t["labels"]
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
    ax.set_xlabel(t["xlabel"], fontsize=10.5)
    ax.set_title(
        t["title"],
        fontsize=14.5, fontweight="bold", pad=16, loc="left",
    )
    ax.grid(axis="x", color=GRID, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)

    ax.text(
        30.5, y[2] + 0.34, t["region"], fontsize=9.5, color=SLOW,
        ha="right", va="bottom",
    )
    stamp(fig, t["stamp"])
    save(fig, "fig-01-perception-gap")


# ---------------------------------------------------------------- ch01 · fig 02
def fig_time_accounting() -> None:
    """两种记账口径：T_first vs T_true。无数值, 只画结构。"""
    t = _t("fig-03-time-accounting")
    fig, ax = plt.subplots(figsize=(9.6, 3.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0.28, 3.7)
    ax.axis("off")

    segs = [
        (t["segs"][0], "#C9D6DF"),
        (t["segs"][1], "#8FB8C9"),
        (t["segs"][2], SLOW),
        (t["segs"][3], SAND),
    ]
    # 传统路径
    ax.text(0.02, 2.92, t["row_hand"], fontsize=11.5, fontweight="bold", color=INK, ha="left")
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
    ax.text(0.02, 1.42, t["row_ai"], fontsize=11.5, fontweight="bold", color=INK, ha="left",
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
    ax.text(1.53, 0.62, t["bracket_first"], fontsize=9, color=FAST, ha="center", va="top")

    ax.annotate(
        "", xy=(7.15, 0.78), xytext=(2.72, 0.78),
        arrowprops=dict(arrowstyle="<->", color=SLOW, linewidth=1.4, linestyle="--"),
    )
    ax.text(4.9, 0.62, t["bracket_rest"], fontsize=9, color=SLOW, ha="center", va="top")

    # 口径线
    ax.annotate(
        "", xy=(8.85, 3.34), xytext=(1.05, 3.34),
        arrowprops=dict(arrowstyle="<->", color=MUTED, linewidth=1.0),
    )
    ax.text(4.95, 3.42, t["rule_true"], fontsize=9.5, color=MUTED,
            ha="center", va="bottom")
    ax.annotate(
        "", xy=(8.85, 1.86), xytext=(1.05, 1.86),
        arrowprops=dict(arrowstyle="<->", color=MUTED, linewidth=1.0),
    )
    ax.text(4.95, 1.94, t["rule_note"], fontsize=9.5, color=MUTED,
            ha="center", va="bottom")

    ax.set_title(t["title"],
                 fontsize=14.5, fontweight="bold", loc="left", pad=8)
    stamp(fig, t["stamp"])
    save(fig, "fig-03-time-accounting")


# ---------------------------------------------------------------- ch01 · fig 03
def fig_context_collapse() -> None:
    t = _t("fig-02-context-collapse")
    turns = np.arange(0, 61)

    def decay(start, k, floor):
        return floor + (1 - floor) * np.exp(-k * np.maximum(turns - start, 0))

    early = decay(0, 0.035, 0.28)
    restated = np.minimum(0.97, decay(0, 0.012, 0.62) + 0.12)

    fig, ax = plt.subplots(figsize=(9.2, 4.5))
    ax.plot(turns, early * 100, color=SLOW, linewidth=2.4,
            label=t["label_early"])
    ax.plot(turns, restated * 100, color=FAST, linewidth=2.4, linestyle="--",
            label=t["label_restate"])

    ax.fill_between(turns, early * 100, restated * 100, color=SLOW, alpha=0.07)

    ax.axhline(50, color="#B8C1CC", linewidth=1, linestyle=":")
    ax.text(59, 51.5, t["ref50"], fontsize=8.8, color=MUTED, ha="right")

    ax.annotate(
        t["collapse"],
        xy=(34, early[34] * 100), xytext=(20, 76),
        fontsize=9.5, color=SLOW,
        arrowprops=dict(arrowstyle="-|>", color=SLOW, linewidth=1.2,
                        connectionstyle="arc3,rad=-0.25"),
    )
    ax.annotate(
        t["point"],
        xy=(40, restated[40] * 100), xytext=(41.5, 45),
        fontsize=9, color=FAST,
        arrowprops=dict(arrowstyle="-|>", color=FAST, linewidth=1.1),
    )

    ax.set_xlabel(t["xlabel"], fontsize=10.5)
    ax.set_ylabel(t["ylabel"], fontsize=10.5)
    ax.set_ylim(20, 104)
    ax.set_xlim(0, 60)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25%", "50%", "75%", "100%"])
    ax.grid(color=GRID, linewidth=0.9)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, fontsize=10, loc="lower left")
    ax.set_title(t["title"],
                 fontsize=14, fontweight="bold", loc="left", pad=14)
    stamp(fig, t["stamp"])
    save(fig, "fig-02-context-collapse")


# ---------------------------------------------------------------- ch02 · fig 04
def fig_context_layers() -> None:
    t = _t("fig-01-context-layers")
    fig, ax = plt.subplots(figsize=(9.8, 4.6))
    ax.set_xlim(0, 10.4)
    ax.set_ylim(0.1, 5.0)
    ax.axis("off")

    layers = [
        (t["layers"][0][0], t["layers"][0][1], t["layers"][0][2], "#3D5A80", 3.55),
        (t["layers"][1][0], t["layers"][1][1], t["layers"][1][2], "#5B8C9E", 2.25),
        (t["layers"][2][0], t["layers"][2][1], t["layers"][2][2], "#8FB8C9", 0.95),
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
    ax.text(0.52, 2.75, t["expand"], fontsize=9.6, color=INK,
            rotation=90, ha="center", va="center", fontweight="bold")

    # 右侧：全塞对照
    ax.add_patch(
        FancyBboxPatch((8.05, 0.95), 1.55, 3.65,
                       boxstyle="round,pad=0.01,rounding_size=0.04",
                       facecolor=PAPER, edgecolor=SLOW, linewidth=1.3, linestyle="--")
    )
    ax.text(8.82, 4.72, t["counter"], fontsize=10.5, fontweight="bold", color=SLOW, ha="center")
    ax.text(8.82, 2.75, t["counter_note"],
            fontsize=8.8, color=MUTED, ha="center", va="center",
            rotation=90, linespacing=2.0)

    ax.text(1.05, 0.36, t["order"],
            fontsize=9.6, color=MUTED)
    ax.set_title(t["title"],
                 fontsize=14, fontweight="bold", loc="left", pad=12)
    stamp(fig, t["stamp"])
    save(fig, "fig-01-context-layers")


# ---------------------------------------------------------------- ch03 · fig 05
def fig_harness_flow() -> None:
    t = _t("fig-01-harness-flow")
    fig, ax = plt.subplots(figsize=(10.2, 4.6))
    ax.set_xlim(0, 10.2)
    ax.set_ylim(0, 4.6)
    ax.axis("off")

    ax.text(1.55, 4.24, t["feedforward"], fontsize=10.5, fontweight="bold",
            color=STEEL, ha="center")
    ax.text(8.55, 4.24, t["feedback"], fontsize=10.5, fontweight="bold",
            color=SLOW, ha="center")

    ff = t["ff"]
    for i, tx in enumerate(ff):
        box(ax, 0.25, 3.32 - i * 0.82, 2.55, 0.62, tx, fc="#EDF2F6", ec=STEEL, fs=8.8)

    fb = t["fb"]
    for i, tx in enumerate(fb):
        box(ax, 7.35, 3.42 - i * 0.66, 2.6, 0.5, tx, fc="#FBEDE6", ec=SLOW, fs=8.6)

    box(ax, 3.35, 2.35, 3.4, 0.95, t["generation"], fc="#1F2933", ec="#1F2933",
        fs=11, bold=True, tc="white")
    box(ax, 3.35, 0.85, 3.4, 0.75, t["human"], fc="#F2EFE4", ec=SAND, fs=10.5, bold=True)

    for i in range(4):
        arrow(ax, (2.85, 3.63 - i * 0.82), (3.32, 2.95), color=STEEL, lw=1.0, rad=0.12)
    for i in range(5):
        arrow(ax, (6.8, 2.85), (7.32, 3.67 - i * 0.66), color=SLOW, lw=1.0, rad=-0.12)

    arrow(ax, (5.05, 2.3), (5.05, 1.65), color=INK, lw=1.6)
    ax.text(5.15, 1.98, t["verdict"], fontsize=8.8, color=INK, va="center")

    ax.add_patch(
        FancyBboxPatch((0.25, 0.12), 2.55, 0.5,
                       boxstyle="round,pad=0.01,rounding_size=0.03",
                       facecolor="white", edgecolor="#B8C1CC", linestyle="--", linewidth=1.1)
    )
    ax.text(1.52, 0.37, t["crosscut"], fontsize=8.4, color=MUTED,
            ha="center", va="center")

    ax.text(3.35, 0.42, t["criterion"],
            fontsize=9.6, color=MUTED, va="center")
    ax.set_title(t["title"],
                 fontsize=14, fontweight="bold", loc="left", pad=8)
    stamp(fig, t["stamp"])
    save(fig, "fig-01-harness-flow")


# ---------------------------------------------------------------- ch03 · fig 06
def fig_gate_cost() -> None:
    t = _t("fig-02-gate-cost")
    stages = t["stages"]
    catches = t["catches"]
    relative_cost = [1, 2.5, 7, 22, 60]
    colors = ["#8FB8C9", "#6E9DB0", "#5B8C9E", "#C98B5E", SLOW]

    fig, ax = plt.subplots(figsize=(9.8, 4.6))
    y = np.arange(len(stages))[::-1]
    ax.barh(y, relative_cost, height=0.5, color=colors, edgecolor="none", zorder=3)

    for yi, c in zip(y, relative_cost):
        ax.text(c * 1.09, yi, t["factor"].format(v=c), fontsize=10.5, color=INK, fontweight="bold",
                va="center")

    ax.set_yticks(y)
    ax.set_yticklabels(
        [f"{s}\n{c}" for s, c in zip(stages, catches)],
        fontsize=9.6, linespacing=1.9,
    )
    ax.set_xscale("log")
    ax.set_xlim(0.7, 260)
    ax.set_xlabel(t["xlabel"], fontsize=10.2)
    ax.grid(axis="x", color=GRID, linewidth=0.9)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.set_title(t["title"],
                 fontsize=14, fontweight="bold", loc="left", pad=14)
    stamp(fig, t["stamp"])
    save(fig, "fig-02-gate-cost")


# ---------------------------------------------------------------- ch04 · fig 07
def fig_ab_timeline() -> None:
    t = _t("fig-01-ab-timeline")
    fig, ax = plt.subplots(figsize=(9.8, 3.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0.18, 3.24)
    ax.axis("off")

    segs = [
        (t["segs"][0], "#C9D6DF"),
        (t["segs"][1], "#8FB8C9"),
        (t["segs"][2], SAND),
        (t["segs"][3], SLOW),
        (t["segs"][4], "#5B8C9E"),
    ]
    rows = [(t["row_hand"], [1.3, 3.2, 0.0, 0.7, 1.4], 2.32),
            (t["row_ai"], [0.9, 1.1, 1.2, 2.3, 2.0], 1.18)]

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

    ax.text(1.6, 0.62, t["note1"],
            fontsize=9.4, color=MUTED)
    ax.text(1.6, 0.34, t["note2"],
            fontsize=9.4, color=SLOW)

    ax.set_title(t["title"],
                 fontsize=14, fontweight="bold", loc="left", pad=8)
    stamp(fig, t["stamp"])
    save(fig, "fig-01-ab-timeline")


def main() -> None:
    global LANG
    ap = argparse.ArgumentParser(description="Generate phase1 figures.")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh", help="figure text language")
    args = ap.parse_args()
    LANG = args.lang
    plt.rcParams["font.sans-serif"] = FONT_STACKS[LANG]
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
