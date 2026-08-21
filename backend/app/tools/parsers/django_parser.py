import os
import ast
import re
from typing import List, Dict, Any, Optional, Set
from app.core.logging import logger

def is_django_project(project_path: str) -> bool:
    """Detects if a project path is a Django project based on manage.py, requirements, or urls.py."""
    if not os.path.exists(project_path):
        return False
        
    # Signal 1: manage.py exists
    if os.path.exists(os.path.join(project_path, "manage.py")):
        return True
        
    # Signal 2: Check dependency manifests
    req_path = os.path.join(project_path, "requirements.txt")
    if os.path.exists(req_path):
        try:
            with open(req_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().lower()
                if "django" in content:
                    return True
        except Exception:
            pass

    # Signal 3: Check for any urls.py with urlpatterns within project directory
    for root, dirs, files in os.walk(project_path):
        rel_depth = os.path.relpath(root, project_path).count(os.sep)
        if rel_depth > 3:
            dirs.clear() # Don't traverse deeper than 3 levels
            continue
        if "urls.py" in files:
            full_path = os.path.join(root, "urls.py")
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    if "urlpatterns" in f.read():
                        return True
            except Exception:
                pass
                
    return False

class DjangoURLVisitor(ast.NodeVisitor):
    """AST visitor that extracts path() and re_path() calls from urlpatterns."""
    
    def __init__(self, current_file: str, project_path: str):
        self.current_file = current_file
        self.project_path = project_path
        self.routes: List[Dict[str, Any]] = []
        self.imports: Dict[str, str] = {} # alias -> full module path

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            name = alias.asname or alias.name
            self.imports[name] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module or ""
        for alias in node.names:
            name = alias.asname or alias.name
            self.imports[name] = f"{module}.{alias.name}" if module else alias.name
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # Match path('route/', ...), re_path(r'^route/', ...), or router.register('prefix', ViewSet)
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name == "register" and len(node.args) >= 2:
            prefix_pattern = ""
            arg0 = node.args[0]
            if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                prefix_pattern = arg0.value
            elif isinstance(arg0, ast.Str):
                prefix_pattern = arg0.s
                
            view_name = self._resolve_view_name(node.args[1])
            for m in ["GET", "POST", "PUT", "DELETE"]:
                self.routes.append({
                    "type": "endpoint",
                    "prefix": prefix_pattern,
                    "view_name": view_name,
                    "method": m,
                    "line": node.lineno
                })

        if func_name in {"path", "re_path", "url"} and len(node.args) >= 2:
            path_pattern = ""
            arg0 = node.args[0]
            if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                path_pattern = arg0.value
            elif isinstance(arg0, ast.Str): # Python <3.8 compatibility
                path_pattern = arg0.s

            arg1 = node.args[1]
            
            # Case A: include('app.urls')
            is_include = False
            if isinstance(arg1, ast.Call):
                call_func_name = ""
                if isinstance(arg1.func, ast.Name):
                    call_func_name = arg1.func.id
                elif isinstance(arg1.func, ast.Attribute):
                    call_func_name = arg1.func.attr
                if call_func_name == "include":
                    is_include = True

            if is_include and arg1.args:
                inc_arg = arg1.args[0]
                target_module = ""
                if isinstance(inc_arg, ast.Constant) and isinstance(inc_arg.value, str):
                    target_module = inc_arg.value
                elif isinstance(inc_arg, ast.Str):
                    target_module = inc_arg.s

                if target_module:
                    self.routes.append({
                        "type": "include",
                        "prefix": path_pattern,
                        "target_module": target_module,
                        "line": node.lineno
                    })

            # Case B: Direct View Function or Class View: path('users/', views.user_list)
            else:
                view_name = self._resolve_view_name(arg1)
                methods = self._guess_http_methods(node, view_name)
                
                for method in methods:
                    self.routes.append({
                        "type": "endpoint",
                        "prefix": path_pattern,
                        "view_name": view_name,
                        "method": method,
                        "line": node.lineno
                    })

        self.generic_visit(node)

    def _resolve_view_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            val_name = self._resolve_view_name(node.value)
            return f"{val_name}.{node.attr}" if val_name else node.attr
        elif isinstance(node, ast.Call): # e.g. views.UserViewSet.as_view()
            return self._resolve_view_name(node.func)
        return "view"

    def _guess_http_methods(self, node: ast.Call, view_name: str) -> List[str]:
        # Inspect for as_view({'get': 'list', 'post': 'create'}) mapping
        methods = set()
        for kw in node.keywords:
            if kw.arg == "name":
                continue
        
        # Check inside as_view({...}) dictionary argument
        if isinstance(node.args[1], ast.Call):
            call_node = node.args[1]
            if call_node.args and isinstance(call_node.args[0], ast.Dict):
                for key in call_node.args[0].keys:
                    if isinstance(key, ast.Constant) and isinstance(key.value, str):
                        methods.add(key.value.upper())
                    elif isinstance(key, ast.Str):
                        methods.add(key.s.upper())

        if not methods:
            # Default HTTP methods for endpoint
            methods = {"GET", "POST"}
            
        return sorted(list(methods))

def module_to_file_path(project_path: str, module_str: str) -> Optional[str]:
    """Converts a Python module dot notation string to an absolute file path inside project_path."""
    parts = module_str.split(".")
    
    # Try as direct file: app/urls.py
    candidate1 = os.path.join(project_path, *parts) + ".py"
    if os.path.exists(candidate1):
        return candidate1
        
    # Try as package directory: app/urls/__init__.py
    candidate2 = os.path.join(project_path, *parts, "__init__.py")
    if os.path.exists(candidate2):
        return candidate2

    # Try searching relative to app subdirectories
    for root, dirs, _ in os.walk(project_path):
        sub_candidate = os.path.join(root, *parts) + ".py"
        if os.path.exists(sub_candidate):
            return sub_candidate
            
    return None

def parse_django_urls_recursive(
    project_path: str, 
    file_path: str, 
    current_prefix: str = "", 
    visited_files: Set[str] = None
) -> List[Dict[str, Any]]:
    """Recursively processes urls.py files and extracts full concatenated route paths."""
    if visited_files is None:
        visited_files = set()

    abs_path = os.path.abspath(file_path)
    if abs_path in visited_files or not os.path.exists(abs_path):
        return []

    visited_files.add(abs_path)

    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
        tree = ast.parse(code, filename=abs_path)
    except Exception as e:
        logger.warning(f"[DjangoParser] Failed to parse AST for {abs_path}: {e}")
        return []

    visitor = DjangoURLVisitor(abs_path, project_path)
    visitor.visit(tree)

    extracted_endpoints = []

    for item in visitor.routes:
        raw_prefix = item["prefix"].strip("^$").lstrip("/")
        combined_prefix = f"{current_prefix}/{raw_prefix}".replace("//", "/")
        if not combined_prefix.startswith("/"):
            combined_prefix = "/" + combined_prefix

        if item["type"] == "include":
            target_file = module_to_file_path(project_path, item["target_module"])
            if target_file:
                sub_endpoints = parse_django_urls_recursive(
                    project_path, target_file, combined_prefix, visited_files
                )
                extracted_endpoints.extend(sub_endpoints)
        elif item["type"] == "endpoint":
            extracted_endpoints.append({
                "name": f"{item['method']} {combined_prefix}",
                "type": "route",
                "signature": f"[{item['method']}] {combined_prefix} -> {item['view_name']}",
                "docstring": f"Django View: {item['view_name']}",
                "line_start": item["line"],
                "line_end": item["line"],
                "file_path": abs_path
            })

    return extracted_endpoints

def extract_django_routes_for_project(project_path: str) -> List[Dict[str, Any]]:
    """Scans all urls.py files in a Django project and returns fully concatenated route symbols."""
    if not is_django_project(project_path):
        return []

    # Find root urls.py candidate
    urls_files = []
    for root, _, files in os.walk(project_path):
        if "urls.py" in files:
            urls_files.append(os.path.join(root, "urls.py"))

    if not urls_files:
        return []

    # Prioritize root config urls.py (e.g., config/urls.py, project/urls.py)
    urls_files.sort(key=lambda p: (
        0 if any(k in p.lower() for k in ["config", "project", "core", "main"]) else 1,
        len(p)
    ))

    all_routes = []
    visited_files: Set[str] = set()

    for root_urls in urls_files:
        routes = parse_django_urls_recursive(project_path, root_urls, "", visited_files)
        all_routes.extend(routes)

    # Deduplicate routes by signature
    unique_routes = []
    seen_sigs = set()
    for r in all_routes:
        if r["signature"] not in seen_sigs:
            seen_sigs.add(r["signature"])
            unique_routes.append(r)

    return unique_routes
