import os
from app.core.logging import logger

def is_safe_path(base_dir: str, target_path: str) -> bool:
    """Verifies that the target path resolves within the boundaries of the base directory (injection protection)."""
    try:
        abs_base = os.path.abspath(base_dir)
        abs_target = os.path.abspath(target_path)
        
        # Verify target is nested within base
        return os.path.commonpath([abs_base, abs_target]) == abs_base
    except Exception as e:
        logger.error(f"[Security] Failed to validate path safety: {e}")
        return False
