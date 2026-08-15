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

import tempfile

def _parse_javascript_file_regex(file_path: str) -> List[Dict[str, Any]]:
    """Safe Fallback: Regex-based line scanner for JS/TS symbols."""
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

def parse_javascript_files_batch(file_paths: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """Batch JS/TS Symbol Extractor: runs single Node.js subprocess pass for N files, then immediately unloads."""
    if not file_paths:
        return {}

    results: Dict[str, List[Dict[str, Any]]] = {fp: [] for fp in file_paths}
    parser_js_path = os.path.join(os.path.dirname(__file__), "ast_parser.js")

    # 1. Attempt single Node.js batch execution
    try:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json", encoding="utf-8") as tf:
            json.dump(file_paths, tf)
            temp_payload_path = tf.name

        try:
            cmd_res = subprocess.run(
                ["node", parser_js_path, f"--payload-file={temp_payload_path}"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if cmd_res.returncode == 0 and cmd_res.stdout.strip():
                parsed_dict = json.loads(cmd_res.stdout)
                if isinstance(parsed_dict, dict):
                    results.update(parsed_dict)
            else:
                logger.debug(f"AST batch parser process returned non-zero code: {cmd_res.stderr}")
        finally:
            if os.path.exists(temp_payload_path):
                try:
                    os.remove(temp_payload_path)
                except Exception:
                    pass
    except Exception as e:
        logger.debug(f"AST batch parser execution failed: {e}. Falling back to Regex scanner.")

    # 2. Fallback: Run safe regex parser for any missing/failed files
    for fp in file_paths:
        if not results.get(fp):
            results[fp] = _parse_javascript_file_regex(fp)

    return results

def parse_javascript_file(file_path: str) -> List[Dict[str, Any]]:
    """Hybrid JS/TS Symbol Extractor for a single file."""
    batch_results = parse_javascript_files_batch([file_path])
    return batch_results.get(file_path, [])

