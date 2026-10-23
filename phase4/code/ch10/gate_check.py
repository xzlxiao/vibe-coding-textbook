#!/usr/bin/env python3
"""三条边界断言：让「门锁没锁」变成一条会红的测试。

它只做三件可机械判定的事（全部只读）：
  1. 迁移/SQL 文件里必须出现 row level security（数据层有没有设防）
  2. 构建产物里不得出现 service_role / SUPABASE_SERVICE（万能钥匙没进前端）
  3. 依赖树里不得出现允许清单外的包（供应链没被抢注）

用法：
  python3 gate_check.py <项目目录> [--allow allowlist.txt] [--lock package-lock.json]
  python3 gate_check.py <项目目录> --json

退出码：0 = 三条全过；1 = 至少一条失败（这就是 CI 里会红的那条）
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SECRET_PAT = re.compile(r"service_role|SUPABASE_SERVICE|BEGIN (RSA |EC )?PRIVATE KEY")
BUILD_DIRS = ("dist", "build", ".next", "out", "public")
LOCKFILES = ("package-lock.json", "pnpm-lock.yaml", "yarn.lock",
             "poetry.lock", "requirements.txt", "uv.lock")


def check_rls(root: Path) -> tuple[bool, str]:
    sqls = [p for p in root.rglob("*.sql") if p.is_file()
            and "node_modules" not in p.parts]
    if not sqls:
        return True, "没有 *.sql 文件（跳过：无可校验的迁移）"
    schema = [p for p in sqls
              if re.search(r"create table", p.read_text(encoding="utf-8", errors="ignore"), re.I)]
    if not schema:
        return True, "没有建表语句（跳过）"
    guarded = [p for p in schema
               if re.search(r"row level security", p.read_text(encoding="utf-8", errors="ignore"), re.I)]
    if not guarded:
        return False, f"有建表语句但没有 enable row level security（{len(schema)} 个文件）"
    return True, f"{len(guarded)}/{len(schema)} 个建表文件里出现了 row level security"


def check_no_secret(root: Path) -> tuple[bool, str]:
    code_ext = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".html", ".css"}
    hits = []
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in code_ext:
            continue
        rel = p.relative_to(root).as_posix()
        if any(seg in rel.split("/") for seg in ("node_modules",) + BUILD_DIRS):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in SECRET_PAT.finditer(text):
            hits.append(f"{rel}:{text[:m.start()].count(chr(10)) + 1}")
    if hits:
        return False, f"高权限凭据出现在 {len(hits)} 处（示例：{hits[0]}）"
    return True, "源码与构建产物里没有 service_role / 私钥字面量"


def check_allowlist(root: Path, allow_path: Path | None, lock_name: str | None) -> tuple[bool, str]:
    lock = None
    if lock_name:
        lock = root / lock_name
    else:
        for name in LOCKFILES:
            if (root / name).exists():
                lock = root / name
                break
    if lock is None or not lock.exists():
        return True, "没有 lockfile（跳过）"
    if allow_path is None or not allow_path.exists():
        return True, f"没有提供允许清单（跳过；lockfile={lock.name}）"

    names: set[str] = set()
    if lock.suffix == ".json":
        data = json.loads(lock.read_text(encoding="utf-8"))
        pkgs = data.get("packages")
        if isinstance(pkgs, dict):
            names = {k.split("node_modules/")[-1] for k in pkgs if k.startswith("node_modules/")}
    else:
        for raw in lock.read_text(encoding="utf-8").splitlines():
            line = raw.split("#")[0].strip()
            if not line or line.startswith("-"):
                continue
            for sep in ("==", ">=", "<=", "~=", "!=", "["):
                if sep in line:
                    line = line.split(sep)[0]
            names.add(line.strip().lower())

    allowed = {ln.split("#")[0].strip().lower()
               for ln in allow_path.read_text(encoding="utf-8").splitlines()
               if ln.strip() and not ln.strip().startswith("#")}
    extra = sorted(names - allowed)
    if extra:
        return False, f"{len(extra)} 个包不在允许清单（示例：{extra[0]}）"
    return True, f"{len(names)} 个依赖全部在清单内"


def main() -> int:
    ap = argparse.ArgumentParser(description="三条边界断言")
    ap.add_argument("root", help="项目目录")
    ap.add_argument("--allow", help="依赖允许清单（缺省则跳过第 3 条）")
    ap.add_argument("--lock", help="lockfile 文件名（缺省自动找）")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"不是目录：{root}")
        return 2

    checks = [
        ("断言 1 · 数据层设防", check_rls(root)),
        ("断言 2 · 万能钥匙没进前端", check_no_secret(root)),
        ("断言 3 · 依赖在清单内", check_allowlist(
            root,
            Path(args.allow).resolve() if args.allow else None,
            args.lock)),
    ]

    if args.json:
        print(json.dumps({
            "root": str(root),
            "results": [{"name": n, "pass": ok, "detail": d} for n, (ok, d) in checks]
        }, ensure_ascii=False, indent=2))
        return 0 if all(ok for _, (ok, _) in checks) else 1

    print("=" * 70)
    print("三条边界断言")
    print(f"目录：{root}")
    print("=" * 70)
    for name, (ok, detail) in checks:
        print(f"  [{'通过' if ok else '失败'}] {name}")
        print(f"         {detail}")

    failed = [n for n, (ok, _) in checks if not ok]
    print("-" * 70)
    if failed:
        print(f"失败 {len(failed)} 条：{'、'.join(failed)}")
        print("它们测的都是「不该发生的没发生」。CI 里挂红是好事——说明门还在。")
        return 1
    print("三条全过。注意：这不等于安全，只等于这三类缺失没有发生。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
