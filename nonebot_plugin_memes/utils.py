from datetime import datetime, timezone


def remove_timezone(dt: datetime) -> datetime:
    """移除时区"""
    if dt.tzinfo is None:
        return dt
    # 先转至 UTC 时间，再移除时区
    dt = dt.astimezone(timezone.utc)
    return dt.replace(tzinfo=None)


def add_timezone(dt: datetime) -> datetime:
    """添加时区"""
    if dt.tzinfo is not None:
        return dt.astimezone()
    return dt.replace(tzinfo=timezone.utc).astimezone()
