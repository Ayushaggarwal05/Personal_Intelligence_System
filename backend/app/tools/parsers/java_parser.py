import re
from typing import List, Dict, Any

# Pattern matches for Java classes and methods
CLASS_PATTERN = re.compile(r'(?:public\s+|private\s+|protected\s+)?(?:static\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w\s,]+)?')
INTERFACE_PATTERN = re.compile(r'(?:public\s+)?interface\s+(\w+)')
METHOD_PATTERN = re.compile(r'(?:public|private|protected|static|final|synchronized|\s)+(?:[\w<>\\[\]]+)\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+[\w\s,]+)?\s*\{')

def parse_java_file(file_path: str) -> List[Dict[str, Any]]:
    """Parses a Java file recursively and extracts classes, interfaces, and methods."""
    symbols = []
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return []

    for line_num, line in enumerate(lines, 1):
        line_strip = line.strip()
        if not line_strip or line_strip.startswith("//") or line_strip.startswith("/*") or line_strip.startswith("*"):
            continue

        # 1. Matches Class Definitions
        class_match = CLASS_PATTERN.search(line_strip)
        if class_match:
            class_name = class_match.group(1)
            symbols.append({
                "name": class_name,
                "type": "class",
                "signature": f"class {class_name}",
                "docstring": "",
                "line_start": line_num,
                "line_end": line_num + 10 # default visual scope
            })
            continue

        # 2. Matches Interface Definitions
        interface_match = INTERFACE_PATTERN.search(line_strip)
        if interface_match:
            inf_name = interface_match.group(1)
            symbols.append({
                "name": inf_name,
                "type": "class",
                "signature": f"interface {inf_name}",
                "docstring": "",
                "line_start": line_num,
                "line_end": line_num + 10
            })
            continue

        # 3. Matches Method Definitions
        method_match = METHOD_PATTERN.search(line_strip)
        if method_match:
            method_name, args = method_match.groups()
            # Filter out language keywords that match method structures (e.g. if, for, while, switch)
            if method_name in {"if", "for", "while", "switch", "catch", "try"}:
                continue
            symbols.append({
                "name": method_name,
                "type": "function",
                "signature": f"{method_name}({args.strip()})",
                "docstring": "",
                "line_start": line_num,
                "line_end": line_num + 5
            })
            continue

    return symbols
