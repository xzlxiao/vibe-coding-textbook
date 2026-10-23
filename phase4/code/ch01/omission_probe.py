#!/usr/bin/env python3
"""缺失型缺陷探测器（启发式，不是安全扫描器）。

它只做一件事：找出项目里「缺了也不会报错」的那类信号——
缺 RLS 策略、缺授权校验、密钥进前端、缺 lockfile、缺测试。
这些缺陷不会让功能测试变红，所以它们靠人想到，而不是靠机器报警。

用法：
  python3 omission_probe.py <项目目录>
  python3 omission_probe.py . --json     # 机器可读输出

退出码：0 = 没有命中信号；1 = 命中（提示人工核对，不是"你已失守"）
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SENSITIVE_NAMES = re.compile(
    r"(^\.env($|\..*)$|credentials|service_account|.*\.pem$|.*\.p12$|id_rsa)", re.I)
FRONTEND_TOKEN = re.compile(
    r"service_role|SUPABASE_SERVICE|sk_live_|AKIA[0-9A-Z]{16}|BEGIN (RSA |EC )?PRIVATE KEY")
SQL_POLICY = re.compile(
    r"row level security|create policy|grant select|deny ", re.I)
TEST_HINTS = ("test", "tests", "__tests__", "spec", "src/test")
CI_HINTS = (".github/workflows", ".gitlab-ci.yml", "Jenkinsfile", ".circleci")
LOCKFILES = ("package-lock.json", "pnpm-lock.yaml", "yarn.lock",
             "poetry.lock", "Pipfile.lock", "uv.lock", "Cargo.lock", "go.sum")


def probe(root: Path) -> list[dict]:
    hits: list[dict] = []

    # 1) 敏感文件出现在会被 serve / 会被打包的位置
    risky_dirs = ("public", "static", "dist", "build", "out", ".next", "www")
    for p in root.rglob("*"):
        if not p.is_file() or p.name == ".DS_Store":
            continue
        rel = p.relative_to(root).as_posix()
        if SENSITIVE_NAMES.search(p.name) and any(seg in rel.split("/") for seg in risky_dirs):
            hits.append({
                "signal": "敏感文件在可被访问的目录里",
                "path": rel,
                "why": "静态目录里的文件不需要任何代码就能被读到，它不会报错，只会泄漏",
                "fix": "移到构建产物之外，并把它写进 .gitignore 与打包排除清单",
            })

    # 2) 前端源码里的高权限字面量
    code_ext = {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".html", ".mjs"}
    for p in root.rglob("*"):
        if p.suffix.lower() not in code_ext or not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if any(seg in rel.split("/") for seg in ("node_modules", ".next", "dist", "build")):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in FRONTEND_TOKEN.finditer(text):
            line = text[: m.start()].count("\n") + 1
            hits.append({
                "signal": "高权限凭据出现在源码里",
                "path": f"{rel}:{line}",
                "why": "前端可见 = 全世界可读；即使它今天只在构建产物里，它也会进 git 历史",
                "fix": "立刻吊销，再移到服务端环境变量；不要先改代码再吊销",
            })

    # 3) 有数据库 schema，但没有权限/RLS 痕迹
    sql_files = [p for p in root.rglob("*.sql") if p.is_file()]
    has_schema = any(re.search(r"create table", p.read_text(encoding="utf-8", errors="ignore"), re.I)
                     for p in sql_files)
    has_policy = any(SQL_POLICY.search(p.read_text(encoding="utf-8", errors="ignore"))
                     for p in sql_files)
    if has_schema and not has_policy:
        hits.append({
            "signal": "有表结构，但没有任何权限策略痕迹",
            "path": "（全部 *.sql）",
            "why": "数据库层没设防时，前端'只查自己的数据'只是前端很乖，不是访问控制",
            "fix": "给每张表每个动作写策略，并加一条'用匿名角色自测必须返回 0 行'的验证",
        })

    # 4) 有依赖清单但没有 lockfile
    manifest = (root / "package.json").exists() or (root / "requirements.txt").exists()
    locked = any((root / name).exists() for name in LOCKFILES)
    if manifest and not locked:
        hits.append({
            "signal": "有依赖清单但没有 lockfile",
            "path": "（依赖清单）",
            "why": "没有锁文件，'装上的那个包'每次都可能不一样，抢注与幻觉包名才有可乘之机",
            "fix": "提交 lockfile，并加一条允许清单校验（见 code/ch07/dependency_allowlist.py）",
        })

    # 5) 没有测试目录，也没有 CI
    has_tests = any((root / t).exists() for t in TEST_HINTS) or \
        any(p.name.startswith("test_") and p.suffix == ".py" for p in root.rglob("*.py"))
    has_ci = any((root / c).exists() for c in CI_HINTS)
    if not has_tests and not has_ci:
        hits.append({
            "signal": "既没有测试目录，也没有 CI 配置",
            "path": "（仓库根）",
            "why": "没有自动化，就没有任何东西替你盯'不该发生的事'；所有边界都靠人记得",
            "fix": "先接一条会跑的检查（哪怕只有一条），再谈门禁体系",
        })

    return hits


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    if not args:
        print(__doc__)
        return 2

    root = Path(args[0]).resolve()
    if not root.is_dir():
        print(f"不是目录：{root}")
        return 2

    hits = probe(root)

    if as_json:
        print(json.dumps({"root": str(root), "hits": hits}, ensure_ascii=False, indent=2))
        return 1 if hits else 0

    print("=" * 78)
    print("缺失型缺陷探测（启发式）")
    print(f"目录：{root}")
    print("=" * 78)
    if not hits:
        print("\n没有命中任何信号。注意：这不代表安全，只代表下面这几类"
              "「缺了也不报错」的信号没有出现。")
        return 0

    for i, h in enumerate(hits, 1):
        print(f"\n[{i}] {h['signal']}")
        print(f"    位置：{h['path']}")
        print(f"    为什么要紧：{h['why']}")
        print(f"    怎么修：{h['fix']}")

    print("\n" + "-" * 78)
    print(f"命中 {len(hits)} 条信号。它们不是'漏洞'，是'没有自动报警的地方'——"
          "请逐条人工核对后再下结论。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
