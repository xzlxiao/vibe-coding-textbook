"""修好的实现 —— 四个缺陷逐一对应的改法都在注释里。

与 coupon_service.py 的差别几乎全是"把没写的写上"，只有 SQL 那一处是"把写错的改对"。
这正是本章的核心：AI 代码的主要风险是 omission（缺失），不是 commission（写错）。
"""

import sqlite3


def sign_token(user_id, code):
    return f"stub.{user_id}.{code}"


def init_db(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS coupons (code TEXT PRIMARY KEY, quota INTEGER, used INTEGER)"
    )
    # 改法 3：让数据库而不是应用代码来保证「一人一次」
    conn.execute(
        "CREATE TABLE IF NOT EXISTS redemptions ("
        "code TEXT, user_id TEXT, UNIQUE(code, user_id))"
    )
    conn.commit()


def redeem(conn, code, user_id):
    cur = conn.cursor()
    try:
        # 改法 1：把「读 + 判 + 写」收进一个立即锁事务，消除交错窗口
        cur.execute("BEGIN IMMEDIATE")
        # 改法 2：参数化查询，券码永远只是数据，不会变成 SQL 语法
        row = cur.execute("SELECT quota, used FROM coupons WHERE code = ?", (code,)).fetchone()
        if row is None:
            cur.execute("ROLLBACK")
            return {"ok": False, "reason": "not_found"}

        quota, used = row
        if used >= quota:
            cur.execute("ROLLBACK")
            return {"ok": False, "reason": "exhausted"}

        # 改法 3（续）：唯一约束就是最后一道闸，重复核销在这里被数据库拒绝
        cur.execute("INSERT INTO redemptions (code, user_id) VALUES (?, ?)", (code, user_id))

        # 改法 4：扣减写成一条带条件的原子语句，条件不成立时 rowcount 为 0
        cur.execute(
            "UPDATE coupons SET used = used + 1 WHERE code = ? AND used < quota", (code,)
        )
        if cur.rowcount != 1:
            cur.execute("ROLLBACK")
            return {"ok": False, "reason": "exhausted"}

        cur.execute("COMMIT")
    except sqlite3.IntegrityError:
        cur.execute("ROLLBACK")
        return {"ok": False, "reason": "already_redeemed"}
    return {"ok": True, "token": sign_token(user_id, code)}
