#!/usr/bin/env python3
"""《关得住：AI 系统的攻击面与爆炸半径》全书配图统一入口。

设计约束（与全库其它各册同一套视觉系统）：
  1. 白底、细线、单一强调色，不放装饰性渐变与 3D 阴影
  2. 中文字体显式回退到 Hiragino Sans GB / STHeiti / Arial Unicode MS
  3. 每张图底部必须标注「实测数据」还是「结构示意」——不允许把示意画成数据
  4. 不使用 Unicode 带圈字母（macOS 中文字体缺字形，会画成豆腐块）
  5. 画布用 add_axes([0,0,1,1]) 满幅，并按 figsize 反算 ylim，
     使 1 个数据单位在 x/y 上等长（圆是圆、方是方），也避免出现大片留白

运行：python3 code/make_figures.py [--lang zh|en] [chNN]   # 全书 / 某章
输出：assets/chNN/fig-YY-*.png（240 dpi）

双语机制（A1′）：--lang zh|en（默认 zh）；每图文案在同册 fig_texts.py 的 T 字典；
几何代码与语言无关，语言差异只在 _t（取文案）与字体栈两处。
"""

from pathlib import Path
import argparse
import sys

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

matplotlib.use("Agg")

from fig_texts import T

LANG = "zh"

FONT_STACKS = {
    "zh": [
        "Hiragino Sans GB",
        "STHeiti",
        "Arial Unicode MS",
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

INK = "#1F2933"
MUTED = "#7B8794"
GRID = "#E4E7EB"
STEEL = "#3D5A80"
SLOW = "#C2571A"
FAST = "#2A9D8F"
SAND = "#C08A00"
ALERT = "#9B2C2C"
PAPER = "#F7F9FB"

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# 输出名映射（阶段 2 提交 (i) 起为终态规则）：en 落 FINAL_REL、zh 落 FINAL_REL 加 .zh 后缀
# （fig-NN-slug.zh.png）；26 处改号已并入 FINAL_REL，58 张 zh 图已 git mv 到位
# （映射依据 .omc/work/bilingual-baseline/05-renumber-map-26.md）。
FINAL_REL = {
    "fig-01-scan-scale": "ch01/fig-01-scan-scale.png",
    "fig-02-omission-spectrum": "ch01/fig-02-omission-spectrum.png",
    "fig-01-privilege-shapes": "ch02/fig-01-privilege-shapes.png",
    "fig-02-agency-ladder": "ch02/fig-02-agency-ladder.png",
    "fig-01-entry-matrix": "ch03/fig-01-entry-matrix.png",
    "fig-01-blast-radius": "ch04/fig-01-blast-radius.png",
    "fig-02-risk-contour": "ch04/fig-02-risk-contour.png",
    "fig-01-injection-paths": "ch05/fig-01-injection-paths.png",
    "fig-02-approval-fatigue": "ch05/fig-02-approval-fatigue.png",
    "fig-01-rls-paths": "ch06/fig-01-rls-paths.png",
    "fig-02-boundary-positions": "ch06/fig-02-boundary-positions.png",
    "fig-01-supply-paths": "ch07/fig-01-supply-paths.png",
    "fig-02-token-relay": "ch07/fig-02-token-relay.png",
    "fig-01-cascade": "ch08/fig-01-cascade.png",
    "fig-02-circuit-breaker": "ch08/fig-02-circuit-breaker.png",
    "fig-01-replay-verdicts": "ch09/fig-01-replay-verdicts.png",
    "fig-02-hitl-matrix": "ch09/fig-02-hitl-matrix.png",
    "fig-01-pipeline": "ch10/fig-01-pipeline.png",
    "fig-02-decay": "ch10/fig-02-decay.png",
}


def _t(fig_id: str) -> dict:
    """取文案——语言差异只允许出现在这里与字体栈。"""
    return T[fig_id][LANG]


def _out(fig_id: str):
    rel = FINAL_REL[fig_id]
    if LANG == "zh":
        rel = rel[:-4] + ".zh.png"
    path = ASSETS / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def canvas(fig_w: float, fig_h: float, x_span: float):
    """满幅画布，返回 (fig, ax, y_span)；1 数据单位在 x/y 上等长。"""
    fig = plt.figure(figsize=(fig_w, fig_h))
    ax = fig.add_axes([0, 0, 1, 1])
    y_span = x_span * fig_h / fig_w
    ax.set_xlim(0, x_span)
    ax.set_ylim(0, y_span)
    ax.axis("off")
    return fig, ax, y_span


def save(fig, fig_id: str) -> None:
    path = _out(fig_id)
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    print(f"  OK {path.name}")


def head(ax, y_span: float, title: str, sub: str | None = None) -> None:
    ax.text(0.10, y_span - 0.22, title, fontsize=15, fontweight="bold", color=INK,
            ha="left", va="top")
    if sub:
        ax.text(0.10, y_span - 0.66, sub, fontsize=9.8, color=MUTED, ha="left", va="top")


def stamp(ax, text: str, y: float = 0.26) -> None:
    ax.text(0.10, y, text, fontsize=8.0, color=MUTED, ha="left", va="top",
            linespacing=1.55)


# ===========================================================================
# ch01 · 图 1-1：两次独立扫描的受害比例（实测数据）
# ===========================================================================
def fig_ch01_scan_scale() -> None:
    t = _t("fig-01-scan-scale")
    rows = [
        (t["headers"][0], t["labels"][0], 1645, 170, 3.55),
        (t["headers"][1], t["labels"][1], 380000, 5000, 1.05),
    ]

    fig, ax, ys = canvas(6.9, 6.9, 7.0)
    cell = 0.20

    for header, label, total, bad, y0 in rows:
        pct = bad / total
        n_red = max(1, round(pct * 100))
        ax.text(0.42, y0 + 10 * cell + 0.10, header, fontsize=10.0, fontweight="bold",
                color=INK, va="bottom")
        for i in range(100):
            r, c = divmod(i, 10)
            row_from_top = 9 - r
            ax.add_patch(Rectangle((0.42 + c * cell, y0 + row_from_top * cell),
                                   cell, cell,
                                   facecolor=ALERT if i < n_red else "#ECEFF2",
                                   edgecolor="white", linewidth=0.9))
        lx = 0.42 + 10 * cell + 0.40
        top = y0 + 10 * cell
        ax.text(lx, top - 0.16, label, fontsize=9.6, color=INK, va="top", ha="left",
                linespacing=1.7, fontweight="bold")
        ax.text(lx, top - 1.12, f"{bad:,} / {total:,}", fontsize=12.2, color=ALERT,
                va="top", ha="left", fontweight="bold")
        ax.text(lx, top - 1.46, t["pct_fmt"].format(pct=pct * 100), fontsize=9.4,
                color=MUTED, va="top", ha="left")

    head(ax, ys, t["title"], t["sub"])
    stamp(ax, t["stamp"], y=0.78)
    save(fig, "fig-01-scan-scale")


# ===========================================================================
# ch01 · 图 1-2：两类缺陷的发现难度谱系（结构示意）
# ===========================================================================
def fig_ch01_omission_spectrum() -> None:
    t = _t("fig-02-omission-spectrum")
    fig, ax, ys = canvas(11.0, 5.6, 12.0)

    # 两个半透明区域：功能测试的舒适区 / 缺失型缺陷的盲区
    ax.add_patch(Rectangle((1.00, 2.75), 4.70, 2.40, facecolor="#E7F3EF",
                           edgecolor=FAST, linewidth=1.1, linestyle="--"))
    ax.add_patch(Rectangle((7.10, 0.85), 4.60, 2.50, facecolor="#F6E4E4",
                           edgecolor=ALERT, linewidth=1.1, linestyle="--"))
    ax.text(3.35, 5.02, t["comfort_title"], fontsize=10.6, color=FAST,
            ha="center", va="top", fontweight="bold")
    ax.text(3.35, 4.72, t["comfort_sub"], fontsize=8.6, color=MUTED,
            ha="center", va="top")
    ax.text(7.25, 3.66, t["blind_title"], fontsize=10.6, color=ALERT,
            ha="left", va="bottom", fontweight="bold")
    ax.text(9.35, 3.66, t["blind_sub"], fontsize=8.6, color=MUTED,
            ha="left", va="bottom")

    # (x, y, label, color, dx, dy, ha)
    pts = [
        (2.05, 4.15, t["pts"][0], STEEL, 0, 0.30, "center"),
        (4.45, 4.15, t["pts"][1], STEEL, 0, 0.30, "center"),
        (3.15, 3.35, t["pts"][2], STEEL, 0, -0.32, "center"),
        (4.55, 3.15, t["pts"][3], STEEL, 0, -0.32, "center"),
        (6.05, 4.45, t["pts"][4], SLOW, 0, 0.30, "center"),
        (6.35, 2.15, t["pts"][5], SLOW, 0, -0.32, "center"),
        (8.15, 2.85, t["pts"][6], ALERT, 0, 0.30, "center"),
        (10.40, 2.85, t["pts"][7], ALERT, 0, 0.30, "center"),
        (8.15, 1.75, t["pts"][8], ALERT, -0.28, -0.05, "right"),
        (10.40, 1.75, t["pts"][9], ALERT, 0, -0.32, "center"),
    ]
    for x, y, label, color, dx, dy, ha in pts:
        ax.add_patch(Circle((x, y), 0.17, facecolor=color, edgecolor="white", linewidth=1.2))
        ax.text(x + dx, y + dy, label, fontsize=9.0, color=INK, ha=ha, va="bottom" if dy > 0 else "top")

    ax.text(6.35, 5.20, t["push"],
            fontsize=9.2, color=ALERT, va="top", ha="left", linespacing=1.6)
    ax.annotate("", xy=(7.05, 2.35), xytext=(6.45, 4.05),
                arrowprops=dict(arrowstyle="-|>", color=ALERT, linewidth=1.2,
                                connectionstyle="arc3,rad=0.20"))

    ax.plot([1.00, 11.75], [0.85, 0.85], color=GRID, linewidth=1.1)
    ax.plot([1.00, 1.00], [0.85, 5.30], color=GRID, linewidth=1.1)
    ax.text(11.75, 0.52, t["xaxis"], fontsize=9.4,
            color=MUTED, ha="right", va="top")
    ax.text(0.52, 3.05, t["yaxis"], fontsize=9.4, color=MUTED,
            ha="center", va="center", rotation=90)

    head(ax, ys, t["title"], t["sub"])
    stamp(ax, t["stamp"])
    save(fig, "fig-02-omission-spectrum")


# ===========================================================================
# ch03 · 图 1-1：LessonVault 的入口矩阵（判定示意）
# ===========================================================================
def fig_ch03_entry_matrix() -> None:
    t = _t("fig-01-entry-matrix")
    rows = [
        # 入口, 无需批准, 可被外部触达, 能产生效果, 结论, 为什么
        (t["rows"][0][0], 1, 1, 0, t["rows"][0][1], t["rows"][0][2]),
        (t["rows"][1][0], 1, 1, 1, t["rows"][1][1], t["rows"][1][2]),
        (t["rows"][2][0], 1, 1, 1, t["rows"][2][1], t["rows"][2][2]),
        (t["rows"][3][0], 1, 1, 1, t["rows"][3][1], t["rows"][3][2]),
        (t["rows"][4][0], 1, 1, 1, t["rows"][4][1], t["rows"][4][2]),
        (t["rows"][5][0], 0, 1, 1, t["rows"][5][1], t["rows"][5][2]),
        (t["rows"][6][0], 0, 1, 1, t["rows"][6][1], t["rows"][6][2]),
    ]
    fig, ax, ys = canvas(11.0, 6.4, 13.0)

    x0, cw = 3.05, 1.62
    cols = t["cols"]
    for j, c in enumerate(cols):
        if j < 3:
            cx = x0 + j * cw + cw / 2
        elif j == 3:
            cx = x0 + 3 * cw + 0.85
        else:
            cx = x0 + 3 * cw + 3.15
        ax.text(cx, 6.52, c, fontsize=9.6, color=INK, ha="center", va="bottom",
                fontweight="bold")
    ax.plot([0.15, 12.85], [6.40, 6.40], color=GRID, linewidth=1.1)

    y = 5.90
    for name, a, b, c, verdict_key, why in rows:
        is_surface = verdict_key != "none"
        verdict = t["verdicts"][verdict_key]
        ax.text(0.15, y, name, fontsize=9.4, color=INK, va="center",
                fontweight="bold" if is_surface else "normal")
        for j, v in enumerate((a, b, c)):
            cx = x0 + j * cw + cw / 2
            mark, color = (t["yes"], STEEL) if v else (t["no"], "#B8C1CC")
            ax.text(cx, y, mark, fontsize=10.0, color=color, ha="center", va="center",
                    fontweight="bold" if v else "normal")
        vx = x0 + 3 * cw + 0.85
        vcolor = ALERT if is_surface else FAST
        ax.text(vx, y, verdict, fontsize=9.6, color=vcolor, ha="center", va="center",
                fontweight="bold")
        ax.text(x0 + 3 * cw + 1.85, y, why, fontsize=8.6, color=MUTED, va="center")
        ax.plot([0.15, 12.85], [y - 0.34, y - 0.34], color="#F1F3F5", linewidth=0.9)
        y -= 0.68

    ax.text(0.15, 1.22, t["note1"],
            fontsize=9.2, color=INK, va="top")
    ax.text(0.15, 0.88, t["note2"],
            fontsize=9.0, color=MUTED, va="top")

    head(ax, ys, t["title"], t["sub"])
    stamp(ax, t["stamp"])
    save(fig, "fig-01-entry-matrix")


# ===========================================================================
# ch04 · 图 1-1：四档配置的爆炸半径（能力矩阵，结构示意）
# ===========================================================================
def fig_ch04_blast_radius() -> None:
    t = _t("fig-01-blast-radius")
    dims = t["dims"]
    configs = [
        (t["configs"][0][0], t["configs"][0][1], [0, 0, 0, 0], t["configs"][0][2]),
        (t["configs"][1][0], t["configs"][1][1], [0, 1, 1, 0], t["configs"][1][2]),
        (t["configs"][2][0], t["configs"][2][1], [2, 2, 2, 1], t["configs"][2][2]),
        (t["configs"][3][0], t["configs"][3][1], [3, 3, 3, 3], t["configs"][3][2]),
    ]

    fig, ax, ys = canvas(10.6, 6.0, 12.2)
    colx = [3.30 + j * 0.80 for j in range(4)]
    brx = 6.10

    for j, d in enumerate(dims):
        ax.text(colx[j], 5.82, d, fontsize=9.8, color=INK, ha="center", va="bottom",
                fontweight="bold")
    ax.text(sum(colx) / 4, 6.14, t["dim_note"], fontsize=9.2,
            color=MUTED, ha="center", va="bottom")
    ax.plot([3.02, 6.42], [5.70, 5.70], color=GRID, linewidth=1.1)
    ax.text(brx, 5.82, t["br_note"], fontsize=9.2, color=MUTED,
            ha="left", va="bottom", fontweight="bold")

    palette = {0: "#E8EBEE", 1: "#A9C6D8", 2: STEEL, 3: ALERT}
    row_y = [5.08, 4.38, 3.68, 2.98]
    for (name, note, strengths, br), y in zip(configs, row_y):
        is_worst = strengths[0] == 3
        ax.text(0.10, y + 0.19, name, fontsize=10.6, fontweight="bold",
                color=ALERT if is_worst else INK, va="center")
        ax.text(0.10, y - 0.14, note, fontsize=8.3, color=MUTED, va="center")
        for j, s in enumerate(strengths):
            r = 0.125 + 0.030 * s
            ax.add_patch(Circle((colx[j], y), r, facecolor=palette[s],
                                edgecolor="white" if s else "#CBD2D9", linewidth=1.1))
        ax.text(brx, y, br, fontsize=9.8, color=ALERT if is_worst else MUTED,
                va="center", ha="left", fontweight="bold" if is_worst else "normal")
        if y != row_y[-1]:
            ax.plot([0.10, 11.90], [y - 0.34, y - 0.34], color=GRID, linewidth=0.9)

    ax.text(0.10, 2.12, t["formula"],
            fontsize=12.2, fontweight="bold", color=INK, va="top")
    ax.text(0.10, 1.64, t["tiers"],
            fontsize=9.4, color=MUTED, linespacing=1.85, va="top")
    ax.text(0.10, 0.98, t["last_tier"],
            fontsize=9.2, color=ALERT, va="top")

    ax.plot([7.30, 7.30], [1.02, 2.22], color=GRID, linewidth=1.4)
    ax.text(7.52, 2.16, t["union"], fontsize=9.0,
            color=INK, va="top", fontweight="bold")
    ax.text(7.52, 1.80, t["union_note"],
            fontsize=8.8, color=MUTED, va="top", linespacing=1.85)

    head(ax, ys, t["title"])
    stamp(ax, t["stamp"])
    save(fig, "fig-01-blast-radius")


# ===========================================================================
# ch04 · 图 1-2：风险排序的等值线（结构示意）
# ===========================================================================
def fig_ch04_risk_contour() -> None:
    t = _t("fig-02-risk-contour")
    fig, ax, ys = canvas(10.4, 5.8, 12.4)

    # 画布：x = BR（对数感，用等距刻度表达量级），y = AS
    ax.plot([1.30, 11.30], [0.95, 0.95], color=GRID, linewidth=1.2)
    ax.plot([1.30, 1.30], [0.95, 5.95], color=GRID, linewidth=1.2)

    # 三条等值线 R = AS × BR × k，取 D=0.5 → k=0.5，用对数坐标下的直线近似
    # 为了不画成精确数学图，这里用手工控制的折线表达"同一条线上等价"的关系
    lines = [
        ([(2.05, 2.05), (4.25, 1.28)], t["lines"][0], FAST),
        ([(3.30, 4.62), (6.60, 2.30), (8.55, 1.72)], t["lines"][1], SAND),
        ([(6.15, 5.55), (9.35, 3.62), (11.10, 2.98)], t["lines"][2], ALERT),
    ]
    for pts, label, color in lines:
        xs = [p[0] for p in pts]
        ys_ = [p[1] for p in pts]
        ax.plot(xs, ys_, color=color, linewidth=2.0, linestyle="-", zorder=2)
        ax.text(xs[-1] + 0.16, ys_[-1], label, fontsize=9.2, color=color,
                va="center", ha="left", fontweight="bold")

    # 两个等价点
    ax.add_patch(Circle((3.55, 4.30), 0.19, facecolor=STEEL, edgecolor="white", linewidth=1.2))
    ax.text(3.55, 4.62, t["pt_a"], fontsize=9.4, color=STEEL, ha="center", va="bottom",
            fontweight="bold")
    ax.text(3.55, 3.96, t["pt_a_note"], fontsize=8.4, color=MUTED,
            ha="center", va="top", linespacing=1.6)

    ax.add_patch(Circle((7.45, 2.15), 0.19, facecolor=STEEL, edgecolor="white", linewidth=1.2))
    ax.text(7.45, 2.47, t["pt_b"], fontsize=9.4, color=STEEL, ha="center", va="bottom",
            fontweight="bold")
    ax.text(7.45, 1.81, t["pt_b_note"], fontsize=8.4, color=MUTED,
            ha="center", va="top", linespacing=1.6)

    ax.annotate("", xy=(7.28, 2.32), xytext=(3.72, 4.12),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, linewidth=1.3,
                                linestyle="--", connectionstyle="arc3,rad=0.16"))
    ax.text(5.42, 3.62, t["same_line"], fontsize=9.0, color=MUTED,
            ha="center", va="bottom", rotation=-22)

    ax.text(11.35, 0.62, t["xaxis"], fontsize=9.6, color=MUTED,
            ha="right", va="top")
    ax.text(0.95, 6.12, t["yaxis"], fontsize=9.6, color=MUTED,
            ha="left", va="bottom")

    ax.text(0.15, 0.52, t["formula"],
            fontsize=9.2, color=INK, va="top")
    ax.text(0.15, 0.18, t["cheaper"],
            fontsize=9.0, color=MUTED, va="top")

    head(ax, ys, t["title"], t["sub"])
    stamp(ax, t["stamp"])
    save(fig, "fig-02-risk-contour")


# ===========================================================================
# ch09 · 图 1-1：未登录重放的三步判读（判定标准示意）
# ===========================================================================
def fig_ch09_replay_verdicts() -> None:
    t = _t("fig-01-replay-verdicts")
    rows = [
        (t["steps"][0][0], [
            (t["steps"][0][1][0], FAST),
            (t["steps"][0][1][1], SAND),
            (t["steps"][0][1][2], ALERT),
        ]),
        (t["steps"][1][0], [
            (t["steps"][1][1][0], FAST),
            (t["steps"][1][1][1], SAND),
            (t["steps"][1][1][2], ALERT),
        ]),
        (t["steps"][2][0], [
            (t["steps"][2][1][0], FAST),
            (t["steps"][2][1][1], SAND),
            (t["steps"][2][1][2], ALERT),
        ]),
    ]

    fig, ax, ys = canvas(10.4, 5.8, 12.4)
    x_start, cw, bh = 3.40, 2.85, 1.20

    for j, (label, color) in enumerate([(t["cols"][0], FAST), (t["cols"][1], SAND), (t["cols"][2], ALERT)]):
        ax.text(x_start + j * cw + cw / 2, 6.30, label, fontsize=10.6, ha="center",
                va="center", color=color, fontweight="bold")

    for (step, verdicts), top in zip(rows, [5.72, 4.28, 2.84]):
        ax.text(0.10, top - bh / 2, step, fontsize=9.3, va="center", color=INK,
                linespacing=1.95, fontweight="bold")
        for j, (text, color) in enumerate(verdicts):
            x = x_start + j * cw
            ax.add_patch(FancyBboxPatch((x + 0.07, top - bh), cw - 0.14, bh,
                                        boxstyle="round,pad=0.01,rounding_size=0.04",
                                        facecolor="white", edgecolor=color,
                                        linewidth=1.2,
                                        linestyle="-" if color != SAND else "--"))
            ax.text(x + cw / 2, top - bh / 2, text, fontsize=8.8, ha="center",
                    va="center", color=ALERT if color == ALERT else INK, linespacing=1.75)

    ax.text(0.10, 1.24, t["note1"],
            fontsize=9.4, color=INK, va="top")
    ax.text(0.10, 0.88, t["note2"],
            fontsize=9.4, color=ALERT, va="top")

    head(ax, ys, t["title"])
    stamp(ax, t["stamp"], 0.03)
    save(fig, "fig-01-replay-verdicts")


# ===========================================================================
# ch09 · 图 1-2：人在环的三判据矩阵（决策框架示意）
# ===========================================================================
def fig_ch09_hitl_matrix() -> None:
    t = _t("fig-02-hitl-matrix")
    cols = t["cols"]
    rows = t["rows"]
    cells = [
        [(t["cells"][0][0][0], t["cells"][0][0][1], "#E7F3EF", FAST),
         (t["cells"][0][1][0], t["cells"][0][1][1], "#F3F6E8", "#6F7F26"),
         (t["cells"][0][2][0], t["cells"][0][2][1], "#FBF0DA", SAND)],
        [(t["cells"][1][0][0], t["cells"][1][0][1], "#F3F6E8", "#6F7F26"),
         (t["cells"][1][1][0], t["cells"][1][1][1], "#FBF0DA", SAND),
         (t["cells"][1][2][0], t["cells"][1][2][1], "#FBEDE6", SLOW)],
        [(t["cells"][2][0][0], t["cells"][2][0][1], "#FBF0DA", SAND),
         (t["cells"][2][1][0], t["cells"][2][1][1], "#FBEDE6", SLOW),
         (t["cells"][2][2][0], t["cells"][2][2][1], "#F6E4E4", ALERT)],
    ]

    fig, ax, ys = canvas(10.0, 6.4, 12.0)
    cw, ch, x_start, y0 = 2.60, 1.30, 3.50, 2.30

    for j, c in enumerate(cols):
        ax.text(x_start + j * cw + cw / 2, y0 + 3 * ch + 0.16, c, fontsize=10.2,
                ha="center", va="bottom", fontweight="bold", color=INK)
    ax.text(x_start + 1.5 * cw, y0 + 3 * ch + 0.58, t["xnote"], fontsize=9.6,
            ha="center", va="bottom", color=MUTED)

    for i, r in enumerate(rows):
        yy = y0 + (2 - i) * ch
        ax.text(x_start - 0.24, yy + ch / 2, r, fontsize=9.8, ha="right", va="center",
                color=INK, linespacing=1.7, fontweight="bold")
        for j in range(3):
            label, tail, fc, tc = cells[i][j]
            x = x_start + j * cw
            ax.add_patch(FancyBboxPatch((x + 0.06, yy + 0.07), cw - 0.12, ch - 0.14,
                                        boxstyle="round,pad=0.01,rounding_size=0.05",
                                        facecolor=fc, edgecolor=tc, linewidth=1.1))
            ax.text(x + cw / 2, yy + ch / 2 + 0.20, label, fontsize=10.4, ha="center",
                    va="center", color=tc, fontweight="bold")
            ax.text(x + cw / 2, yy + ch / 2 - 0.24, tail, fontsize=8.6, ha="center",
                    va="center", color=MUTED)

    ax.text(0.42, y0 + 1.5 * ch, t["ynote"], fontsize=10.6, color=INK,
            ha="center", va="center", fontweight="bold", rotation=90)

    ax.text(0.10, 1.72, t["note1"],
            fontsize=9.9, color=INK, va="top")
    ax.text(0.10, 1.32, t["note2"],
            fontsize=9.2, color=MUTED, va="top")

    head(ax, ys, t["title"], t["sub"])
    stamp(ax, t["stamp"])
    save(fig, "fig-02-hitl-matrix")


# ===========================================================================
# ch02 · 图 1-1：三类越权的对照矩阵（结构示意）
# ===========================================================================
def fig_ch02_privilege_shapes() -> None:
    t = _t("fig-01-privilege-shapes")
    fig, ax, ys = canvas(11.2, 6.0, 12.6)

    rows = [
        # (形态键, 形态名, 白话, 怎么发现)
        (t["rows"][0][0], t["rows"][0][1], t["rows"][0][2], t["rows"][0][3]),
        (t["rows"][1][0], t["rows"][1][1], t["rows"][1][2], t["rows"][1][3]),
        (t["rows"][2][0], t["rows"][2][1], t["rows"][2][2], t["rows"][2][3]),
    ]

    y_rows = [5.05, 3.55, 2.05]
    for (kind, name, plain, detect), y in zip(rows, y_rows):
        ax.text(0.15, y + 0.30, name, fontsize=11.0, fontweight="bold", color=INK, va="center")
        ax.text(0.15, y - 0.10, plain, fontsize=8.8, color=MUTED, va="center")

        # 迷你示意（x 3.4—7.0）
        if kind == "horizontal":
            ax.add_patch(Circle((3.75, y), 0.24, facecolor=STEEL, edgecolor="white", linewidth=1.2))
            ax.add_patch(Circle((5.55, y), 0.24, facecolor=ALERT, edgecolor="white", linewidth=1.2))
            ax.text(3.75, y, t["ab"][0], fontsize=9.2, color="white", ha="center", va="center", fontweight="bold")
            ax.text(5.55, y, t["ab"][1], fontsize=9.2, color="white", ha="center", va="center", fontweight="bold")
            ax.plot([4.65, 4.65], [y - 0.55, y + 0.55], color=MUTED, linewidth=1.1, linestyle="--")
            ax.annotate("", xy=(5.25, y), xytext=(4.05, y),
                        arrowprops=dict(arrowstyle="-|>", color=ALERT, linewidth=1.5))
        elif kind == "vertical":
            ax.add_patch(Circle((3.75, y - 0.32), 0.24, facecolor=STEEL, edgecolor="white", linewidth=1.2))
            ax.add_patch(Circle((5.55, y + 0.32), 0.24, facecolor=ALERT, edgecolor="white", linewidth=1.2))
            ax.text(3.75, y - 0.32, t["low"], fontsize=8.6, color="white", ha="center", va="center", fontweight="bold")
            ax.text(5.55, y + 0.32, t["high"], fontsize=8.6, color="white", ha="center", va="center", fontweight="bold")
            ax.plot([3.30, 6.00], [y, y], color=MUTED, linewidth=1.1, linestyle="--")
            ax.annotate("", xy=(5.28, y + 0.28), xytext=(4.02, y - 0.26),
                        arrowprops=dict(arrowstyle="-|>", color=ALERT, linewidth=1.5,
                                        connectionstyle="arc3,rad=-0.18"))
        else:
            ax.add_patch(Circle((3.55, y - 0.28), 0.22, facecolor="#B8C1CC", edgecolor="white", linewidth=1.2))
            ax.add_patch(Circle((5.15, y), 0.26, facecolor=STEEL, edgecolor="white", linewidth=1.2))
            ax.add_patch(Circle((6.75, y + 0.28), 0.22, facecolor=ALERT, edgecolor="white", linewidth=1.2))
            ax.text(3.55, y - 0.28, t["proxy_labels"][0], fontsize=8.6, color="white", ha="center", va="center", fontweight="bold")
            ax.text(5.15, y, t["proxy_labels"][1], fontsize=8.6, color="white", ha="center", va="center", fontweight="bold")
            ax.text(6.75, y + 0.28, t["proxy_labels"][2], fontsize=8.6, color="white", ha="center", va="center", fontweight="bold")
            ax.annotate("", xy=(4.92, y - 0.06), xytext=(3.78, y - 0.22),
                        arrowprops=dict(arrowstyle="-|>", color=MUTED, linewidth=1.3))
            ax.annotate("", xy=(6.52, y + 0.22), xytext=(5.42, y + 0.06),
                        arrowprops=dict(arrowstyle="-|>", color=ALERT, linewidth=1.5))
            ax.text(5.15, y - 0.46, t["holds_cred"], fontsize=8.0, color=MUTED, ha="center", va="top")

        ax.text(7.70, y, detect, fontsize=9.0, color=INK, va="center", linespacing=1.7)
        ax.plot([0.15, 12.35], [y - 0.78, y - 0.78], color="#F1F3F5", linewidth=0.9)

    ax.text(0.15, 1.06, t["note1"],
            fontsize=9.4, color=ALERT, va="top")
    ax.text(0.15, 0.70, t["note2"],
            fontsize=9.0, color=MUTED, va="top")

    head(ax, ys, t["title"], t["sub"])
    stamp(ax, t["stamp"])
    save(fig, "fig-01-privilege-shapes")


# ===========================================================================
# ch02 · 图 1-2：自主度阶梯与半径放大（结构示意）
# ===========================================================================
def fig_ch02_agency_ladder() -> None:
    t = _t("fig-02-agency-ladder")
    fig, ax, ys = canvas(10.8, 5.9, 12.2)

    steps = [
        (t["steps"][0][0], t["steps"][0][1], t["steps"][0][2], 0.80, FAST),
        (t["steps"][1][0], t["steps"][1][1], t["steps"][1][2], 1.70, "#6F7F26"),
        (t["steps"][2][0], t["steps"][2][1], t["steps"][2][2], 2.90, SAND),
        (t["steps"][3][0], t["steps"][3][1], t["steps"][3][2], 4.15, ALERT),
    ]

    x0, bw, gap = 1.35, 2.35, 0.42
    base_y = 1.95
    for i, (title, note, reach, h, color) in enumerate(steps):
        x = x0 + i * (bw + gap)
        ax.add_patch(FancyBboxPatch((x, base_y), bw, h,
                                    boxstyle="round,pad=0.012,rounding_size=0.04",
                                    facecolor=color, edgecolor="none", alpha=0.92))
        ax.text(x + bw / 2, base_y + h - 0.34, title, fontsize=11.2, color="white",
                ha="center", va="center", fontweight="bold")
        ax.text(x + bw / 2, base_y + h - 0.70, reach, fontsize=9.0, color="white",
                ha="center", va="center")
        ax.text(x + bw / 2, base_y - 0.24, note, fontsize=8.8, color=INK,
                ha="center", va="top", linespacing=1.5)

    ax.plot([0.90, 11.85], [base_y - 0.86, base_y - 0.86], color=GRID, linewidth=1.1)
    ax.text(11.85, base_y - 1.10, t["xaxis"], fontsize=9.4, color=MUTED, ha="right", va="top")
    ax.text(0.62, 3.55, t["yaxis"], fontsize=9.4, color=MUTED,
            ha="center", va="center", rotation=90)

    ax.text(0.15, 0.86, t["note1"],
            fontsize=9.2, color=INK, va="top")
    ax.text(0.15, 0.52, t["note2"],
            fontsize=9.0, color=MUTED, va="top")

    head(ax, ys, t["title"], t["sub"])
    stamp(ax, t["stamp"], 0.14)
    save(fig, "fig-02-agency-ladder")


# ===========================================================================
# ch05 · 图 1-1：注入进入上下文的四条路径（结构示意）
# ===========================================================================
def fig_ch05_injection_paths() -> None:
    t = _t("fig-01-injection-paths")
    fig, ax, ys = canvas(11.0, 6.0, 12.4)

    # 中央：上下文窗口
    ax.add_patch(FancyBboxPatch((4.55, 2.35), 3.30, 1.95,
                                boxstyle="round,pad=0.012,rounding_size=0.05",
                                facecolor="#ECEFF2", edgecolor=INK, linewidth=1.3))
    ax.text(6.20, 3.72, t["center_title"], fontsize=11.6, color=INK, ha="center", va="center",
            fontweight="bold")
    ax.text(6.20, 3.28, t["center_l1"], fontsize=9.0, color=MUTED,
            ha="center", va="center")
    ax.text(6.20, 2.90, t["center_l2"], fontsize=9.0, color=MUTED,
            ha="center", va="center")

    paths = [
        (t["paths"][0][0], t["paths"][0][1], 1.85, 5.35, SLOW),
        (t["paths"][1][0], t["paths"][1][1], 1.85, 2.05, SLOW),
        (t["paths"][2][0], t["paths"][2][1], 9.35, 5.35, SAND),
        (t["paths"][3][0], t["paths"][3][1], 9.35, 2.05, ALERT),
    ]
    for name, example, x, y, color in paths:
        ax.add_patch(FancyBboxPatch((x - 1.55, y - 0.52), 3.10, 1.04,
                                    boxstyle="round,pad=0.012,rounding_size=0.05",
                                    facecolor="white", edgecolor=color, linewidth=1.3))
        ax.text(x, y + 0.16, name, fontsize=10.2, color=color, ha="center", va="center",
                fontweight="bold")
        ax.text(x, y - 0.24, example, fontsize=8.2, color=MUTED, ha="center", va="center",
                linespacing=1.5)
        # 指向中心
        tx = 6.20 + (-1.30 if x < 6.20 else 1.30)
        ty = 3.32 + (0.55 if y > 3.32 else -0.55)
        ax.annotate("", xy=(tx, ty), xytext=(x + (1.58 if x < 6.20 else -1.58), y),
                    arrowprops=dict(arrowstyle="-|>", color=color, linewidth=1.4,
                                    connectionstyle="arc3,rad=0.10" if x < 6.20 else "arc3,rad=-0.10"))

    ax.text(0.15, 1.10, t["note1"],
            fontsize=9.2, color=INK, va="top")
    ax.text(0.15, 0.74, t["note2"],
            fontsize=9.0, color=ALERT, va="top")

    head(ax, ys, t["title"], t["sub"])
    stamp(ax, t["stamp"])
    save(fig, "fig-01-injection-paths")


# ===========================================================================
# ch05 · 图 1-2：审批频率与实际阅读率（定性示意）
# ===========================================================================
def fig_ch05_approval_fatigue() -> None:
    t = _t("fig-02-approval-fatigue")
    fig, ax, ys = canvas(10.2, 5.6, 11.6)

    # 坐标轴
    ax.plot([1.25, 10.95], [1.15, 1.15], color=GRID, linewidth=1.2)
    ax.plot([1.25, 1.25], [1.15, 5.35], color=GRID, linewidth=1.2)

    # 衰减曲线（定性）
    xs = [1.25 + i * 0.32 for i in range(31)]
    ys_curve = [1.15 + 3.9 * (0.92 ** (i * 0.9)) for i in range(31)]
    ax.plot(xs, ys_curve, color=SLOW, linewidth=2.2)

    # 标注点：第 40 次
    ax.add_patch(Circle((7.45, 1.15 + 3.9 * (0.92 ** (19 * 0.9))), 0.17,
                        facecolor=ALERT, edgecolor="white", linewidth=1.2))
    ax.text(7.75, 1.15 + 3.9 * (0.92 ** (19 * 0.9)) + 0.22,
            t["p40"], fontsize=9.2, color=ALERT, ha="left", va="bottom")
    ax.add_patch(Circle((2.05, 1.15 + 3.9 * (0.92 ** (2.5 * 0.9))), 0.17,
                        facecolor=FAST, edgecolor="white", linewidth=1.2))
    ax.text(2.35, 1.15 + 3.9 * (0.92 ** (2.5 * 0.9)) + 0.22,
            t["p1"], fontsize=9.2, color=FAST, ha="left", va="bottom")

    ax.text(10.95, 0.82, t["xaxis"], fontsize=9.4, color=MUTED, ha="right", va="top")
    ax.text(0.82, 3.25, t["yaxis"], fontsize=9.4, color=MUTED, ha="center", va="center",
            rotation=90)

    ax.text(0.15, 0.62, t["note1"],
            fontsize=9.2, color=INK, va="top")
    ax.text(0.15, 0.28, t["note2"],
            fontsize=9.0, color=MUTED, va="top")

    head(ax, ys, t["title"], t["sub"])
    stamp(ax, t["stamp"])
    save(fig, "fig-02-approval-fatigue")


# ===========================================================================
# ch06 · 图 1-1：一次请求在 RLS 开 / 关下的两条路径（结构示意）
# ===========================================================================
def fig_ch06_rls_paths() -> None:
    t = _t("fig-01-rls-paths")
    fig, ax, ys = canvas(11.2, 5.8, 12.6)

    def node(x, y, w, h, label, fc, ec, tc=None, fs=9.2, bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                    boxstyle='round,pad=0.012,rounding_size=0.04',
                                    facecolor=fc, edgecolor=ec, linewidth=1.2))
        ax.text(x + w / 2, y + h / 2, label, fontsize=fs,
                color=tc or INK, ha='center', va='center',
                fontweight='bold' if bold else 'normal', linespacing=1.6)

    def arrow(x1, y1, x2, y2, color):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='-|>', color=color, linewidth=1.5))

    # 上排：RLS 关
    ax.text(0.15, 5.28, t["row_off"], fontsize=11.0, fontweight='bold', color=ALERT, va='center')
    node(1.95, 4.80, 1.85, 0.90, t["browser"], '#ECEFF2', '#B8C1CC')
    node(4.35, 4.80, 1.85, 0.90, t["rest"], '#ECEFF2', '#B8C1CC')
    node(6.75, 4.80, 1.85, 0.90, t["db"], '#ECEFF2', '#B8C1CC')
    node(9.15, 4.80, 2.35, 0.90, t["ret_all"], '#F6E4E4', ALERT, tc=ALERT, bold=True)
    arrow(3.85, 5.25, 4.30, 5.25, MUTED)
    arrow(6.25, 5.25, 6.70, 5.25, MUTED)
    arrow(8.65, 5.25, 9.10, 5.25, ALERT)
    ax.text(5.45, 4.52, t["off_note"], fontsize=8.6,
            color=MUTED, ha='center', va='top')

    ax.plot([0.15, 12.35], [3.75, 3.75], color=GRID, linewidth=1.1)

    # 下排：RLS 开
    ax.text(0.15, 2.72, t["row_on"], fontsize=11.0, fontweight='bold', color=FAST, va='center')
    node(1.95, 2.24, 1.85, 0.90, t["browser"], '#ECEFF2', '#B8C1CC')
    node(4.35, 2.24, 1.85, 0.90, t["rest"], '#ECEFF2', '#B8C1CC')
    node(6.75, 2.24, 1.85, 0.90, t["policy"], '#E7F3EF', FAST, tc=FAST, bold=True)
    node(9.15, 2.24, 2.35, 0.90, t["ret_zero"], '#E7F3EF', FAST, tc=FAST, bold=True)
    arrow(3.85, 2.69, 4.30, 2.69, MUTED)
    arrow(6.25, 2.69, 6.70, 2.69, MUTED)
    arrow(8.65, 2.69, 9.10, 2.69, FAST)
    ax.text(5.45, 1.96, t["on_note"], fontsize=8.6,
            color=MUTED, ha='center', va='top')

    ax.text(0.15, 1.10, t["note1"],
            fontsize=9.2, color=INK, va='top')
    ax.text(0.15, 0.72, t["note2"],
            fontsize=9.0, color=MUTED, va='top')

    head(ax, ys, t["title"], t["sub"])
    stamp(ax, t["stamp"])
    save(fig, "fig-01-rls-paths")


