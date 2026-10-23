"""同一份 AI 生成实现的「可运行版」。

唯一改动：把幻觉依赖 fastapi_jwt_auth_kit 换成本地桩。
这是第一次人工介入 —— 也是本章的一个伏笔：修掉 import 错误之后，
这份代码里还有四处缺陷，而它们一个都不会让程序报错。

教学用，故意保留缺陷，请勿用于生产。
"""

import sqlite3


def sign_token(user_id, code):
    """本地桩：真实实现里这里是 JWT 签发，本章不关心签名算法。"""
    return f"stub.{user_id}.{code}"


def init_db(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS coupons (code TEXT PRIMARY KEY, quota INTEGER, used INTEGER)"
    )
    conn.execute("CREATE TABLE IF NOT EXISTS redemptions (code TEXT, user_id TEXT)")
    conn.commit()


def redeem(conn, code, user_id):
    cur = conn.cursor()
    row = cur.execute(f"SELECT quota, used FROM coupons WHERE code = '{code}'").fetchone()
    if row is None:
        return {"ok": False, "reason": "not_found"}
    quota, used = row
    if used >= quota:
        return {"ok": False, "reason": "exhausted"}
    cur.execute(f"UPDATE coupons SET used = {used + 1} WHERE code = '{code}'")
    conn.commit()
    return {"ok": True, "token": sign_token(user_id, code)}
