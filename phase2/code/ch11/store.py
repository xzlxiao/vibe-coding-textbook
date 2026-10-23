#!/usr/bin/env python3
"""候补报名系统 —— 核心逻辑参考实现（第 11 章配套）。

刻意只做「逻辑层」，不做 HTTP 层：这样 constraints 可以被直接验证，
而不是被网络与框架的细节掩盖。把它接到任何 Web 框架上都很薄。

对应规格：specs/waitlist/spec.md（第 02 章七段式）
对应约束：C1 幂等 / C2 并发 / C3 通知降级 / C4 权限（示例从略）/ C5 性能（示例从略）

实现取舍（写在这里，是为了让读者知道哪一条是「教学简化」）：
- 用 SQLite 单连接 + 进程内锁。SQLite 是单写者，锁是它的正确用法。
  换成 PostgreSQL 时，应改为「唯一约束 + 冲突重试」，不要照搬这把锁。
- 座位号 seq_no 由「最小空闲号」分配，配合 UNIQUE(event_id, seq_no) 保证不重号。
- offer 过期用轮询扫描（scan_expired），不用延迟队列，因为参考实现不想引入 Redis。
"""

from __future__ import annotations

import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Optional

OFFER_TTL_SECONDS = 15 * 60
MAX_DELIVERY_ATTEMPTS = 5
BACKOFF_BASE_SECONDS = 1.0


class DomainError(Exception):
    def __init__(self, code: str, message: str, status: int = 409):
        super().__init__(message)
        self.code = code
        self.status = status


@dataclass
class SignupResult:
    registration_id: str
    status: str            # confirmed / waiting
    seat_no: Optional[int]
    queue_no: Optional[int]
    reused: bool           # 是否是幂等重放（返回首次结果）


