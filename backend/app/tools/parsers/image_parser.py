import os
from typing import Dict, Any

def parse_image_file_metadata(file_path: str) -> Dict[str, Any]:
    """Extracts basic image sizing and formatting metadata without compiling heavy image processors."""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    size_bytes = 0
    if os.path.exists(file_path):
        try:
            size_bytes = os.path.getsize(file_path)
        except Exception:
            pass
            
    return {
        "file_name": os.path.basename(file_path),
        "extension": ext,
        "size_bytes": size_bytes,
        "type": "image"
    }
