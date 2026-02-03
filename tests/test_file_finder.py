"""Test file discovery."""
from src.config import Config
from src.clients.github_client import GitHubClient
from src.analyzers.file_finder import FileFinder

def test_find_files():
    """Test finding files in a repo without cloning."""
    config = Config()
    client = GitHubClient(config.github_token, config.github_org)
    
    # Test with first repo
    repo_name = config.target_repos[0]
    print(f"\nAnalyzing: {repo_name}")
    
    repo = client.get_repo(repo_name)
    finder = FileFinder(repo)
    
    found = finder.find_files()
    
    # Display results
    print("\nFiles Found:")
    for lang, files in found.items():
        if lang == 'readme':
            if files:
                print(f"  [OK] README: {files.name}")
        elif files:
            print(f"  {lang.upper()}:")
            for f in files:
                print(f"    - {f.name}")
    
    # Try reading README
    if found['readme']:
        print("\nREADME Preview (first 200 chars):")
        content = finder.get_file_content(found['readme'])
        if content:
            print(f"{content[:200]}...")
    
    return found

if __name__ == "__main__":
    test_find_files()