#!/usr/bin/env python3
"""第 1 章配套工具：依赖幻觉扫描器 (dependency hallucination scanner)

它回答一个非常具体的问题：
    「这段 AI 生成的代码 import 的东西，到底存不存在？」

为什么需要它：
    LLM 会生成"听起来非常合理"的包名。这不是偶发 bug，而是 token 预测的
    结构性后果——一个包名在语料里出现足够多次的"碎片"（前缀 pydantic-、
    后缀 -repair、动作动词 fix_），模型就会把它拼成一个新名字，并且用起来
    信心十足。运行之前完全看不出来。

三层判定（从便宜到贵）：
    1. 标准库？        sys.stdlib_module_names —— 本地，零成本
    2. 装了吗？        importlib.util.find_spec —— 本地，零成本
    3. 注册表里有吗？  PyPI JSON API —— 需要联网，能区分"没装"与"不存在"

用法：
    python check_deps.py sample_ai_output.py
    python check_deps.py sample_ai_output.py --online
    python check_deps.py src/ --declared requirements.txt

退出码：0 全部可解析；1 存在无法解析的模块（可直接接进 CI）。
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import sys
import urllib.error
import urllib.request
from importlib.metadata import packages_distributions
from pathlib import Path

STDLIB = set(sys.stdlib_module_names)

# 说明：包名与 import 名不一定相同（PyYAML → yaml），因此"装没装"一律以
# importlib.util.find_spec 为准，不靠发行版名去猜。packages_distributions()
# 只在读取 requirements 声明时才用得到。

def collect_imports(path: Path) -> dict[str, list[str]]:
    """返回 {顶层模块名: [出现位置, ...]}，位置精确到 file:line。"""
    found: dict[str, list[str]] = {}
    files = [path] if path.is_file() else sorted(path.rglob("*.py"))
    for f in files:
        if any(part in {".git", ".venv", "node_modules", "__pycache__"} for part in f.parts):
            continue
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError as exc:  # 语法错误本身也值得报出来
            found.setdefault("<syntax-error>", []).append(f"{f}:{exc.lineno}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    found.setdefault(top, []).append(f"{f.name}:{node.lineno}")
            elif isinstance(node, ast.ImportFrom):
                if node.level:  # 相对导入，不查
                    continue
                if node.module:
                    top = node.module.split(".")[0]
                    found.setdefault(top, []).append(f"{f.name}:{node.lineno}")
    return found


def local_status(module: str) -> str:
    """'stdlib' / 'installed' / 'missing'"""
    if module in STDLIB:
        return "stdlib"
    try:
        if importlib.util.find_spec(module) is not None:
            return "installed"
    except (ModuleNotFoundError, ValueError):
        pass
    return "missing"


def index_status(module: str, timeout: float = 6.0) -> str:
    """查 PyPI：'exists' / 'absent' / 'unknown'。

    absent 才是"幻觉包名"的强证据；unknown 表示网络不通或接口异常，
    绝不能当成 absent 用——这是本工具里最容易犯的口径错误。
    """
    url = f"https://pypi.org/pypi/{module.replace('_', '-')}/json"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            # 只认状态码。不要在这里解析响应体：注册表返回的 JSON 可能很大，
            # 读一半就 json.loads 会抛异常，结果所有"存在的包"都被判成 unknown。
            return "exists" if resp.status == 200 else "unknown"
    except urllib.error.HTTPError as exc:
        return "absent" if exc.code == 404 else "unknown"
    except Exception:
        return "unknown"


def declared_packages(path: Path) -> set[str]:
    """从 requirements.txt 里读声明的包名（忽略版本号与环境标记）。"""
    names: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        name = line.split("==")[0].split(">=")[0].split("[")[0].split(";")[0].strip()
        names.add(name.lower().replace("-", "_"))
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description="扫描代码里的可疑 import")
    parser.add_argument("path", type=Path)
    parser.add_argument("--online", action="store_true", help="额外查询 PyPI 注册表")
    parser.add_argument("--declared", type=Path, default=None, help="requirements.txt 路径")
    args = parser.parse_args()

    if not args.path.exists():
        print(f"路径不存在：{args.path}", file=sys.stderr)
        return 2

    imports = collect_imports(args.path)
    declared = declared_packages(args.declared) if args.declared else None

    rows: list[tuple[str, str, str, str]] = []
    for module in sorted(imports):
        status = local_status(module)
        verdict = {"stdlib": "标准库", "installed": "已安装", "missing": "本地缺失"}[status]
        note = ""
        if status == "missing" and args.online:
            idx = index_status(module)
            verdict = {"absent": "★ 注册表不存在", "exists": "存在但未安装",
                       "unknown": "无法判定"}[idx]
            note = "" if idx == "absent" else "（先 pip install 再判断）"
        if declared is not None and status != "stdlib":
            key = module.lower().replace("-", "_")
            if key not in declared:
                note = (note + " 未在 requirements 中声明，不可复现").strip()
        rows.append((module, verdict, imports[module][0], note))

    width = max((len(r[0]) for r in rows), default=8)
    print(f"\n扫描目标：{args.path}")
    print(f"顶层模块：{len(rows)} 个\n")
    print(f"{'模块'.ljust(width)}  {'判定'.ljust(14)} {'首次出现'.ljust(18)} 备注")
    print("-" * (width + 46))
    for module, verdict, where, note in rows:
        print(f"{module.ljust(width)}  {verdict.ljust(14)} {where.ljust(18)} {note}")

    fatal = [r for r in rows if r[1] in {"本地缺失", "★ 注册表不存在"}]
    print()
    if fatal:
        print(f"结论：{len(fatal)} 个模块无法解析 → 这段代码在干净环境里必然 import 失败。")
        for module, _, where, _ in fatal:
            print(f"  · {module}（{where}）")
        return 1
    print("结论：全部模块可解析。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