# ===========================================================================
# ch06 · 图 1-2：三种修法，三个边界位置（结构示意）
# ===========================================================================
def fig_ch06_boundary_positions() -> None:
    t = _t("fig-02-boundary-positions")
    fig, ax, ys = canvas(11.2, 5.8, 12.6)

    schemes = [
        (t["schemes"][0][0], t["schemes"][0][1], t["schemes"][0][2], 2, t["schemes"][0][3]),
        (t["schemes"][1][0], t["schemes"][1][1], t["schemes"][1][2], 1, t["schemes"][1][3]),
        (t["schemes"][2][0], t["schemes"][2][1], t["schemes"][2][2], 1, t["schemes"][2][3]),
    ]

    x0, cw = 0.85, 3.75
    for i, (title, sub, layers, boundary_at, note) in enumerate(schemes):
        x = x0 + i * cw
        ax.text(x + 1.55, 5.42, title, fontsize=10.6, fontweight='bold', color=INK,
                ha='center', va='bottom')
        ax.text(x + 1.55, 5.16, sub, fontsize=8.4, color=MUTED, ha='center', va='bottom')

        # 三层方块
        for j, layer in enumerate(layers):
            y = 3.95 - j * 1.05
            fc = '#E7F3EF' if j == boundary_at else '#ECEFF2'
            ec = FAST if j == boundary_at else '#B8C1CC'
            ax.add_patch(FancyBboxPatch((x + 0.30, y), 2.50, 0.78,
                                        boxstyle='round,pad=0.012,rounding_size=0.04',
                                        facecolor=fc, edgecolor=ec, linewidth=1.2))
            ax.text(x + 1.55, y + 0.39, layer, fontsize=9.0,
                    color=FAST if j == boundary_at else INK,
                    ha='center', va='center',
                    fontweight='bold' if j == boundary_at else 'normal')
            if j < 2:
                ax.annotate('', xy=(x + 1.55, y - 0.08), xytext=(x + 1.55, y + 0.86),
                            arrowprops=dict(arrowstyle='-|>', color=MUTED, linewidth=1.2))

        # 信任边界（虚线）画在边界层的上沿
        by = 3.95 - boundary_at * 1.05 + 0.90
        ax.plot([x + 0.10, x + 3.00], [by, by], color=ALERT, linewidth=1.4, linestyle='--')
        ax.text(x + 3.02, by, t["boundary"], fontsize=8.2, color=ALERT, ha='left', va='center')

        ax.text(x + 1.55, 0.98, note, fontsize=8.2, color=MUTED, ha='center', va='top',
                linespacing=1.6)

    ax.text(0.15, 0.52, t["note"],
            fontsize=9.2, color=INK, va='top')

    head(ax, ys, t["title"], t["sub"])
    stamp(ax, t["stamp"])
    save(fig, "fig-02-boundary-positions")


