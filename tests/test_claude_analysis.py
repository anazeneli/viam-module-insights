"""Test Claude analysis on real repo files."""
import json
from src.config import Config
from src.clients.github_client import GitHubClient
from src.clients.claude_client import ClaudeClient
from src.analyzers.file_finder import FileFinder

def test_analyze_dependencies():
    """Test Claude analyzing a real dependency file."""
    config = Config()
    
    # Setup clients
    github = GitHubClient(config.github_token, config.github_org)
    claude = ClaudeClient(config.anthropic_api_key, config.anthropic_model)
    
    # Get repo
    repo_name = "camera-zone"  # Python module
    print(f"\nAnalyzing: {repo_name}")
    
    repo = github.get_repo(repo_name)
    finder = FileFinder(repo)
    found = finder.find_files()
    
    # Analyze Python requirements
    if found['python']:
        req_file = found['python'][0]
        print(f"\nFound: {req_file.name}")
        
        content = finder.get_file_content(req_file)
        if content:
            print(f"\nDependencies:\n{content}\n")
            
            print("Claude's Analysis:")
            print("-" * 60)
            
            analysis_json = claude.analyze_dependency_file(
                module_name=repo_name,
                language='python',
                filename=req_file.name,
                file_contents=content
            )
            
            # Parse JSON response
            try:
                analysis = json.loads(analysis_json)
                
                # Display status
                print(f"\nStatus: {analysis['status']}")
                print(f"Health Score: {analysis['health_score']}/100")
                print(f"Viam SDK: {'[OK]' if analysis['viam_sdk_present'] else '[MISSING]'} {analysis.get('viam_sdk_version', 'Not found')}")
                
                if analysis['issues']:
                    print(f"\nIssues ({len(analysis['issues'])}):")
                    for issue in analysis['issues']:
                        print(f"  - {issue}")
                
                if analysis['recommendations']:
                    print("\nRecommendations:")
                    for rec in analysis['recommendations']:
                        print(f"  - {rec}")
                
            except json.JSONDecodeError:
                print("Error parsing JSON response:")
                print(analysis_json)
            
            print("-" * 60)
    
    return True

if __name__ == "__main__":
    test_analyze_dependencies()