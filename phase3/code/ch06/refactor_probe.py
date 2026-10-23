"""第 06 章实验：一次无害的重构，把哪套测试打红？

重构内容（行为完全不变）：
  R1  把变量 row 改名成 record
  R2  把两条 SQL 提成模块级常量，顺便规范化空白
  R3  把"读库存"抽成一个辅助函数 _fetch_quota

三套测试分别跑一遍重构后的实现：
  A 空断言型（test_coupon_ai）
  B mock 型（test_coupon_mock）
  C 规格行为型（test_coupon_behavior）

跑法：python refactor_probe.py
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASE = HERE.parent / "case_coupon"

REFACTORED = '''"""同样的行为，换一种写法 —— 一次无害的重构。"""

import sqlite3

_SQL_SELECT = "SELECT quota, used FROM coupons WHERE code = ?"
_SQL_UPDATE = "UPDATE coupons SET used = used + 1 WHERE code = ?"


def sign_token(user_id, code):
    return f"stub.{user_id}.{code}"


def init_db(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS coupons (code TEXT PRIMARY KEY, quota INTEGER, used INTEGER)"
    )
    conn.execute("CREATE TABLE IF NOT EXISTS redemptions (code TEXT, user_id TEXT)")
    conn.commit()


def _fetch_quota(cur, code):
    return cur.execute(_SQL_SELECT, (code,)).fetchone()


def redeem(conn, code, user_id):
    cur = conn.cursor()
    record = _fetch_quota(cur, code)
    if record is None:
        return {"ok": False, "reason": "not_found"}
    quota, used = record
    if used >= quota:
        return {"ok": False, "reason": "exhausted"}
    cur.execute(_SQL_UPDATE, (code,))
    conn.commit()
    return {"ok": True, "token": sign_token(user_id, code)}
'''

SUITES = [
    ("A 空断言型", "test_coupon_ai.py"),
    ("B mock 型  ", "test_coupon_mock.py"),
    ("C 规格行为型", "test_coupon_behavior.py"),
]


def run(suite_file: str, impl_source: str) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "coupon_service.py").write_text(impl_source, encoding="utf-8")
        src = HERE / suite_file
        if not src.exists():
            src = CASE / suite_file
        shutil.copy(src, t / suite_file)
        proc = subprocess.run(
            [sys.executable, "-m", "unittest", Path(suite_file).stem, "-q"],
            cwd=t, capture_output=True, text=True,
        )
        return proc.returncode == 0


def main() -> None:
    baseline = (CASE / "coupon_service.py").read_text(encoding="utf-8")

    print(f"{'测试套件':<14}{'重构前':<10}{'重构后'}")
    print("-" * 44)
    flipped = 0
    for label, suite in SUITES:
        before = run(suite, baseline)
        after = run(suite, REFACTORED)
        if before != after:
            flipped += 1
            verdict = "结论翻转（被重构影响）"
        else:
            verdict = "结论不变（抗重构通过）"
        print(f"{label:<14}{'绿' if before else '红':<10}{'绿' if after else '红'}  {verdict}")

    print("-" * 44)
    print(f"{flipped} 套测试的结论被一次无害重构翻转。")
    print("判据：不改行为的重构，不该改变任何测试的结论。翻转了，说明它测的是写法，不是承诺。")


if __name__ == "__main__":
    main()
