import re
from typing import List, Dict, Any

# Simple regex-based parser for JavaScript and TypeScript files.
# This prevents compilation errors with tree-sitter on Windows machines.
CLASS_PATTERN = re.compile(r'(?:export\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?')
FUNC_PATTERN = re.compile(r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)')
ARROW_FUNC_PATTERN = re.compile(r'(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>')
METHOD_PATTERN = re.compile(r'(?:async\s+)?(\w+)\s*\(([^)]*)\)\s*\{')
EXPRESS_ROUTE_PATTERN = re.compile(r'(?:app|router|route)\.(get|post|put|delete|patch|use)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]')

def parse_javascript_file(file_path: str) -> List[Dict[str, Any]]:
    """Regex-based symbol extractor for JS/TS to ensure zero-dependency local cross-platform operation."""
    symbols = []
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return []

    # Simple line-by-line scanning to find symbols and assign lines
    for line_num, line in enumerate(lines, 1):
        line_strip = line.strip()
        if not line_strip or line_strip.startswith("//") or line_strip.startswith("/*") or line_strip.startswith("*"):
            continue

        # 1. Express / NestJS Router Route matching
        route_match = EXPRESS_ROUTE_PATTERN.search(line_strip)
        if route_match:
            method, route_path = route_match.groups()
            symbols.append({
                "name": f"{method.upper()} {route_path}",
                "type": "route",
                "signature": f"[{method.upper()}] {route_path}",
                "docstring": "",
                "line_start": line_num,
                "line_end": line_num
            })
            continue

        # 2. Class Definitions
        class_match = CLASS_PATTERN.search(line_strip)
        if class_match:
            class_name = class_match.group(1)
            symbols.append({
                "name": class_name,
                "type": "class",
                "signature": f"class {class_name}",
                "docstring": "",
                "line_start": line_num,
                "line_end": line_num + 5 # fallback range
            })
            continue

        # 3. Standard Functions
        func_match = FUNC_PATTERN.search(line_strip)
        if func_match:
            name, args = func_match.groups()
            symbols.append({
                "name": name,
                "type": "function",
                "signature": f"function {name}({args.strip()})",
                "docstring": "",
                "line_start": line_num,
                "line_end": line_num + 5
            })
            continue

        # 4. Arrow Functions
        arrow_match = ARROW_FUNC_PATTERN.search(line_strip)
        if arrow_match:
            name, args = arrow_match.groups()
            symbols.append({
                "name": name,
                "type": "function",
                "signature": f"const {name} = ({args.strip()}) =>",
                "docstring": "",
                "line_start": line_num,
                "line_end": line_num + 5
            })
            continue

    return symbols
