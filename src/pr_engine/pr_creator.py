"""Create branches, commits, and PRs on GitHub for a PR plan."""
from src.pr_engine.triager import PRPlan


class PRCreator:
    """Pushes fixes to GitHub as branches + pull requests."""

    def __init__(self, github_client):
        self.github = github_client

    def create_pr(self, repo_name: str, pr_plan: PRPlan, fixes: dict[str, str]) -> dict:
        """Create a branch, commit each fixed file, and open a PR.

        Args:
            repo_name: Repository name (without org prefix).
            pr_plan: The plan describing the PR to create.
            fixes: Mapping of file path → fixed file content.

        Returns:
            dict with ``status``, ``pr_url``, ``pr_number``, ``branch_name``, ``files_changed``.
        """
        branch = pr_plan.branch_name

        # 1. Create branch
        print(f"    Creating branch {branch} …")
        self.github.create_branch(repo_name, branch)

        # 2. Commit each fixed file
        for file_path, content in fixes.items():
            msg = f"{pr_plan.concern}: fix {file_path}"
            print(f"    Committing {file_path} …")
            self.github.update_file_on_branch(
                repo_name, branch, file_path, content, msg,
            )

        # 3. Open PR
        print(f"    Opening PR: {pr_plan.title}")
        pr_result = self.github.create_pull_request(
            repo_name, branch, pr_plan.title, pr_plan.body,
        )

        return {
            "status": "created",
            "pr_url": pr_result["pr_url"],
            "pr_number": pr_result["pr_number"],
            "branch_name": branch,
            "files_changed": list(fixes.keys()),
        }
