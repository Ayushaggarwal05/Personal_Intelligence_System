import re
import os
import subprocess
import json
from typing import List, Dict, Any
from app.core.logging import logger

CLASS_PATTERN = re.compile(r'(?:export\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?')
FUNC_PATTERN = re.compile(r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)')
ARROW_FUNC_PATTERN = re.compile(r'(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>')
EXPRESS_ROUTE_PATTERN = re.compile(r'(?:app|router|route)\.(get|post|put|delete|patch|use)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]')

def parse_javascript_file(file_path: str) -> List[Dict[str, Any]]:
    """Hybrid JS/TS Symbol Extractor: uses Node-based AST parser with automatic safe Regex fallback."""
    # 1. Attempt AST-based parsing via Node.js helper
    try:
        parser_js_path = os.path.join(os.path.dirname(__file__), "ast_parser.js")
        
        # Check if node is available on system command line
        result = subprocess.run(
            ["node", parser_js_path, file_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            parsed_symbols = json.loads(result.stdout)
            if parsed_symbols:
                return parsed_symbols
        else:
            logger.debug(f"AST parser subprocess returned non-zero code for {file_path}: {result.stderr}")
    except Exception as e:
        logger.debug(f"AST parser execution failed for {file_path}: {e}. Falling back to Regex scanner.")

    # 2. Safe Fallback: Regex-based line scanner
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

        # Express / NestJS Router Route matching
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

        # Class Definitions
        class_match = CLASS_PATTERN.search(line_strip)
        if class_match:
            class_name = class_match.group(1)
            symbols.append({
                "name": class_name,
                "type": "class",
                "signature": f"class {class_name}",
                "docstring": "",
                "line_start": line_num,
                "line_end": line_num + 5
            })
            continue

        # Standard Functions
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

        # Arrow Functions
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
