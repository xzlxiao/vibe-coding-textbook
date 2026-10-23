#!/usr/bin/env python3
"""依赖允许清单校验：lockfile 里出现清单外的包就退出码 1。

只做一件事，因为它要能进 CI 并且三秒跑完。
支持 package-lock.json（npm v2/v3）与 requirements.txt（行式）。

用法：
  python3 dependency_allowlist.py --lock package-lock.json --allow allowlist.txt
  python3 dependency_allowlist.py --lock requirements.txt --allow allowlist.txt
  python3 dependency_allowlist.py --lock ... --allow ... --update   # 把当前依赖写回清单（需人审）
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_npm_lock(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    packages = data.get("packages")
    if isinstance(packages, dict):          # lockfileVersion 2 / 3
        for key in packages:
            if key.startswith("node_modules/"):
                names.add(key.split("node_modules/")[-1])
    deps = data.get("dependencies")
    if isinstance(deps, dict):              # lockfileVersion 1
        names.update(deps.keys())
    return names


def load_requirements(path: Path) -> set[str]:
    names: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#")[0].strip()
        if not line or line.startswith("-"):
            continue
        for sep in ("==", ">=", "<=", "~=", "!=", ">", "<", "["):
            if sep in line:
                line = line.split(sep)[0]
        names.add(line.strip().lower())
    return names


def main() -> int:
    ap = argparse.ArgumentParser(description="依赖允许清单校验")
    ap.add_argument("--lock", required=True, help="package-lock.json 或 requirements.txt")
    ap.add_argument("--allow", required=True, help="允许清单（每行一个包名）")
    ap.add_argument("--update", action="store_true", help="把当前依赖写回清单")
    args = ap.parse_args()

    lock, allow = Path(args.lock), Path(args.allow)
    if not lock.exists():
        print(f"找不到 lockfile：{lock}")
        return 2

    current = (load_npm_lock(lock) if lock.name.endswith(".json")
               else load_requirements(lock))
    current = {c.lower() for c in current}

    if args.update:
        allow.write_text("\n".join(sorted(current)) + "\n", encoding="utf-8")
        print(f"已写入 {len(current)} 个包到 {allow}（记得人工过一遍再提交）")
        return 0

    allowed = {line.split("#")[0].strip().lower()
               for line in allow.read_text(encoding="utf-8").splitlines()
               if line.strip() and not line.strip().startswith("#")}

    unexpected = sorted(current - allowed)
    missing = sorted(allowed - current)

    if unexpected:
        print(f"发现 {len(unexpected)} 个不在允许清单里的包：")
        for name in unexpected[:30]:
            print(f"  - {name}")
        if len(unexpected) > 30:
            print(f"  …… 另有 {len(unexpected) - 30} 个")
        print("\n判据：新包必须由人看过来源与 postinstall，再手动加进清单。")
        return 1

    print(f"通过：{len(current)} 个依赖全部在清单内。")
    if missing:
        print(f"提示：清单里有 {len(missing)} 个包已不在依赖树中，可清理：{', '.join(missing[:10])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
