#!/usr/bin/env python3
"""双语仓最小检查器（阶段 0 雏形；stdlib-only）。

用法：
    python3 tools/check_bilingual.py --min        # 最小模式（提交 (h) 起接 pre-commit）
    python3 tools/check_bilingual.py --strict     # 把 WARN 也升为 ERROR（阶段 2 (ii) 后启用）
    python3 tools/check_bilingual.py --report     # 数量对账报表（阶段 4 补齐）

检查集（随阶段扩容，见计划 §5.1 扩容表）：
    M4 链接半   ERROR（全程启用）：扫描域内 md 相对链接全部解析存在。
    M4 语言半   ERROR（配对出现即查）：X.zh.md 只引用 .zh.png；X.md 不得引用 .zh.png（只查图片目标）。
    M5 图题     ERROR（提交 (ii) 起）：文件 fig-NN ↔ 图题「图 C-NN」双处同号，C==chapter_id；章内 prose 无悬空图号。
    M9 README   ERROR（提交 (ii) 起）：树行路径全存在 + 叶名语言约定 + 「N 张图」总量口径==58。
    A 类旧名    ERROR（26 旧 PNG 名自 (i)、5 中文模板名自 (ii) 全量拦截）。
    M6 文件名   ERROR（提交 (i) 起拦截）：路径字符全部 <= 0x7F。
    M8 遗留     ERROR（提交 (iii) 起）：phase3/drafts、phase4/_archive、.coverage 存在数=0。

扫描域（计划 §四 开头，写死）：phase*/、根 README*、docs/、tools/、.githooks/；
排除 .omc/ 与 .git/。链接扫描另排除 phase3/drafts/ 与 phase4/_archive/（legacy 6 处坏引用，
提交 (iii) 删除后移除该排除——见 LEGACY_EXCLUDE，届时置空）。
"""

from __future__ import annotations

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCAN_TOP = ["phase1", "phase2", "phase3", "phase4", "phase5", "README.md",
            "README.zh.md", "docs", "tools", ".githooks"]
EXCLUDE_DIRS = {".git", ".omc", ".omc-hook", "__pycache__"}
# legacy 排除（(iii) 已删除遗留，置空——链接/语言半全量生效）
LEGACY_EXCLUDE = ()

# A 类消失名（阶段 0 基线 05-renumber-map-26.md + 5 中文模板名；终态字符串真消失）
# 分两档：26 旧 PNG 名在提交 (i) 清零并拦截；5 中文模板名随提交 (ii) README 树行改写清零。
A_CLASS_VANISH_PNG = [
    # 26 旧 PNG 名（改号者）
    "fig-04-context-layers.png", "fig-05-harness-flow.png", "fig-06-gate-cost.png",
    "fig-07-ab-timeline.png",
    "fig-02-rework-cost.png", "fig-02-batch-size.png", "fig-02-first-pass.png",
    "fig-02-cognitive-debt.png",
    "fig-03-cost-waterfall.png", "fig-04-margin-curve.png", "fig-05-paid-loop.png",
    "fig-06-scope-quadrant.png", "fig-07-rollback-layers.png", "fig-08-expand-contract.png",
    "fig-09-burn-rate.png", "fig-10-budget-stairs.png", "fig-11-rto-rpo.png",
    "fig-12-downgrade.png", "fig-13-cost-gates.png", "fig-14-budget-guard.png",
    "fig-15-obligation-matrix.png", "fig-16-ai-act-timeline.png",
    "fig-17-health-dashboard.png", "fig-18-rewrite-score.png", "fig-19-gantt.png",
    "fig-20-cashflow.png",
]

A_CLASS_VANISH_TPL = [
    # 5 中文模板名（(ii) README 树行改写后清零）
    "上线包检查单.md", "单用户月成本表.csv", "回滚演练记录.md", "成本合规边界说明.md", "收钱判定书.md",
]

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
CAP_RE = re.compile(r"!\[图\s*(\d+)\s*[-–—]\s*(\d+)[^\]]*\]\(([^)\s]+\.png)\)")
FIG_NUM_RE = re.compile(r"fig-(\d+)")


