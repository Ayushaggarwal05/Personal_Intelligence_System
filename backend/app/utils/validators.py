from app.core.security import is_safe_path

def validate_safe_workspace_path(base_dir: str, target_path: str) -> bool:
    """Validates that a path is safe and inside boundaries."""
    return is_safe_path(base_dir, target_path)
