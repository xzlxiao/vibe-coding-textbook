"""依赖核验门禁 —— 最便宜的一道闸，0 依赖、0 网络、毫秒级。

规则只有一条：第三方 import 必须出现在 allowed_deps.txt 里，清单只由人添加。
理由：AI 推荐不存在的包名是可复现的（同一提示词多次生成会稳定复现同一个假名），
可复现就意味着有人可以抢先注册它、塞进恶意代码。这类缺陷在后面的所有门禁里都看不见，
因为代码根本跑不起来 —— 或者说，跑起来的正是别人注册的那个包。

用法：
    python dependency_gate.py coupon_service.as_generated.py   # 预期失败
    python dependency_gate.py coupon_service.py               # 预期通过
"""

import ast
import sys
from pathlib import Path

HERE = Path(__file__).parent
ALLOWLIST_FILE = HERE / "allowed_deps.txt"


def load_allowlist() -> set[str]:
    if not ALLOWLIST_FILE.exists():
        return set()
    lines = ALLOWLIST_FILE.read_text(encoding="utf-8").splitlines()
    return {ln.strip() for ln in lines if ln.strip() and not ln.startswith("#")}


def top_level_imports(path: Path) -> list[tuple[str, int]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.append((alias.name.split(".")[0], node.lineno))
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.append((node.module.split(".")[0], node.lineno))
    return sorted(set(found), key=lambda x: x[1])


def main(paths: list[str]) -> int:
    allow = load_allowlist() | set(sys.stdlib_module_names)
    failed = False
    print(f"{'文件':<34}{'行':>4}  {'模块':<30}{'判定'}")
    print("-" * 86)
    for raw in paths:
        path = Path(raw)
        for module, lineno in top_level_imports(path):
            verdict = "stdlib" if module in sys.stdlib_module_names else (
                "允许清单" if module in allow else "未登记"
            )
            if verdict == "未登记":
                failed = True
            print(f"{path.name:<34}{lineno:>4}  {module:<30}{verdict}")
    print("-" * 86)
    if failed:
        print("GATE FAILED：存在未登记依赖。先人工确认它在真实注册表里存在、且是你要的那个包，")
        print("再由人写进 allowed_deps.txt —— 不要让智能体自己往清单里加。")
        return 1
    print("GATE PASSED：所有 import 都在 stdlib 或允许清单内。")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:] or ["coupon_service.py"]
    sys.exit(main(args))
