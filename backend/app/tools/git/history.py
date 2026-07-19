import subprocess
from app.core.logging import logger

def get_git_history_diff_stats(workspace_path: str) -> str:
    """Runs git log stat summaries command locally to extract file modification history metrics."""
    try:
        res = subprocess.run(
            ["git", "log", "-n", "5", "--stat"],
            cwd=workspace_path,
            capture_output=True,
            text=True,
            timeout=5.0
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception as e:
        logger.warning(f"[GitHistory] Failed to query git history stats: {e}")
    return "No git revision history details found."

def get_git_diff_patch(workspace_path: str, count: int = 1) -> str:
    """Runs git show command locally to extract exact diff patch snippets of recent changes."""
    try:
        res = subprocess.run(
            ["git", "show", f"-{count}"],
            cwd=workspace_path,
            capture_output=True,
            text=True,
            timeout=5.0
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception as e:
        logger.warning(f"[GitHistory] Failed to query git diff patches: {e}")
    return "No recent git modifications detected."
