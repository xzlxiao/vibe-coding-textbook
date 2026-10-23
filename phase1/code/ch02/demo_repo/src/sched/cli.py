"""命令行入口：把 store / recur / export 串起来。

这里是唯一允许出现 print 与文件 IO 的地方——业务模块必须保持可测。
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

from .export import to_csv
from .models import Event
from .store import EventStore


def build_store(raw: list[tuple[str, str, int]]) -> EventStore:
    """把 (title, 起始时间, 分钟数) 元组列表装进 store。"""
    store = EventStore()
    for title, start, minutes in raw:
        begin = datetime.fromisoformat(start)
        store.add(Event(title, begin, begin + timedelta(minutes=minutes)))
    return store


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="sched")
    ap.add_argument("--out", type=Path, default=Path("events.csv"))
    args = ap.parse_args(argv)
    store = build_store([("晨会", "2026-10-20T09:00", 30), ("评审", "2026-10-20T15:00", 60)])
    return to_csv(store.all(), args.out)
