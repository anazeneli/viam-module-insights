"""Test ChangelogFetcher."""
from src.clients.changelog_fetcher import ChangelogFetcher


def test_changelog_fetch_returns_content():
    """Fetch the changelog and verify it contains expected keywords."""
    fetcher = ChangelogFetcher()
    text = fetcher.fetch_changelog()

    print(f"\nChangelog text length: {len(text)} chars")
    print(f"First 500 chars:\n{text[:500]}")

    assert len(text) > 100, "Changelog text seems too short"
    # Should contain at least one of our signal keywords
    assert any(kw in text.lower() for kw in ['deprecat', 'breaking', 'removed', 'renamed']), (
        "Changelog does not mention any deprecation/breaking keywords"
    )


def test_changelog_caching():
    """Second call should return cached result without re-fetching."""
    fetcher = ChangelogFetcher()

    first = fetcher.fetch_changelog()
    second = fetcher.fetch_changelog()

    assert first is second, "Expected cached (identical object) on second call"
