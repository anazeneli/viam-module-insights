"""Test CodeScanner against a real repo."""
from src.config import Config
from src.clients.github_client import GitHubClient
from src.analyzers.code_scanner import CodeScanner


def test_code_scanner_finds_source_files():
    """Scan camera-zone and verify we get .py files with content."""
    config = Config()
    github = GitHubClient(config.github_token, config.github_org)
    repo = github.get_repo("camera-zone")

    scanner = CodeScanner(repo)
    files = scanner.scan_repo()

    print(f"\nFound {len(files)} source files:")
    for f in files:
        print(f"  {f['path']} ({f['size']} chars)")

    # Should find at least one Python file
    py_files = [f for f in files if f['path'].endswith('.py')]
    assert len(py_files) > 0, "Expected at least one .py file in camera-zone"

    # Every file should have content (except __init__.py which can be empty)
    for f in files:
        assert f['content'] is not None, f"None content for {f['path']}"
        if not f['path'].endswith('__init__.py'):
            assert f['size'] > 0, f"Empty content for {f['path']}"



def test_code_scanner_respects_size_limits():
    """Verify no single file exceeds MAX_FILE_BYTES and total is within limit."""
    config = Config()
    github = GitHubClient(config.github_token, config.github_org)
    repo = github.get_repo("camera-zone")

    scanner = CodeScanner(repo)
    files = scanner.scan_repo()

    total = sum(f['size'] for f in files)
    print(f"\nTotal chars: {total} (limit: {CodeScanner.MAX_TOTAL_CHARS})")

    assert total <= CodeScanner.MAX_TOTAL_CHARS
    for f in files:
        assert f['size'] <= CodeScanner.MAX_FILE_BYTES, (
            f"{f['path']} is {f['size']} bytes, exceeds {CodeScanner.MAX_FILE_BYTES}"
        )
