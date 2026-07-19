import subprocess
from typing import List
from app.core.logging import logger

def list_git_branches(workspace_path: str) -> List[str]:
    """Runs git branch command locally to list project repository branch lines."""
    try:
        res = subprocess.run(
            ["git", "branch", "-a"],
            cwd=workspace_path,
            capture_output=True,
            text=True,
            timeout=5.0
        )
        if res.returncode == 0:
            lines = [line.replace("*", "").strip() for line in res.stdout.splitlines()]
            return [l for l in lines if l]
    except Exception as e:
        logger.warning(f"[GitBranches] Failed to query branches: {e}")
    return ["main"]
