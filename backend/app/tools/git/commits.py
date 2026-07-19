import subprocess
from typing import List
from app.core.logging import logger

def list_recent_git_commits(workspace_path: str, limit: int = 10) -> List[str]:
    """Runs git log command locally to fetch a list of recent commit messages hashes."""
    try:
        res = subprocess.run(
            ["git", "log", f"-n", str(limit), "--oneline"],
            cwd=workspace_path,
            capture_output=True,
            text=True,
            timeout=5.0
        )
        if res.returncode == 0:
            lines = [line.strip() for line in res.stdout.splitlines()]
            return [l for l in lines if l]
    except Exception as e:
        logger.warning(f"[GitCommits] Failed to query commit log: {e}")
    return ["Initial commit placeholder"]
