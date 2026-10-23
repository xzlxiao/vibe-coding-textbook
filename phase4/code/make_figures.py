#!/usr/bin/env python3
"""《关得住：AI 系统的攻击面与爆炸半径》全书配图统一入口。

设计约束（与全库其它各册同一套视觉系统）：
  1. 白底、细线、单一强调色，不放装饰性渐变与 3D 阴影
  2. 中文字体显式回退到 Hiragino Sans GB / STHeiti / Arial Unicode MS
  3. 每张图底部必须标注「实测数据」还是「结构示意」——不允许把示意画成数据
  4. 不使用 Unicode 带圈字母（macOS 中文字体缺字形，会画成豆腐块）
  5. 画布用 add_axes([0,0,1,1]) 满幅，并按 figsize 反算 ylim，
     使 1 个数据单位在 x/y 上等长（圆是圆、方是方），也避免出现大片留白

运行：python3 code/make_figures.py           # 生成全书 7 张图
      python3 code/make_figures.py ch04      # 只重绘某一章
输出：assets/chNN/fig-YY-*.png（240 dpi）
"""

from pathlib import Path
import sys

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

matplotlib.use("Agg")

plt.rcParams["font.sans-serif"] = [
    "Hiragino Sans GB",
    "STHeiti",
    "Arial Unicode MS",
    "PingFang SC",
    "DejaVu Sans",
]
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


def canvas(fig_w: float, fig_h: float, x_span: float):
    """满幅画布，返回 (fig, ax, y_span)；1 数据单位在 x/y 上等长。"""
    fig = plt.figure(figsize=(fig_w, fig_h))
    ax = fig.add_axes([0, 0, 1, 1])
    y_span = x_span * fig_h / fig_w
    ax.set_xlim(0, x_span)
    ax.set_ylim(0, y_span)
    ax.axis("off")
    return fig, ax, y_span


