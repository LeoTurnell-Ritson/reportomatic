from datetime import datetime

from gitlab import Gitlab, GitlabGetError

from .base import Adapter
from .objects import Issue, Pull, User, Milestone
from .states import IssueState, MilestoneState, PullState


class GitLabAdapter(Adapter):
    ISSUE_STATE_MAP = {
        IssueState.OPEN: "opened",
        IssueState.CLOSED: "closed",
    }
    PULL_STATE_MAP = {
        PullState.OPEN: "opened",
        PullState.CLOSED: "closed",
        PullState.MERGED: "merged",
    }
    MILESTONE_STATE_MAP = {
        MilestoneState.OPEN: "active",
        MilestoneState.CLOSED: "closed",
    }

    @property
    def connection(self):
        return Gitlab(
            url=f"{self._scheme}://{self._hostname}",
            private_token=self._token,
        )

    @property
    def project(self):
        try:
            return self._connection.projects.get(self._path)
        except GitlabGetError:
            return self._connection.groups.get(self._path)

    def issues(self, state=IssueState.OPEN, updated_after=None):
        gl_state = self.ISSUE_STATE_MAP.get(state)
        issues = self.project.issues.list(
            state=gl_state,
            updated_after=updated_after,
            all=True
        )
        for gl_issue in issues:
            yield self.issue(gl_issue)

    def pulls(self, state=PullState.OPEN, updated_after=None):
        gl_state = self.PULL_STATE_MAP.get(state)
        mrs = self.project.mergerequests.list(
            state=gl_state,
            updated_after=updated_after,
            all=True
        )
        for gl_mr in mrs:
            yield Pull(
                id=gl_mr.iid,
                title=gl_mr.title,
                state=gl_mr.state,
                created_at=gl_mr.created_at,
                updated_at=gl_mr.updated_at,
                merged_at=(
                    datetime.fromisoformat(gl_mr.merged_at)
                    if gl_mr.merged_at else None
                ),
                url=gl_mr.web_url,
                merged_by=self.user(gl_mr.merged_by) if gl_mr.merged_by else None,
                reviewers=(
                    [self.user(r) for r in gl_mr.reviewers]
                    if hasattr(gl_mr, 'reviewers') else []
                ),
                assignees=(
                    [self.user(a) for a in gl_mr.assignees]
                    if hasattr(gl_mr, 'assignees') else []
                ),
            )

    def milestones(self, state=MilestoneState.OPEN, updated_after=None):
        gl_state = self.MILESTONE_STATE_MAP.get(state)
        for milestone in self.project.milestones.list(
            state=gl_state,
            updated_after=updated_after,
            all=True,
            sort="desc",
            order_by="due_date",
        ):
            yield Milestone(
                id=milestone.iid,
                title=milestone.title,
                description=milestone.description,
                state=milestone.state,
                created_at=milestone.created_at,
                updated_at=milestone.updated_at,
                closed_at=milestone.closed_at if hasattr(milestone, 'closed_at') else None,
                due_on=milestone.due_date,
                issues=[self.issue(i) for i in milestone.issues(list=True, all=True)],
                url=milestone.web_url,
            )

    def user(self, data):
        return User(
            id=data["id"],
            username=data.get("username", ""),
            name=data.get("name", ""),
        )

    def issue(self, data):
        return Issue(
            id=data.iid,
            title=data.title,
            state=data.state,
            created_at=data.created_at,
            updated_at=data.updated_at,
            closed_at=data.closed_at,
            url=data.web_url,
        )
