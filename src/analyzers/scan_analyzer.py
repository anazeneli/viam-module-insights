"""Orchestrator: code scan → changelog → Claude analysis."""
import requests
from src.analyzers.code_scanner import CodeScanner


class ScanAnalyzer:
    """Wires together CodeScanner + ChangelogFetcher + Claude to produce a scan report."""

    PYPI_URL = "https://pypi.org/pypi/viam-sdk/json"

    def __init__(self, github_client, claude_client, changelog_fetcher):
        self.github = github_client
        self.claude = claude_client
        self.changelog = changelog_fetcher

    def scan_module(self, repo_name):
        """
        Full code-scan pipeline for a single module.

        Args:
            repo_name: Repository name (without org prefix).

        Returns:
            dict: Structured scan results from Claude.
        """
        print(f"\n{'=' * 60}")
        print(f"CODE SCAN: {repo_name}")
        print('=' * 60)

        # 1. Fetch changelog (cached after first call)
        changelog_text = self.changelog.fetch_changelog()
        print(f"  Changelog: {len(changelog_text)} chars")

        # 2. Scan source files
        repo = self.github.get_repo(repo_name)
        scanner = CodeScanner(repo)
        source_files = scanner.scan_repo()
        total_chars = sum(f['size'] for f in source_files)
        print(f"  Source files: {len(source_files)} files, {total_chars} chars total")

        if not source_files:
            return {
                "can_build_with_latest_sdk": None,
                "severity": "unknown",
                "breaking_changes": [],
                "deprecation_warnings": [],
                "sdk_version_info": {},
                "summary": "No source files found to scan.",
            }

        # 3. Look up the latest stable SDK version from PyPI
        latest_sdk = self._fetch_latest_sdk_version()
        if latest_sdk:
            print(f"  Latest stable viam-sdk: {latest_sdk}")

        # 4. Send to Claude for analysis
        print("  Sending to Claude for analysis …")
        result = self.claude.analyze_code_scan(
            module_name=repo_name,
            source_files=source_files,
            changelog_text=changelog_text,
            latest_sdk_version=latest_sdk,
        )

        print(f"  Severity: {result.get('severity', 'unknown')}")
        print(f"  Breaking changes: {len(result.get('breaking_changes', []))}")
        print(f"  Deprecation warnings: {len(result.get('deprecation_warnings', []))}")
        print(f"  Can build with latest SDK: {result.get('can_build_with_latest_sdk')}")

        return result

    def _fetch_latest_sdk_version(self) -> str | None:
        """Fetch the latest stable viam-sdk version from PyPI."""
        try:
            resp = requests.get(self.PYPI_URL, timeout=10)
            resp.raise_for_status()
            return resp.json()["info"]["version"]
        except Exception as e:
            print(f"  Warning: could not fetch latest SDK version from PyPI: {e}")
            return None
