"""Test complete module analysis."""
import json
from src.config import Config
from src.clients.github_client import GitHubClient
from src.clients.claude_client import ClaudeClient
from src.analyzers.file_finder import FileFinder
from src.analyzers.module_analyzer import ModuleAnalyzer

def test_full_module_analysis():
    """Test analyzing a complete module."""
    config = Config()
    
    # Setup
    github = GitHubClient(config.github_token, config.github_org)
    claude = ClaudeClient(config.anthropic_api_key, config.anthropic_model)
    finder = FileFinder(None)  # Will be created per-repo
    
    analyzer = ModuleAnalyzer(github, claude, finder)
    
    # Analyze first module
    repo_name = config.target_repos[0]
    report = analyzer.analyze_module(repo_name)
    
    # Display report
    print("\n" + "=" * 70)
    print(f"MODULE HEALTH REPORT: {report['module_name']}")
    print("=" * 70)
    print(f"\nOverall Status: {report['overall_status']}")
    print(f"Health Score: {report['health_score']}/100")
    print(f"Repository: {report['repository_url']}")
    
    print(f"\nViam Files:")
    print(f"  meta.json: {'Present' if report['viam_specific']['meta_json_present'] else 'MISSING'}")
    print(f"  README.md: {'Present' if report['viam_specific']['readme_present'] else 'MISSING'}")
    
    print(f"\nLanguage Analysis:")
    for lang, data in report['languages'].items():
        print(f"  {lang.upper()}: {data['status']} (Score: {data['health_score']}/100)")
        if data.get('viam_sdk_present'):
            print(f"    Viam SDK: {data['viam_sdk_version']}")
    
    if report['issues']:
        print(f"\nIssues ({len(report['issues'])}):")
        for issue in report['issues'][:5]:  # Show first 5
            print(f"  - {issue}")
        if len(report['issues']) > 5:
            print(f"  ... and {len(report['issues']) - 5} more")
    
    if report['recommendations']:
        print(f"\nRecommendations ({len(report['recommendations'])}):")
        for rec in report['recommendations'][:5]:  # Show first 5
            print(f"  - {rec}")
        if len(report['recommendations']) > 5:
            print(f"  ... and {len(report['recommendations']) - 5} more")
    
    print("\n" + "=" * 70)
    
    # Save report
    print(f"\nFull report saved to: report_{repo_name}.json")
    with open(f"report_{repo_name}.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

if __name__ == "__main__":
    test_full_module_analysis()