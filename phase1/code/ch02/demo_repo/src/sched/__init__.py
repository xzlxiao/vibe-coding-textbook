"""schedule-kit：把日程导出成 CSV。"""

__all__ = ["Event", "EventStore", "to_csv"]


def __getattr__(name: str):  # 延迟导入，避免子模块循环引用
    if name == "Event":
        from .models import Event

        return Event
    if name == "EventStore":
        from .store import EventStore

        return EventStore
    if name == "to_csv":
        from .export import to_csv

        return to_csv
    raise AttributeError(name)
