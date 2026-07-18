import os
import re
import json
from typing import List

def extract_dependencies(project_path: str) -> List[str]:
    """Reads project configuration files and returns a list of unique dependency package names."""
    dependencies = set()
    project_path = os.path.abspath(project_path)

    # 1. Python requirements.txt
    req_file = os.path.join(project_path, "requirements.txt")
    if os.path.exists(req_file):
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
    pkg_file = os.path.join(project_path, "package.json")
    if os.path.exists(pkg_file):
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
    go_file = os.path.join(project_path, "go.mod")
    if os.path.exists(go_file):
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
    cargo_file = os.path.join(project_path, "Cargo.toml")
    if os.path.exists(cargo_file):
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

    # 5. Java Maven pom.xml (simple regex parser to avoid complex xml schemas)
    pom_file = os.path.join(project_path, "pom.xml")
    if os.path.exists(pom_file):
        try:
            with open(pom_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                # find all artifactId matches
                matches = re.findall(r"<artifactId>([^<]+)</artifactId>", content)
                for match in matches:
                    dependencies.add(match.strip())
        except Exception:
            pass

    return sorted(list(dependencies))
