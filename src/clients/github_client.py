"""GitHub API client."""
from github import Github

class GitHubClient:
    """Wrapper for GitHub API operations."""
    
    def __init__(self, token, org_name):
        self.github = Github(token)
        self.org_name = org_name
        # For personal repos, we don't use organization
        self.is_personal = True
    
    def get_repo(self, repo_name):
        """Get a single repository."""
        full_name = f"{self.org_name}/{repo_name}"
        return self.github.get_repo(full_name)
    
    def get_repo_info(self, repo):
        """Get basic info about a repo."""
        return {
            'name': repo.name,
            'full_name': repo.full_name,
            'url': repo.html_url,
            'language': repo.language,
        }