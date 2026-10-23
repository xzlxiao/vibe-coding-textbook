"""不变量测试：这些错误必须在构造时就炸，而不是在导出时悄悄变成脏数据。"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from sched.models import Event


def _at(minutes: int = 30) -> tuple[datetime, datetime]:
    start = datetime(2026, 10, 20, 9, 0)
    return start, start + timedelta(minutes=minutes)


def test_end_must_be_after_start() -> None:
    with pytest.raises(ValueError):
        Event("x", *_at(0))


def test_title_is_trimmed_for_emptiness() -> None:
    with pytest.raises(ValueError):
        Event("   ", *_at())


def test_tags_must_be_sorted_unique_lowercase() -> None:
    with pytest.raises(ValueError):
        Event("x", *_at(), tags=("Work", "work"))