def save(fig, rel: str) -> None:
    path = ASSETS / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    print(f"  OK {rel}")


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
    rows = [
        ("第一批 · 同一类构建器生成的应用",
         "AI 构建器生成的 Web 应用\n（Lovable 类工具，CVE-2025-48757）",
         1645, 170, 3.55),
        ("第二批 · 公开可达的 AI 构建资产",
         "公开可访问的 AI 构建资产\n（RedAccess 全网扫描）",
         380000, 5000, 1.05),
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
        ax.text(lx, top - 1.46, f"= {pct * 100:.1f}%　（图中红格）", fontsize=9.4,
                color=MUTED, va="top", ha="left")

    head(ax, ys, "这不是小概率事件",
         "两次独立扫描量出的受害面 · 每一格 = 1%，红格 = 存在未授权读写问题的比例")
    stamp(ax,
          "实测数据 · 但两次扫描口径不同：前者分母是「同一工具生成的应用」，后者分母是「公开可访问的构建资产」。\n"
          "二者不可相加、不可相乘，也不能外推成「你的项目有 10% 概率出事」。\n"
          "它们只证明一件事：这个失效模式是成批出现的，不是个别事故。", y=0.78)
    save(fig, "ch01/fig-01-scan-scale.png")


# ===========================================================================
# ch01 · 图 1-2：两类缺陷的发现难度谱系（结构示意）
# ===========================================================================
def fig_ch01_omission_spectrum() -> None:
    fig, ax, ys = canvas(11.0, 5.6, 12.0)

    # 两个半透明区域：功能测试的舒适区 / 缺失型缺陷的盲区
    ax.add_patch(Rectangle((1.00, 2.75), 4.70, 2.40, facecolor="#E7F3EF",
                           edgecolor=FAST, linewidth=1.1, linestyle="--"))
    ax.add_patch(Rectangle((7.10, 0.85), 4.60, 2.50, facecolor="#F6E4E4",
                           edgecolor=ALERT, linewidth=1.1, linestyle="--"))
    ax.text(3.35, 5.02, "功能测试的舒适区", fontsize=10.6, color=FAST,
            ha="center", va="top", fontweight="bold")
    ax.text(3.35, 4.72, "错了会报错、测试能复现", fontsize=8.6, color=MUTED,
            ha="center", va="top")
    ax.text(7.25, 3.66, "缺失型缺陷的盲区", fontsize=10.6, color=ALERT,
            ha="left", va="bottom", fontweight="bold")
    ax.text(9.35, 3.66, "错了不报错，要靠人想到去问", fontsize=8.6, color=MUTED,
            ha="left", va="bottom")

    # (x, y, label, color, dx, dy, ha)
    pts = [
        (2.05, 4.15, "语法错误", STEEL, 0, 0.30, "center"),
        (4.45, 4.15, "依赖不存在", STEEL, 0, 0.30, "center"),
        (3.15, 3.35, "空指针崩溃", STEEL, 0, -0.32, "center"),
        (4.55, 3.15, "格式化错列", STEEL, 0, -0.32, "center"),
        (6.05, 4.45, "并发竞态", SLOW, 0, 0.30, "center"),
        (6.35, 2.15, "性能退化", SLOW, 0, -0.32, "center"),
        (8.15, 2.85, "缺 RLS 策略", ALERT, 0, 0.30, "center"),
        (10.40, 2.85, "缺授权校验", ALERT, 0, 0.30, "center"),
        (8.15, 1.75, "密钥进前端", ALERT, -0.28, -0.05, "right"),
        (10.40, 1.75, "无备份 / 无回滚", ALERT, 0, -0.32, "center"),
    ]
    for x, y, label, color, dx, dy, ha in pts:
        ax.add_patch(Circle((x, y), 0.17, facecolor=color, edgecolor="white", linewidth=1.2))
        ax.text(x + dx, y + dy, label, fontsize=9.0, color=INK, ha=ha, va="bottom" if dy > 0 else "top")

    ax.text(6.35, 5.20, "AI 把产量往右下推：\n写得快，也缺得快",
            fontsize=9.2, color=ALERT, va="top", ha="left", linespacing=1.6)
    ax.annotate("", xy=(7.05, 2.35), xytext=(6.45, 4.05),
                arrowprops=dict(arrowstyle="-|>", color=ALERT, linewidth=1.2,
                                connectionstyle="arc3,rad=0.20"))

    ax.plot([1.00, 11.75], [0.85, 0.85], color=GRID, linewidth=1.1)
    ax.plot([1.00, 1.00], [0.85, 5.30], color=GRID, linewidth=1.1)
    ax.text(11.75, 0.52, "发现难度 →　（会自动报错 → ？ → 要靠人想到）", fontsize=9.4,
            color=MUTED, ha="right", va="top")
    ax.text(0.52, 3.05, "一次出事的影响面 ↑", fontsize=9.4, color=MUTED,
            ha="center", va="center", rotation=90)

    head(ax, ys, "两类缺陷住在地图的两个角：越靠右下，越没有自动报警",
         "纵轴是影响面，横轴是发现难度；圆点只表达相对位置，不表达坐标数值")
    stamp(ax, "结构示意：坐标不对应任何实测值。这张图只想说明一件事——功能测试的舒适区，恰好不覆盖缺失型缺陷所在的区域。")
    save(fig, "ch01/fig-02-omission-spectrum.png")


# ===========================================================================
# ch03 · 图 1-1：LessonVault 的入口矩阵（判定示意）
# ===========================================================================
def fig_ch03_entry_matrix() -> None:
    rows = [
        # 入口, 无需批准, 可被外部触达, 能产生效果, 结论
        ("/　落地页（静态）", 1, 1, 0, "不算", "只读公开内容，改不了任何状态"),
        ("/login　登录页", 1, 1, 1, "算（小）", "可被撞库 / 可被枚举账号"),
        ("/app　笔记列表", 1, 1, 1, "算（小）", "必须验身份，但有登录页挡着"),
        ("/api/notes　自己的 API", 1, 1, 1, "算（大）", "业务逻辑全在这里，绕过即越权"),
        ("Supabase REST　直连", 1, 1, 1, "算（最大）", "数据库自己开的门，中间没有你的代码"),
        ("Storage 签名 URL", 0, 1, 1, "算（中）", "签名本身是凭据，URL 可被转发"),
        ("MCP 工具端点", 0, 1, 1, "算（大）", "每次调用都能改状态，且无人逐次批准"),
    ]
    fig, ax, ys = canvas(11.0, 6.4, 13.0)

    x0, cw = 3.05, 1.62
    cols = ["无需人工批准", "可被外部触达", "能产生实际效果", "结论", "为什么"]
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
    for name, a, b, c, verdict, why in rows:
        is_surface = verdict != "不算"
        ax.text(0.15, y, name, fontsize=9.4, color=INK, va="center",
                fontweight="bold" if is_surface else "normal")
        for j, v in enumerate((a, b, c)):
            cx = x0 + j * cw + cw / 2
            mark, color = ("是", STEEL) if v else ("否", "#B8C1CC")
            ax.text(cx, y, mark, fontsize=10.0, color=color, ha="center", va="center",
                    fontweight="bold" if v else "normal")
        vx = x0 + 3 * cw + 0.85
        vcolor = ALERT if is_surface else FAST
        ax.text(vx, y, verdict, fontsize=9.6, color=vcolor, ha="center", va="center",
                fontweight="bold")
        ax.text(x0 + 3 * cw + 1.85, y, why, fontsize=8.6, color=MUTED, va="center")
        ax.plot([0.15, 12.85], [y - 0.34, y - 0.34], color="#F1F3F5", linewidth=0.9)
        y -= 0.68

    ax.text(0.15, 1.22, "三个限定词全为「是」才算攻击面。注意倒数第二行：它没有界面、没人会点，但它一开门就是最大那扇。",
            fontsize=9.2, color=INK, va="top")
    ax.text(0.15, 0.88, "本表判定的是「面」，不是「资产」——落地页也是资产，只是它不构成不需要你点头就能走通的路。",
            fontsize=9.0, color=MUTED, va="top")

    head(ax, ys, "入口矩阵：七个入口，逐条过三个限定词",
         "判据不是「重不重要」，而是「无需人工批准 / 可被外部触达 / 能产生实际效果」")
    stamp(ax, "判定示意：本例的结论按 LessonVault 的设定推演，你自己的项目要重做一遍，不能照抄。")
    save(fig, "ch03/fig-01-entry-matrix.png")


# ===========================================================================
# ch04 · 图 1-1：四档配置的爆炸半径（能力矩阵，结构示意）
# ===========================================================================
def fig_ch04_blast_radius() -> None:
    dims = ["凭据", "工具", "数据", "出网"]
    configs = [
        ("编辑器内补全", "无工具调用，只见当前文件", [0, 0, 0, 0], "一个文件"),
        ("本地智能体（容器内）", "能跑命令，但出不去", [0, 1, 1, 0], "一个仓库"),
        ("CI 智能体（持部署凭据）", "能部署、能读日志；出网白名单", [2, 2, 2, 1], "一个服务"),
        ("全权限 shell（持生产凭据）", "特权账号 + 任意输入", [3, 3, 3, 3], "整个租户"),
    ]

    fig, ax, ys = canvas(10.6, 6.0, 12.2)
    colx = [3.30 + j * 0.80 for j in range(4)]
    brx = 6.10

    for j, d in enumerate(dims):
        ax.text(colx[j], 5.82, d, fontsize=9.8, color=INK, ha="center", va="bottom",
                fontweight="bold")
    ax.text(sum(colx) / 4, 6.14, "可达维度（圆点越大 = 该维度越宽）", fontsize=9.2,
            color=MUTED, ha="center", va="bottom")
    ax.plot([3.02, 6.42], [5.70, 5.70], color=GRID, linewidth=1.1)
    ax.text(brx, 5.82, "单次动作的最大影响面", fontsize=9.2, color=MUTED,
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

    ax.text(0.10, 2.12, "爆炸半径  BR = C（凭据）∪ T（工具）∪ D（数据）∪ N（网络出口）",
            fontsize=12.2, fontweight="bold", color=INK, va="top")
    ax.text(0.10, 1.64,
            "四行从上往下，正是「省事」的四个档位：每往下一格，交付快一点，半径大一截。\n"
            "半径本身不是罪——不知道自己半径有多大，才是。",
            fontsize=9.4, color=MUTED, linespacing=1.85, va="top")
    ax.text(0.10, 0.98,
            "最后一档不是「更聪明的助手」，是一个持你工牌、可被任意文本操控的临时工。",
            fontsize=9.2, color=ALERT, va="top")

    ax.plot([7.30, 7.30], [1.02, 2.22], color=GRID, linewidth=1.4)
    ax.text(7.52, 2.16, "一次越权用的是并集，不是四项相加", fontsize=9.0,
            color=INK, va="top", fontweight="bold")
    ax.text(7.52, 1.80,
            "凭据让它进门，工具让它动手，\n数据决定能拿多少，出口决定能带走多远。\n任意一项放宽，半径就按最宽的那项算。",
            fontsize=8.8, color=MUTED, va="top", linespacing=1.85)

    head(ax, ys, "四档配置的爆炸半径：省掉的每一道限制，都会变成半径上的一格")
    stamp(ax, "结构示意：圆点大小表示「该维度是否可达及其宽窄」，不代表任何具体数值；四档是常见形态，不是完整分类。")
    save(fig, "ch04/fig-01-blast-radius.png")


# ===========================================================================
# ch04 · 图 1-2：风险排序的等值线（结构示意）
# ===========================================================================
def fig_ch04_risk_contour() -> None:
    fig, ax, ys = canvas(10.4, 5.8, 12.4)

    # 画布：x = BR（对数感，用等距刻度表达量级），y = AS
    ax.plot([1.30, 11.30], [0.95, 0.95], color=GRID, linewidth=1.2)
    ax.plot([1.30, 1.30], [0.95, 5.95], color=GRID, linewidth=1.2)

    # 三条等值线 R = AS × BR × k，取 D=0.5 → k=0.5，用对数坐标下的直线近似
    # 为了不画成精确数学图，这里用手工控制的折线表达"同一条线上等价"的关系
    lines = [
        ([(2.05, 2.05), (4.25, 1.28)], "R = 小", FAST),
        ([(3.30, 4.62), (6.60, 2.30), (8.55, 1.72)], "R = 中", SAND),
        ([(6.15, 5.55), (9.35, 3.62), (11.10, 2.98)], "R = 大", ALERT),
    ]
    for pts, label, color in lines:
        xs = [p[0] for p in pts]
        ys_ = [p[1] for p in pts]
        ax.plot(xs, ys_, color=color, linewidth=2.0, linestyle="-", zorder=2)
        ax.text(xs[-1] + 0.16, ys_[-1], label, fontsize=9.2, color=color,
                va="center", ha="left", fontweight="bold")

    # 两个等价点
    ax.add_patch(Circle((3.55, 4.30), 0.19, facecolor=STEEL, edgecolor="white", linewidth=1.2))
    ax.text(3.55, 4.62, "A：小而多", fontsize=9.4, color=STEEL, ha="center", va="bottom",
            fontweight="bold")
    ax.text(3.55, 3.96, "入口多（AS 大）\n但每次影响小（BR 小）", fontsize=8.4, color=MUTED,
            ha="center", va="top", linespacing=1.6)

    ax.add_patch(Circle((7.45, 2.15), 0.19, facecolor=STEEL, edgecolor="white", linewidth=1.2))
    ax.text(7.45, 2.47, "B：大而少", fontsize=9.4, color=STEEL, ha="center", va="bottom",
            fontweight="bold")
    ax.text(7.45, 1.81, "入口少（AS 小）\n但每次影响大（BR 大）", fontsize=8.4, color=MUTED,
            ha="center", va="top", linespacing=1.6)

    ax.annotate("", xy=(7.28, 2.32), xytext=(3.72, 4.12),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, linewidth=1.3,
                                linestyle="--", connectionstyle="arc3,rad=0.16"))
    ax.text(5.42, 3.62, "落在同一条线上：排序时它们同级", fontsize=9.0, color=MUTED,
            ha="center", va="bottom", rotation=-22)

    ax.text(11.35, 0.62, "爆炸半径 BR（对象数）→", fontsize=9.6, color=MUTED,
            ha="right", va="top")
    ax.text(0.95, 6.12, "攻击面 AS（未授权可达的入口数）↑", fontsize=9.6, color=MUTED,
            ha="left", va="bottom")

    ax.text(0.15, 0.52,
            "R ≈ AS × BR × (1 - D)：D 是门禁实际拦住的比例。同一条线上的两点等价，先改哪一点取决于「哪个便宜」。",
            fontsize=9.2, color=INK, va="top")
    ax.text(0.15, 0.18,
            "多数情况下，缩 BR 比缩 AS 便宜：改一个参数校验，比拆掉一整个入口快得多。",
            fontsize=9.0, color=MUTED, va="top")

    head(ax, ys, "同一个风险，有两种长相：小而多，或大而少",
         "等值线上两点等价；这张图只用来排序先后，不用于估算概率")
    stamp(ax, "结构示意：曲线形状只表达「乘积等价」这一关系，坐标轴无刻度值。若有人拿它算出「我有 0.3 的风险」，那是误用。")
    save(fig, "ch04/fig-02-risk-contour.png")


# ===========================================================================
# ch09 · 图 1-1：未登录重放的三步判读（判定标准示意）
# ===========================================================================
def fig_ch09_replay_verdicts() -> None:
    rows = [
        ("第一步\n未登录加载页面\n捕获所有数据库请求", [
            ("只看到公开数据\n私有表无请求", FAST),
            ("anon key 出现在\n前端 bundle 里", SAND),
            ("未登录即可读\n私有表", ALERT),
        ]),
        ("第二步\n重放并要求\n「给我全表」", [
            ("返回 0 行 / 403", FAST),
            ("返回少量\n非本人数据", SAND),
            ("返回整张表", ALERT),
        ]),
        ("第三步\n用 A 的身份\n请求 B 的数据", [
            ("403 / 空结果", FAST),
            ("越界读到\n个别字段", SAND),
            ("完整读到 B 的\n身份与订单", ALERT),
        ]),
    ]

    fig, ax, ys = canvas(10.4, 5.8, 12.4)
    x_start, cw, bh = 3.40, 2.85, 1.20

    for j, (label, color) in enumerate([("健康", FAST), ("可疑", SAND), ("已失守", ALERT)]):
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

    ax.text(0.10, 1.24,
            "第三步最容易被漏掉：第二步全过，只说明「陌生人进不来」；第三步才回答「进来的人会不会互相看见」。",
            fontsize=9.4, color=INK, va="top")
    ax.text(0.10, 0.88,
            "三步都在浏览器里完成，不碰生产写入；任何一步拿到「已失守」，第一动作是吊销密钥，不是改代码。",
            fontsize=9.4, color=ALERT, va="top")

    head(ax, ys, "未登录重放：三步走完，才知道门是虚掩还是没装")
    stamp(ax, "判定标准示意：具体状态码按你的后端而定；判据是「未授权主体能否拿到非公开数据」，不是状态码本身。", 0.03)
    save(fig, "ch09/fig-01-replay-verdicts.png")


# ===========================================================================
# ch09 · 图 1-2：人在环的三判据矩阵（决策框架示意）
# ===========================================================================
def fig_ch09_hitl_matrix() -> None:
    cols = ["1 行 / 1 个对象", "1 千行 / 1 个服务", "全库 / 全租户"]
    rows = ["可回滚\n（有备份或幂等）", "需恢复\n（有快照，分钟级）", "不可逆\n（对外已发生）"]
    cells = [
        [("自动放行", "记录即可", "#E7F3EF", FAST),
         ("自动 + 事后审", "次日抽样", "#F3F6E8", "#6F7F26"),
         ("单人在环", "看 diff 再按", "#FBF0DA", SAND)],
        [("自动 + 告警", "失败即通知", "#F3F6E8", "#6F7F26"),
         ("单人在环", "带预演输出", "#FBF0DA", SAND),
         ("双人 + 预演", "先 dry-run", "#FBEDE6", SLOW)],
        [("单人在环", "说清不可逆", "#FBF0DA", SAND),
         ("双人 + 预演", "二次确认不复用", "#FBEDE6", SLOW),
         ("默认禁止", "走例外流程", "#F6E4E4", ALERT)],
    ]

    fig, ax, ys = canvas(10.0, 6.4, 12.0)
    cw, ch, x_start, y0 = 2.60, 1.30, 3.50, 2.30

    for j, c in enumerate(cols):
        ax.text(x_start + j * cw + cw / 2, y0 + 3 * ch + 0.16, c, fontsize=10.2,
                ha="center", va="bottom", fontweight="bold", color=INK)
    ax.text(x_start + 1.5 * cw, y0 + 3 * ch + 0.58, "影响半径 →", fontsize=9.6,
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

    ax.text(0.42, y0 + 1.5 * ch, "可逆性 ↑", fontsize=10.6, color=INK,
            ha="center", va="center", fontweight="bold", rotation=90)

    ax.text(0.10, 1.72,
            "唯一需要背下来的一条：可观测性是可加项——看不见的动作，一律升一档复核。",
            fontsize=9.9, color=INK, va="top")
    ax.text(0.10, 1.32,
            "因为左边的判据（影响几行、能不能回滚）都要求你「先看得见」；看不见时你并没有判断，只有赌。",
            fontsize=9.2, color=MUTED, va="top")

    head(ax, ys, "一个动作要不要人在环：看三件事，而不是看「重不重要」",
         "判据 = 不可逆性 × 影响半径；可观测性作为升档修正项")
    stamp(ax, "决策框架示意：档位名称可按团队调整；「默认禁止」不是保守，是承认这类动作缺少可回退路径。")
    save(fig, "ch09/fig-02-hitl-matrix.png")


# ===========================================================================
# ch02 · 图 1-1：三类越权的对照矩阵（结构示意）
# ===========================================================================
def fig_ch02_privilege_shapes() -> None:
    fig, ax, ys = canvas(11.2, 6.0, 12.6)

    rows = [
        # (形态名, 白话, 怎么发现)
        ("横向越权", "同层的人互相看见", "用 A 的令牌请求 B 的资源，看是否 200"),
        ("纵向越权", "低权限干高权限的事", "用普通账号逐个请求管理端路由"),
        ("代理越权", "借你之手做他没权限做的事", "审计日志里「操作者」 != 「实际授权者」"),
    ]

    y_rows = [5.05, 3.55, 2.05]
    for (name, plain, detect), y in zip(rows, y_rows):
        ax.text(0.15, y + 0.30, name, fontsize=11.0, fontweight="bold", color=INK, va="center")
        ax.text(0.15, y - 0.10, plain, fontsize=8.8, color=MUTED, va="center")

        # 迷你示意（x 3.4—7.0）
        if name == "横向越权":
            ax.add_patch(Circle((3.75, y), 0.24, facecolor=STEEL, edgecolor="white", linewidth=1.2))
            ax.add_patch(Circle((5.55, y), 0.24, facecolor=ALERT, edgecolor="white", linewidth=1.2))
            ax.text(3.75, y, "A", fontsize=9.2, color="white", ha="center", va="center", fontweight="bold")
            ax.text(5.55, y, "B", fontsize=9.2, color="white", ha="center", va="center", fontweight="bold")
            ax.plot([4.65, 4.65], [y - 0.55, y + 0.55], color=MUTED, linewidth=1.1, linestyle="--")
            ax.annotate("", xy=(5.25, y), xytext=(4.05, y),
                        arrowprops=dict(arrowstyle="-|>", color=ALERT, linewidth=1.5))
        elif name == "纵向越权":
            ax.add_patch(Circle((3.75, y - 0.32), 0.24, facecolor=STEEL, edgecolor="white", linewidth=1.2))
            ax.add_patch(Circle((5.55, y + 0.32), 0.24, facecolor=ALERT, edgecolor="white", linewidth=1.2))
            ax.text(3.75, y - 0.32, "低", fontsize=8.6, color="white", ha="center", va="center", fontweight="bold")
            ax.text(5.55, y + 0.32, "高", fontsize=8.6, color="white", ha="center", va="center", fontweight="bold")
            ax.plot([3.30, 6.00], [y, y], color=MUTED, linewidth=1.1, linestyle="--")
            ax.annotate("", xy=(5.28, y + 0.28), xytext=(4.02, y - 0.26),
                        arrowprops=dict(arrowstyle="-|>", color=ALERT, linewidth=1.5,
                                        connectionstyle="arc3,rad=-0.18"))
        else:
            ax.add_patch(Circle((3.55, y - 0.28), 0.22, facecolor="#B8C1CC", edgecolor="white", linewidth=1.2))
            ax.add_patch(Circle((5.15, y), 0.26, facecolor=STEEL, edgecolor="white", linewidth=1.2))
            ax.add_patch(Circle((6.75, y + 0.28), 0.22, facecolor=ALERT, edgecolor="white", linewidth=1.2))
            ax.text(3.55, y - 0.28, "攻", fontsize=8.6, color="white", ha="center", va="center", fontweight="bold")
            ax.text(5.15, y, "智", fontsize=8.6, color="white", ha="center", va="center", fontweight="bold")
            ax.text(6.75, y + 0.28, "资", fontsize=8.6, color="white", ha="center", va="center", fontweight="bold")
            ax.annotate("", xy=(4.92, y - 0.06), xytext=(3.78, y - 0.22),
                        arrowprops=dict(arrowstyle="-|>", color=MUTED, linewidth=1.3))
            ax.annotate("", xy=(6.52, y + 0.22), xytext=(5.42, y + 0.06),
                        arrowprops=dict(arrowstyle="-|>", color=ALERT, linewidth=1.5))
            ax.text(5.15, y - 0.46, "持凭据", fontsize=8.0, color=MUTED, ha="center", va="top")

        ax.text(7.70, y, detect, fontsize=9.0, color=INK, va="center", linespacing=1.7)
        ax.plot([0.15, 12.35], [y - 0.78, y - 0.78], color="#F1F3F5", linewidth=0.9)

    ax.text(0.15, 1.06,
            "第三种是智能体时代的新主力：它不需要攻破任何权限，只需要说服一个已经拥有权限的程序。",
            fontsize=9.4, color=ALERT, va="top")
    ax.text(0.15, 0.70,
            "前两种越权靠「查得细」，第三种靠「看链路」——它的痕迹不在请求里，在审计日志的角色差异里。",
            fontsize=9.0, color=MUTED, va="top")

    head(ax, ys, "三种越权，三种发现方式：前两种测请求，第三种测链路",
         "圆点只是位置示意；虚线表示一条边界（同层 / 权限级别 / 身份与执行的分离）")
    stamp(ax, "结构示意：不对应任何真实系统。第三种（代理越权）是本书第 02 章之后所有讨论的主语。")
    save(fig, "ch02/fig-01-privilege-shapes.png")


# ===========================================================================
# ch02 · 图 1-2：自主度阶梯与半径放大（结构示意）
# ===========================================================================
def fig_ch02_agency_ladder() -> None:
    fig, ax, ys = canvas(10.8, 5.9, 12.2)

    steps = [
        ("逐次批准", "每一步都按一下", "1 次动作", 0.80, FAST),
        ("单步批准", "同一步内自动续跑", "几次动作", 1.70, "#6F7F26"),
        ("计划批准", "批的是「计划」，不是动作", "一条链路", 2.90, SAND),
        ("自主循环", "无人在环，自己决定下一步", "无限次", 4.15, ALERT),
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
    ax.text(11.85, base_y - 1.10, "自主度 →", fontsize=9.4, color=MUTED, ha="right", va="top")
    ax.text(0.62, 3.55, "单次动作可影响的对象数 ↑", fontsize=9.4, color=MUTED,
            ha="center", va="center", rotation=90)

    ax.text(0.15, 0.86,
            "注意「计划批准」这一格：它看起来有人把关，但被批准的是一段描述，不是那个确切的动作——批准文本 != 批准行为。",
            fontsize=9.2, color=INK, va="top")
    ax.text(0.15, 0.52,
            "所以「最小自主性」要问的是：这一步之后，还有没有人能在结果发生前拦下来？",
            fontsize=9.0, color=MUTED, va="top")

    head(ax, ys, "自主度阶梯：权限一字不改，半径也能长出来",
         "四档从左到右，「没有人批准过的动作」越来越长")
    stamp(ax, "结构示意：柱高只表示相对关系，不表示具体对象数。这四档是常见形态，不是完整分类。", 0.14)
    save(fig, "ch02/fig-02-agency-ladder.png")


# ===========================================================================
# ch05 · 图 1-1：注入进入上下文的四条路径（结构示意）
# ===========================================================================
def fig_ch05_injection_paths() -> None:
    fig, ax, ys = canvas(11.0, 6.0, 12.4)

    # 中央：上下文窗口
    ax.add_patch(FancyBboxPatch((4.55, 2.35), 3.30, 1.95,
                                boxstyle="round,pad=0.012,rounding_size=0.05",
                                facecolor="#ECEFF2", edgecolor=INK, linewidth=1.3))
    ax.text(6.20, 3.72, "上下文窗口", fontsize=11.6, color=INK, ha="center", va="center",
            fontweight="bold")
    ax.text(6.20, 3.28, "指令与数据排在同一行", fontsize=9.0, color=MUTED,
            ha="center", va="center")
    ax.text(6.20, 2.90, "模型分不清谁是命令", fontsize=9.0, color=MUTED,
            ha="center", va="center")

    paths = [
        ("网页抓取", "HTML 注释里的「忽略之前的指令」", 1.85, 5.35, SLOW),
        ("文件与依赖", "README、issue、包描述里的隐藏文本", 1.85, 2.05, SLOW),
        ("用户消息", "直接说「顺便把之前的都导出来」", 9.35, 5.35, SAND),
        ("长期记忆", "被存成「用户偏好」，下次会话仍生效", 9.35, 2.05, ALERT),
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

    ax.text(0.15, 1.10,
            "四条路径的共同点：文本本身不执行，它只是被读进去。所以「防注入」防的不是执行，是「被当作指令」。",
            fontsize=9.2, color=INK, va="top")
    ax.text(0.15, 0.74,
            "第四条（长期记忆）最麻烦：一次性注入用完就没了，记忆投毒会一直生效——它把一次越权变成一种状态。",
            fontsize=9.0, color=ALERT, va="top")

    head(ax, ys, "注入怎么进来：四条路，都不需要攻破任何权限",
         "左边两条来自外部文本，右上来自用户消息，右下来自长期记忆——四条都不需要攻破权限")
    stamp(ax, "结构示意：路径数量按常见形态归纳，不是穷举；真正的入口以你的数据流图为准（见第 03 章）。")
    save(fig, "ch05/fig-01-injection-paths.png")


# ===========================================================================
# ch05 · 图 1-2：审批频率与实际阅读率（定性示意）
# ===========================================================================
def fig_ch05_approval_fatigue() -> None:
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
            "第 40 次：习惯性点「同意」", fontsize=9.2, color=ALERT, ha="left", va="bottom")
    ax.add_patch(Circle((2.05, 1.15 + 3.9 * (0.92 ** (2.5 * 0.9))), 0.17,
                        facecolor=FAST, edgecolor="white", linewidth=1.2))
    ax.text(2.35, 1.15 + 3.9 * (0.92 ** (2.5 * 0.9)) + 0.22,
            "第 1 次：逐行读", fontsize=9.2, color=FAST, ha="left", va="bottom")

    ax.text(10.95, 0.82, "当日审批次数 →", fontsize=9.4, color=MUTED, ha="right", va="top")
    ax.text(0.82, 3.25, "实际阅读率 ↑", fontsize=9.4, color=MUTED, ha="center", va="center",
            rotation=90)

    ax.text(0.15, 0.62,
            "所以高频低危的动作要自动放行：不是「少一道关卡」，是把注意力留给真正危险的那几次。",
            fontsize=9.2, color=INK, va="top")
    ax.text(0.15, 0.28,
            "审批的设计目标不是「让人看见」，是「让人在关键那一次真的看」。",
            fontsize=9.0, color=MUTED, va="top")

    head(ax, ys, "审批疲劳：弹窗越多，读的人越少",
         "曲线形状表达机制，不表达任何测量结果")
    stamp(ax, "定性示意：横纵坐标无刻度值。这条曲线在人因工程里被反复观察到，但它不是本章的实测数据。")
    save(fig, "ch05/fig-02-approval-fatigue.png")


# ===========================================================================
# ch06 · 图 1-1：一次请求在 RLS 开 / 关下的两条路径（结构示意）
# ===========================================================================
def fig_ch06_rls_paths() -> None:
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
    ax.text(0.15, 5.28, 'RLS 关（默认值）', fontsize=11.0, fontweight='bold', color=ALERT, va='center')
    node(1.95, 4.80, 1.85, 0.90, '浏览器\nanon key', '#ECEFF2', '#B8C1CC')
    node(4.35, 4.80, 1.85, 0.90, 'REST 接口', '#ECEFF2', '#B8C1CC')
    node(6.75, 4.80, 1.85, 0.90, '数据库', '#ECEFF2', '#B8C1CC')
    node(9.15, 4.80, 2.35, 0.90, '返回全表', '#F6E4E4', ALERT, tc=ALERT, bold=True)
    arrow(3.85, 5.25, 4.30, 5.25, MUTED)
    arrow(6.25, 5.25, 6.70, 5.25, MUTED)
    arrow(8.65, 5.25, 9.10, 5.25, ALERT)
    ax.text(5.45, 4.52, '没有任何一层做过「这个人能不能读这一行」的判断', fontsize=8.6,
            color=MUTED, ha='center', va='top')

    ax.plot([0.15, 12.35], [3.75, 3.75], color=GRID, linewidth=1.1)

    # 下排：RLS 开
    ax.text(0.15, 2.72, 'RLS 开（加四条策略）', fontsize=11.0, fontweight='bold', color=FAST, va='center')
    node(1.95, 2.24, 1.85, 0.90, '浏览器\nanon key', '#ECEFF2', '#B8C1CC')
    node(4.35, 2.24, 1.85, 0.90, 'REST 接口', '#ECEFF2', '#B8C1CC')
    node(6.75, 2.24, 1.85, 0.90, '策略判定', '#E7F3EF', FAST, tc=FAST, bold=True)
    node(9.15, 2.24, 2.35, 0.90, '返回 0 行', '#E7F3EF', FAST, tc=FAST, bold=True)
    arrow(3.85, 2.69, 4.30, 2.69, MUTED)
    arrow(6.25, 2.69, 6.70, 2.69, MUTED)
    arrow(8.65, 2.69, 9.10, 2.69, FAST)
    ax.text(5.45, 1.96, '每一行都要过一遍 owner_id = auth.uid()；过不了就不返回', fontsize=8.6,
            color=MUTED, ha='center', va='top')

    ax.text(0.15, 1.10,
            '两排的差别只有一处：中间多了「策略判定」。页面长得一模一样，登录都能成功——所以它不会报错，它只是不拦。',
            fontsize=9.2, color=INK, va='top')
    ax.text(0.15, 0.72,
            '这就是第 01 章说的缺失型缺陷：功能测试跑两排都会绿，只有「应当失败」的断言能分出差别。',
            fontsize=9.0, color=MUTED, va='top')

    head(ax, ys, '同一个请求，两种结果：差别不在代码，在一行策略',
         '上排是默认值；下排是加了四条 policy 之后')
    stamp(ax, '结构示意：REST 接口与数据库之间的中间层按你的架构而定；关键在于「谁做策略判定」。')
    save(fig, 'ch06/fig-01-rls-paths.png')


# ===========================================================================
# ch06 · 图 1-2：三种修法，三个边界位置（结构示意）
# ===========================================================================
def fig_ch06_boundary_positions() -> None:
    fig, ax, ys = canvas(11.2, 5.8, 12.6)

    schemes = [
        ('A. 行级安全（RLS）', '策略写在数据库里',
         ['浏览器', 'REST 直连', '数据库 + 策略'], 2, '改策略 = 改数据库；开发最省事，策略多了难维护'),
        ('B. 服务端代理', '收回前端直连，读写都走你的 API',
         ['浏览器', '你的 API', '数据库'], 1, '多一层代码与延迟；业务规则与审计都在你手里'),
        ('C. 受限视图', '前端只读视图，写全走函数',
         ['浏览器', '受限视图', '数据库'], 1, '视图要跟 schema 演进；复杂查询受限'),
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
        ax.text(x + 3.02, by, '边界', fontsize=8.2, color=ALERT, ha='left', va='center')

        ax.text(x + 1.55, 0.98, note, fontsize=8.2, color=MUTED, ha='center', va='top',
                linespacing=1.6)

    ax.text(0.15, 0.52,
            '三者没有谁更安全，只有「你更愿意维护哪一层」。不选，等于把边界放在「攻击者的善意」上。',
            fontsize=9.2, color=INK, va='top')

    head(ax, ys, '三种修法：信任边界放在三个不同的地方',
         '绿色那层是「判定发生的地方」；虚线之上是不可信区，之下是可信区')
    stamp(ax, '结构示意：层次按常见架构归纳；你的系统可能多一层（CDN、网关），判定位置不变即可。')
    save(fig, 'ch06/fig-02-boundary-positions.png')


# ===========================================================================
# ch07 · 图 1-1：依赖进入系统的四条路径与各自唯一的拦截点
# ===========================================================================
def fig_ch07_supply_paths() -> None:
    fig, ax, ys = canvas(11.2, 6.0, 12.6)

    lanes = [
        ('包管理器', 'npm install / pip install', '幻觉包名被抢注', 'lockfile + 允许清单'),
        ('MCP 服务器', '装配置就等于装代码', '启动时读 ~/.aws/credentials', '来源三对齐 + 容器隔离'),
        ('构建脚本', 'postinstall / prepare', '安装时就执行任意命令', '审查 scripts 字段'),
        ('远程资源', '模型/工具下载的文件', '内容被替换', '校验哈希 + 固定版本'),
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
        ax.text(10.15, y, '你的进程', fontsize=8.8, color=MUTED, va='center')
        if i < 3:
            ax.plot([0.15, 12.35], [y - 0.52, y - 0.52], color='#F1F3F5', linewidth=0.9)

    ax.text(0.15, 0.72,
            '四条路径的共同点：「进入点只有一个」，而拦截点也只有一个。错过那个点，后面没有任何一层会替你拦。',
            fontsize=9.2, color=INK, va='top')
    ax.text(0.15, 0.38,
            '「我把源码看了一遍」不构成控制——你看的不是运行时真正执行的那份代码（postinstall、远程下载、传递依赖都会绕过它）。',
            fontsize=9.0, color=MUTED, va='top')

    head(ax, ys, '依赖不是「装个包」，是「放一段代码进来」',
         '每条路径只有一个拦截点；拦不住的那一格，就是你的攻击面')
    stamp(ax, '结构示意：四条路径按常见形态归纳，不是穷举；真正的入口以你的构建与安装流程为准。')
    save(fig, 'ch07/fig-01-supply-paths.png')


# ===========================================================================
# ch07 · 图 1-2：令牌透传与受众绑定（结构示意）
# ===========================================================================
def fig_ch07_token_relay() -> None:
    fig, ax, ys = canvas(11.2, 5.8, 12.6)

    def box(x, y, w, h, label, fc, ec, tc=None):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                    boxstyle='round,pad=0.012,rounding_size=0.04',
                                    facecolor=fc, edgecolor=ec, linewidth=1.2))
        ax.text(x + w / 2, y + h / 2, label, fontsize=9.2, color=tc or INK,
                ha='center', va='center', linespacing=1.6)

    # 上排：有受众绑定
    ax.text(0.15, 5.05, '有受众绑定（RFC 8707）', fontsize=11.0, fontweight='bold',
            color=FAST, va='center')
    box(1.60, 4.55, 1.90, 0.86, '用户', '#ECEFF2', '#B8C1CC')
    box(4.35, 4.55, 1.90, 0.86, '服务 A', '#E7F3EF', FAST, tc=FAST)
    box(7.10, 4.55, 1.90, 0.86, '服务 B', '#F6E4E4', ALERT, tc=ALERT)
    box(9.85, 4.55, 1.90, 0.86, '拒绝', '#F6E4E4', ALERT, tc=ALERT, )
    ax.annotate('', xy=(4.30, 4.98), xytext=(3.55, 4.98),
                arrowprops=dict(arrowstyle='-|>', color=MUTED, linewidth=1.4))
    ax.annotate('', xy=(7.05, 4.98), xytext=(6.30, 4.98),
                arrowprops=dict(arrowstyle='-|>', color=ALERT, linewidth=1.4))
    ax.text(6.68, 5.22, '转发', fontsize=8.0, color=ALERT, ha='center', va='bottom')
    ax.annotate('', xy=(9.80, 4.98), xytext=(9.05, 4.98),
                arrowprops=dict(arrowstyle='-|>', color=ALERT, linewidth=1.4))
    ax.text(9.42, 5.22, '拒收', fontsize=8.0, color=ALERT, ha='center', va='bottom')
    ax.text(5.20, 4.28, 'token 只对 A 有效', fontsize=8.4, color=FAST,
            ha='center', va='top')

    ax.plot([0.15, 12.35], [3.55, 3.55], color=GRID, linewidth=1.1)

    # 下排：无受众绑定
    ax.text(0.15, 2.72, '无受众绑定（令牌透传）', fontsize=11.0, fontweight='bold',
            color=ALERT, va='center')
    box(1.60, 2.22, 1.90, 0.86, '用户', '#ECEFF2', '#B8C1CC')
    box(4.35, 2.22, 1.90, 0.86, '服务 A', '#ECEFF2', '#B8C1CC')
    box(7.10, 2.22, 1.90, 0.86, '服务 B', '#F6E4E4', ALERT, tc=ALERT)
    box(9.85, 2.22, 1.90, 0.86, '服务 C', '#F6E4E4', ALERT, tc=ALERT)
    for x1, x2 in ((3.55, 4.30), (6.30, 7.05), (9.05, 9.80)):
        ax.annotate('', xy=(x2, 2.65), xytext=(x1, 2.65),
                    arrowprops=dict(arrowstyle='-|>', color=ALERT, linewidth=1.4))
    ax.text(5.20, 1.95, '一环失守，全链沦陷', fontsize=8.4, color=ALERT,
            ha='center', va='top')

    ax.text(0.15, 1.02,
            '受众绑定要求 token 里写明「这是发给谁的」。没有它，下游无法分辨「这是用户本人，还是 A 在借用」。',
            fontsize=9.2, color=INK, va='top')
    ax.text(0.15, 0.66,
            '同理，「请在对话框里粘贴你的 API key」也是把凭据送进日志与上下文——URL 模式授权才是对的。',
            fontsize=9.0, color=MUTED, va='top')

    head(ax, ys, '令牌透传：一环失守，为什么全链沦陷',
         '上排是正确设计；下排是没有受众绑定时的现实')
    stamp(ax, '结构示意：服务数量与调用关系按常见形态简化；判据是「下游能否分辨调用者身份」。')
    save(fig, 'ch07/fig-02-token-relay.png')


# ===========================================================================
# ch08 · 图 1-1：级联故障的放大链（结构示意）
# ===========================================================================
def fig_ch08_cascade() -> None:
    fig, ax, ys = canvas(11.2, 5.8, 12.6)

    steps = [
        ('上游限流', '一次 429', 1.35, SAND),
        ('客户端重试', '×3 立即重试', 1.75, SLOW),
        ('更多 429', '并发放大', 2.15, SLOW),
        ('重试风暴', '×3 ×3 = 9 倍', 2.55, ALERT),
        ('全站不可用', '不相干的服务也挂', 2.30, ALERT),
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

    ax.annotate('每一格都「合理」：失败了当然要重试。\n但没有人算过 3 × 3 × 3 会变成多少。',
                xy=(3.10, 4.45), xytext=(1.20, 5.15),
                fontsize=9.2, color=ALERT, linespacing=1.6,
                arrowprops=dict(arrowstyle='-|>', color=ALERT, linewidth=1.2,
                                connectionstyle='arc3,rad=-0.18'))

    ax.text(0.15, 2.30,
            '断路的作用：在「更多 429」之前把重试掐掉。它不是让服务更快，是让失败变便宜。',
            fontsize=9.2, color=INK, va='top')
    ax.text(0.15, 1.92,
            '配套纪律：重试要有预算（次数 + 总时长），且必须指数退避；无预算的重试等于把一次故障放大成一次事故。',
            fontsize=9.0, color=MUTED, va='top')

    head(ax, ys, '级联故障：一次失败怎么变成全站事故',
         '每一步单独看都合理；合起来是一条放大链')
    stamp(ax, '结构示意：倍数只表达「乘法放大」这一关系，不对应任何具体系统的实测值。')
    save(fig, 'ch08/fig-01-cascade.png')


# ===========================================================================
# ch08 · 图 1-2：断路器状态机（结构示意）
# ===========================================================================
def fig_ch08_circuit_breaker() -> None:
    fig, ax, ys = canvas(11.2, 5.6, 12.6)

    states = [
        ('闭合', '正常放行\n失败计数 +1', 1.55, 3.55, '#E7F3EF', FAST),
        ('打开', '全部快速失败\n不发请求', 5.05, 3.55, '#F6E4E4', ALERT),
        ('半开', '放一个试探请求\n成功→闭合', 8.55, 3.55, '#FBF0DA', SAND),
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
    ax.text(4.55, 4.34, '失败超阈值', fontsize=8.2, color=ALERT, ha='center', va='bottom')
    ax.annotate('', xy=(8.50, 4.22), xytext=(7.60, 4.22),
                arrowprops=dict(arrowstyle='-|>', color=SAND, linewidth=1.4))
    ax.text(8.05, 4.34, '超时到期', fontsize=8.2, color=SAND, ha='center', va='bottom')

    # 一条回边：半开 →（试探成功）→ 闭合，走方框下方
    xs = [10.20, 10.20, 2.80, 2.80]
    ys_path = [3.55, 2.75, 2.75, 3.55]
    ax.plot(xs[:3], ys_path[:3], color=FAST, linewidth=1.5)
    ax.annotate('', xy=(2.80, 3.52), xytext=(2.80, 3.10),
                arrowprops=dict(arrowstyle='-|>', color=FAST, linewidth=1.5))
    ax.text(6.50, 2.52, '试探成功 → 回到闭合（试探失败 → 回到打开）', fontsize=8.6,
            color=FAST, ha='center', va='top')

    ax.text(0.15, 1.72,
            '三个状态的价值在于「让失败变便宜」：打开时请求不发出去，上游喘口气，你也省了钱。',
            fontsize=9.2, color=INK, va='top')
    ax.text(0.15, 1.34,
            '没演练过的断路器不算有：它会在你最需要它的时候才发现阈值配错了。',
            fontsize=9.0, color=MUTED, va='top')

    head(ax, ys, '断路器：让失败变便宜的三个状态',
         '闭合 → 打开 → 半开 → 闭合；关键在「半开只放一个试探」')
    stamp(ax, '结构示意：阈值与超时按你的上游而定；状态机形状是标准做法，不是本书发明。', 0.30)
    save(fig, 'ch08/fig-02-circuit-breaker.png')


# ===========================================================================
# ch10 · 图 1-1：三条断言在流水线上的位置
# ===========================================================================
def fig_ch10_pipeline() -> None:
    fig, ax, ys = canvas(11.2, 5.6, 12.6)

    stages = [
        ('本地编辑', 1.65),
        ('提交 / pre-commit', 2.35),
        ('CI / PR', 2.35),
        ('预发布', 1.95),
        ('生产', 1.65),
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
        ('断言 1 · 数据层越权必须失败', 2, 'replay_probe 退出码', SLOW),
        ('断言 2 · 前端产物无万能钥匙', 1, 'grep 构建产物', STEEL),
        ('断言 3 · 依赖不在清单外', 1, 'dependency_allowlist', STEEL),
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

    ax.text(0.15, 1.02,
            '三条断言越靠左越便宜。它们测的都是「不该发生的没发生」，而不是「该发生的发生了」。',
            fontsize=9.2, color=INK, va='top')
    ax.text(0.15, 0.66,
            '第 1 条最关键：它是唯一一条测数据层的。其余两条测的是产物与依赖——门锁没锁，只能问数据库。',
            fontsize=9.0, color=MUTED, va='top')

    head(ax, ys, '三条断言放在哪：越靠左越便宜',
         '圆点是断言挂载的位置；它不是「多一道检查」，是「一条会红的测试」')
    stamp(ax, '结构示意：流水线阶段按常见形态归纳；你的 CI 工具不同，位置逻辑不变。')
    save(fig, 'ch10/fig-01-pipeline.png')


# ===========================================================================
# ch10 · 图 1-2：安全属性的退化曲线（定性示意）
# ===========================================================================
def fig_ch10_decay() -> None:
    fig, ax, ys = canvas(10.2, 5.6, 11.6)

    ax.plot([1.25, 10.95], [1.15, 1.15], color=GRID, linewidth=1.2)
    ax.plot([1.25, 1.25], [1.15, 5.35], color=GRID, linewidth=1.2)

    xs = [1.25 + i * 0.32 for i in range(31)]
    no_gate = [4.35 - 3.10 * (i / 30) ** 0.7 for i in range(31)]
    with_gate = [4.35 - 0.35 * (i / 30) for i in range(31)]

    ax.plot(xs, no_gate, color=SLOW, linewidth=2.2)
    ax.plot(xs, with_gate, color=FAST, linewidth=2.2, linestyle='--')

    ax.text(8.35, no_gate[22] - 0.30, '不接断言：边界随功能增长持续退化',
            fontsize=9.0, color=SLOW, ha='left', va='top')
    ax.text(6.15, with_gate[20] + 0.20, '接了断言：每次改动都被打回去',
            fontsize=9.0, color=FAST, ha='left', va='bottom')

    ax.add_patch(Circle((2.05, 4.35), 0.16, facecolor=INK, edgecolor='white', linewidth=1.2))
    ax.text(2.35, 4.52, '上线那天', fontsize=8.8, color=INK, ha='left', va='bottom')

    ax.text(10.95, 0.95, '时间（月）→', fontsize=9.4, color=MUTED, ha='right', va='top')
    ax.text(0.82, 3.25, '边界完整性 ↑', fontsize=9.4, color=MUTED, ha='center', va='center',
            rotation=90)

    ax.text(0.15, 0.62,
            '这条曲线只表达一件事：不接回归的边界，会随功能增长持续退化，直到回到「全开」——'
            '所以第 10 章不是锦上添花，是让前面九章活过三个月。',
            fontsize=9.2, color=INK, va='top')

    head(ax, ys, '安全属性会退化：不做回归，它就回到全开',
         '实线是不接断言时；虚线是接了断言时')
    stamp(ax, '定性示意：纵轴无刻度值，曲线形状表达机制，不表达任何实测结果。', 0.22)
    save(fig, 'ch10/fig-02-decay.png')


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
    only = sys.argv[1] if len(sys.argv) > 1 else None
    print("生成配图：")
    for ch, fns in ALL.items():
        if only and ch != only:
            continue
        for fn in fns:
            fn()
    print("完成。")


if __name__ == "__main__":
    main()