class Report:
    def __init__(self, strict: bool):
        self.strict = strict
        self.errors: list[str] = []
        self.warns: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        (self.errors if self.strict else self.warns).append(msg)


def scan_md_files(include_legacy: bool) -> list[str]:
    out = []
    for top in SCAN_TOP:
        p = os.path.join(ROOT, top)
        if not os.path.exists(p):
            continue
        if os.path.isfile(p):
            if p.endswith(".md"):
                out.append(p)
            continue
        for d, ds, fs in os.walk(p):
            ds[:] = [x for x in ds if x not in EXCLUDE_DIRS]
            for f in sorted(fs):
                if not f.endswith(".md"):
                    continue
                rel = os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/")
                if not include_legacy and rel.startswith(LEGACY_EXCLUDE):
                    continue
                out.append(os.path.join(d, f))
    return out


def scan_text_files(include_legacy: bool) -> list[str]:
    out = []
    for top in SCAN_TOP:
        p = os.path.join(ROOT, top)
        if not os.path.exists(p):
            continue
        if os.path.isfile(p):
            out.append(p)
            continue
        for d, ds, fs in os.walk(p):
            ds[:] = [x for x in ds if x not in EXCLUDE_DIRS]
            for f in sorted(fs):
                if f.endswith((".png", ".coverage", ".DS_Store")):
                    continue
                rel = os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/")
                if not include_legacy and rel.startswith(LEGACY_EXCLUDE):
                    continue
                out.append(os.path.join(d, f))
    return out


def check_m4_links(rep: Report) -> None:
    """M4 链接半：md 相对链接（图+目录）全部解析存在。"""
    n = 0
    for path in scan_md_files(include_legacy=False):
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        text = open(path, encoding="utf-8").read()
        for i, line in enumerate(text.splitlines(), 1):
            for m in LINK_RE.finditer(line):
                target = m.group(1)
                if re.match(r"^[a-z]+://", target) or target.startswith("#"):
                    continue
                t = target.split("#")[0]
                if not t:
                    continue
                n += 1
                resolved = os.path.normpath(os.path.join(os.path.dirname(path), t))
                if not os.path.exists(resolved):
                    rep.error("M4 链接半：%s:%d 断链 -> %s" % (rel, i, target))
    print("[M4-链接半] 检查相对链接 %d 处（legacy 排除已清空，全量生效）" % n)


def check_m4_lang(rep: Report) -> None:
    """M4 语言半（只查图片链接目标 .png）：zh 侧只引 .zh.png；en 侧不得引 .zh.png。"""
    zh_n = en_n = 0
    for path in scan_md_files(include_legacy=False):
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        text = open(path, encoding="utf-8").read()
        is_zh = os.path.basename(path).endswith(".zh.md") or path.endswith(".zh.csv")
        for i, line in enumerate(text.splitlines(), 1):
            for m in LINK_RE.finditer(line):
                t = m.group(1)
                if ".png" not in t:
                    continue
                if is_zh:
                    zh_n += 1
                    if not t.endswith(".zh.png"):
                        rep.error("M4 语言半(zh)：%s:%d X.zh.md 引用了非 .zh.png -> %s" % (rel, i, t))
                else:
                    en_n += 1
                    if t.endswith(".zh.png"):
                        rep.error("M4 语言半(en)：%s:%d X.md 引用了 .zh.png -> %s" % (rel, i, t))
    print("[M4-语言半] zh 侧图片引用 %d 处 / en 侧 %d 处（配对出现即断言）" % (zh_n, en_n))


