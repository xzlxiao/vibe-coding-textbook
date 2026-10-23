"""重复日程：把一条规则展开成具体事件。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .models import Event


@dataclass(frozen=True)
class Recurrence:
    """重复规则。只支持"每 N 天/周"——刻意不做 RFC 5545 全量语法。

    不变量：times 必须是 1..52 的整数；UNTIL 之后不再生成。
    """

    every_days: int
    times: int

    def expand(self, base: Event) -> list[Event]:
        events: list[Event] = []
        for i in range(self.times):
            shift = timedelta(days=self.every_days * i)
            events.append(
                Event(
                    title=base.title,
                    starts_at=base.starts_at + shift,
                    ends_at=base.ends_at + shift,
                    tags=base.tags,
                )
            )
        return events


def next_occurrence(event: Event, after: datetime) -> datetime | None:
    """下一次开始时间；已经过期返回 None。调用方负责处理时区。"""
    if event.ends_at <= after:
        return None
    return event.starts_at if event.starts_at > after else event.ends_at
