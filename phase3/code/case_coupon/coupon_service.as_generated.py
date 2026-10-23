"""AI 生成的优惠券核销实现 —— 原样保存，一字未改。

设定：把规格「用户可用一张券一次；库存扣减；返回核销凭证」交给编码智能体，
它一次给出下面这份实现。语法正确、happy path 能跑。

这份文件保留原样，是为了让「依赖核验门禁」有东西可抓：
它在 import 阶段就会失败。后续脚本用的是把这一行换成本地桩的版本。
"""

import sqlite3

from fastapi_jwt_auth_kit import sign_token  # 幻觉依赖：PyPI 上不存在这个包


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
