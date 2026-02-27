#!/usr/bin/env python3
"""CLI entry point: scan → triage → fix → PR pipeline."""
import argparse
import json
import sys

from src.config import Config
from src.clients.github_client import GitHubClient
from src.clients.claude_client import ClaudeClient
from src.clients.changelog_fetcher import ChangelogFetcher
from src.analyzers.scan_analyzer import ScanAnalyzer
from src.pr_engine.triager import PRTriager
from src.pr_engine.fix_generator import FixGenerator
from src.pr_engine.pr_creator import PRCreator


def run_pipeline(repo_name: str, *, dry_run: bool = False, scan_only: bool = False):
    """Execute the full scan → triage → fix → PR pipeline."""
    config = Config()
    github = GitHubClient(config.github_token, config.github_org)
    claude = ClaudeClient(config.anthropic_api_key, model=config.anthropic_model)
    changelog = ChangelogFetcher()

    # --- Phase 1: Scan ---
    scan_file = f"scan_{repo_name}.json"
    print(f"\n[1/4] SCAN")
    try:
        with open(scan_file) as f:
            scan_result = json.load(f)
        print(f"  Loaded cached scan from {scan_file}")
    except FileNotFoundError:
        analyzer = ScanAnalyzer(github, claude, changelog)
        scan_result = analyzer.scan_module(repo_name)
        with open(scan_file, "w") as f:
            json.dump(scan_result, f, indent=2)
        print(f"  Saved scan to {scan_file}")

    if scan_only:
        print(json.dumps(scan_result, indent=2))
        return

    # --- Phase 2: Triage ---
    print(f"\n[2/4] TRIAGE")
    triager = PRTriager()
    plans = triager.triage(scan_result)
    print(f"  {len(plans)} PR plan(s) created:")
    for plan in plans:
        print(f"    - [{plan.concern}] {plan.title}")
        for fc in plan.file_changes:
            print(f"        {fc.path}: {fc.description}")

    if dry_run:
        print("\n  --dry-run: stopping before fix generation.")
        return

    # --- Phase 3: Generate fixes ---
    print(f"\n[3/4] GENERATE FIXES")
    fix_gen = FixGenerator(claude, github)
    all_fixes: list[tuple] = []   # (plan, fixes_dict)
    for plan in plans:
        print(f"  Plan: {plan.concern}")
        fixes = fix_gen.generate_fixes(repo_name, plan)
        all_fixes.append((plan, fixes))
        print(f"    {len(fixes)} file(s) fixed")

    # --- Phase 4: Create PRs ---
    print(f"\n[4/4] CREATE PRs")
    creator = PRCreator(github)
    results = []
    for plan, fixes in all_fixes:
        print(f"  PR: {plan.title}")
        result = creator.create_pr(repo_name, plan, fixes)
        results.append(result)
        print(f"    ✓ {result['pr_url']}")

    # --- Summary ---
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print("=" * 60)
    for r in results:
        print(f"  PR #{r['pr_number']}: {r['pr_url']}")
        print(f"    Branch: {r['branch_name']}")
        print(f"    Files:  {', '.join(r['files_changed'])}")


def main():
    parser = argparse.ArgumentParser(
        description="Viam Module Insights — scan, triage, fix, PR pipeline",
    )
    parser.add_argument("repo", help="Target repository name (e.g. camera-zone)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and triage only — do not generate fixes or create PRs",
    )
    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="Run the scan and print results — do not triage or create PRs",
    )
    args = parser.parse_args()
    run_pipeline(args.repo, dry_run=args.dry_run, scan_only=args.scan_only)


if __name__ == "__main__":
    main()
