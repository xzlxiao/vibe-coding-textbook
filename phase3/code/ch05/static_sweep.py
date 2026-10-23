"""第 05 章实验：静态检查能看见什么，看不见什么。

这不是一个完整的 linter，是四类典型静态检查的最小实现，
用来说明"静态检查"这一类工具的**能力形状**：
  C1 语法与编译         —— 形状能不能立起来
  C2 危险模式匹配         —— f-string 拼 SQL、eval、裸 except
  C3 硬编码密钥           —— 长随机串赋值
  C4 未使用变量 / 参数    —— 写了但没用的东西

判分标准：把每条规则打到两份实现上，看它抓到哪几个已知缺陷。

跑法：python static_sweep.py
"""

import ast
import py_compile
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASE = HERE.parent / "case_coupon"

TARGETS = [
    ("AI 原版", CASE / "coupon_service.py"),
    ("修复版 ", CASE / "coupon_service_fixed.py"),
]

# 已知缺陷清单（来自第 02 章的"应该有什么"核对）
KNOWN = [
    ("D1 幻觉依赖", "需要先换成本地桩才可运行，静态检查看不见"),
    ("D2 拼接 SQL", "f-string 把券码拼进语句"),
    ("D3 一人一次未实现", "缺失，没有任何文本形态"),
    ("D4 读改写非原子", "缺失，没有任何文本形态"),
    ("D5 凭证可能为 None", "行为属性，不在语法里"),
]


def c1_compile(path: Path) -> list[str]:
    try:
        py_compile.compile(str(path), doraise=True, cfile="/tmp/_pc.pyc")
        return []
    except py_compile.PyCompileError as e:
        return [f"编译失败：{e.msg}"]


def c2_patterns(path: Path) -> list[str]:
    hits = []
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        # f-string 拼 SQL
        if isinstance(node, ast.JoinedStr):
            raw = ast.unparse(node)
            if re.search(r"\b(SELECT|UPDATE|DELETE|INSERT)\b", raw, re.I):
                hits.append(f"L{node.lineno} f-string 拼 SQL：{raw[:60]}")
        # eval / exec
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in {"eval", "exec"}:
                hits.append(f"L{node.lineno} 使用了 {node.func.id}()")
        # 裸 except
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            hits.append(f"L{node.lineno} 裸 except")
    return sorted(hits, key=lambda h: int(h.split()[0][1:]))


def c3_secrets(path: Path) -> list[str]:
    hits = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = re.search(r"=\s*['\"]([A-Za-z0-9_\-]{24,})['\"]", line)
        if m and not line.strip().startswith("#"):
            hits.append(f"L{i} 疑似硬编码密钥（长度 {len(m.group(1))}）")
    return hits


def c4_unused(path: Path) -> list[str]:
    hits = []
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        assigned, used = set(), set()
        for node in ast.walk(fn):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    assigned.add(node.id)
                else:
                    used.add(node.id)
        for name in sorted(assigned - used):
            hits.append(f"{fn.name}(): 变量 {name} 赋值后未使用")
        for arg in [a.arg for a in fn.args.args]:
            if arg not in used and arg != "self":
                hits.append(f"{fn.name}(): 参数 {arg} 未使用")
    return hits


CHECKS = [("C1 编译", c1_compile), ("C2 危险模式", c2_patterns),
          ("C3 硬编码密钥", c3_secrets), ("C4 未使用变量", c4_unused)]


def main() -> None:
    print("已知缺陷：")
    for name, why in KNOWN:
        print(f"  {name:<18}{why}")
    print()

    for label, path in TARGETS:
        print(f"=== {label}（{path.name}）===")
        total = 0
        for cname, fn in CHECKS:
            hits = fn(path)
            total += len(hits)
            if hits:
                print(f"  {cname}：{len(hits)} 处")
                for h in hits:
                    print(f"      {h}")
            else:
                print(f"  {cname}：无")
        print(f"  合计命中 {total} 处 / 已知缺陷 {len(KNOWN)} 个\n")

    print("结论：静态检查抓到了 D2 的形态（拼接 SQL），")
    print("      对 D3 / D4 / D5 一个都没有命中——它们不是形态问题。")


if __name__ == "__main__":
    main()
