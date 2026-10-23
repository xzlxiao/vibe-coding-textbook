"""iCalendar（.ics）适配器：只做单向导出，不做导入。

为什么要单独一个目录：格式适配是最容易"越改越乱"的一层。
把它隔离出来，将来换格式（CSV → ics → CalDAV）不会传染到领域层。
"""

from __future__ import annotations

from .models import Event


def _fmt(dt) -> str:
    return dt.strftime("%Y%m%dT%H%M%S")


def to_ics(events: list[Event], calendar_name: str = "schedule-kit") -> str:
    """生成 RFC 5545 最小可用的 VCALENDAR 文本。

    注意：折行（75 字节）与转义（逗号、分号、反斜杠）这里**没有实现**，
    接入真实日历客户端前必须补上——这正是"看起来能用"与"能用"的差别。
    """
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//{calendar_name}//CN",
        "BEGIN:VTIMEZONE",
        "TZID:Asia/Shanghai",
        "END:VTIMEZONE",
    ]
    for i, event in enumerate(events, start=1):
        lines += [
            "BEGIN:VEVENT",
            f"UID:{i}@{calendar_name}",
            f"DTSTART;TZID=Asia/Shanghai:{_fmt(event.starts_at)}",
            f"DTEND;TZID=Asia/Shanghai:{_fmt(event.ends_at)}",
            f"SUMMARY:{event.title}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