# ===========================================================================
# ch07 · 图 1-1：依赖进入系统的四条路径与各自唯一的拦截点
# ===========================================================================
def fig_ch07_supply_paths() -> None:
    t = _t("fig-01-supply-paths")
    fig, ax, ys = canvas(11.2, 6.0, 12.6)

    lanes = [
        (t["lanes"][0][0], t["lanes"][0][1], t["lanes"][0][2], t["lanes"][0][3]),
        (t["lanes"][1][0], t["lanes"][1][1], t["lanes"][1][2], t["lanes"][1][3]),
        (t["lanes"][2][0], t["lanes"][2][1], t["lanes"][2][2], t["lanes"][2][3]),
        (t["lanes"][3][0], t["lanes"][3][1], t["lanes"][3][2], t["lanes"][3][3]),
    ]

    y0 = 5.05
    for i, (name, entry, risk, gate) in enumerate(lanes):
        y = y0 - i * 1.05
        ax.text(0.15, y, name, fontsize=10.4, fontweight='bold', color=INK, va='center')
        ax.text(0.15, y - 0.30, entry, fontsize=8.2, color=MUTED, va='center')

        ax.add_patch(FancyBboxPatch((3.05, y - 0.34), 2.60, 0.68,
                                    boxstyle='round,pad=0.012,rounding_size=0.04',
                                    facecolor='#FBEDE6', edgecolor=SLOW, linewidth=1.1))
        ax.text(4.35, y, risk, fontsize=8.6, color=SLOW, ha='center', va='center',
                linespacing=1.5)

        ax.annotate('', xy=(6.35, y), xytext=(5.75, y),
                    arrowprops=dict(arrowstyle='-|>', color=MUTED, linewidth=1.3))

        ax.add_patch(FancyBboxPatch((6.45, y - 0.34), 2.75, 0.68,
                                    boxstyle='round,pad=0.012,rounding_size=0.04',
                                    facecolor='#E7F3EF', edgecolor=FAST, linewidth=1.1))
        ax.text(7.82, y, gate, fontsize=8.6, color=FAST, ha='center', va='center',
                fontweight='bold')

        ax.annotate('', xy=(9.95, y), xytext=(9.30, y),
                    arrowprops=dict(arrowstyle='-|>', color=MUTED, linewidth=1.3))
        ax.text(10.15, y, t["proc"], fontsize=8.8, color=MUTED, va='center')
        if i < 3:
            ax.plot([0.15, 12.35], [y - 0.52, y - 0.52], color='#F1F3F5', linewidth=0.9)

    ax.text(0.15, 0.72, t["note1"],
            fontsize=9.2, color=INK, va='top')
    ax.text(0.15, 0.38, t["note2"],
            fontsize=9.0, color=MUTED, va='top')

    head(ax, ys, t["title"], t["sub"])
    stamp(ax, t["stamp"])
    save(fig, "fig-01-supply-paths")


