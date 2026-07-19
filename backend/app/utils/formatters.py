from app.utils.helpers import format_bytes, json_safe_dumps

def format_file_size(size_bytes: int) -> str:
    """Format bytes size to human-readable text."""
    return format_bytes(size_bytes)

def format_json_string(data: any) -> str:
    """Safely dumps variables to JSON string format."""
    return json_safe_dumps(data)
