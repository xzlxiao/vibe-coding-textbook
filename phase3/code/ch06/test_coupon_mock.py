"""另一种常见的 AI 测试形态：mock 型。

它和 test_coupon_ai.py 的病不一样：
  空断言型：断言太弱，什么都没守住（防回归 = 0）
  mock 型  ：断言太死，绑住了实现细节（抗重构 = 0）

这份测试能抓到一部分真实缺陷（因为它确实检查了 SQL 里的数字），
但它会在一次无害的重构之后集体变红——那时团队就会开始改断言，
改到它重新变绿为止，而每次修改都在削弱它。

跑法：python -m unittest test_coupon_mock
"""

import unittest
from unittest.mock import MagicMock

from coupon_service import redeem


class TestRedeemMock(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.cur = self.conn.cursor.return_value
        # 模拟数据库返回：库存 5，已用 2
        self.cur.execute.return_value.fetchone.return_value = (5, 2)

    def test_update_statement_is_exact(self):
        """断言"发出的 SQL 一字不差"——这是 mock 型测试的典型写法。"""
        redeem(self.conn, "WELCOME", "u1")
        last_sql = self.cur.execute.call_args_list[-1][0][0]
        self.assertEqual(last_sql, "UPDATE coupons SET used = 3 WHERE code = 'WELCOME'")

    def test_commit_called(self):
        redeem(self.conn, "WELCOME", "u1")
        self.assertTrue(self.conn.commit.called)


if __name__ == "__main__":
    unittest.main()
