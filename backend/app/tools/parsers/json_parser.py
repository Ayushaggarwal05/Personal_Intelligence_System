import json
from typing import Dict, Any, Optional
from app.core.logging import logger

def parse_json_file_content(file_path: str) -> Optional[Dict[str, Any]]:
    """Loads and returns JSON dictionary objects from text config files safely."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"[JSONParser] Failed to parse JSON file {file_path}: {e}")
        return None
