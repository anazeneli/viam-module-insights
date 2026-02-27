"""Tests for the scan → triage → fix → PR pipeline."""
import json
from src.config import Config
from src.clients.github_client import GitHubClient
from src.clients.claude_client import ClaudeClient
from src.pr_engine.triager import PRTriager
from src.pr_engine.fix_generator import FixGenerator
from src.pr_engine.pr_creator import PRCreator


SCAN_FILE = "scan_camera-zone.json"
REPO_NAME = "camera-zone"


def _load_scan():
    with open(SCAN_FILE) as f:
        return json.load(f)


def test_triage_camera_zone():
    """Triage the cached scan result and verify the expected PR plans."""
    scan = _load_scan()
    triager = PRTriager()
    plans = triager.triage(scan)

    print("\n--- PR Plans ---")
    for p in plans:
        print(f"  [{p.priority}] {p.concern}: {p.title}")
        for fc in p.file_changes:
            print(f"       {fc.path} ({fc.change_type}): {fc.description}")

    # We expect at least an SDK bump and a deprecated-API migration
    concerns = {p.concern for p in plans}
    assert "sdk-version-bump" in concerns, f"Missing sdk-version-bump plan. Got: {concerns}"
    assert "migrate-deprecated-apis" in concerns, f"Missing migrate-deprecated-apis plan. Got: {concerns}"

    # SDK bump should target requirements.txt
    sdk_plan = next(p for p in plans if p.concern == "sdk-version-bump")
    assert any(fc.path == "requirements.txt" for fc in sdk_plan.file_changes)

    # Deprecated API plan should target zone.py
    api_plan = next(p for p in plans if p.concern == "migrate-deprecated-apis")
    assert any("zone.py" in fc.path for fc in api_plan.file_changes)

    # Priority ordering: SDK bump first
    assert sdk_plan.priority < api_plan.priority


def test_fix_generation():
    """Generate fixes for camera-zone and verify non-empty output."""
    config = Config()
    github = GitHubClient(config.github_token, config.github_org)
    claude = ClaudeClient(config.anthropic_api_key, config.anthropic_model)

    scan = _load_scan()
    triager = PRTriager()
    plans = triager.triage(scan)

    fix_gen = FixGenerator(claude, github)

    for plan in plans:
        print(f"\n--- Generating fixes for: {plan.concern} ---")
        fixes = fix_gen.generate_fixes(REPO_NAME, plan)

        assert len(fixes) > 0, f"No fixes generated for {plan.concern}"
        for path, content in fixes.items():
            print(f"  {path}: {len(content)} chars")
            assert len(content) > 0, f"Empty fix for {path}"


def test_full_pipeline():
    """End-to-end: scan → triage → fix → create PRs on camera-zone."""
    config = Config()
    github = GitHubClient(config.github_token, config.github_org)
    claude = ClaudeClient(config.anthropic_api_key, config.anthropic_model)

    # 1. Load scan
    scan = _load_scan()
    print(f"\nScan severity: {scan.get('severity')}")

    # 2. Triage
    triager = PRTriager()
    plans = triager.triage(scan)
    print(f"Plans: {len(plans)}")

    # 3. Generate fixes
    fix_gen = FixGenerator(claude, github)
    all_fixes = []
    for plan in plans:
        fixes = fix_gen.generate_fixes(REPO_NAME, plan)
        all_fixes.append((plan, fixes))

    # 4. Create PRs
    creator = PRCreator(github)
    results = []
    for plan, fixes in all_fixes:
        result = creator.create_pr(REPO_NAME, plan, fixes)
        results.append(result)
        print(f"\n  PR #{result['pr_number']}: {result['pr_url']}")

    assert len(results) == len(plans), "Not all plans got PRs"
    for r in results:
        assert r["status"] == "created"
        assert r["pr_url"].startswith("https://")


if __name__ == "__main__":
    test_triage_camera_zone()