# ===========================================================================
# ch07 · 图 1-2：令牌透传与受众绑定（结构示意）
# ===========================================================================
def fig_ch07_token_relay() -> None:
    t = _t("fig-02-token-relay")
    fig, ax, ys = canvas(11.2, 5.8, 12.6)

    def box(x, y, w, h, label, fc, ec, tc=None):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                    boxstyle='round,pad=0.012,rounding_size=0.04',
                                    facecolor=fc, edgecolor=ec, linewidth=1.2))
        ax.text(x + w / 2, y + h / 2, label, fontsize=9.2, color=tc or INK,
                ha='center', va='center', linespacing=1.6)

    # 上排：有受众绑定
    ax.text(0.15, 5.05, t["row_on"], fontsize=11.0, fontweight='bold',
            color=FAST, va='center')
    box(1.60, 4.55, 1.90, 0.86, t["user"], '#ECEFF2', '#B8C1CC')
    box(4.35, 4.55, 1.90, 0.86, t["svc_a"], '#E7F3EF', FAST, tc=FAST)
    box(7.10, 4.55, 1.90, 0.86, t["svc_b"], '#F6E4E4', ALERT, tc=ALERT)
    box(9.85, 4.55, 1.90, 0.86, t["reject"], '#F6E4E4', ALERT, tc=ALERT, )
    ax.annotate('', xy=(4.30, 4.98), xytext=(3.55, 4.98),
                arrowprops=dict(arrowstyle='-|>', color=MUTED, linewidth=1.4))
    ax.annotate('', xy=(7.05, 4.98), xytext=(6.30, 4.98),
                arrowprops=dict(arrowstyle='-|>', color=ALERT, linewidth=1.4))
    ax.text(6.68, 5.22, t["forward"], fontsize=8.0, color=ALERT, ha='center', va='bottom')
    ax.annotate('', xy=(9.80, 4.98), xytext=(9.05, 4.98),
                arrowprops=dict(arrowstyle='-|>', color=ALERT, linewidth=1.4))
    ax.text(9.42, 5.22, t["refuse"], fontsize=8.0, color=ALERT, ha='center', va='bottom')
    ax.text(5.20, 4.28, t["on_note"], fontsize=8.4, color=FAST,
            ha='center', va='top')

    ax.plot([0.15, 12.35], [3.55, 3.55], color=GRID, linewidth=1.1)

    # 下排：无受众绑定
    ax.text(0.15, 2.72, t["row_off"], fontsize=11.0, fontweight='bold',
            color=ALERT, va='center')
    box(1.60, 2.22, 1.90, 0.86, t["user"], '#ECEFF2', '#B8C1CC')
    box(4.35, 2.22, 1.90, 0.86, t["svc_a"], '#ECEFF2', '#B8C1CC')
    box(7.10, 2.22, 1.90, 0.86, t["svc_b"], '#F6E4E4', ALERT, tc=ALERT)
    box(9.85, 2.22, 1.90, 0.86, t["svc_c"], '#F6E4E4', ALERT, tc=ALERT)
    for x1, x2 in ((3.55, 4.30), (6.30, 7.05), (9.05, 9.80)):
        ax.annotate('', xy=(x2, 2.65), xytext=(x1, 2.65),
                    arrowprops=dict(arrowstyle='-|>', color=ALERT, linewidth=1.4))
    ax.text(5.20, 1.95, t["off_note"], fontsize=8.4, color=ALERT,
            ha='center', va='top')

    ax.text(0.15, 1.02, t["note1"],
            fontsize=9.2, color=INK, va='top')
    ax.text(0.15, 0.66, t["note2"],
            fontsize=9.0, color=MUTED, va='top')

    head(ax, ys, t["title"], t["sub"])
    stamp(ax, t["stamp"])
    save(fig, "fig-02-token-relay")


