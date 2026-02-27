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

    def analyze_code_scan(self, module_name, source_files, changelog_text, latest_sdk_version=None):
        """
        Analyze a module's source code against the Viam changelog.

        Args:
            module_name: Name of the module being scanned.
            source_files: list[dict] from CodeScanner (path, content, size).
            changelog_text: Formatted changelog text from ChangelogFetcher.
            latest_sdk_version: Latest stable viam-sdk version from PyPI (optional).

        Returns:
            dict: Structured analysis with breaking_changes, deprecation_warnings, etc.
        """
        formatted_sources = self._format_source_files(source_files)

        sdk_version_hint = ""
        if latest_sdk_version:
            sdk_version_hint = f"\n\nIMPORTANT: The latest stable viam-sdk version on PyPI is {latest_sdk_version}. Use this as the latest_recommended value in sdk_version_info. Do NOT recommend pre-release or beta versions."

        prompt = f"""You are a Viam module compatibility analyzer. You have two inputs:

1. The SOURCE CODE of a Viam module called "{module_name}"
2. The Viam SDK CHANGELOG containing breaking changes and deprecations

Your job: find every place where the source code uses an API that the changelog says is deprecated, removed, or replaced.

IMPORTANT INSTRUCTIONS:
- For EVERY function/method defined or called in the source code, check if the changelog mentions it as deprecated or replaced.
- Pay special attention to method names that match changelog entries (e.g. if the changelog says "GetImages replaced GetImage", then any definition or call of get_image is a deprecation).
- Report BOTH method definitions (async def get_image) AND call sites (await camera.get_image()) as separate issues.
- set can_build_with_latest_sdk to false if ANY deprecated/removed API is used.

=== SOURCE CODE ===
{formatted_sources}

=== CHANGELOG (breaking changes & deprecations only) ===
{changelog_text}

For every issue found, cite:
- The specific file and line number(s)
- The deprecated/removed API call
- What it should be replaced with

Respond with ONLY raw JSON, no markdown formatting, no code fences:
{{
  "can_build_with_latest_sdk": true/false,
  "severity": "none|low|medium|high|critical",
  "breaking_changes": [
    {{
      "file": "path/to/file.py",
      "line": 42,
      "description": "what is broken",
      "current_usage": "the deprecated call",
      "replacement": "what to use instead"
    }}
  ],
  "deprecation_warnings": [
    {{
      "file": "path/to/file.py",
      "line": 10,
      "description": "what is deprecated",
      "current_usage": "the deprecated call",
      "replacement": "what to use instead"
    }}
  ],
  "sdk_version_info": {{
    "detected_sdk": "package name or null",
    "detected_version": "version string or null",
    "latest_recommended": "latest stable version (not pre-release/beta) or null"
  }},
  "summary": "1-2 sentence summary of findings"
}}{sdk_version_hint}"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
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

        return json.loads(response_text)

    def generate_code_fix(self, repo_name, file_path, current_content, issues, concern):
        """Ask Claude to produce a fixed version of a source file.

        Args:
            repo_name: Module repository name (for context).
            file_path: Path of the file being fixed.
            current_content: Current file content.
            issues: list[dict] — each has ``description``, ``current_usage``, ``replacement``.
            concern: High-level concern label (e.g. ``migrate-deprecated-apis``).

        Returns:
            str: The complete fixed file content.
        """
        issues_text = "\n".join(
            f"- {i['description']}: replace `{i['current_usage']}` with `{i['replacement']}`"
            for i in issues
        )

        prompt = f"""You are fixing a file in the Viam module "{repo_name}".

Concern: {concern}
File: {file_path}

Issues to fix:
{issues_text}

Current file content:
{current_content}

Return ONLY the complete fixed file content. Do not wrap in code fences.
Make minimal changes — fix only what the issues describe. Preserve formatting, comments, and all unrelated code exactly as-is."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text.strip()

        # Strip code fences if the model adds them
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            response_text = "\n".join(lines)

        return response_text

    @staticmethod
    def _format_source_files(source_files):
        """Format source files with line numbers for the prompt."""
        parts = []
        for f in source_files:
            numbered_lines = []
            for i, line in enumerate(f['content'].splitlines(), start=1):
                numbered_lines.append(f"{i:4d} | {line}")
            numbered = '\n'.join(numbered_lines)
            parts.append(f"--- {f['path']} ({f['size']} chars) ---\n{numbered}")
        return '\n\n'.join(parts)
