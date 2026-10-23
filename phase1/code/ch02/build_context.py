#!/usr/bin/env python3
"""第 2 章配套工具：把"一句话需求"变成"三层输入"。

三种输入方式的差别，不是措辞，而是「模型能看见什么」：

    A 一句话提示      —— 只有意图（约 30 tokens）
    B 全塞            —— 整个仓库 + 全部文档（上万 tokens，且大半无关）
    C 三层渐进披露    —— L0 索引（地图）+ L1 契约（图纸）+ L2 全文（墙面）

本脚本只生成 C 的三层文本，并给出 token 估算，供你对照 B 的规模。

用法：
    python build_context.py <repo> --task "给导出加按 tag 过滤" \
        --focus src/sched/export.py --focus tests/test_export.py

    python build_context.py <repo> --task "..." --out prompt.md

token 估算是**粗略**的：中文按 1 字 ≈ 1 token、其余按 4 字符 ≈ 1 token。
不同分词器会差 20%—40%，但用来比较量级足够。
"""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".mypy_cache", ".ruff_cache"}
SKIP_SUFFIX = {".pyc", ".png", ".jpg", ".lock", ".csv"}

CJK = re.compile(r"[\u3400-\u9fff\u3000-\u303f\uff00-\uffef]")


def estimate_tokens(text: str) -> int:
    cjk = len(CJK.findall(text))
    return int(round(cjk + (len(text) - cjk) / 4))


def iter_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for p in sorted(root.rglob("*")):
        if p.is_dir() or p.suffix in SKIP_SUFFIX:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        out.append(p)
    return out


def pretty_args(node: ast.AST) -> str:
    """ast.unparse 会把默认值写成 `x: int=3`，补成人类习惯的空格。"""
    return re.sub(r"(?<![=!<>])=(?!=)", " = ", ast.unparse(node))


def first_line_doc(node: ast.AST) -> str:
    doc = ast.get_docstring(node) or ""
    return doc.strip().splitlines()[0].strip() if doc.strip() else ""


def py_summary(path: Path) -> list[str]:
    """L1：只保留"别人调用它时需要知道的东西"——签名、边界、不变量。"""
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    lines: list[str] = []
    mod_doc = first_line_doc(tree)
    if mod_doc:
        lines.append(f"- 职责：{mod_doc}")

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = ", ".join(ast.unparse(b) for b in node.bases) or "object"
            doc = first_line_doc(node)
            lines.append(f"- class {node.name}({bases})" + (f" — {doc}" if doc else ""))
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if sub.name.startswith("_") and not sub.name.startswith("__"):
                        continue
                    lines.append(f"    · {sub.name}({pretty_args(sub.args)})")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("_"):
                continue
            doc = first_line_doc(node)
            ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
            lines.append(f"- def {node.name}({pretty_args(node.args)}){ret}" + (f" — {doc}" if doc else ""))
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    lines.append(f"- const {target.id} = {ast.unparse(node.value)[:60]}")
    return lines


def build_l0(root: Path, files: list[Path]) -> str:
    out = [f"仓库根：{root.name}", "", "文件树（只为回答「东西在哪」）："]
    for p in files:
        out.append(f"  {p.relative_to(root)}")
    out += ["", "各文件一句话职责："]
    for p in files:
        hint = ""
        if p.suffix == ".py":
            try:
                hint = first_line_doc(ast.parse(p.read_text(encoding="utf-8")))
            except SyntaxError:
                hint = "(语法错误，未能解析)"
        elif p.suffix in {".md", ".rst"}:
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.startswith("#"):
                    hint = line.lstrip("# ").strip()
                    break
        out.append(f"  {p.relative_to(root)}" + (f" — {hint}" if hint else ""))
    return "\n".join(out)


def build_l1(root: Path, files: list[Path]) -> str:
    out: list[str] = []
    for p in files:
        if p.suffix != ".py":
            continue
        out.append(f"\n### {p.relative_to(root)}")
        out.extend(py_summary(p))
    return "\n".join(out).strip() or "（仓库里没有 Python 文件）"


def build_l2(root: Path, focus: list[str]) -> str:
    out: list[str] = []
    for rel in focus:
        p = (root / rel).resolve()
        out.append(f"\n### {rel}")
        out.append("```")
        out.append(p.read_text(encoding="utf-8").rstrip())
        out.append("```")
    return "\n".join(out).strip() or "（未指定 --focus，L2 为空；这是故意的——不命中就不展开）"


def main() -> int:
    ap = argparse.ArgumentParser(description="生成三层渐进披露输入")
    ap.add_argument("repo", type=Path)
    ap.add_argument("--task", required=True, help="一句话需求，放在最前面")
    ap.add_argument("--focus", action="append", default=[], help="需要 L2 全文的文件（可多次）")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    root = args.repo.resolve()
    files = iter_files(root)

    l0, l1, l2 = build_l0(root, files), build_l1(root, files), build_l2(root, args.focus)
    parts = [
        f"# 任务\n{args.task}",
        f"# L0 索引层（常驻）\n{l0}",
        f"# L1 契约层（相关模块）\n{l1}",
        f"# L2 全文层（本次要改的文件）\n{l2}",
    ]
    doc = "\n\n".join(parts)
    naive = "\n\n".join(p.read_text(encoding="utf-8") for p in files)

    print(doc)
    print("\n" + "=" * 62)
    print(f"{'层':<26}{'tokens（估算）':>14}{'占全塞比例':>12}")
    print("-" * 62)
    total_naive = max(estimate_tokens(naive), 1)
    for label, text in [
        ("L0 索引层", l0),
        ("L1 契约层", l1),
        ("L2 全文层", l2),
        ("合计（三层）", doc),
        ("对照：全塞整个仓库", naive),
    ]:
        t = estimate_tokens(text)
        print(f"{label:<26}{t:>14}{t / total_naive:>11.0%}")
    print("=" * 62)
    print("注意：省下的不是字数，是「注意力被无关内容稀释」这件事。")

    if args.out:
        args.out.write_text(doc, encoding="utf-8")
        print(f"\n已写入：{args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
