"""Anthropic Claude API client."""
import json
from anthropic import Anthropic

class ClaudeClient:
    """Wrapper for Claude API."""
    
    def __init__(self, api_key, model="claude-sonnet-4-20250514"):
        self.client = Anthropic(api_key=api_key)
        self.model = model
    
    def analyze_dependency_file(self, module_name, language, filename, file_contents):
        """
        Analyze a dependency file and return health assessment.
        
        Returns:
            dict: Parsed JSON with status, score, issues, and recommendations
        """
        prompt = f"""You are analyzing a Viam module for health and compliance. Follow the standards in VIAM_MODULE_HEALTH_CHECKER.md.

Module: {module_name}
Language: {language}
File: {filename}

File Contents:
{file_contents}

Analyze this dependency file and provide:
1. Overall Status: GREEN (80-100), YELLOW (50-79), or RED (<50)
2. Health Score: 0-100 based on:
   - Version pinning (-10 per unpinned dependency)
   - Dependency age (if >6 months: -5 each, if >12 months: -15 each)
   - Viam SDK present and pinned (+0 baseline, -30 if missing)
3. Specific issues found
4. Actionable recommendations with exact version pins

Respond with ONLY raw JSON, no markdown formatting, no code fences:
{{
  "status": "GREEN|YELLOW|RED",
  "health_score": 0-100,
  "issues": ["issue 1", "issue 2"],
  "recommendations": ["rec 1", "rec 2"],
  "viam_sdk_present": true/false,
  "viam_sdk_version": "version or null"
}}"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text.strip()

        # Remove markdown code fences if present
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            response_text = '\n'.join(lines).strip()

        # Parse and return JSON
        return json.loads(response_text)