# ===========================================================================
# ch08 · 图 1-1：级联故障的放大链（结构示意）
# ===========================================================================
def fig_ch08_cascade() -> None:
    t = _t("fig-01-cascade")
    fig, ax, ys = canvas(11.2, 5.8, 12.6)

    steps = [
        (t["steps"][0][0], t["steps"][0][1], 1.35, SAND),
        (t["steps"][1][0], t["steps"][1][1], 1.75, SLOW),
        (t["steps"][2][0], t["steps"][2][1], 2.15, SLOW),
        (t["steps"][3][0], t["steps"][3][1], 2.55, ALERT),
        (t["steps"][4][0], t["steps"][4][1], 2.30, ALERT),
    ]

    x = 0.45
    for i, (title, note, w, color) in enumerate(steps):
        ax.add_patch(FancyBboxPatch((x, 3.15), w, 1.15,
                                    boxstyle='round,pad=0.012,rounding_size=0.05',
                                    facecolor=color, edgecolor='none', alpha=0.92))
        ax.text(x + w / 2, 3.92, title, fontsize=10.0, color='white',
                ha='center', va='center', fontweight='bold')
        ax.text(x + w / 2, 3.52, note, fontsize=8.2, color='white', ha='center', va='center')
        if i < 4:
            ax.annotate('', xy=(x + w + 0.32, 3.72), xytext=(x + w + 0.04, 3.72),
                        arrowprops=dict(arrowstyle='-|>', color=INK, linewidth=1.4))
        x += w + 0.38

    ax.annotate(t["callout"],
                xy=(3.10, 4.45), xytext=(1.20, 5.15),
                fontsize=9.2, color=ALERT, linespacing=1.6,
                arrowprops=dict(arrowstyle='-|>', color=ALERT, linewidth=1.2,
                                connectionstyle='arc3,rad=-0.18'))

    ax.text(0.15, 2.30, t["note1"],
            fontsize=9.2, color=INK, va='top')
    ax.text(0.15, 1.92, t["note2"],
            fontsize=9.0, color=MUTED, va='top')

    head(ax, ys, t["title"], t["sub"])
    stamp(ax, t["stamp"])
    save(fig, "fig-01-cascade")


