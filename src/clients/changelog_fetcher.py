"""Viam changelog fetcher — downloads and extracts breaking changes."""
import re
import requests


class ChangelogFetcher:
    """Fetches the Viam changelog and extracts breaking-change / deprecation info."""

    CHANGELOG_URL = "https://docs.viam.com/dev/reference/changelog/"

    # Keywords that signal a breaking change or deprecation
    KEYWORDS = re.compile(
        r'(breaking|deprecated?|removed|renamed|replaced|migrat|incompatible)',
        re.IGNORECASE,
    )

    def __init__(self):
        self._cached_text = None

    def fetch_changelog(self):
        """
        Fetch the Viam changelog, strip HTML, and return relevant sections.

        The result is cached on the instance so repeated calls (e.g. across
        multiple modules in one run) do not re-fetch.

        Returns:
            str: Formatted text with breaking changes / deprecations.
        """
        if self._cached_text is not None:
            return self._cached_text

        print("  Fetching Viam changelog …")
        resp = requests.get(self.CHANGELOG_URL, timeout=30)
        resp.raise_for_status()

        raw_text = self._strip_html(resp.text)
        relevant = self._extract_relevant_lines(raw_text)
        self._cached_text = relevant
        return relevant

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _strip_html(html):
        """Crude HTML → plain-text conversion."""
        # Remove script/style blocks
        text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # Convert <br>, </p>, </div>, </li> to newlines
        text = re.sub(r'<br\s*/?>|</p>|</div>|</li>', '\n', text, flags=re.IGNORECASE)
        # Strip remaining tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Collapse whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        # Collapse blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _extract_relevant_lines(self, text):
        """Keep only paragraphs/lines that mention breaking changes or deprecations."""
        paragraphs = text.split('\n\n')
        relevant = []
        for para in paragraphs:
            if self.KEYWORDS.search(para):
                relevant.append(para.strip())

        if not relevant:
            return "(No breaking changes or deprecations found in changelog)"

        header = "=== Viam Changelog — Breaking Changes & Deprecations ===\n\n"
        return header + "\n\n---\n\n".join(relevant)
