"""CSV 导出。列顺序是契约，改动必须同步 README 与测试。"""

from __future__ import annotations

import csv
from collections.abc import Iterable, Sequence
from pathlib import Path

COLUMNS: tuple[str, ...] = ("id", "name", "amount", "note")


def _row(record: Sequence[str | int]) -> list[str]:
    if len(record) != len(COLUMNS):
        raise ValueError(f"记录长度必须是 {len(COLUMNS)}，收到 {len(record)}")
    return [str(v) for v in record]


def to_csv(records: Iterable[Sequence[str | int]], path: Path) -> int:
    """写入 CSV 并返回数据行数。

    newline="" 是必须的：否则 Windows 上 csv 模块会写出空行。
    """
    rows = [_row(r) for r in records]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(COLUMNS)
        writer.writerows(rows)
    return len(rows)
