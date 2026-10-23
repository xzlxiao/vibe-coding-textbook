"""并发交错复现 —— 为什么「读一遍代码没问题」会漏掉这一类缺陷。

这个脚本不调用 redeem()，而是把它内部的 SQL 按两种交错顺序手工执行一遍。
理由：用线程去碰运气复现竞态，会得到一个时灵时不灵的测试；时灵时不灵的测试
等于没有测试。确定性复现看到的不是"事故现场"，而是"事故的可能性"。

它证明的是一件事：这段代码没有把「读」和「写」放进同一个原子操作里，
所以下面这个交错是合法的执行序列 —— 只要两个请求挨得足够近，它就会发生。
"""

import sqlite3
import tempfile
from pathlib import Path


def open_db(path: str) -> sqlite3.Connection:
    return sqlite3.connect(path, isolation_level=None)


def seed(path: str) -> None:
    conn = open_db(path)
    conn.execute("CREATE TABLE IF NOT EXISTS coupons (code TEXT PRIMARY KEY, quota INTEGER, used INTEGER)")
    conn.execute("DELETE FROM coupons")
    conn.execute("INSERT INTO coupons VALUES ('LIMITED', 1, 0)")  # 库存只有 1 张
    conn.close()


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = str(Path(tmp) / "race.db")
        seed(db)
        c1, c2 = open_db(db), open_db(db)

        print("库存：quota=1, used=0\n")
        print(f"{'步':<4}{'请求':<6}{'动作':<48}{'手里看到的 used'}")
        print("-" * 78)

        # 两个请求都先读，都读到 0 —— 这是正常实现也会发生的事
        r1 = c1.execute("SELECT quota, used FROM coupons WHERE code='LIMITED'").fetchone()
        print(f"{1:<4}{'A':<6}{'SELECT quota, used':<48}{r1[1]}")
        r2 = c2.execute("SELECT quota, used FROM coupons WHERE code='LIMITED'").fetchone()
        print(f"{2:<4}{'B':<6}{'SELECT quota, used':<48}{r2[1]}")

        # 两个请求各自用「刚才读到的值 + 1」去写
        successes = 0
        for step, (name, conn, row) in enumerate((("A", c1, r1), ("B", c2, r2)), start=3):
            quota, used = row
            if used >= quota:  # 用自己手里的旧值判断 —— 这就是缺口
                print(f"{step:<4}{name:<6}{'判定 exhausted，返回失败':<48}{used}")
                continue
            conn.execute(f"UPDATE coupons SET used = {used + 1} WHERE code='LIMITED'")
            successes += 1
            print(f"{step:<4}{name:<6}{f'UPDATE used = {used + 1}':<48}{used}")

        final = c1.execute("SELECT used FROM coupons WHERE code='LIMITED'").fetchone()[0]
        print("-" * 78)
        print(f"最终 used = {final}；成功核销 {successes} 次，库存 1 张 → 超发 {successes - 1} 张")
        print("\n注意：每一步单独看都是对的。错的是「两步之间没有锁」。")
        print("这类缺陷不在任何一行代码里，所以读代码时眼睛会自动跳过它。")


if __name__ == "__main__":
    main()
