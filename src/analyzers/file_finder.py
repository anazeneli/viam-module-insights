"""Find relevant files in a repository."""

class FileFinder:
    """Locate dependency and config files in a repo."""
    
    LANGUAGE_FILES = {
        'python': ['requirements.txt', 'pyproject.toml', 'setup.py'],
        'go': ['go.mod', 'go.sum'],
        'typescript': ['package.json', 'package-lock.json', 'yarn.lock']
    }
    
    VIAM_FILES = ['meta.json', 'README.md', '.viam', 'module.yaml']
    
    def __init__(self, github_repo):
        """
        Args:
            github_repo: PyGithub Repository object
        """
        self.repo = github_repo
    
    def find_files(self):
        """
        Find all relevant files using GitHub API (no cloning).
        
        Returns:
            dict: Categorized file objects
        """
        found = {
            'python': [],
            'go': [],
            'typescript': [],
            'viam': [],
            'readme': None
        }
        
        try:
            # Get all files in repo root
            contents = self.repo.get_contents("")
            
            for item in contents:
                filename = item.name
                
                # Check for README
                if filename.lower() == 'readme.md':
                    found['readme'] = item
                
                # Check for Viam files
                if filename in self.VIAM_FILES:
                    found['viam'].append(item)
                
                # Check for language-specific files
                for lang, patterns in self.LANGUAGE_FILES.items():
                    if filename in patterns:
                        found[lang].append(item)
            
            return found
            
        except Exception as e:
            print(f"Error finding files: {e}")
            return found
    
    def get_file_content(self, file_item):
        """
        Get content of a file from GitHub.
        
        Args:
            file_item: GitHub ContentFile object
            
        Returns:
            str: Decoded file content
        """
        try:
            return file_item.decoded_content.decode('utf-8')
        except Exception as e:
            print(f"Error reading {file_item.name}: {e}")
            return None