# ===========================================================================
# ch08 · 图 1-2：断路器状态机（结构示意）
# ===========================================================================
def fig_ch08_circuit_breaker() -> None:
    t = _t("fig-02-circuit-breaker")
    fig, ax, ys = canvas(11.2, 5.6, 12.6)

    states = [
        (t["states"][0][0], t["states"][0][1], 1.55, 3.55, '#E7F3EF', FAST),
        (t["states"][1][0], t["states"][1][1], 5.05, 3.55, '#F6E4E4', ALERT),
        (t["states"][2][0], t["states"][2][1], 8.55, 3.55, '#FBF0DA', SAND),
    ]
    for name, note, x, y, fc, ec in states:
        ax.add_patch(FancyBboxPatch((x, y), 2.50, 1.35,
                                    boxstyle='round,pad=0.012,rounding_size=0.05',
                                    facecolor=fc, edgecolor=ec, linewidth=1.4))
        ax.text(x + 1.25, y + 1.00, name, fontsize=11.2, color=ec,
                ha='center', va='center', fontweight='bold')
        ax.text(x + 1.25, y + 0.48, note, fontsize=8.4, color=INK,
                ha='center', va='center', linespacing=1.6)

    # 两条直边：闭合→打开、打开→半开
    ax.annotate('', xy=(5.00, 4.22), xytext=(4.10, 4.22),
                arrowprops=dict(arrowstyle='-|>', color=ALERT, linewidth=1.4))
    ax.text(4.55, 4.34, t["to_open"], fontsize=8.2, color=ALERT, ha='center', va='bottom')
    ax.annotate('', xy=(8.50, 4.22), xytext=(7.60, 4.22),
                arrowprops=dict(arrowstyle='-|>', color=SAND, linewidth=1.4))
    ax.text(8.05, 4.34, t["to_half"], fontsize=8.2, color=SAND, ha='center', va='bottom')

    # 一条回边：半开 →（试探成功）→ 闭合，走方框下方
    xs = [10.20, 10.20, 2.80, 2.80]
    ys_path = [3.55, 2.75, 2.75, 3.55]
    ax.plot(xs[:3], ys_path[:3], color=FAST, linewidth=1.5)
    ax.annotate('', xy=(2.80, 3.52), xytext=(2.80, 3.10),
                arrowprops=dict(arrowstyle='-|>', color=FAST, linewidth=1.5))
    ax.text(6.50, 2.52, t["back"], fontsize=8.6,
            color=FAST, ha='center', va='top')

    ax.text(0.15, 1.72, t["note1"],
            fontsize=9.2, color=INK, va='top')
    ax.text(0.15, 1.34, t["note2"],
            fontsize=9.0, color=MUTED, va='top')

    head(ax, ys, t["title"], t["sub"])
    stamp(ax, t["stamp"], 0.30)
    save(fig, "fig-02-circuit-breaker")


