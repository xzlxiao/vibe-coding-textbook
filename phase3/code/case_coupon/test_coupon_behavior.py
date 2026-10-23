"""行为测试 —— 写成「业务规则」，不写「实现细节」。

与 test_coupon_ai.py 的区别只有一条：断言的对象是规格里的句子，
不是函数的内部动作。因此这份测试在换实现时不用改。

用 COUPON_IMPL 选择被测实现：
    python -m unittest test_coupon_behavior                       # 默认 coupon_service（AI 原版）
    COUPON_IMPL=coupon_service_fixed python -m unittest test_coupon_behavior
"""

import importlib
import os
import sqlite3
import unittest

_IMPL = os.environ.get("COUPON_IMPL", "coupon_service")
_impl = importlib.import_module(_IMPL)


def _fresh(quota=2):
    conn = sqlite3.connect(":memory:", isolation_level=None)
    _impl.init_db(conn)
    conn.execute("INSERT INTO coupons VALUES ('WELCOME', ?, 0)", (quota,))
    return conn


class TestCouponRules(unittest.TestCase):
    """规格的四句话，一条一句测试。"""

    def test_01_same_user_can_only_redeem_once(self):
        """规格：「每个用户对同一张券只能核销一次」。"""
        conn = _fresh()
        self.assertTrue(_impl.redeem(conn, "WELCOME", "u1")["ok"])
        second = _impl.redeem(conn, "WELCOME", "u1")
        self.assertFalse(second["ok"], "同一用户第二次核销必须被拒绝")

    def test_02_quota_is_not_exceeded(self):
        """规格：「总核销次数不超过库存」。"""
        conn = _fresh(quota=2)
        self.assertTrue(_impl.redeem(conn, "WELCOME", "u1")["ok"])
        self.assertTrue(_impl.redeem(conn, "WELCOME", "u2")["ok"])
        self.assertFalse(_impl.redeem(conn, "WELCOME", "u3")["ok"], "库存耗尽后必须拒绝")

    def test_03_code_with_quote_is_handled_as_data(self):
        """券码是用户输入：含单引号的合法券码不能被当成 SQL 语法。"""
        conn = _fresh()
        conn.execute("INSERT INTO coupons VALUES (?, 1, 0)", ("A'B",))
        result = _impl.redeem(conn, "A'B", "u1")
        self.assertTrue(result["ok"], f"合法券码应当能核销，实际返回 {result}")

    def test_04_injection_string_cannot_redeem(self):
        """券码是用户输入：注入串不能换来一次成功核销。"""
        conn = _fresh()
        before = conn.execute("SELECT used FROM coupons WHERE code='WELCOME'").fetchone()[0]
        result = _impl.redeem(conn, "X' OR '1'='1", "u1")
        self.assertFalse(result["ok"], "注入串不应当核销成功")
        after = conn.execute("SELECT used FROM coupons WHERE code='WELCOME'").fetchone()[0]
        self.assertEqual(before, after, "注入串不应当改动任何一张券的已用次数")

    def test_05_token_is_a_usable_string(self):
        """规格：「返回核销凭证」—— 凭证得是个能用的字符串，不是 None。"""
        conn = _fresh()
        token = _impl.redeem(conn, "WELCOME", "u1").get("token")
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0, "凭证不能是空串")


if __name__ == "__main__":
    unittest.main(verbosity=2)
