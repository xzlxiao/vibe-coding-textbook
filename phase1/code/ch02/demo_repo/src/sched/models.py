"""领域对象：日程事件。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Event:
    """一条日程。

    不变量（任何改动都必须保持）：
      1. ends_at 必须晚于 starts_at；
      2. title 去空白后非空、长度 ≤ 80；
      3. tags 里的元素全部小写，且不重复。
    """

    title: str
    starts_at: datetime
    ends_at: datetime
    tags: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at 必须晚于 starts_at")
        if not self.title.strip() or len(self.title) > 80:
            raise ValueError("title 必须非空且不超过 80 字")
        if tuple(sorted(set(self.tags))) != self.tags:
            raise ValueError("tags 必须小写、去重、有序")

    @property
    def duration_minutes(self) -> int:
        return int((self.ends_at - self.starts_at).total_seconds() // 60)
