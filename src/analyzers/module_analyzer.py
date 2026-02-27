"""Complete module health analyzer."""
from datetime import datetime

class ModuleAnalyzer:
    """Orchestrates full module health analysis."""
    
    def __init__(self, github_client, claude_client, file_finder):
        self.github = github_client
        self.claude = claude_client
        self.finder = file_finder
    
    def analyze_module(self, repo_name):
        """
        Run complete health analysis on a module.
        
        Args:
            repo_name: Name of the repository
            
        Returns:
            dict: Complete health report
        """
        print(f"\nAnalyzing module: {repo_name}")
        
        # Get repo
        repo = self.github.get_repo(repo_name)
        
        # Find all files
        found_files = self.finder.__class__(repo).find_files()
        
        # Initialize report
        report = {
            "module_name": repo_name,
            "repository_url": repo.html_url,
            "last_checked": datetime.now().isoformat(),
            "overall_status": "UNKNOWN",
            "health_score": 0,
            "languages": {},
            "viam_specific": {
                "meta_json_present": False,
                "readme_present": False
            },
            "issues": [],
            "recommendations": []
        }
        
        # Analyze dependencies for each language
        for lang in ['python', 'go', 'typescript']:
            if found_files[lang]:
                lang_analysis = self._analyze_language_dependencies(
                    repo_name, lang, found_files[lang], self.finder.__class__(repo)
                )
                if lang_analysis:
                    report['languages'][lang] = lang_analysis
        
        # Check for Viam-specific files
        report['viam_specific']['meta_json_present'] = any(
            f.name == 'meta.json' for f in found_files['viam']
        )
        report['viam_specific']['readme_present'] = found_files['readme'] is not None
        
        # Calculate overall status
        self._calculate_overall_status(report)
        
        return report
    
    def _analyze_language_dependencies(self, module_name, language, files, finder):
        """Analyze dependency files for a specific language."""
        if not files:
            return None
        
        # Use first dependency file found
        dep_file = files[0]
        print(f"  Analyzing {language}: {dep_file.name}")
        
        content = finder.get_file_content(dep_file)
        if not content:
            return None
        
        # Get Claude analysis (returns dict directly)
        analysis = self.claude.analyze_dependency_file(
            module_name=module_name,
            language=language,
            filename=dep_file.name,
            file_contents=content
        )

        if not analysis:
            return None

        return {
            "status": analysis['status'],
            "health_score": analysis['health_score'],
            "files_analyzed": [dep_file.name],
            "issues": analysis['issues'],
            "recommendations": analysis['recommendations'],
            "viam_sdk_present": analysis.get('viam_sdk_present', False),
            "viam_sdk_version": analysis.get('viam_sdk_version')
        }
    
    def _calculate_overall_status(self, report):
        """Calculate overall module status from language analyses."""
        # Collect all language scores
        scores = []
        statuses = []
        
        for lang_data in report['languages'].values():
            scores.append(lang_data['health_score'])
            statuses.append(lang_data['status'])
            report['issues'].extend(lang_data['issues'])
            report['recommendations'].extend(lang_data['recommendations'])
        
        if scores:
            # Average health score
            report['health_score'] = sum(scores) // len(scores)
            
            # Overall status: worst status wins
            if 'RED' in statuses:
                report['overall_status'] = 'RED'
            elif 'YELLOW' in statuses:
                report['overall_status'] = 'YELLOW'
            else:
                report['overall_status'] = 'GREEN'
        
        # Penalize missing critical files
        if not report['viam_specific']['meta_json_present']:
            report['issues'].append("Missing meta.json file")
            report['overall_status'] = 'RED'
            report['health_score'] = min(report['health_score'], 40)
        
        if not report['viam_specific']['readme_present']:
            report['issues'].append("Missing README.md file")
            if report['overall_status'] == 'GREEN':
                report['overall_status'] = 'YELLOW'