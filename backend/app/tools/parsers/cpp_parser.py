import re
from typing import List, Dict, Any

# Pattern matches for C++ symbols
CLASS_PATTERN = re.compile(r'(?:class|struct)\s+(\w+)(?:\s*:\s*(?:public|private|protected)?\s*\w+)?')
NAMESPACE_PATTERN = re.compile(r'namespace\s+(\w+)')
FUNC_PATTERN = re.compile(r'(?:[\w::<>*&]+)\s+(\w+)\s*\(([^)]*)\)\s*(?:const)?\s*\{')

def parse_cpp_file(file_path: str) -> List[Dict[str, Any]]:
    """Parses a C++ source/header file and extracts classes, structs, namespaces, and functions."""
    symbols = []
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return []

    for line_num, line in enumerate(lines, 1):
        line_strip = line.strip()
        if not line_strip or line_strip.startswith("//") or line_strip.startswith("/*") or line_strip.startswith("*") or line_strip.startswith("#"):
            continue

        # 1. Matches Namespace
        namespace_match = NAMESPACE_PATTERN.search(line_strip)
        if namespace_match:
            ns_name = namespace_match.group(1)
            symbols.append({
                "name": ns_name,
                "type": "class",
                "signature": f"namespace {ns_name}",
                "docstring": "",
                "line_start": line_num,
                "line_end": line_num + 10
            })
            continue

        # 2. Matches Class/Struct
        class_match = CLASS_PATTERN.search(line_strip)
        if class_match:
            class_name = class_match.group(1)
            symbols.append({
                "name": class_name,
                "type": "class",
                "signature": f"class {class_name}",
                "docstring": "",
                "line_start": line_num,
                "line_end": line_num + 10
            })
            continue

        # 3. Matches Functions/Methods
        func_match = FUNC_PATTERN.search(line_strip)
        if func_match:
            func_name, args = func_match.groups()
            # Ignore language control blocks
            if func_name in {"if", "for", "while", "switch", "catch", "try", "switch"}:
                continue
            symbols.append({
                "name": func_name,
                "type": "function",
                "signature": f"{func_name}({args.strip()})",
                "docstring": "",
                "line_start": line_num,
                "line_end": line_num + 5
            })
            continue

    return symbols