# ===========================================================================
# ch10 · 图 1-1：三条断言在流水线上的位置
# ===========================================================================
def fig_ch10_pipeline() -> None:
    t = _t("fig-01-pipeline")
    fig, ax, ys = canvas(11.2, 5.6, 12.6)

    stages = [
        (t["stages"][0], 1.65),
        (t["stages"][1], 2.35),
        (t["stages"][2], 2.35),
        (t["stages"][3], 1.95),
        (t["stages"][4], 1.65),
    ]
    x = 0.45
    centers = []
    for name, w in stages:
        ax.add_patch(FancyBboxPatch((x, 3.55), w, 0.95,
                                    boxstyle='round,pad=0.012,rounding_size=0.04',
                                    facecolor='#ECEFF2', edgecolor='#B8C1CC', linewidth=1.1))
        ax.text(x + w / 2, 4.02, name, fontsize=9.2, color=INK, ha='center', va='center')
        centers.append(x + w / 2)
        if x > 0.45:
            ax.annotate('', xy=(x - 0.06, 4.02), xytext=(x - 0.34, 4.02),
                        arrowprops=dict(arrowstyle='-|>', color=MUTED, linewidth=1.2))
        x += w + 0.40

    asserts = [
        (t["asserts"][0][0], 2, t["asserts"][0][1], SLOW),
        (t["asserts"][1][0], 1, t["asserts"][1][1], STEEL),
        (t["asserts"][2][0], 1, t["asserts"][2][1], STEEL),
    ]
    for i, (name, idx, how, color) in enumerate(asserts):
        cx = centers[idx]
        y = 2.75 - i * 0.62
        ax.add_patch(Circle((cx, 4.62), 0.14, facecolor=color, edgecolor='white', linewidth=1.2))
        ax.annotate('', xy=(cx, 4.48), xytext=(cx, y + 0.16),
                    arrowprops=dict(arrowstyle='-|>', color=color, linewidth=1.2,
                                    connectionstyle=f'arc3,rad={0.18 if i == 0 else -0.12}'))
        ax.text(cx + 0.35, y, name, fontsize=8.8, color=color, va='center', fontweight='bold')
        ax.text(cx + 0.35, y - 0.24, how, fontsize=8.0, color=MUTED, va='center')

    ax.text(0.15, 1.02, t["note1"],
            fontsize=9.2, color=INK, va='top')
    ax.text(0.15, 0.66, t["note2"],
            fontsize=9.0, color=MUTED, va='top')

    head(ax, ys, t["title"], t["sub"])
    stamp(ax, t["stamp"])
    save(fig, "fig-01-pipeline")


