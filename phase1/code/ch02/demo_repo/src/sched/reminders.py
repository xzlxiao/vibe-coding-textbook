"""提醒：算出"该提醒谁、什么时候提醒"。

这一层刻意不负责发送。发送属于副作用，必须由调用方（CLI 或调度器）决定，
这样这个模块永远可以被单测覆盖。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .models import Event


@dataclass(frozen=True)
class Reminder:
    event_title: str
    fire_at: datetime
    channel: str = "inbox"


def due_reminders(
    events: list[Event],
    now: datetime,
    lead: timedelta = timedelta(minutes=10),
    channel: str = "inbox",
) -> list[Reminder]:
    """返回 upcoming 窗口内需要触发的提醒，按触发时间升序。

    边界：恰好等于 now + lead 的事件**包含**在内（闭区间），
    因为"提前 10 分钟"是人写的规则，不是浮点比较。
    """
    out: list[Reminder] = []
    horizon = now + lead
    for event in events:
        if now < event.starts_at <= horizon:
            out.append(Reminder(event.title, event.starts_at - lead, channel))
    return sorted(out, key=lambda r: r.fire_at)
