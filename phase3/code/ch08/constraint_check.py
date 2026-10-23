"""第 08 章：约束级检查 —— 不测并发，测"约束在不在"。

思路：并发缺陷不可稳定复现，但"应该存在的约束"是可以静态确认的。
  K1  核销记录表上必须有 UNIQUE(code, user_id)
  K2  扣减语句必须是带条件的原子更新（WHERE ... used < quota）
  K3  取消/核销必须在一个显式事务里（BEGIN IMMEDIATE）

这三条都是"必须存在的东西"，所以能被检查——这正是第 02 章那份清单的用法。

跑法：python constraint_check.py
"""

import ast
import os
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASE = HERE.parent / "case_coupon"

# 传参只测一个（用于流水线，失败时退出码 1）；不传参对照两个（用于教学演示）
TARGET_ONE = sys.argv[1] if len(sys.argv) > 1 else None
TARGETS = [(TARGET_ONE, TARGET_ONE)] if TARGET_ONE else [
    ("AI 原版", "coupon_service.py"),
    ("修复版 ", "coupon_service_fixed.py"),
]


def k1_unique_index(module_name: str) -> tuple[bool, str]:
    """把模块的建表语句真跑一遍，然后问数据库：这张表上有没有唯一索引。"""
    mod = __import__(module_name)
    conn = sqlite3.connect(":memory:", isolation_level=None)
    mod.init_db(conn)
    rows = conn.execute("PRAGMA index_list('redemptions')").fetchall()
    conn.close()
    unique = [r for r in rows if r[2] == 1]  # r[2] == 1 表示 unique
    if unique:
        return True, f"发现 {len(unique)} 个唯一索引"
    return False, "redemptions 表上没有唯一索引"


def k2_conditional_update(path: Path) -> tuple[bool, str]:
    """扫源码里的 UPDATE 语句，看有没有 used < quota 这类条件。"""
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value.strip().upper()
            if s.startswith("UPDATE") and "WHERE" in s:
                if "USED < QUOTA" in s.replace("  ", " "):
                    return True, f"发现条件更新：{node.value[:52]}..."
    # f-string 拼出来的语句也要看
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            raw = ast.unparse(node).upper()
            if "UPDATE" in raw and "USED < QUOTA" in raw:
                return True, "发现条件更新（f-string 形态）"
    return False, "扣减语句里没有 used < quota 条件"


def k3_explicit_transaction(path: Path) -> tuple[bool, str]:
    src = path.read_text(encoding="utf-8").upper()
    if "BEGIN IMMEDIATE" in src or "BEGIN EXCLUSIVE" in src:
        return True, "扣减位于显式锁事务内"
    return False, "没有显式锁事务（读与写之间存在窗口）"


CHECKS = [
    ("K1 唯一约束", lambda name, path: k1_unique_index(name)),
    ("K2 条件更新", lambda name, path: k2_conditional_update(path)),
    ("K3 显式事务", lambda name, path: k3_explicit_transaction(path)),
]


def main() -> int:
    sys.path.insert(0, str(CASE))
    all_ok = True
    for label, filename in TARGETS:
        path = CASE / filename
        module = path.stem
        print(f"=== {label}：{filename} ===")
        passed = 0
        for cname, fn in CHECKS:
            ok, detail = fn(module, path)
            passed += ok
            print(f"  {'通过' if ok else '失败'}  {cname}  ·  {detail}")
        print(f"  → {passed}/{len(CHECKS)} 条约束成立\n")
        if passed != len(CHECKS):
            all_ok = False

    if TARGET_ONE:
        return 0 if all_ok else 1

    print("读法：这份检查不需要并发、不需要起线程、0.1 秒跑完，")
    print("      它证明的不是'这次没超发'，而是'结构上不可能超发'。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
