from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class User:
    id: int
    username: str
    name: str

    def __str__(self):
        return self.name or self.username or str(self.id)


@dataclass
class Issue:
    id: int
    title: str
    state: str
    created_at: datetime
    updated_at: datetime
    closed_at: datetime
    url: str

    def __str__(self):
        return (
            f"**{self.state.upper()}** "
            f"[{self.title.strip()}]"
            f"({self.url})"
        )


@dataclass
class Pull:
    id: int
    title: str
    state: str
    created_at: datetime
    updated_at: datetime
    merged_at: datetime
    url: str
    merged_by: User = None
    reviewers: List[User] = field(default_factory=list)
    assignees: List[User] = field(default_factory=list)

    def __str__(self):
        extras = " (" + ', '.join(self.extras()) + ")" if self.extras() else ''
        return (
            f"**{self.state.upper()}** "
            f"[{self.title.strip()}{extras}]"
            f"({self.url.strip()})"
        )

    def extras(self):
        extras = []
        if self.assignees:
            assignees_str = ", ".join(str(assignee) for assignee in self.assignees)
            extras.append(f"assigned to {assignees_str}")
        if self.reviewers:
            reviewers_str = ", ".join(str(reviewer) for reviewer in self.reviewers)
            extras.append(f"review by {reviewers_str}")
        if self.merged_at:
            extras.append(f"merged by {self.merged_by} on {self.merged_at.date()}")

        return extras


@dataclass
class Milestone:
    id: int
    title: str
    description: str
    state: str
    created_at: datetime
    updated_at: datetime
    closed_at: datetime
    due_on: datetime
    url: str
    issues: List[Issue] = field(default_factory=list)

    def __str__(self):
        return (
            f"**{self.state.upper()}** "
            f"[{self.title.strip()} (due {self.due_on.date() if self.due_on else 'date not set'})]"
            f"({self.url})"
        )
