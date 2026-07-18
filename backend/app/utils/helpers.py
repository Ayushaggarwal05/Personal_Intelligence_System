import hashlib
import time
import json
from typing import Any

def calculate_sha256(content: str) -> str:
    """Computes the SHA-256 hash of a string content."""
    sha256 = hashlib.sha256()
    sha256.update(content.encode("utf-8"))
    return sha256.hexdigest()

def get_utc_now() -> int:
    """Returns the current Unix timestamp (UTC seconds)."""
    return int(time.time())

def format_bytes(size: int) -> str:
    """Converts bytes to a human-readable file size format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def json_safe_dumps(data: Any) -> str:
    """Safely dumps data into a JSON string, handling parsing issues gracefully."""
    try:
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        # Fallback raw string representation
        return json.dumps(str(data))
