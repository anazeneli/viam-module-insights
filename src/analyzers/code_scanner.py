"""Recursive source code reader for GitHub repositories."""

class CodeScanner:
    """Reads all source files from a GitHub repo via the API."""

    SOURCE_EXTENSIONS = (
        '.py', '.go', '.ts', '.js', '.json', '.md', '.sh',
        '.yaml', '.yml', '.toml', '.cfg', '.txt', '.mod', '.sum',
    )

    SKIP_DIRS = {
        'vendor', 'node_modules', '__pycache__', 'venv', '.venv',
        'env', '.git', 'dist', 'build', '.eggs', '.tox',
        '.mypy_cache', '.pytest_cache', 'htmlcov',
    }

    MAX_TOTAL_CHARS = 150_000
    MAX_FILE_BYTES = 50 * 1024  # 50KB per file

    def __init__(self, github_repo):
        """
        Args:
            github_repo: PyGithub Repository object
        """
        self.repo = github_repo

    def scan_repo(self):
        """
        Recursively read all source files from the repo.

        Returns:
            list[dict]: Each dict has 'path', 'content', 'size'.
        """
        files = []
        total_chars = 0
        self._walk("", files, total_chars)
        return files

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _walk(self, path, files, total_chars):
        """Recursively walk the repo tree, collecting source files."""
        try:
            contents = self.repo.get_contents(path)
        except Exception as e:
            print(f"  Warning: could not read {path or '/'}: {e}")
            return total_chars

        for item in contents:
            if total_chars >= self.MAX_TOTAL_CHARS:
                break

            if item.type == "dir":
                if item.name in self.SKIP_DIRS:
                    continue
                total_chars = self._walk(item.path, files, total_chars)

            elif item.type == "file":
                if not self._is_source_file(item.name):
                    continue
                if item.size > self.MAX_FILE_BYTES:
                    print(f"  Skipping {item.path} ({item.size} bytes > {self.MAX_FILE_BYTES} limit)")
                    continue

                content = self._read_file(item)
                if content is None:
                    continue

                if total_chars + len(content) > self.MAX_TOTAL_CHARS:
                    print(f"  Stopping scan: total char limit reached at {item.path}")
                    break

                files.append({
                    "path": item.path,
                    "content": content,
                    "size": len(content),
                })
                total_chars += len(content)

        return total_chars

    def _is_source_file(self, filename):
        """Check if a file has a recognized source extension."""
        return any(filename.endswith(ext) for ext in self.SOURCE_EXTENSIONS)

    def _read_file(self, file_item):
        """Read and decode a single file from GitHub."""
        try:
            return file_item.decoded_content.decode('utf-8')
        except Exception as e:
            print(f"  Warning: could not decode {file_item.path}: {e}")
            return None
