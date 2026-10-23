"""导出成 CSV。

列顺序是**对外契约**：改顺序等于改接口，必须同步改 README 与测试。
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

from .models import Event
from .store import EventStore

COLUMNS = ("start", "end", "minutes", "title", "tags")


def _row(event: Event) -> list[str]:
    return [
        event.starts_at.isoformat(timespec="minutes"),
        event.ends_at.isoformat(timespec="minutes"),
        str(event.duration_minutes),
        event.title,
        "|".join(event.tags),
    ]


def to_csv(events: list[Event], path: Path) -> int:
    """写入 CSV，返回写入行数。用 newline="" 避免 Windows 上多出空行。"""
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(COLUMNS)
        for event in events:
            writer.writerow(_row(event))
    return len(events)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    out = Path(args[args.index("--out") + 1]) if "--out" in args else Path("events.csv")
    store = EventStore()
    return to_csv(store.all(), out)
