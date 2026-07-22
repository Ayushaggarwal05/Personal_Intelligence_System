import os
import re
import json
from typing import List

def extract_dependencies(project_path: str) -> List[str]:
    """Reads project configuration files recursively and returns a list of unique dependency package names."""
    dependencies = set()
    project_path = os.path.abspath(project_path)

    # Find all dependency configuration files up to depth 3
    config_files = {
        "requirements.txt": [],
        "package.json": [],
        "go.mod": [],
        "Cargo.toml": [],
        "pom.xml": []
    }

    for root, dirs, files in os.walk(project_path):
        # Limit depth to keep walk extremely fast
        depth = root[len(project_path):].count(os.sep)
        if depth > 3:
            dirs[:] = []
            continue

        # Prune ignored system directories
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in {"node_modules", "venv", "__pycache__", "dist", "build"}]

        for file in files:
            if file in config_files:
                config_files[file].append(os.path.join(root, file))

    # 1. Python requirements.txt
    for req_file in config_files["requirements.txt"]:
        try:
            with open(req_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line_strip = line.strip()
                    if not line_strip or line_strip.startswith("#"):
                        continue
                    # Match name before comparison operators
                    match = re.match(r"^([a-zA-Z0-9_\-]+)", line_strip)
                    if match:
                        dependencies.add(match.group(1).lower())
        except Exception:
            pass

    # 2. JavaScript/TypeScript package.json
    for pkg_file in config_files["package.json"]:
        try:
            with open(pkg_file, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
                for key in ["dependencies", "devDependencies"]:
                    if key in data:
                        for pkg in data[key].keys():
                            dependencies.add(pkg)
        except Exception:
            pass

    # 3. Go modules go.mod
    for go_file in config_files["go.mod"]:
        try:
            with open(go_file, "r", encoding="utf-8", errors="ignore") as f:
                in_require_block = False
                for line in f:
                    line_strip = line.strip()
                    if line_strip.startswith("require ("):
                        in_require_block = True
                        continue
                    elif in_require_block and line_strip.startswith(")"):
                        in_require_block = False
                        continue
                    
                    if in_require_block:
                        match = re.match(r"^([a-zA-Z0-9_\.\-/]+)", line_strip)
                        if match:
                            dependencies.add(match.group(1))
                    elif line_strip.startswith("require "):
                        match = re.match(r"^require\s+([a-zA-Z0-9_\.\-/]+)", line_strip)
                        if match:
                            dependencies.add(match.group(1))
        except Exception:
            pass

    # 4. Rust Cargo.toml
    for cargo_file in config_files["Cargo.toml"]:
        try:
            with open(cargo_file, "r", encoding="utf-8", errors="ignore") as f:
                in_dependencies = False
                for line in f:
                    line_strip = line.strip()
                    if line_strip.startswith("[dependencies]") or line_strip.startswith("[dev-dependencies]"):
                        in_dependencies = True
                        continue
                    elif line_strip.startswith("[") and in_dependencies:
                        in_dependencies = False
                        
                    if in_dependencies:
                        match = re.match(r"^([a-zA-Z0-9_\-]+)\s*=", line_strip)
                        if match:
                            dependencies.add(match.group(1))
        except Exception:
            pass

    # 5. Java Maven pom.xml
    for pom_file in config_files["pom.xml"]:
        try:
            with open(pom_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                matches = re.findall(r"<artifactId>([^<]+)</artifactId>", content)
                for match in matches:
                    dependencies.add(match.strip())
        except Exception:
            pass

    return sorted(list(dependencies))
