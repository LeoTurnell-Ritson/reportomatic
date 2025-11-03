from datetime import timezone

from github import Github

from .base import Adapter
from .objects import Issue, Milestone, Pull, User
from .states import IssueState, MilestoneState, PullState


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
    MILESTONE_STATE_MAP = {
        MilestoneState.OPEN: "open",
        MilestoneState.CLOSED: "closed",
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
            yield self.issue(gh_issue)

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

    def milestones(self, state=MilestoneState.OPEN, updated_after=None):
        gh_state = self.MILESTONE_STATE_MAP.get(state)
        for gh_milestone in self.project.get_milestones(
            state=gh_state,
            sort="due_on",
            direction="desc"
        ):
            milestone_updated = (
                gh_milestone
                .updated_at
                .astimezone(timezone.utc)
                .replace(tzinfo=None)
            )
            if updated_after and milestone_updated < updated_after:
                continue

            yield Milestone(
                id=gh_milestone.number,
                title=gh_milestone.title,
                description=gh_milestone.description or "",
                state=gh_milestone.state,
                created_at=gh_milestone.created_at,
                updated_at=gh_milestone.updated_at,
                closed_at=gh_milestone.closed_at,
                due_on=gh_milestone.due_on,
                issues=[
                    self.issue(x)
                    for x in self.project.get_issues(
                        milestone=gh_milestone,
                        state="all"
                    )
                ],
                url=gh_milestone.html_url,
            )

    def user(self, data):
        return User(
            id=data.id,
            username=data.login,
            name=data.name or "",
        )

    def issue(self, data):
        return Issue(
            id=data.number,
            title=data.title,
            state=data.state,
            created_at=data.created_at,
            updated_at=data.updated_at,
            closed_at=data.closed_at,
            url=data.html_url,
        )
