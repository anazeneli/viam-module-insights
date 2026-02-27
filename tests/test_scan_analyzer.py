"""End-to-end test: scan camera-zone for compatibility issues."""
import json
from src.config import Config
from src.clients.github_client import GitHubClient
from src.clients.claude_client import ClaudeClient
from src.clients.changelog_fetcher import ChangelogFetcher
from src.analyzers.scan_analyzer import ScanAnalyzer


def test_scan_camera_zone():
    """
    Scan camera-zone and expect it to flag get_image → get_images deprecation.
    Saves full results to scan_camera-zone.json.
    """
    config = Config()

    github = GitHubClient(config.github_token, config.github_org)
    claude = ClaudeClient(config.anthropic_api_key, config.anthropic_model)
    changelog = ChangelogFetcher()

    analyzer = ScanAnalyzer(github, claude, changelog)
    result = analyzer.scan_module("camera-zone")

    # Pretty-print full results
    print("\n" + "=" * 60)
    print("SCAN RESULTS")
    print("=" * 60)
    print(json.dumps(result, indent=2))

    # Save to file
    with open("scan_camera-zone.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\nSaved to scan_camera-zone.json")

    # Assertions
    assert result.get("can_build_with_latest_sdk") is not None, "Missing can_build_with_latest_sdk"
    assert result.get("severity") in ("none", "low", "medium", "high", "critical"), (
        f"Unexpected severity: {result.get('severity')}"
    )

    # We expect at least one deprecation or breaking change mentioning get_image
    all_issues = result.get("breaking_changes", []) + result.get("deprecation_warnings", [])

    def mentions_get_image(issue):
        """Check all string fields for get_image / getimage (case-insensitive)."""
        searchable = " ".join(
            str(v) for v in issue.values() if isinstance(v, str)
        ).lower()
        return "get_image" in searchable or "getimage" in searchable

    get_image_issues = [issue for issue in all_issues if mentions_get_image(issue)]
    print(f"\nget_image related issues: {len(get_image_issues)}")
    for issue in get_image_issues:
        print(f"  - {issue['file']}:{issue.get('line', '?')} — {issue['description']}")

    assert len(get_image_issues) > 0, (
        f"Expected at least one issue mentioning get_image deprecation. "
        f"Got {len(all_issues)} total issues: {json.dumps(all_issues, indent=2)}"
    )


if __name__ == "__main__":
    test_scan_camera_zone()
