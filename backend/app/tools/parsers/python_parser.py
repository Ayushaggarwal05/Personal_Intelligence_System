import ast
from typing import List, Dict, Any

def parse_python_file(file_path: str) -> List[Dict[str, Any]]:
    """Parses a Python file using standard AST and extracts classes, functions, routes, and models."""
    symbols = []
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code_content = f.read()
            
        tree = ast.parse(code_content, filename=file_path)
    except Exception as e:
        # If parsing syntax error occurs, return empty list (will be logged by caller)
        return []

    # Utility helper to format arguments signature
    def get_function_signature(node: Any) -> str:
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        if node.args.kwonlyargs:
            args.append("*")
            for arg in node.args.kwonlyargs:
                args.append(arg.arg)
        prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
        return f"{prefix} {node.name}({', '.join(args)})"

    # Utility helper to check if node has a router/app decorator (FastAPI routes)
    def check_is_route(node: Any) -> bool:
        for decorator in node.decorator_list:
            # Check for standard Call decorators like @app.get("/...")
            if isinstance(decorator, ast.Call):
                func = decorator.func
                # Handles node decorator like app.get or router.post
                if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                    if func.attr in {"get", "post", "put", "delete", "patch", "options", "head"}:
                        return True
            # Check for Name decorators (less common for routes but possible)
            elif isinstance(decorator, ast.Attribute):
                if decorator.attr in {"get", "post", "put", "delete", "patch"}:
                    return True
        return False

    # Utility helper to check if class is a Database Model or Schema
    def get_class_type(node: ast.ClassDef) -> str:
        # Check bases (inheritance)
        for base in node.bases:
            # e.g., Base or BaseModel
            if isinstance(base, ast.Name):
                if base.id in {"Base", "BaseModel"}:
                    return "model"
            # e.g., declarative_base class, or schemas.BaseModel
            elif isinstance(base, ast.Attribute):
                if base.attr in {"BaseModel", "Base"}:
                    return "model"
        return "class"

    for node in ast.walk(tree):
        # 1. Parse Classes
        if isinstance(node, ast.ClassDef):
            class_type = get_class_type(node)
            docstring = ast.get_docstring(node)
            symbols.append({
                "name": node.name,
                "type": class_type,
                "signature": f"class {node.name}",
                "docstring": docstring or "",
                "line_start": node.lineno,
                "line_end": getattr(node, "end_lineno", node.lineno)
            })
            
        # 2. Parse Functions/Methods
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            is_route = check_is_route(node)
            symbol_type = "route" if is_route else "function"
            
            # Reconstruct route signature if possible to include the HTTP route path
            sig = get_function_signature(node)
            if is_route:
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                        method = dec.func.attr.upper()
                        # Extract first arg if it's the route path string literal
                        if dec.args and isinstance(dec.args[0], ast.Constant):
                            path = dec.args[0].value
                            sig = f"[{method}] {path} -> {sig}"
                            break
            
            docstring = ast.get_docstring(node)
            symbols.append({
                "name": node.name,
                "type": symbol_type,
                "signature": sig,
                "docstring": docstring or "",
                "line_start": node.lineno,
                "line_end": getattr(node, "end_lineno", node.lineno)
            })

    return symbols