def check_m5_captions(rep: Report) -> None:
    """M5 图题一致（阶段 2 出口闸）：文件 fig-NN ↔ 图题「图 C-NN」，C==frontmatter chapter_id；
    alt 与斜体图题双处同号；章内 prose「图 C-F」均有对应图文件（README 规划图表行为计划性描述，不入断言）。
    Figure 形态留待阶段 3 补入（英文 X.md 出现后同口径）。"""
    ITA_RE = re.compile(r"^\*图\s*(\d+)\s*[-–—]\s*(\d+)")
    PROSE_RE = re.compile(r"图\s*(\d+)\s*[-–—]\s*(\d+)")
    n_cap = n_ita = n_prose = n_prose_readme = bad = 0
    for path in scan_md_files(include_legacy=False):
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        text = open(path, encoding="utf-8").read()
        m_id = re.search(r"^chapter_id:\s*['\"]?(?:ch)?(\d+)", text, re.M)
        chap = m_id.group(1) if m_id else None
        lines = text.splitlines()
        alts, itas = [], []
        in_fence = False
        for i, line in enumerate(lines, 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            for m in CAP_RE.finditer(line):
                n_cap += 1
                c, f, target = m.group(1), m.group(2), m.group(3)
                mf = FIG_NUM_RE.search(os.path.basename(target))
                fn = mf.group(1) if mf else "?"
                if (mf is None) or int(f) != int(fn) or (chap is not None and int(c) != int(chap)):
                    bad += 1
                    rep.error("M5 图题：%s:%d 图题 %s-%s vs 文件 fig-%s（chapter_id=%s） -> %s"
                              % (rel, i, c, f, fn, chap, target))
                alts.append((i, c, f))
            s = line.strip()
            mi = ITA_RE.match(s)
            if mi:
                n_ita += 1
                itas.append((i, mi.group(1), mi.group(2)))
            # prose：剔除本行 alt / 斜体图题跨度后再查「图 C-F」
            stripped = CAP_RE.sub("", line)
            if mi:
                stripped = stripped.replace(s, "", 1) if s in stripped else ""
            for m in PROSE_RE.finditer(stripped):
                c, f = m.group(1), m.group(2)
                if chap is None:
                    n_prose_readme += 1
                    continue
                n_prose += 1
                cdir = os.path.join(rel.split("/")[0], "assets", "ch%02d" % int(c))
                glob_ok = any(re.match(r"^fig-%02d-.+\.png$" % int(f), x)
                              for x in (os.listdir(cdir) if os.path.isdir(cdir) else []))
                if not glob_ok:
                    bad += 1
                    rep.error("M5 prose 悬空图号：%s:%d 「图 %s-%s」无对应图文件（%s/fig-%02d-*.png）"
                              % (rel, i, c, f, cdir, int(f)))
        # 双处编号：alt 与斜体图题同号配对（±4 行内）
        for i, c, f in alts:
            if not any(abs(j - i) <= 4 and (c2, f2) == (c, f) for j, c2, f2 in itas):
                bad += 1
                rep.error("M5 双处编号：%s:%d alt 图题 %s-%s 无同号斜体图题" % (rel, i, c, f))
        for i, c, f in itas:
            if not any(abs(j - i) <= 4 and (c2, f2) == (c, f) for j, c2, f2 in alts):
                bad += 1
                rep.error("M5 双处编号：%s:%d 斜体图题 %s-%s 无同号 alt 图题" % (rel, i, c, f))
    print("[M5 图题] alt %d / 斜体 %d / 章内 prose %d（README 规划图表 %d 条不入断言），违例 %d（ERROR）"
          % (n_cap, n_ita, n_prose, n_prose_readme, bad))


PAIRING_EN_NAMES = set(
    [os.path.basename(l.strip()) for l in open(os.path.join(ROOT, ".omc/work/bilingual-baseline/03-md-67.txt"), encoding="utf-8")
     if "/chapters/" in l] if os.path.exists(os.path.join(ROOT, ".omc/work/bilingual-baseline/03-md-67.txt")) else []
) | {"README.md", "spec.md", "plan.md", "tasks.md", "requirements-checklist.md",
     "threat-model.md", "replay-report.md", "permission-matrix.md",
     "release-package-checklist.md", "rollback-drill-record.md",
     "cost-compliance-boundary.md", "revenue-decision-record.md", "monthly-cost-per-user.csv"}
FIG_LEAF_RE = re.compile(r"^fig-\d{2}-[a-z0-9-]+(\.zh)?\.png$")
TOK_FILE_RE = re.compile(r"^[\w.\-/]+\.(md|csv|png|py|sh|toml|yaml|yml)$")
TOK_DIR_RE = re.compile(r"^[\w.\-/]+/$")
ROW_RE = re.compile(r"^((?:│   |    )*)(├── |└── )?(.*)$")


def check_m9_readme(rep: Report) -> None:
    """M9 README 口径：树行逐行解析出的路径全部存在（占位行不入断言、占位行下的结构行走名字级核对）；
    终态叶名约定（中文版树列 .zh 叶名、英文版树列非 .zh 叶名，仅对配对域文件名断言）；
    「N 张图」总量口径句数字 == 58。"""
    zh_rows = en_rows = 0
    img_hits = []

    def name_exists(name):
        base = name.rstrip("/")
        for d, ds, fs in os.walk(ROOT):
            ds[:] = [x for x in ds if x not in EXCLUDE_DIRS and not x.startswith(".omc")]
            if base in ds or base in fs:
                return True
        return False

    for vol in ["", "phase1", "phase2", "phase3", "phase4", "phase5"]:
        for lang in ("zh", "en"):
            rel = os.path.join(vol, "README.zh.md" if lang == "zh" else "README.md") if vol else                   ("README.zh.md" if lang == "zh" else "README.md")
            if not os.path.exists(rel):
                continue
            text = open(rel, encoding="utf-8").read()
            # (1) 「N 张图」总量口径
            for m in re.finditer(r"共\s*\d+\s*章、(\d+)\s*张图", text):
                img_hits.append((rel, m.group(1)))
            for m in re.finditer(r"(\d+)\s*张图（中英各一套", text):
                img_hits.append((rel, m.group(1)))
            # (2) 树块
            in_tree = False
            stack = {}   # depth -> 相对段
            schema = {}  # depth -> 该层是否处于占位行之下
            for line in text.splitlines():
                if line.lstrip().startswith("```"):
                    if in_tree:
                        in_tree = False
                        continue
                    if "├──" in text[text.find(line):text.find(line) + 400] or "└──" in line:
                        in_tree = True
                    continue
                if not in_tree or not line.strip():
                    continue
                m = ROW_RE.match(line.rstrip())
                if not m:
                    continue
                prefix, branch, rest = m.group(1), m.group(2), m.group(3)
                depth = len(prefix) // 4 + (1 if branch else 0)
                name_part = rest.split("#")[0]
                placeholder = ("…" in name_part or "..." in name_part and "phaseN" in name_part
                               or "phaseN" in name_part or "chNN" in name_part or "…" in rest)
                if "phaseN" in name_part or "chNN" in name_part or "…" in name_part:
                    placeholder = True
                tokens = re.findall(r"[\w.\-/]+", name_part)
                toks = [t for t in tokens if TOK_FILE_RE.match(t) or TOK_DIR_RE.match(t)]
                if placeholder:
                    schema[depth] = True
                    continue
                parent_is_schema = any(schema.get(d) for d in range(depth))
                stack = {d: v for d, v in stack.items() if d < depth}
                for t in toks:
                    is_dir = t.endswith("/")
                    leaf = t.rstrip("/").rsplit("/", 1)[-1]
                    if parent_is_schema:
                        ok = name_exists(leaf)
                    else:
                        base = "".join(stack.get(d, "") for d in range(depth))
                        full = os.path.normpath(os.path.join(base, t))
                        ok = os.path.isdir(full) if is_dir else os.path.isfile(full)
                    if not ok:
                        rep.error("M9 树行路径缺失：%s  [%s]（解析为 %s）" % (rel, t, full))
                    # 叶名语言约定（仅配对域文件名）
                    if not is_dir and not parent_is_schema:
                        en_form = leaf.replace(".zh.md", ".md").replace(".zh.png", ".png").replace(".zh.csv", ".csv")
                        paired = en_form in PAIRING_EN_NAMES or FIG_LEAF_RE.match(en_form)
                        if paired and leaf != "AGENTS.md":
                            has_zh = ".zh." in leaf
                            if lang == "zh" and not has_zh:
                                rep.error("M9 叶名约定：%s 树列了非 .zh 叶名 %s" % (rel, leaf))
                            if lang == "en" and has_zh:
                                rep.error("M9 叶名约定：%s 树列了 .zh 叶名 %s" % (rel, leaf))
                if toks:
                    if parent_is_schema:
                        stack[depth] = ""
                    else:
                        stack[depth] = toks[-1]
                if lang == "zh":
                    zh_rows += 1
                else:
                    en_rows += 1
    for rel, num in img_hits:
        if num != "58":
            rep.error("M9 图数口径：%s 「%s 张图」≠ 58" % (rel, num))
    for need in ("README.zh.md", "README.md"):
        if not any(r == need for r, _ in img_hits):
            rep.error("M9 图数口径：%s 缺总量口径句「共 N 章、58 张图」或「58 张图（中英各一套」" % need)
    print("[M9 README] 树行 zh %d / en %d 条已核；图数口径句 %d 处（须全为 58）" % (zh_rows, en_rows, len(img_hits)))


def check_a_class_vanish(rep: Report) -> None:
    """A 类消失名 grep：26 旧 PNG 名 + 5 中文模板名（提交 (ii) 起全部 ERROR）。"""
    hits_png = hits_tpl = 0
    for path in scan_text_files(include_legacy=True):
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        if rel == "tools/check_bilingual.py":  # 检查器自身承载名单，不计残留
            continue
        for i, line in enumerate(open(path, encoding="utf-8", errors="replace").read().splitlines(), 1):
            for name in A_CLASS_VANISH_PNG:
                if name in line:
                    hits_png += 1
                    rep.error("A 类旧名残留(26 旧 PNG 名)：%s:%d 含 %s" % (rel, i, name))
            for name in A_CLASS_VANISH_TPL:
                if name in line:
                    hits_tpl += 1
                    rep.error("A 类旧名残留(5 中文模板名)：%s:%d 含 %s" % (rel, i, name))
    print("[A 类旧名] 旧 PNG 名 %d 处 / 中文模板名 %d 处（ERROR）"
          % (hits_png, hits_tpl))


LEGACY_PATHS = ("phase3/drafts", "phase4/_archive")


def check_m8_legacy(rep: Report) -> None:
    """M8 遗留闭合：phase3/drafts、phase4/_archive、.coverage 三类路径（闭合列举）存在数=0。"""
    hits = 0
    for p in LEGACY_PATHS:
        if os.path.exists(p):
            hits += 1
            rep.error("M8 遗留未闭合：%s 仍存在" % p)
    for d, ds, fs in os.walk(ROOT):
        ds[:] = [x for x in ds if x not in EXCLUDE_DIRS]
        for f in fs:
            if f == ".coverage":
                hits += 1
                rep.error("M8 遗留未闭合：%s" % os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/"))
    print("[M8 遗留] 三类路径存在数 %d（ERROR；0=已闭合）" % hits)


def check_m6_filenames(rep: Report) -> None:
    """M6 文件名 ASCII。"""
    hits = 0
    for top in SCAN_TOP:
        p = os.path.join(ROOT, top)
        if not os.path.exists(p):
            continue
        for d, ds, fs in os.walk(p):
            ds[:] = [x for x in ds if x not in EXCLUDE_DIRS]
            for name in list(fs) + list(ds):
                full = os.path.join(d, name)
                rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
                if any(ord(c) > 127 for c in rel):
                    hits += 1
                    rep.error("M6 非 ASCII 文件名：%s" % rel)
    print("[M6 文件名] 非 ASCII 路径 %d 处（ERROR）" % hits)



SCRIPTS = [
    "phase1/code/make_figures.py",
    "phase2/code/figures/make_figures.py",
    "phase3/code/make_figures.py",
    "phase4/code/make_figures.py",
    "phase5/code/make_figures_p5.py",
]
STYLE_FILES = ["phase3/code/_figstyle.py", "phase5/code/_figstyle.py"]


def _non_ascii(value):
    return any(ord(c) > 127 for c in value)


def check_m11(rep: Report) -> None:
    """M11 T 字典 AST 断言（图内标注文案）：键集==图 id 全集、zh/en 同构非空；
    非 ASCII 字面量仅限 T 字典 / fig_texts.py / 字体栈配置 / docstring / print。"""
    import ast as _ast

    def allowed_checker(rel, is_textfile):
        tree = _ast.parse(open(rel, encoding="utf-8").read())
        t_nodes, font_nodes, doc_ids, print_ids = set(), set(), set(), set()
        for node in tree.body:
            if isinstance(node, _ast.Assign):
                for tgt in node.targets:
                    if not isinstance(tgt, _ast.Name):
                        continue
                    bucket = None
                    if tgt.id == "T":
                        bucket = t_nodes
                    elif "FONT" in tgt.id:
                        bucket = font_nodes
                    if bucket is not None:
                        for sub in _ast.walk(node.value):
                            bucket.add(id(sub))
        funcs = [tree]
        funcs += [n for n in _ast.walk(tree) if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef))]
        for f in funcs:
            body = getattr(f, "body", [])
            if body and isinstance(body[0], _ast.Expr):
                v = body[0].value
                if isinstance(v, _ast.Constant) and isinstance(v.value, str):
                    doc_ids.add(id(v))
        for call in (n for n in _ast.walk(tree) if isinstance(n, _ast.Call)):
            fn = call.func
            name = fn.id if isinstance(fn, _ast.Name) else getattr(fn, "attr", "")
            if name == "print":
                for arg in call.args:
                    for sub in _ast.walk(arg):
                        print_ids.add(id(sub))

        def allowed(const_node):
            if is_textfile:
                return True
            cid = id(const_node)
            return (cid in t_nodes) or (cid in font_nodes) or (cid in doc_ids) or (cid in print_ids)

        return tree, allowed

    total_bad = 0
    for script_rel in SCRIPTS:
        tree = _ast.parse(open(script_rel, encoding="utf-8").read())
        universe, finals, t_dict, t_where = set(), set(), None, ""
        finals_copy = False
        for node in tree.body:
            if isinstance(node, _ast.Assign):
                for tgt in node.targets:
                    if not isinstance(tgt, _ast.Name):
                        continue
                    if tgt.id in ("OLD_REL", "FINAL_REL"):
                        try:
                            d = _ast.literal_eval(node.value)
                            (universe if tgt.id == "OLD_REL" else finals).update(d.keys())
                        except ValueError:
                            if tgt.id == "FINAL_REL":
                                finals_copy = True
                            else:
                                raise
                    if tgt.id == "T":
                        t_dict = _ast.literal_eval(node.value)
                        t_where = script_rel
        if not universe:
            # 阶段 2 提交 (i) 起脚本只余 FINAL_REL：图 id 全集以 FINAL_REL 为准
            universe = set(finals)
        if t_dict is None:
            ft = os.path.join(os.path.dirname(script_rel), "fig_texts.py")
            ft_tree = _ast.parse(open(ft, encoding="utf-8").read())
            for node in ft_tree.body:
                if isinstance(node, _ast.Assign):
                    for tgt in node.targets:
                        if isinstance(tgt, _ast.Name) and tgt.id == "T":
                            t_dict = _ast.literal_eval(node.value)
                            t_where = ft
        if t_dict is None:
            rep.error("M11: %s 未找到 T 字典" % script_rel)
            total_bad += 1
            continue
        if finals_copy:
            finals = set(universe)
        keys = set(t_dict.keys())
        if keys != universe:
            total_bad += 1
            rep.error("M11: %s T 键集 != 图 id 全集（多 %s / 少 %s）" % (script_rel, sorted(keys - universe), sorted(universe - keys)))
        if finals != universe:
            total_bad += 1
            rep.error("M11: %s FINAL_REL 键集 != OLD_REL 键集" % script_rel)
        for fig_id, langs in t_dict.items():
            if set(langs.keys()) != {"zh", "en"}:
                total_bad += 1
                rep.error("M11: %s/%s 缺 zh/en 栏" % (script_rel, fig_id))
                continue
            zh_keys, en_keys = set(langs["zh"].keys()), set(langs["en"].keys())
            if zh_keys != en_keys:
                total_bad += 1
                rep.error("M11: %s/%s zh/en 槽位不同构（zh-only %s / en-only %s）" % (script_rel, fig_id, sorted(zh_keys - en_keys), sorted(en_keys - zh_keys)))
            def walk_pair(a, b):
                if isinstance(a, str) and isinstance(b, str):
                    yield a, b
                elif isinstance(a, dict) and isinstance(b, dict):
                    for k in a:
                        for pair in walk_pair(a[k], b[k]):
                            yield pair
                elif (isinstance(a, (list, tuple)) and isinstance(b, (list, tuple))
                      and len(a) == len(b)):
                    for x, y in zip(a, b):
                        for pair in walk_pair(x, y):
                            yield pair
                else:
                    yield a, b

            for slot in langs["zh"]:
                for za, en in walk_pair(langs["zh"][slot], langs["en"][slot]):
                    if not isinstance(za, str) or not isinstance(en, str):
                        total_bad += 1
                        rep.error("M11: %s/%s/%s 存在非字符串叶子或结构不平行" % (script_rel, fig_id, slot))
                    elif (za == "") != (en == ""):
                        total_bad += 1
                        rep.error("M11: %s/%s/%s 单侧空串（一侧有文案另一侧缺）" % (script_rel, fig_id, slot))
        print("[M11] %s：T@%s 图 %d 张（键集==图 id 全集）" % (script_rel, t_where, len(keys)))
        scan = [(script_rel, False), (t_where, True)]
        for sf in STYLE_FILES:
            if os.path.dirname(sf) == os.path.dirname(script_rel):
                scan.append((sf, False))
        for rel, is_text in scan:
            if not os.path.exists(rel):
                continue
            tree2, allowed = allowed_checker(rel, is_text)
            bad = []
            for node in _ast.walk(tree2):
                if isinstance(node, _ast.Constant) and isinstance(node.value, str):
                    if _non_ascii(node.value) and not allowed(node):
                        bad.append((getattr(node, "lineno", -1), node.value[:40]))
            total_bad += len(bad)
            for lineno, val in bad:
                rep.error("M11: %s:%d 非 ASCII 字面量出现在豁免位之外：%r" % (rel, lineno, val))
    print("[M11] 违例合计 %d（0=全绿）" % total_bad)