class Store:
    def __init__(self, path: str = ":memory:", sms_down: bool = False):
        self._lock = threading.RLock()
        self._db = sqlite3.connect(path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA foreign_keys=ON")
        self.sms_down = sms_down
        self._create_schema()

    # ---------------------------------------------------------------- schema
    def _create_schema(self) -> None:
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                capacity INTEGER NOT NULL CHECK (capacity > 0)
            );
            CREATE TABLE IF NOT EXISTS registrations (
                registration_id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL REFERENCES events(event_id),
                seq_no INTEGER NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                status TEXT NOT NULL,            -- confirmed / reserved / cancelled
                idempotency_key TEXT NOT NULL UNIQUE,
                created_at REAL NOT NULL
            );
            -- C2：并发下不重号、不超卖。用部分唯一索引，让已取消的行可以保留旧座位号。
            CREATE UNIQUE INDEX IF NOT EXISTS ux_seat
                ON registrations (event_id, seq_no)
                WHERE status IN ('confirmed', 'reserved');
            CREATE TABLE IF NOT EXISTS waitlist (
                entry_id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL REFERENCES events(event_id),
                registration_id TEXT NOT NULL REFERENCES registrations(registration_id),
                queue_no INTEGER NOT NULL,
                status TEXT NOT NULL,            -- waiting / offered / expired / confirmed
                offer_round INTEGER NOT NULL DEFAULT 0,
                offered_at REAL,
                UNIQUE (event_id, queue_no)
            );
            CREATE TABLE IF NOT EXISTS outbox (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dedupe_key TEXT NOT NULL UNIQUE, -- C3：同一邀请只发一次
                event_id TEXT NOT NULL,
                entry_id TEXT NOT NULL,
                body TEXT NOT NULL,
                status TEXT NOT NULL,            -- pending / sent / dead
                attempts INTEGER NOT NULL DEFAULT 0,
                next_at REAL NOT NULL
            );
            """
        )
        self._db.commit()

    # ---------------------------------------------------------------- helpers
    def _tx(self):
        return _Tx(self._db)

    def create_event(self, event_id: str, capacity: int) -> None:
        with self._lock:
            self._db.execute(
                "INSERT INTO events(event_id, capacity) VALUES (?, ?)", (event_id, capacity)
            )
            self._db.commit()

    def _capacity(self, event_id: str) -> int:
        row = self._db.execute(
            "SELECT capacity FROM events WHERE event_id=?", (event_id,)
        ).fetchone()
        if row is None:
            raise DomainError("EVENT_NOT_FOUND", "活动不存在", 404)
        return int(row["capacity"])

    def _free_seat_no(self, event_id: str, capacity: int) -> Optional[int]:
        used = {
            r["seq_no"]
            for r in self._db.execute(
                "SELECT seq_no FROM registrations "
                "WHERE event_id=? AND status IN ('confirmed','reserved')",
                (event_id,),
            )
        }
        for n in range(1, capacity + 1):
            if n not in used:
                return n
        return None

    def _next_queue_no(self, event_id: str) -> int:
        row = self._db.execute(
            "SELECT COALESCE(MAX(queue_no), 0) AS m FROM waitlist WHERE event_id=?",
            (event_id,),
        ).fetchone()
        return int(row["m"]) + 1

    def _cached(self, key: str):
        row = self._db.execute(
            "SELECT registration_id, status, seq_no FROM registrations "
            "WHERE idempotency_key=?",
            (key,),
        ).fetchone()
        if row is None:
            return None
        return SignupResult(
            registration_id=row["registration_id"],
            status=row["status"],
            seat_no=row["seq_no"],
            queue_no=None,
            reused=True,
        )

    # ---------------------------------------------------------------- 报名
    def signup(self, event_id: str, name: str, phone: str, idempotency_key: str) -> SignupResult:
        """C1：key 必填；重复 key 返回首次结果，不新建记录。"""
        if not idempotency_key:
            raise DomainError("MISSING_IDEMPOTENCY_KEY", "缺少 Idempotency-Key", 400)
        if not name or not phone:
            raise DomainError("INVALID_PROFILE", "姓名与手机号必填", 422)
        if not (len(phone) == 11 and phone.isdigit()):
            raise DomainError("INVALID_PHONE", "手机号必须为 11 位数字", 422)

        with self._lock, self._tx():
            cached = self._cached(idempotency_key)
            if cached is not None:
                return cached

            capacity = self._capacity(event_id)
            seat = self._free_seat_no(event_id, capacity)
            reg_id = uuid.uuid4().hex
            now = time.time()

            if seat is not None:
                self._db.execute(
                    "INSERT INTO registrations(registration_id, event_id, seq_no, name, phone,"
                    " status, idempotency_key, created_at) VALUES (?,?,?,?,?,?,?,?)",
                    (reg_id, event_id, seat, name, phone, "confirmed", idempotency_key, now),
                )
                return SignupResult(reg_id, "confirmed", seat, None, False)

            # 满员：进候补。seq_no 用一个永不冲突的负数占位，避免唯一约束互撞。
            seq_placeholder = -(self._next_queue_no(event_id))
            self._db.execute(
                "INSERT INTO registrations(registration_id, event_id, seq_no, name, phone,"
                " status, idempotency_key, created_at) VALUES (?,?,?,?,?,?,?,?)",
                (reg_id, event_id, seq_placeholder, name, phone, "waiting", idempotency_key, now),
            )
            queue_no = self._next_queue_no(event_id)
            entry_id = uuid.uuid4().hex
            self._db.execute(
                "INSERT INTO waitlist(entry_id, event_id, registration_id, queue_no, status)"
                " VALUES (?,?,?,?, 'waiting')",
                (entry_id, event_id, reg_id, queue_no),
            )
            return SignupResult(reg_id, "waiting", None, queue_no, False)

    # ---------------------------------------------------------------- 取消
    def cancel(self, registration_id: str, idempotency_key: str = "auto") -> dict:
        """取消后：名额置 reserved，邀请候补第一位；通知失败不影响取消。"""
        with self._lock, self._tx():
            row = self._db.execute(
                "SELECT * FROM registrations WHERE registration_id=?", (registration_id,)
            ).fetchone()
            if row is None:
                raise DomainError("NOT_FOUND", "报名不存在", 404)
            if row["status"] == "cancelled":
                return {"status": "cancelled", "reused": True}
            if row["status"] == "waiting":
                # 候补者自己退出：只退队列，不涉及名额
                self._db.execute(
                    "UPDATE registrations SET status='cancelled' WHERE registration_id=?",
                    (registration_id,),
                )
                self._db.execute(
                    "UPDATE waitlist SET status='expired' WHERE registration_id=?",
                    (registration_id,),
                )
                return {"status": "cancelled", "reused": False, "offer": None}

            event_id = row["event_id"]
            self._db.execute(
                "UPDATE registrations SET status='cancelled' WHERE registration_id=?",
                (registration_id,),
            )
            offer = self._offer_next(event_id)
            return {"status": "cancelled", "reused": False, "offer": offer}

    def _offer_next(self, event_id: str) -> Optional[dict]:
        """把刚释放的名额交给候补第一位，并写一条待发通知。"""
        capacity = self._capacity(event_id)
        seat = self._free_seat_no(event_id, capacity)
        if seat is None:
            return None
        entry = self._db.execute(
            "SELECT * FROM waitlist WHERE event_id=? AND status='waiting' "
            "ORDER BY queue_no ASC LIMIT 1",
            (event_id,),
        ).fetchone()
        if entry is None:
            return None

        # 该候补者的报名记录从 waiting 转为 reserved，占用释放出来的座位号
        self._db.execute(
            "UPDATE registrations SET status='reserved', seq_no=? WHERE registration_id=?",
            (seat, entry["registration_id"]),
        )
        self._db.execute(
            "UPDATE waitlist SET status='offered', offered_at=?, offer_round=offer_round+1"
            " WHERE entry_id=?",
            (time.time(), entry["entry_id"]),
        )
        dedupe = f"{entry['entry_id']}:{int(entry['offer_round']) + 1}"
        self._db.execute(
            "INSERT OR IGNORE INTO outbox(dedupe_key, event_id, entry_id, body, status, next_at)"
            " VALUES (?,?,?,?, 'pending', ?)",
            (dedupe, event_id, entry["entry_id"], "您已获得一个名额，请在 15 分钟内确认",
             time.time()),
        )
        return {"entry_id": entry["entry_id"], "seat_no": seat, "dedupe_key": dedupe}

    # ---------------------------------------------------------------- 确认 / 过期
    def confirm(self, entry_id: str) -> dict:
        with self._lock, self._tx():
            entry = self._db.execute(
                "SELECT * FROM waitlist WHERE entry_id=?", (entry_id,)
            ).fetchone()
            if entry is None:
                raise DomainError("NOT_FOUND", "候补记录不存在", 404)
            if entry["status"] != "offered":
                raise DomainError("NOT_OFFERED", "当前状态不可确认", 409)
            self._db.execute(
                "UPDATE waitlist SET status='confirmed' WHERE entry_id=?", (entry_id,)
            )
            self._db.execute(
                "UPDATE registrations SET status='confirmed' WHERE registration_id=?",
                (entry["registration_id"],),
            )
            return {"entry_id": entry_id, "status": "confirmed"}

    def expire_offers(self, ttl: float = OFFER_TTL_SECONDS, now: Optional[float] = None) -> list[str]:
        """扫描超时邀请：置 expired，释放名额，顺延给下一位。"""
        now = time.time() if now is None else now
        expired: list[str] = []
        with self._lock, self._tx():
            rows = self._db.execute(
                "SELECT * FROM waitlist WHERE status='offered' AND offered_at IS NOT NULL"
            ).fetchall()
            for e in rows:
                if now - float(e["offered_at"]) < ttl:
                    continue
                self._db.execute(
                    "UPDATE waitlist SET status='expired' WHERE entry_id=?", (e["entry_id"],)
                )
                self._db.execute(
                    "UPDATE registrations SET status='cancelled' WHERE registration_id=?",
                    (e["registration_id"],),
                )
                expired.append(e["entry_id"])
                self._offer_next(e["event_id"])
        return expired

    # ---------------------------------------------------------------- 通知投递
    def drain_outbox(self, limit: int = 50, now: Optional[float] = None) -> dict:
        """C3：至少一次投递 + 去重 + 指数退避。sms_down=True 时模拟网关故障。"""
        now = time.time() if now is None else now
        sent = failed = 0
        with self._lock:
            rows = self._db.execute(
                "SELECT * FROM outbox WHERE status='pending' AND next_at<=? ORDER BY id LIMIT ?",
                (now, limit),
            ).fetchall()
            for m in rows:
                if self.sms_down:
                    attempts = int(m["attempts"]) + 1
                    if attempts >= MAX_DELIVERY_ATTEMPTS:
                        self._db.execute(
                            "UPDATE outbox SET status='dead', attempts=? WHERE id=?",
                            (attempts, m["id"]),
                        )
                    else:
                        delay = BACKOFF_BASE_SECONDS * (2 ** (attempts - 1))
                        self._db.execute(
                            "UPDATE outbox SET attempts=?, next_at=? WHERE id=?",
                            (attempts, now + delay, m["id"]),
                        )
                    failed += 1
                else:
                    self._db.execute(
                        "UPDATE outbox SET status='sent', attempts=attempts+1 WHERE id=?",
                        (m["id"],),
                    )
                    sent += 1
            self._db.commit()
        return {"sent": sent, "failed": failed}

    # ---------------------------------------------------------------- 查询（测试与运营用）
    def confirmed_count(self, event_id: str) -> int:
        with self._lock:
            return int(
                self._db.execute(
                    "SELECT COUNT(*) AS c FROM registrations "
                    "WHERE event_id=? AND status IN ('confirmed','reserved')",
                    (event_id,),
                ).fetchone()["c"]
            )

    def waiting_count(self, event_id: str) -> int:
        with self._lock:
            return int(
                self._db.execute(
                    "SELECT COUNT(*) AS c FROM waitlist WHERE event_id=? AND status='waiting'",
                    (event_id,),
                ).fetchone()["c"]
            )

    def outbox_status(self) -> dict:
        with self._lock:
            rows = self._db.execute(
                "SELECT status, COUNT(*) AS c FROM outbox GROUP BY status"
            ).fetchall()
            return {r["status"]: int(r["c"]) for r in rows}

    def close(self) -> None:
        with self._lock:
            self._db.close()


class _Tx:
    """显式事务：BEGIN IMMEDIATE 避免读后写的窗口（对应 C2 的思路）。"""

    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def __enter__(self):
        self.db.execute("BEGIN IMMEDIATE")
        return self.db

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.db.commit()
        else:
            self.db.rollback()
        return False
