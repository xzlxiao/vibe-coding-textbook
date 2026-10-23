"""AI 生成的测试 —— 原样保存。

特征（也是本章要拆的东西）：
  1. 断言的是「有没有返回」「有没有 token」，不是「业务规则对不对」；
  2. 每一条路径都跑到了，所以行覆盖率是满的；
  3. 因此它给出的绿灯，是一个只能证明"代码跑完了"的绿灯。
"""

import sqlite3
import unittest

from coupon_service import init_db, redeem


def _fresh():
    conn = sqlite3.connect(":memory:", isolation_level=None)
    init_db(conn)
    conn.execute("INSERT INTO coupons VALUES ('WELCOME', 2, 0)")
    return conn


class TestRedeem(unittest.TestCase):
    def test_happy_path_returns_token(self):
        conn = _fresh()
        result = redeem(conn, "WELCOME", "u1")
        self.assertTrue(result["ok"])
        self.assertIn("token", result)

    def test_all_paths_do_not_crash(self):
        """四条分支全跑一遍 —— 这一条就是覆盖率 100% 的来源。"""
        conn = _fresh()
        self.assertIsNotNone(redeem(conn, "WELCOME", "u1"))  # ok
        self.assertIsNotNone(redeem(conn, "WELCOME", "u2"))  # ok（第二张）
        self.assertIsNotNone(redeem(conn, "WELCOME", "u3"))  # exhausted
        self.assertIsNotNone(redeem(conn, "NOPE", "u1"))     # not_found


if __name__ == "__main__":
    unittest.main()