def main() -> int:
    ap = argparse.ArgumentParser(description="双语仓最小检查器")
    ap.add_argument("--min", action="store_true", help="最小模式：M4 链接半 ERROR，其余 WARN")
    ap.add_argument("--strict", action="store_true", help="WARN 全部升 ERROR")
    ap.add_argument("--report", action="store_true", help="数量对账报表（阶段 4 补齐）")
    ap.add_argument("--m11", action="store_true", help="T 字典 AST 断言（阶段 1 起）")
    args = ap.parse_args()

    os.chdir(ROOT)
    rep = Report(strict=args.strict)
    print("扫描根：%s" % ROOT)
    check_m4_links(rep)
    check_m4_lang(rep)
    check_m5_captions(rep)
    check_a_class_vanish(rep)
    check_m6_filenames(rep)
    check_m8_legacy(rep)
    check_m9_readme(rep)
    if args.m11:
        check_m11(rep)
    if args.report:
        print("[--report] 阶段 0 雏形：数量对账留 .omc/work/bilingual-baseline/00-baseline-report.md；阶段 4 在此出 §2.3 全量对账")

    for w in rep.warns:
        print("WARN " + w)
    for e in rep.errors:
        print("ERROR " + e)
    print("结果：ERROR %d / WARN %d" % (len(rep.errors), len(rep.warns)))
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
