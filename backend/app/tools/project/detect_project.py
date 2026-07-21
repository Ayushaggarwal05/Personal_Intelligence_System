import os
from typing import Dict, Any, List

def detect_project_profile(project_path: str) -> Dict[str, Any]:
    """Inspects files at project_path and extracts framework and environment profile metadata."""
    project_path = os.path.abspath(project_path)
    
    frameworks = []
    databases = []
    languages = []
    managers = []
    
    # Check for configuration files on root
    files_on_root = set(os.listdir(project_path)) if os.path.exists(project_path) else set()

    # 1. Package manager indicators
    if "package.json" in files_on_root:
        languages.append("JavaScript/TypeScript")
        managers.append("npm")
        if "yarn.lock" in files_on_root:
            managers.append("yarn")
        elif "pnpm-lock.yaml" in files_on_root:
            managers.append("pnpm")
            
    if "requirements.txt" in files_on_root or "pyproject.toml" in files_on_root or "poetry.lock" in files_on_root:
        languages.append("Python")
        managers.append("pip")
        if "poetry.lock" in files_on_root:
            managers.append("poetry")

    if "go.mod" in files_on_root:
        languages.append("Go")
        managers.append("go-modules")

    if "Cargo.toml" in files_on_root:
        languages.append("Rust")
        managers.append("cargo")

    if "pom.xml" in files_on_root:
        languages.append("Java")
        managers.append("maven")

    # 2. Deep file scanning to match framework triggers
    for root, dirs, files in os.walk(project_path):
        # Limit depth to keep it fast
        depth = root[len(project_path):].count(os.sep)
        if depth > 3:
            dirs[:] = [] # stop deep traversal
            continue

        # Ignore dotfiles/ignored folders dynamically
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in {"node_modules", "venv", "__pycache__"}]

        for file in files:
            file_lower = file.lower()
            
            # Framework matching in code files
            if file_lower.endswith(".py"):
                # Check Python frameworks in main / app files
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if "from fastapi import" in content or "import fastapi" in content:
                            frameworks.append("FastAPI")
                        if "django.core" in content or "from django" in content:
                            frameworks.append("Django")
                        if "from flask import" in content or "import flask" in content:
                            frameworks.append("Flask")
                        if "sqlite" in content or "sqlite3" in content:
                            databases.append("SQLite")
                        if "postgresql" in content or "postgres" in content or "psycopg2" in content:
                            databases.append("PostgreSQL")
                except Exception:
                    pass

            elif file_lower.endswith((".js", ".ts", ".jsx", ".tsx")):
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if "express()" in content or "require('express')" in content:
                            frameworks.append("Express")
                        if "from 'react'" in content or 'from "react"' in content:
                            frameworks.append("React")
                        if "next/router" in content or "next/link" in content or "from 'next'" in content:
                            frameworks.append("Next.js")
                        if "mongodb" in content or "mongoose" in content:
                            databases.append("MongoDB")
                except Exception:
                    pass

    # Deduplicate lists
    frameworks = list(set(frameworks))
    databases = list(set(databases))
    languages = list(set(languages))
    managers = list(set(managers))

    # Derive primary descriptors
    primary_lang = ", ".join(languages) if languages else "Unknown"
    primary_framework = ", ".join(frameworks) if frameworks else "Unknown"
    primary_db = ", ".join(databases) if databases else "SQLite"

    return {
        "project_type": primary_lang,
        "framework": primary_framework,
        "database_type": primary_db,
        "package_managers": managers,
        "languages": languages,
        "frameworks": frameworks
    }
