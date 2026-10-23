"""全书配图生成器 —— 一次跑完八张，输出到 assets/chXX/。

所有数字要么来自本仓代码的真实运行，要么在图下方标了出处；
没有任何一张图是"为了好看"画的。标 [示意] 的图在正文里也会被点明。

跑法：python make_figures.py
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import _figstyle as S

S.apply()
INK, MUTED, RULE, ACCENT, NEUTRAL, GOOD, WASH = (
    S.INK, S.MUTED, S.RULE, S.ACCENT, S.NEUTRAL, S.GOOD, S.WASH
)


# ============================================================ 第 01 章
def ch01_detection_matrix():
    defects = ["幻觉依赖\nsign_token 不存在", "拼接 SQL\n券码当语法", "一用户一次\n表建了没人写",
               "并发超发\n读与写之间无锁", "凭证为 None\n断言只查键名"]
    methods = ["依赖门禁", "编译器\n+ linter", "AI 单测\n覆盖率 100%", "行为测试\n按规格写", "并发压测"]
    # 真实结果：来自 case_coupon 的 four-gate 运行与 ch08 压测
    m = [
        [1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 1, 0],
    ]

    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    for r, row in enumerate(m):
        for c, v in enumerate(row):
            ax.add_patch(Rectangle((c, len(m) - 1 - r), 0.94, 0.94,
                                   facecolor=GOOD if v else "#EDEFF2",
                                   edgecolor="white", linewidth=2))
            ax.text(c + 0.47, len(m) - 1 - r + 0.47, "抓到" if v else "漏",
                    ha="center", va="center", fontsize=9.5,
                    color="white" if v else "#9CA3AF",
                    fontweight="bold" if v else "normal")

    ax.set_xlim(0, len(methods))
    ax.set_ylim(0, len(m))
    # 列名不用刻度标签，直接画在格子上方——避免与副标题抢位置
    ax.set_xticks([])
    for c, name in enumerate(methods):
        ax.text(c + 0.47, len(m) + 0.28, name, ha="center", va="bottom",
                fontsize=9.5, color=INK, linespacing=1.5)
    ax.set_yticks([len(m) - 1 - i + 0.47 for i in range(len(defects))])
    ax.set_yticklabels(defects, fontsize=9.5, color=INK)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    ax.set_title("五个缺陷，五道闸，每一列都只覆盖了一种失败",
                 loc="left", fontsize=12.5, color=INK, pad=54, fontweight="bold")
    ax.text(0.0, -0.115, "同一份代码，没有一列能单独撑住", transform=ax.transAxes,
            fontsize=9.5, color=MUTED, va="top")
    S.footnote(fig, "数据：case_coupon 真实运行结果（dependency_gate / py_compile / unittest / stress_oversell）。",
               "注意右下角的空行：并发超发只被压测抓到，而压测按定义不能进 CI 做门禁。")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(S.out("ch01", "fig-01-detection-matrix.png"), bbox_inches="tight")
    plt.close(fig)


# ============================================================ 第 02 章
def ch02_pass_rate():
    fig, ax = plt.subplots(figsize=(7.4, 4.2))

    ax.bar(0, 100, width=0.62, color=NEUTRAL)
    ax.text(0, 103, "100%", ha="center", va="bottom", fontsize=15, color=INK, fontweight="bold")

    ax.bar(1, 56, width=0.62, color=ACCENT)
    ax.text(1, 59, "56%", ha="center", va="bottom", fontsize=15, color=ACCENT, fontweight="bold")

    ax.add_patch(Rectangle((2 - 0.31, 0), 0.62, 108, facecolor=WASH,
                           edgecolor=RULE, linestyle=(0, (4, 3)), linewidth=1.2))
    ax.text(2, 54, "没有\n可信数据", ha="center", va="center", fontsize=11, color=MUTED)
    ax.annotate("", xy=(2, 104), xytext=(2, 4),
                arrowprops=dict(arrowstyle="<->", color=RULE, linewidth=1.2))

    ax.set_xticks(range(3))
    ax.set_xticklabels(["语法通过率\n能解析、能编译", "安全通过率\n无已知漏洞模式",
                        "叠加人工复核\n与完整工具链之后"],
                       fontsize=9.5, color=INK)
    ax.set_ylim(0, 128)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(["0", "25", "50", "75", "100%"])
    ax.grid(axis="y", color=RULE, linewidth=0.8, alpha=0.6)
    ax.set_axisbelow(True)
    S.clean(ax)

    S.titles(ax, "同一批生成结果，两把尺子量出 44 个百分点的差",
             "编译器只检查「形状」，不检查「意图」")
    S.footnote(fig,
               "数据：Veracode《2026 GenAI Code Security Report》，100+ 模型、四轮快照。",
               "第三列不是 0，是「没有可信数据」——报告自述这是缺口，不是结论。")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(S.out("ch02", "fig-01-pass-rate-gap.png"), bbox_inches="tight")
    plt.close(fig)


# ============================================================ 第 04 章
def ch04_hallucinated():
    fig = plt.figure(figsize=(7.4, 3.5))
    ax = fig.add_axes([0.155, 0.30, 0.815, 0.52])
    rows = [("开源模型", 21.7, ACCENT), ("全部模型（均值）", 19.7, ACCENT), ("商用模型", 5.2, NEUTRAL)]

    for y, (lab, val, col) in enumerate(rows):
        ax.barh(y, val, height=0.28, color=col)
        ax.text(val + 0.5, y, f"{val}%", va="center", fontsize=12.5,
                color=col if col != NEUTRAL else INK, fontweight="bold")

    ax.set_yticks(range(3))
    ax.set_yticklabels([r[0] for r in rows], fontsize=10, color=INK)
    ax.set_xlim(0, 26)
    ax.set_xlabel("推荐出的包名在真实注册表里不存在的比例", fontsize=9.5, color=MUTED)
    ax.invert_yaxis()
    ax.grid(axis="x", color=RULE, linewidth=0.8, alpha=0.6)
    ax.set_axisbelow(True)
    S.clean(ax)

    S.titles(ax, "AI 推荐的包名有近五分之一根本不存在", "幻觉不是偶发错误，是可复现的行为")
    fig.text(0.012, 0.095, "数据：USENIX Security 2025 论文（本次经二手汇总转引）；独有幻觉包名 205,474 个。",
             fontsize=8, color=MUTED)
    fig.text(0.012, 0.030, "其中 43% 每次查询都复现同一个假名 —— 可复现就意味着可以被抢先注册。",
             fontsize=8, color=ACCENT)
    fig.savefig(S.out("ch04", "fig-01-hallucinated-packages.png"), bbox_inches="tight")
    plt.close(fig)


# ============================================================ 第 06 章
def ch06_pillars():
    pillars = ["防回归", "抗重构", "快速反馈", "可维护"]
    suites = ["A 空断言型", "B mock 型", "C 规格行为型"]
    # 评分依据见正文 6.4 节：防回归看变异分数，抗重构看重构探针，
    # 快速反馈看单次耗时，可维护看新人能否看懂断言意图。
    scores = [
        [1, 2, 5],
        [5, 1, 5],
        [5, 4, 4],
        [2, 2, 4],
    ]

    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    for r in range(len(pillars)):
        for c in range(len(suites)):
            v = scores[r][c]
            alpha = 0.15 + 0.85 * (v / 5)
            color = GOOD if v >= 4 else (ACCENT if v <= 2 else "#C08A2E")
            ax.add_patch(Rectangle((c, len(pillars) - 1 - r), 0.94, 0.94,
                                   facecolor=color, alpha=alpha, edgecolor="white", linewidth=2))
            ax.text(c + 0.47, len(pillars) - 1 - r + 0.47, str(v), ha="center", va="center",
                    fontsize=15, color=INK, fontweight="bold")

    ax.set_xlim(0, len(suites))
    ax.set_ylim(0, len(pillars))
    ax.set_xticks([])
    for c, s in enumerate(suites):
        ax.text(c + 0.47, len(pillars) + 0.16, s, ha="center", va="bottom", fontsize=9.5, color=INK)
    ax.set_yticks([len(pillars) - 1 - i + 0.47 for i in range(len(pillars))])
    ax.set_yticklabels(pillars, fontsize=10.5, color=INK)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)

    ax.set_title("两种烂法，烂在不同地方", loc="left", fontsize=12.5, color=INK,
                 pad=42, fontweight="bold")
    ax.text(0.0, -0.10, "分数 0—5，越高越好；四格的判据分别来自变异分数、重构探针、耗时与可读性",
            transform=ax.transAxes, fontsize=9.5, color=MUTED, va="top")
    S.footnote(fig, "评分是判断，不是测量；每条扣分理由在正文 6.4 节逐条给出，可复核。")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(S.out("ch06", "fig-01-four-pillars.png"), bbox_inches="tight")
    plt.close(fig)


# ============================================================ 第 07 章
def ch07_coverage_vs_mutation():
    fig, ax = plt.subplots(figsize=(7.4, 3.4))
    metrics = [("行覆盖率", [100, 100, 100]), ("变异分数", [25, 50, 100])]
    colors = [NEUTRAL, "#C08A2E", GOOD]
    names = ["A 空断言型", "B mock 型", "C 规格行为型"]

    for i, (name, vals) in enumerate(metrics):
        base = 1 - i
        for j, (v, col) in enumerate(zip(vals, colors)):
            y = base + 0.22 - j * 0.22
            ax.barh(y, v, height=0.18, color=col)
            ax.text(v + 1.5, y, f"{v}%", va="center", fontsize=10.5,
                    color=col if col != NEUTRAL else INK, fontweight="bold")

    ax.set_yticks([1, 0])
    ax.set_yticklabels([m[0] for m in metrics], fontsize=10.5, color=INK)
    ax.set_xlim(0, 118)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0", "25", "50", "75", "100%"])
    ax.grid(axis="x", color=RULE, linewidth=0.8, alpha=0.6)
    ax.set_axisbelow(True)
    S.clean(ax)
    ax.axhline(0.5, color=RULE, linewidth=0.8)

    handles = [Rectangle((0, 0), 1, 1, color=c) for c in colors]
    ax.legend(handles, names, frameon=False, fontsize=9.5, loc="upper center",
              bbox_to_anchor=(0.5, -0.16), ncol=3, labelcolor=INK)

    S.titles(ax, "覆盖率一样，守住的规则差四倍",
             "同一份实现、同一批变异体，只换测试套件")
    S.footnote(fig, "数据：case_coupon 真实运行（mutation_demo.py），变异体 4 个。")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(S.out("ch07", "fig-01-coverage-vs-mutation.png"), bbox_inches="tight")
    plt.close(fig)


# ============================================================ 第 08 章
def ch08_stress():
    labels = ["组1 原版\n配额 10 · 24 并发", "组2 原版\n配额 100 · 24 并发",
              "组3 修复版\n配额 10 · 24 并发", "组4 原版\n配额 1 · 2 并发"]
    rates = [100, 0, 0, 100]
    colors = [ACCENT, "#F0B429", GOOD, ACCENT]

    fig, ax = plt.subplots(figsize=(7.4, 3.9))
    bars = ax.bar(range(4), rates, width=0.55, color=colors)
    for b, v in zip(bars, rates):
        ax.text(b.get_x() + b.get_width() / 2, v + 3, f"{v}%", ha="center", va="bottom",
                fontsize=14, color=INK, fontweight="bold")

    ax.set_xticks(range(4))
    ax.set_xticklabels(labels, fontsize=9, color=INK)
    ax.set_ylim(0, 122)
    ax.set_yticks([0, 50, 100])
    ax.set_yticklabels(["0", "50", "100%"])
    ax.set_ylabel("30 轮里撞上超发的比例", fontsize=9.5, color=MUTED)
    ax.grid(axis="y", color=RULE, linewidth=0.8, alpha=0.6)
    ax.set_axisbelow(True)
    S.clean(ax)

    ax.annotate("这盏绿灯什么都没证明：\n负载没到配额，本来就撞不上",
                xy=(1, 4), xytext=(1.35, 55), fontsize=9.5, color="#8A5A00",
                arrowprops=dict(arrowstyle="-", color="#C08A2E", linewidth=1))

    S.titles(ax, "同样一盏绿灯，含义可以完全相反",
             "四组对照，每组 30 轮，代码只改一处")
    S.footnote(fig, "数据：code/ch08/stress_oversell.py 真实运行（每组 30 轮）。",
               "组2 与组3 都是 0%，但一个是负载不足，一个是真的修好了。")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(S.out("ch08", "fig-01-stress-detection.png"), bbox_inches="tight")
    plt.close(fig)


# ============================================================ 第 09 章
def ch09_three_readings():
    labels = ["行覆盖率", "分支覆盖率", "变异分数"]
    values = [100, 100, 25]
    colors = [NEUTRAL, NEUTRAL, ACCENT]

    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    bars = ax.bar(range(3), values, width=0.5, color=colors)
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, f"{v}%", ha="center", va="bottom",
                fontsize=15, color=ACCENT if v == 25 else INK, fontweight="bold")

    ax.set_xticks(range(3))
    ax.set_xticklabels(labels, fontsize=10.5, color=INK)
    ax.set_ylim(0, 120)
    ax.set_yticks([0, 50, 100])
    ax.set_yticklabels(["0", "50", "100%"])
    ax.grid(axis="y", color=RULE, linewidth=0.8, alpha=0.6)
    ax.set_axisbelow(True)
    S.clean(ax)

    ax.annotate("两个更精细的指标都说满分，\n只有它会说不对",
                xy=(2, 28), xytext=(1.15, 68), fontsize=10, color=INK,
                arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=1))

    S.titles(ax, "同一套测试，三个指标给出三个答案",
             "对象是 case_coupon 里那套 AI 写的测试")
    S.footnote(fig, "数据：coverage --branch 与 mutation_demo.py 真实运行。",
               "逃逸率没有画——它要等线上出事才有数，这正是它可信的原因。")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(S.out("ch09", "fig-01-three-readings.png"), bbox_inches="tight")
    plt.close(fig)


# ============================================================ 第 12 章
def ch12_gate_cost():
    gates = ["依赖门禁", "行为测试", "覆盖率统计", "变异测试（4 个变异体）"]
    secs = [0.05, 0.04, 0.05, 1.12]

    fig, ax = plt.subplots(figsize=(7.4, 3.4))
    bars = ax.barh(range(len(gates)), secs, height=0.45,
                   color=[GOOD, GOOD, GOOD, "#F0B429"])
    for b, v in zip(bars, secs):
        ax.text(v * 1.12, b.get_y() + b.get_height() / 2, f"{v:.2f}s",
                va="center", fontsize=11, color=INK)

    ax.set_yticks(range(len(gates)))
    ax.set_yticklabels(gates, fontsize=10, color=INK)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(0.02, 3)
    ax.set_xticks([0.05, 0.1, 0.5, 1.0])
    ax.set_xticklabels(["0.05", "0.1", "0.5", "1"], fontsize=9)
    ax.xaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_xlabel("单次运行耗时（秒，对数轴）", fontsize=9.5, color=MUTED)
    ax.grid(axis="x", color=RULE, linewidth=0.8, alpha=0.6)
    ax.set_axisbelow(True)
    S.clean(ax)

    S.titles(ax, "四道闸的成本差 28 倍，拦截能力却不能按成本排序",
             "变异测试贵，是因为它要把测试跑 N 遍；快的那三道闸便宜，是因为它们只跑一遍")
    S.footnote(fig, "数据：本仓真实计时（/usr/bin/time），代码量约 40 行，真实项目按测试数量等比放大。")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(S.out("ch12", "fig-01-gate-cost.png"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    ch01_detection_matrix()
    ch02_pass_rate()
    ch04_hallucinated()
    ch06_pillars()
    ch07_coverage_vs_mutation()
    ch08_stress()
    ch09_three_readings()
    ch12_gate_cost()
    print("done")
