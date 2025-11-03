from enum import Enum


class IssueState(Enum):
    OPEN = "opened"
    CLOSED = "closed"


class PullState(Enum):
    OPEN = "opened"
    CLOSED = "closed"
    MERGED = "merged"


class MilestoneState(Enum):
    OPEN = "opened"
    CLOSED = "closed"
