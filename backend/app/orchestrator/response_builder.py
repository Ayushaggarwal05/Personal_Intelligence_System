import json
from typing import Dict, Any

class ResponseBuilder:
    """Formatter tool sanitizing raw agent response payloads."""
    def __init__(self):
        pass

    def build_structured_response(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Wraps answer string content in JSON payload schema format."""
        return {
            "success": True,
            "response": content,
            "metadata": metadata or {}
        }

    def safe_parse_json(self, raw_str: str) -> Dict[str, Any]:
        """Tries to strip code block markdown tags and parse JSON responses safely."""
        clean_str = raw_str.strip()
        if clean_str.startswith("```json"):
            clean_str = clean_str[7:]
        if clean_str.endswith("```"):
            clean_str = clean_str[:-3]
            
        try:
            return json.loads(clean_str.strip())
        except Exception:
            return {"raw_text": raw_str}
