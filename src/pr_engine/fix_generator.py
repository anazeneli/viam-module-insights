"""Generate code fixes for each file in a PR plan using Claude."""
from src.pr_engine.triager import PRPlan


class FixGenerator:
    """Uses Claude to produce fixed file contents for a PR plan."""

    def __init__(self, claude_client, github_client):
        self.claude = claude_client
        self.github = github_client

    def generate_fixes(self, repo_name: str, pr_plan: PRPlan) -> dict[str, str]:
        """Produce fixed file contents for every FileChange in *pr_plan*.

        Args:
            repo_name: Repository name (without org prefix).
            pr_plan: The PR plan whose file changes need fixes.

        Returns:
            dict mapping file path → complete fixed content.
        """
        fixes: dict[str, str] = {}

        for fc in pr_plan.file_changes:
            print(f"    Fixing {fc.path} …")
            current_content = self.github.get_file_content(repo_name, fc.path)
            fixed = self.claude.generate_code_fix(
                repo_name=repo_name,
                file_path=fc.path,
                current_content=current_content,
                issues=fc.issues,
                concern=pr_plan.concern,
            )
            fixes[fc.path] = fixed

        return fixes
