from .adapters import GitHubAdapter, GitLabAdapter, states


class Client:

    def __init__(self, url):
        if "github" in url:
            self._adapter = GitHubAdapter(url)
        elif "gitlab" in url:
            self._adapter = GitLabAdapter(url)
        else:
            raise ValueError(f"Unsupported URL: {url}")

    def issues(self, state=states.IssueState.OPEN, updated_after=None):
        return self._adapter.issues(state=state, updated_after=updated_after)

    def pulls(self, state=states.PullState.OPEN, updated_after=None):
        return self._adapter.pulls(state=state, updated_after=updated_after)
