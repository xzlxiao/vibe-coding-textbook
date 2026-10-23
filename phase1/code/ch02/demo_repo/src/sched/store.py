"""内存存储。写入只能走 add() —— 这样"重复日程"的判定只存在一处。"""

from __future__ import annotations

from .models import Event


class EventStore:
    def __init__(self) -> None:
        self._events: list[Event] = []

    def add(self, event: Event) -> None:
        """幂等：同一 (title, starts_at) 视为同一条，重复添加直接忽略。"""
        if any(e.title == event.title and e.starts_at == event.starts_at for e in self._events):
            return
        self._events.append(event)

    def all(self) -> list[Event]:
        """按开始时间升序返回副本，调用方改不到内部状态。"""
        return sorted(self._events, key=lambda e: e.starts_at)

    def __len__(self) -> int:
        return len(self._events)
