"""Configuration loader for viam-module-monitor."""
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

class Config:
    """Application configuration."""
    
    def __init__(self, config_path="config.yaml"):
        load_dotenv()  # Load .env file
        
        with open(config_path, 'r') as f:
            self.data = yaml.safe_load(f)
    
    @property
    def github_token(self):
        """Get GitHub token from environment."""
        env_var = self.data['github']['token_env']
        token = os.getenv(env_var)
        if not token:
            raise ValueError(f"{env_var} not set in environment")
        return token
    
    @property
    def anthropic_api_key(self):
        """Get Anthropic API key from environment."""
        env_var = self.data['anthropic']['api_key_env']
        key = os.getenv(env_var)
        if not key:
            raise ValueError(f"{env_var} not set in environment")
        return key
    
    @property
    def anthropic_model(self):
        return self.data['anthropic']['model']
    
    @property
    def anthropic_max_tokens(self):
        return self.data['anthropic']['max_tokens']
    
    @property
    def github_org(self):
        return self.data['github']['org']
    
    @property
    def target_repos(self):
        return self.data['target_repos']
    
    def __repr__(self):
        return f"Config(org={self.github_org}, repos={len(self.target_repos)})"