import os
import re

def search_files_by_keyword(file_paths: list[str], keyword: str, case_sensitive: bool = False) -> list[dict]:
    """Searches a list of file paths for occurrences of a keyword. Returns list of matches with file, line, and content."""
    matches = []
    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(re.escape(keyword), flags)

    for path in file_paths:
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line_num, line in enumerate(f, 1):
                    if pattern.search(line):
                        matches.append({
                            "file": path,
                            "line_num": line_num,
                            "line_content": line.strip()
                        })
        except Exception:
            # Skip unreadable files
            continue
            
    return matches
