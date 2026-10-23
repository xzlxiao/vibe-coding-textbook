"""导出契约的回归测试。修改 COLUMNS 必须同步改这里——这是"测试即文档"。"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from sched.export import COLUMNS, to_csv
from sched.models import Event
from sched.store import EventStore


def _event(title: str = "晨会", tags: tuple[str, ...] = ("work",)) -> Event:
    start = datetime(2026, 10, 19, 9, 0)
    return Event(title=title, starts_at=start, ends_at=start + timedelta(minutes=30), tags=tags)


def test_columns_are_contract() -> None:
    assert COLUMNS == ("start", "end", "minutes", "title", "tags")


def test_csv_has_header_and_one_row(tmp_path: Path) -> None:
    out = tmp_path / "e.csv"
    assert to_csv([_event()], out) == 1
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    assert lines[0].split(",") == list(COLUMNS)
    assert "晨会" in lines[1]


def test_title_with_comma_is_escaped(tmp_path: Path) -> None:
    out = tmp_path / "e.csv"
    to_csv([_event(title="周会, 含产品与研发")], out)
    assert '"周会, 含产品与研发"' in out.read_text(encoding="utf-8")


def test_store_is_idempotent() -> None:
    store = EventStore()
    store.add(_event())
    store.add(_event())
    assert len(store) == 1
