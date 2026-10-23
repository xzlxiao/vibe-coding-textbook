"""第 08 章的实验：压测的"通过"到底证明了什么。

四组对照。注意第二组——它才是本章的主菜。

  组1  原版 · 24 并发 · 配额 10   → 期望：撞上
  组2  原版 · 24 并发 · 配额 100  → 期望：撞不上（不是安全，是负载不够）
  组3  修复版 · 24 并发 · 配额 10 → 期望：撞不上
  组4  原版 ·  2 并发 · 配额 1    → 期望：看运气

跑法：python stress_oversell.py
"""

import importlib
import sqlite3
import sys
import tempfile
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "case_coupon"))

THREADS_DEFAULT = 24
ROUNDS = 30


def one_round(db_path: str, mod, quota: int, threads: int) -> int:
    conn = sqlite3.connect(db_path, isolation_level=None)
    conn.execute("DELETE FROM coupons")
    conn.execute("INSERT INTO coupons VALUES ('HOT', ?, 0)", (quota,))
    conn.close()

    successes = []
    lock = threading.Lock()
    barrier = threading.Barrier(threads)

    def worker(i: int) -> None:
        c = sqlite3.connect(db_path, timeout=10, isolation_level=None)
        barrier.wait()
        try:
            r = mod.redeem(c, "HOT", f"u{i}")
        except sqlite3.OperationalError:
            r = {"ok": False}
        finally:
            c.close()
        if r.get("ok"):
            with lock:
                successes.append(i)

    ts = [threading.Thread(target=worker, args=(i,)) for i in range(threads)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return max(0, len(successes) - quota)


def run(label: str, module_name: str, quota: int, threads: int, db_path: str) -> dict:
    mod = importlib.import_module(module_name)
    conn = sqlite3.connect(db_path, isolation_level=None)
    mod.init_db(conn)
    conn.close()
    results = [one_round(db_path, mod, quota, threads) for _ in range(ROUNDS)]
    hits = sum(1 for r in results if r > 0)
    print(f"{label}  检出 {hits:>2}/{ROUNDS} 轮（{hits / ROUNDS:>3.0%}）  单轮最大超发 {max(results):>2} 张")
    return {"label": label, "hits": hits, "rounds": ROUNDS, "max": max(results)}


def main() -> None:
    print(f"每组重复 {ROUNDS} 轮\n")
    with tempfile.TemporaryDirectory() as tmp:
        db = str(Path(tmp) / "stress.db")
        run("组1  原版 · 24 并发 · 配额 10 ", "coupon_service", 10, 24, db)
        run("组2  原版 · 24 并发 · 配额 100", "coupon_service", 100, 24, db)
        run("组3  修复版 · 24 并发 · 配额 10", "coupon_service_fixed", 10, 24, db)
        run("组4  原版 ·  2 并发 · 配额  1 ", "coupon_service", 1, 2, db)

    print()
    print("组2 的绿灯最危险：它什么都没证明，只是你没给够负载。")
    print("组4 说明同一个洞在小负载下可能一次都撞不上——所以压测的'通过'不等于'安全'。")


if __name__ == "__main__":
    main()
