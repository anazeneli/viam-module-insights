"""GitHub API client."""
from github import Github, Auth, GithubException


class GitHubClient:
    """Wrapper for GitHub API operations."""

    def __init__(self, token, org_name):
        self.github = Github(auth=Auth.Token(token))
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

    def get_file_content(self, repo_name, file_path, ref=None):
        """Fetch the decoded text content of a file from a repo.

        Args:
            repo_name: Repository name (without org prefix).
            file_path: Path within the repo (e.g. ``src/models/zone.py``).
            ref: Optional branch/tag/sha. Defaults to the repo's default branch.

        Returns:
            str: Decoded file content.
        """
        repo = self.get_repo(repo_name)
        kwargs = {"ref": ref} if ref else {}
        content_file = repo.get_contents(file_path, **kwargs)
        return content_file.decoded_content.decode("utf-8")

    def create_branch(self, repo_name, branch_name, base_branch=None):
        """Create a new branch from the head of *base_branch*.

        Args:
            repo_name: Repository name (without org prefix).
            branch_name: New branch name.
            base_branch: Base branch name. Defaults to the repo's default branch.

        Returns:
            str: The full ref string (e.g. ``refs/heads/auto/sdk-version-bump-...``).
        """
        repo = self.get_repo(repo_name)
        base = base_branch or repo.default_branch
        base_sha = repo.get_branch(base).commit.sha
        ref = f"refs/heads/{branch_name}"
        repo.create_git_ref(ref=ref, sha=base_sha)
        return ref

    def update_file_on_branch(self, repo_name, branch_name, file_path, new_content, commit_message):
        """Create or update a file on an existing branch.

        Args:
            repo_name: Repository name (without org prefix).
            branch_name: Target branch.
            file_path: Path within the repo.
            new_content: Full replacement content for the file.
            commit_message: Commit message.

        Returns:
            dict: ``{sha, commit_sha}`` of the resulting commit.
        """
        repo = self.get_repo(repo_name)
        try:
            existing = repo.get_contents(file_path, ref=branch_name)
            result = repo.update_file(
                path=file_path,
                message=commit_message,
                content=new_content,
                sha=existing.sha,
                branch=branch_name,
            )
        except GithubException as exc:
            if exc.status == 404:
                result = repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=new_content,
                    branch=branch_name,
                )
            else:
                raise
        return {
            "sha": result["content"].sha,
            "commit_sha": result["commit"].sha,
        }

    def create_pull_request(self, repo_name, branch_name, title, body, base_branch=None):
        """Open a pull request.

        Args:
            repo_name: Repository name (without org prefix).
            branch_name: Head branch with the changes.
            title: PR title.
            body: PR body (markdown).
            base_branch: Base branch to merge into. Defaults to the repo's default branch.

        Returns:
            dict: ``{pr_url, pr_number}``.
        """
        repo = self.get_repo(repo_name)
        base = base_branch or repo.default_branch
        pr = repo.create_pull(
            title=title,
            body=body,
            head=branch_name,
            base=base,
        )
        return {"pr_url": pr.html_url, "pr_number": pr.number}