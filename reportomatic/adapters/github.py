from datetime import timezone

from github import Github

from .base import Adapter
from .objects import Issue, Pull, User
from .states import IssueState, PullState


class GitHubAdapter(Adapter):
    ISSUE_STATE_MAP = {
        IssueState.OPEN: "open",
        IssueState.CLOSED: "closed",
    }
    PULL_STATE_MAP = {
        PullState.OPEN: "open",
        PullState.CLOSED: "closed",
        PullState.MERGED: "closed",
    }

    @property
    def connection(self):
        return Github(self._token)

    @property
    def project(self):
        return self._connection.get_repo(self._path)

    def issues(self, state=IssueState.OPEN, updated_after=None):
        gh_state = self.ISSUE_STATE_MAP.get(state)
        for gh_issue in self.project.get_issues(state=gh_state, since=updated_after):
            yield Issue(
                id=gh_issue.number,
                title=gh_issue.title,
                state=gh_issue.state,
                created_at=gh_issue.created_at,
                updated_at=gh_issue.updated_at,
                closed_at=gh_issue.closed_at,
                url=gh_issue.html_url,
            )

    def pulls(self, state=PullState.OPEN, updated_after=None):
        gh_state = self.PULL_STATE_MAP.get(state)
        for gh_pr in self.project.get_pulls(
                state=gh_state,
                sort="updated",
                direction="desc"
        ):
            pr_updated = gh_pr.updated_at.astimezone(timezone.utc).replace(tzinfo=None)
            if updated_after and pr_updated < updated_after:
                continue

            yield Pull(
                id=gh_pr.number,
                title=gh_pr.title,
                state=gh_pr.state,
                created_at=gh_pr.created_at,
                updated_at=gh_pr.updated_at,
                merged_at=gh_pr.merged_at,
                merged_by=self.user(gh_pr.merged_by) if gh_pr.merged_by else None,
                reviewers=[self.user(r) for r in gh_pr.requested_reviewers],
                assignees=[self.user(a) for a in gh_pr.assignees],
                url=gh_pr.html_url,
            )

    def user(self, data):
        return User(
            id=data.id,
            username=data.login,
            name=data.name or "",
        )
