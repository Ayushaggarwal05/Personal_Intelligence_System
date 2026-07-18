import os
import re
from typing import List, Optional

class IgnoreMatcher:
    def __init__(self, base_path: str, patterns: List[str]):
        self.base_path = os.path.abspath(base_path)
        self.regexes = []
        for pat in patterns:
            regex = self._pattern_to_regex(pat)
            if regex:
                self.regexes.append(regex)

    def _pattern_to_regex(self, pattern: str) -> Optional[re.Pattern]:
        pattern = pattern.strip()
        if not pattern or pattern.startswith("#"):
            return None

        # Clean gitignore negation (we treat normal matches for simplicity)
        if pattern.startswith("!"):
            pattern = pattern[1:]

        # Handle directory-only rules (trailing slash)
        is_dir_only = pattern.endswith("/")
        if is_dir_only:
            pattern = pattern[:-1]

        # Escape special regex chars except glob operators
        regex_parts = []
        i = 0
        n = len(pattern)
        
        # Check if matched relative to root or anywhere
        if pattern.startswith("/"):
            regex_parts.append("^")
            pattern = pattern[1:]
        elif "/" not in pattern:
            # Match in any directory level
            regex_parts.append("(^|/)")
        else:
            regex_parts.append("^")

        while i < n:
            char = pattern[i]
            if char == "*":
                if i + 1 < n and pattern[i + 1] == "*":
                    regex_parts.append(".*")
                    i += 2
                    # Consume any trailing slash after double asterisk
                    if i < n and pattern[i] == "/":
                        i += 1
                else:
                    regex_parts.append("[^/]*")
                    i += 1
            elif char == "?":
                regex_parts.append("[^/]")
                i += 1
            elif char in {".", "+", "^", "$", "(", ")", "[", "]", "{", "}", "|", "\\"}:
                regex_parts.append("\\" + char)
                i += 1
            else:
                regex_parts.append(char)
                i += 1

        if is_dir_only:
            regex_parts.append("($|/)")
        else:
            regex_parts.append("($|/)")

        try:
            return re.compile("".join(regex_parts))
        except re.error:
            return None

    def should_ignore(self, file_path: str) -> bool:
        """Returns True if the file path matches any compiled ignore regex rules."""
        abs_path = os.path.abspath(file_path)
        rel_path = os.path.relpath(abs_path, self.base_path).replace(os.sep, "/")
        
        # Force directories comparison matching format
        for regex in self.regexes:
            if regex.search(rel_path):
                return True
        return False


def load_gitignore_matcher(workspace_path: str, custom_rules: List[str] = None) -> IgnoreMatcher:
    """Reads .gitignore and merges custom ignore rules, yielding a consolidated ignore matcher."""
    patterns = []
    
    # 1. Load from workspace .gitignore
    gitignore_path = os.path.join(workspace_path, ".gitignore")
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
                patterns.extend(f.readlines())
        except Exception:
            pass

    # 2. Append custom rules
    if custom_rules:
        patterns.extend(custom_rules)
        
    return IgnoreMatcher(workspace_path, patterns)
