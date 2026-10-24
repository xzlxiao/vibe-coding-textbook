#!/usr/bin/env python3
"""双语仓最小检查器（阶段 0 雏形；stdlib-only）。

用法：
    python3 tools/check_bilingual.py --min        # 最小模式（提交 (h) 起接 pre-commit）
    python3 tools/check_bilingual.py --strict     # 把 WARN 也升为 ERROR（阶段 2 (ii) 后启用）
    python3 tools/check_bilingual.py --report     # 数量对账报表（阶段 4 补齐）

检查集（随阶段扩容，见计划 §5.1 扩容表）：
    M4 链接半   ERROR（全程启用）：扫描域内 md 相对链接全部解析存在。
    M4 语言半   ERROR（配对出现即查）：X.zh.md 只引用 .zh.png；X.md 不得引用 .zh.png（只查图片目标）。
    M5 图题     WARN（提交 (ii) 起升 ERROR）：文件 fig-NN ↔ 图题「图 C-NN」，C==frontmatter chapter_id。
    A 类旧名    WARN（提交 (i)/(ii) 起升 ERROR）：26 旧 PNG 名 + 5 中文模板名 grep=0。
    M6 文件名   WARN（提交 (i) 起升 ERROR）：路径字符全部 <= 0x7F。

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
# legacy 排除（仅覆盖链接扫描与语言半；(iii) 删除遗留后置空）
LEGACY_EXCLUDE = ("phase3/drafts/", "phase4/_archive/")

# A 类消失名（阶段 0 基线 05-renumber-map-26.md + 5 中文模板名；终态字符串真消失）
A_CLASS_VANISH = [
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
    # 5 中文模板名
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
    print("[M4-链接半] 检查相对链接 %d 处（排除 legacy 两目录）" % n)


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
    """M5 图题：文件 fig-NN ↔ 图题 图 C-NN，C==章 frontmatter chapter_id。"""
    n = bad = 0
    for path in scan_md_files(include_legacy=False):
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        text = open(path, encoding="utf-8").read()
        m_id = re.search(r"^chapter_id:\s*['\"]?(?:ch)?(\d+)", text, re.M)
        chap = m_id.group(1) if m_id else None
        for i, line in enumerate(text.splitlines(), 1):
            for m in CAP_RE.finditer(line):
                n += 1
                c, f, target = m.group(1), m.group(2), m.group(3)
                mf = FIG_NUM_RE.search(os.path.basename(target))
                fn = mf.group(1) if mf else "?"
                if (mf is None) or int(f) != int(fn) or (chap is not None and int(c) != int(chap)):
                    bad += 1
                    rep.warn("M5 图题：%s:%d 图题 %s-%s vs 文件 fig-%s（chapter_id=%s） -> %s"
                             % (rel, i, c, f, fn, chap, target))
    print("[M5 图题] 嵌入图题 %d 处，编号不一致 %d 处（WARN：提交 (ii) 后升 ERROR）" % (n, bad))


def check_a_class_vanish(rep: Report) -> None:
    """A 类消失名 grep：26 旧 PNG 名 + 5 中文模板名。"""
    hits = 0
    for path in scan_text_files(include_legacy=True):
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        if rel == "tools/check_bilingual.py":  # 检查器自身承载名单，不计残留
            continue
        for i, line in enumerate(open(path, encoding="utf-8", errors="replace").read().splitlines(), 1):
            for name in A_CLASS_VANISH:
                if name in line:
                    hits += 1
                    rep.warn("A 类旧名残留：%s:%d 含 %s" % (rel, i, name))
    print("[A 类旧名] 消失名提及 %d 处（WARN：提交 (i)/(ii) 后应为 0 并升 ERROR）" % hits)


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
                    rep.warn("M6 非 ASCII 文件名：%s" % rel)
    print("[M6 文件名] 非 ASCII 路径 %d 处（WARN：提交 (i) 后应为 0 并升 ERROR）" % hits)



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
