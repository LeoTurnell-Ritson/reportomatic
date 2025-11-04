from datetime import datetime


def to_datetime(value):
    if isinstance(value, datetime):
        return value

    return datetime.fromisoformat(value) if value else None
