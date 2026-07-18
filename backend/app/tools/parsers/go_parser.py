import re
from typing import List, Dict, Any

# Pattern matches for Go symbols
FUNC_PATTERN = re.compile(r'^func\s+(\w+)\s*\(([^)]*)\)\s*([^{]*)')
METHOD_PATTERN = re.compile(r'^func\s*\(\s*(\w+)\s*\*?(\w+)\s*\)\s*(\w+)\s*\(([^)]*)\)\s*([^{]*)')
STRUCT_PATTERN = re.compile(r'^type\s+(\w+)\s+struct')
INTERFACE_PATTERN = re.compile(r'^type\s+(\w+)\s+interface')
IMPORT_PATTERN = re.compile(r'^import\s+\(\s*([^)]*)\)', re.MULTILINE)

def parse_go_file(file_path: str) -> List[Dict[str, Any]]:
    """Parses a Go file and extracts package imports, structs, interfaces, functions, and methods."""
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

        # 1. Matches Method definitions, e.g. func (s *Store) Save(data string) error
        method_match = METHOD_PATTERN.search(line_strip)
        if method_match:
            recv_name, recv_type, method_name, args, ret_val = method_match.groups()
            sig = f"func ({recv_name} *{recv_type}) {method_name}({args.strip()}) {ret_val.strip()}"
            symbols.append({
                "name": f"{recv_type}.{method_name}",
                "type": "function",
                "signature": sig.strip(),
                "docstring": "",
                "line_start": line_num,
                "line_end": line_num + 5
            })
            continue

        # 2. Matches Standalone function definitions, e.g. func InitLogger()
        func_match = FUNC_PATTERN.search(line_strip)
        if func_match:
            func_name, args, ret_val = func_match.groups()
            sig = f"func {func_name}({args.strip()}) {ret_val.strip()}"
            symbols.append({
                "name": func_name,
                "type": "function",
                "signature": sig.strip(),
                "docstring": "",
                "line_start": line_num,
                "line_end": line_num + 5
            })
            continue

        # 3. Struct definition
        struct_match = STRUCT_PATTERN.search(line_strip)
        if struct_match:
            struct_name = struct_match.group(1)
            symbols.append({
                "name": struct_name,
                "type": "class",
                "signature": f"type {struct_name} struct",
                "docstring": "",
                "line_start": line_num,
                "line_end": line_num + 5
            })
            continue

        # 4. Interface definition
        interface_match = INTERFACE_PATTERN.search(line_strip)
        if interface_match:
            inf_name = interface_match.group(1)
            symbols.append({
                "name": inf_name,
                "type": "class",
                "signature": f"type {inf_name} interface",
                "docstring": "",
                "line_start": line_num,
                "line_end": line_num + 5
            })
            continue

    return symbols