# ===========================================================================
# ch10 · 图 1-2：安全属性的退化曲线（定性示意）
# ===========================================================================
def fig_ch10_decay() -> None:
    t = _t("fig-02-decay")
    fig, ax, ys = canvas(10.2, 5.6, 11.6)

    ax.plot([1.25, 10.95], [1.15, 1.15], color=GRID, linewidth=1.2)
    ax.plot([1.25, 1.25], [1.15, 5.35], color=GRID, linewidth=1.2)

    xs = [1.25 + i * 0.32 for i in range(31)]
    no_gate = [4.35 - 3.10 * (i / 30) ** 0.7 for i in range(31)]
    with_gate = [4.35 - 0.35 * (i / 30) for i in range(31)]

    ax.plot(xs, no_gate, color=SLOW, linewidth=2.2)
    ax.plot(xs, with_gate, color=FAST, linewidth=2.2, linestyle='--')

    ax.text(8.35, no_gate[22] - 0.30, t["no_gate"],
            fontsize=9.0, color=SLOW, ha='left', va='top')
    ax.text(6.15, with_gate[20] + 0.20, t["with_gate"],
            fontsize=9.0, color=FAST, ha='left', va='bottom')

    ax.add_patch(Circle((2.05, 4.35), 0.16, facecolor=INK, edgecolor='white', linewidth=1.2))
    ax.text(2.35, 4.52, t["launch"], fontsize=8.8, color=INK, ha='left', va='bottom')

    ax.text(10.95, 0.95, t["xaxis"], fontsize=9.4, color=MUTED, ha='right', va='top')
    ax.text(0.82, 3.25, t["yaxis"], fontsize=9.4, color=MUTED, ha='center', va='center',
            rotation=90)

    ax.text(0.15, 0.62, t["note"],
            fontsize=9.2, color=INK, va='top')

    head(ax, ys, t["title"], t["sub"])
    stamp(ax, t["stamp"], 0.22)
    save(fig, "fig-02-decay")


ALL = {
    "ch01": [fig_ch01_scan_scale, fig_ch01_omission_spectrum],
    "ch02": [fig_ch02_privilege_shapes, fig_ch02_agency_ladder],
    "ch03": [fig_ch03_entry_matrix],
    "ch04": [fig_ch04_blast_radius, fig_ch04_risk_contour],
    "ch05": [fig_ch05_injection_paths, fig_ch05_approval_fatigue],
    "ch06": [fig_ch06_rls_paths, fig_ch06_boundary_positions],
    "ch07": [fig_ch07_supply_paths, fig_ch07_token_relay],
    "ch08": [fig_ch08_cascade, fig_ch08_circuit_breaker],
    "ch09": [fig_ch09_replay_verdicts, fig_ch09_hitl_matrix],
    "ch10": [fig_ch10_pipeline, fig_ch10_decay],
}


def main() -> None:
    global LANG
    ap = argparse.ArgumentParser(description="Generate phase4 figures.")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh", help="figure text language")
    ap.add_argument("chapters", nargs="*", help="chapter ids like ch04 (default: all)")
    args = ap.parse_args()
    LANG = args.lang
    plt.rcParams["font.sans-serif"] = FONT_STACKS[LANG]
    only = args.chapters[0] if args.chapters else None
    print("生成配图：")
    for ch, fns in ALL.items():
        if only and ch != only:
            continue
        for fn in fns:
            fn()
    print("完成。")


if __name__ == "__main__":
    main()
