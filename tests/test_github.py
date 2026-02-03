"""Test GitHub connectivity."""
from src.config import Config
from src.clients.github_client import GitHubClient

def test_github_connection():
    """Test that we can connect to GitHub and fetch repos."""
    config = Config()
    client = GitHubClient(config.github_token, config.github_org)
    
    # Test with first repo only
    repo_name = config.target_repos[0]
    print(f"\nTesting GitHub connection with: {repo_name}")
    
    try:
        repo = client.get_repo(repo_name)
        info = client.get_repo_info(repo)
        
        print(f"[OK] Repository: {info['full_name']}")
        print(f"  Language: {info['language']}")
        print(f"  URL: {info['url']}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

if __name__ == "__main__":
    test_github_connection()