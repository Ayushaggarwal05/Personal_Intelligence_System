import json
import re
import httpx
from sqlalchemy.orm import Session
from app.database.models.symbol import Symbol
from app.database.models.file import File
from app.core.settings import settings
from app.core.exceptions import PEISException
from app.core.logging import logger

class DiagramGenerator:
    """Tool generating dynamic, deterministic Mermaid.js diagrams using scoped Gemini/Groq API keys."""

    def __init__(self):
        self._cache = {}

    def clear_cache(self, project_id: str = None):
        """Flushes the in-memory diagram cache for a specific project or all projects."""
        if project_id:
            keys_to_del = [k for k in self._cache if k.startswith(f"{project_id}_")]
            for k in keys_to_del:
                del self._cache[k]
            logger.info(f"[DiagramGenerator] Cleared diagram cache for project: {project_id}")
        else:
            self._cache.clear()
            logger.info("[DiagramGenerator] Cleared all diagram cache.")

    def _call_cloud_llm_for_mermaid(self, prompt: str, db: Session = None, project_id: str = None, diag_type: str = None) -> str:
        """Helper to invoke Gemini or Groq exclusively for diagram generation with deterministic settings."""
        gemini_key = settings.GEMINI_API_KEY
        groq_key = settings.GROQ_API_KEY

        if not gemini_key and not groq_key:
            if db and project_id and diag_type:
                logger.info("[DiagramGenerator] No API Key set. Serving clean AST-driven diagram.")
                return self._generate_deterministic_fallback(db, project_id, diag_type)
            raise PEISException("NO_API_KEY: No Diagram API Key configured in Settings.", status_code=400)

        # 1. Try Gemini API
        if gemini_key:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.0
                }
            }
            try:
                with httpx.Client(timeout=15.0) as client:
                    res = client.post(url, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        cleaned = self._clean_mermaid_markup(text)
                        if cleaned:
                            return cleaned
                        logger.warning("[DiagramGenerator] Gemini returned invalid markup. Trying Groq or fallback.")
                    else:
                        logger.warning(f"[DiagramGenerator] Gemini API status {res.status_code}. Trying Groq or fallback.")
            except Exception as e:
                logger.warning(f"[DiagramGenerator] Gemini API call exception: {e}")

        # 2. Try Groq API
        if groq_key:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
            payload = {
                "model": "qwen/qwen3.6-27b",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0
            }
            try:
                with httpx.Client(timeout=15.0) as client:
                    res = client.post(url, headers=headers, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        text = data["choices"][0]["message"]["content"]
                        cleaned = self._clean_mermaid_markup(text)
                        if cleaned:
                            return cleaned
                        logger.warning("[DiagramGenerator] Groq returned invalid markup. Serving fallback.")
                    else:
                        logger.warning(f"[DiagramGenerator] Groq API status {res.status_code}: {res.text}. Trying fallback.")
            except Exception as e:
                logger.warning(f"[DiagramGenerator] Groq API call exception: {e}")

        if db and project_id and diag_type:
            logger.info("[DiagramGenerator] Serving clean AST-driven fallback diagram.")
            return self._generate_deterministic_fallback(db, project_id, diag_type)

        raise PEISException("NO_API_KEY: No Diagram API Key configured in Settings.", status_code=400)

    def _clean_mermaid_markup(self, text: str) -> str:
        """Strips thinking tags (<think>...</think>), markdown code blocks, conversational text, and sanitizes common LLM Mermaid syntax errors."""
        text = text.strip()
        
        # 0. Strip LLM reasoning thinking tags e.g. <think>...</think>
        text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE).strip()

        # 1. Extract block inside markdown backticks if present
        match = re.search(r"```(?:mermaid)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if match:
            text = match.group(1).strip()

        # 2. Strip leading/trailing backticks or markdown markers
        text = re.sub(r"^`+(?:mermaid)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*`+$", "", text)

        # 3. Trim pre-conversational text (find first valid diagram header)
        lines = text.split("\n")
        valid_keywords = {"graph", "erdiagram", "sequencediagram", "flowchart", "classdiagram"}
        start_idx = -1
        for idx, line in enumerate(lines):
            clean_l = line.strip().lower()
            if any(clean_l.startswith(kw) for kw in valid_keywords):
                start_idx = idx
                break

        if start_idx != -1:
            text = "\n".join(lines[start_idx:])

        # 4. Fix invalid LLM arrow syntax: e.g. -->|METHOD|> into valid -->|METHOD|
        text = re.sub(r"-->\|([^|\n]+)\|>", r"-->|\1|", text)
        text = re.sub(r"->\|([^|\n]+)\|>", r"->|\1|", text)

        # 5. Escape URL path parameters like <int:pk> to &lt;int:pk&gt; so HTML parser doesn't crash
        text = re.sub(r"<([a-zA-Z0-9_:.-]+)>", r"&lt;\1&gt;", text)

        # 6. Validation Guard: If output contains '...' or doesn't start with a valid header, reject
        cleaned_lines = [l.strip() for l in text.split("\n") if l.strip()]
        if not cleaned_lines or "..." in text or not any(cleaned_lines[0].lower().startswith(kw) for kw in valid_keywords):
            logger.warning("[DiagramGenerator] LLM output failed validation (contained '...' or invalid header).")
            return ""

        return text.strip()

    def _generate_deterministic_fallback(self, db: Session, project_id: str, diag_type: str) -> str:
        """AST-driven fallback producing 100% valid Mermaid syntax directly from SQLite symbols."""
        symbols = db.query(Symbol, File.relative_path).join(File, Symbol.file_id == File.id).filter(
            File.project_id == project_id
        ).all()

        if diag_type == "er":
            classes = [sym.name for sym, _ in symbols if sym.type == "class"]
            lines = ["erDiagram"]
            if not classes:
                lines.append("    WORKSPACE ||--o{ FILE : contains")
                lines.append("    FILE ||--o{ SYMBOL : declares")
            else:
                for cls in set(classes[:20]):
                    clean_cls = re.sub(r"[^a-zA-Z0-9_]", "", cls)
                    if clean_cls:
                        lines.append(f"    MODEL ||--o{{ {clean_cls} : defines")
                        lines.append(f"    {clean_cls} {{")
                        lines.append("        string id")
                        lines.append("        string status")
                        lines.append("    }")
            return "\n".join(lines)

        elif diag_type == "api-flow":
            routes = [sym for sym, _ in symbols if sym.type == "route"]
            lines = ["graph LR", "    Client[\"Frontend Client\"]"]
            if not routes:
                lines.append("    Client --> Route1[\"[GET] /api/health\"]")
                lines.append("    Client --> Route2[\"[POST] /api/chat/stream\"]")
            else:
                for idx, r in enumerate(routes[:20]):
                    node_id = f"r_{idx}"
                    method = "API"
                    if "GET" in r.name.upper(): method = "GET"
                    elif "POST" in r.name.upper(): method = "POST"
                    elif "DELETE" in r.name.upper(): method = "DELETE"
                    
                    clean_label = r.name.replace('"', '').replace('<', '&lt;').replace('>', '&gt;')
                    lines.append(f"    Client -->|{method}| {node_id}[\"{clean_label}\"]")
            return "\n".join(lines)

        else: # sequence
            return (
                "sequenceDiagram\n"
                "    autonumber\n"
                "    actor Client as Frontend UI\n"
                "    participant Controller as API Router\n"
                "    participant Service as Business Service\n"
                "    participant DB as SQLite Storage\n\n"
                "    Client->>Controller: HTTP Request\n"
                "    Controller->>Service: Dispatch Request Payload\n"
                "    Service->>DB: Query Indexed Workspace Symbols\n"
                "    DB-->>Service: Return Symbol Records\n"
                "    Service-->>Controller: Return Structured Output\n"
                "    Controller-->>Client: HTTP JSON Response"
            )

    def _get_project_symbols_summary(self, db: Session, project_id: str) -> dict:
        """Extracts structured files, classes, functions, and routes from SQLite for the prompt payload."""
        symbols = db.query(Symbol, File.relative_path).join(File, Symbol.file_id == File.id).filter(
            File.project_id == project_id
        ).all()

        routes = []
        models = []
        classes = []
        functions = []

        # Universal framework non-model exclusion keywords
        non_model_kw = {"view", "serializer", "controller", "service", "adapter", "config", "pagination", "renderer", "filter", "permission", "middleware", "test"}

        for sym, rel_path in symbols:
            info = f"{sym.name} (in {rel_path})"
            if sym.type == "route":
                clean_route_name = sym.name.replace('<', '&lt;').replace('>', '&gt;')
                routes.append(f"Route {clean_route_name}: {sym.signature or ''} [{rel_path}]")
            elif sym.type == "class":
                classes.append(info)
                rel_lower = rel_path.lower()
                name_lower = sym.name.lower()
                is_model_file = any(kw in rel_lower for kw in ["model", "entity", "schema", "db", "domain"])
                is_model_name = any(kw in name_lower for kw in ["model", "entity", "schema", "table"]) or not any(kw in name_lower for kw in non_model_kw)
                if is_model_file or is_model_name:
                    models.append(info)
            elif sym.type == "function":
                functions.append(info)

        return {
            "routes": sorted(list(set(routes)))[:30],
            "models": sorted(list(set(models)))[:25],
            "classes": sorted(list(set(classes)))[:35],
            "functions": sorted(list(set(functions)))[:45]
        }

    def generate_er_diagram(self, db: Session, project_id: str, force_refresh: bool = False) -> str:
        """Generates a comprehensive, detailed Mermaid ER diagram for all project model entities."""
        cache_key = f"{project_id}_er"
        if not force_refresh and cache_key in self._cache:
            logger.info(f"[DiagramGenerator] Returning cached ER diagram for project: {project_id}")
            return self._cache[cache_key]

        summary = self._get_project_symbols_summary(db, project_id)
        target_entities = summary['models'] if summary['models'] else summary['classes']
        prompt = (
            "You are a Mermaid.js diagram generator.\n"
            "Generate a valid Mermaid Entity-Relationship (ER) diagram (`erDiagram`) for ALL the following codebase data models:\n\n"
            f"DATA MODELS & ENTITIES:\n{json.dumps(target_entities, indent=2)}\n\n"
            "REQUIREMENTS:\n"
            "1. Output ONLY valid Mermaid syntax starting with 'erDiagram'.\n"
            "2. Include ALL model entities provided in the input.\n"
            "3. Use compact ER syntax: ENTITY_A ||--o{ ENTITY_B : \"relationship\".\n"
            "4. Ensure entity names contain ONLY plain alphanumeric characters (no spaces, dashes, or dots).\n"
            "5. Wrap your code inside a ```mermaid ... ``` markdown block.\n"
            "6. Do NOT include any conversational explanation text before or after the code block."
        )
        markup = self._call_cloud_llm_for_mermaid(prompt, db=db, project_id=project_id, diag_type="er")
        if markup:
            self._cache[cache_key] = markup
        return markup

    def generate_api_flow(self, db: Session, project_id: str, force_refresh: bool = False) -> str:
        """Generates a detailed Mermaid graph diagram mapping all backend API routes."""
        cache_key = f"{project_id}_api-flow"
        if not force_refresh and cache_key in self._cache:
            logger.info(f"[DiagramGenerator] Returning cached API flow diagram for project: {project_id}")
            return self._cache[cache_key]

        summary = self._get_project_symbols_summary(db, project_id)
        prompt = (
            "You are a Mermaid.js diagram generator.\n"
            "Generate a detailed Mermaid flowchart diagram (`graph LR`) mapping backend API routes for this project:\n\n"
            f"BACKEND API ROUTES:\n{json.dumps(summary['routes'], indent=2)}\n\n"
            f"CLASSES:\n{json.dumps(summary['classes'], indent=2)}\n\n"
            "STRICT SYNTAX RULES:\n"
            "1. Output ONLY valid Mermaid syntax starting with 'graph LR'.\n"
            "2. For arrows with text labels, use EXACT syntax: NodeA[\"Label A\"] -->|POST| NodeB[\"Label B\"].\n"
            "3. CRITICAL: DO NOT add a trailing '>' inside arrow text labels like '-->|POST|>'. That is invalid syntax.\n"
            "4. Enclose all node label text inside double quotes.\n"
            "5. Wrap your code inside a ```mermaid ... ``` markdown block.\n"
            "6. Do NOT include any conversational text before or after the code block."
        )
        markup = self._call_cloud_llm_for_mermaid(prompt, db=db, project_id=project_id, diag_type="api-flow")
        self._cache[cache_key] = markup
        return markup

    def generate_sequence_diagram(self, db: Session, project_id: str, force_refresh: bool = False) -> str:
        """Generates a dynamic Mermaid sequence diagram mapping the overall Frontend to Backend request flow."""
        cache_key = f"{project_id}_sequence"
        if not force_refresh and cache_key in self._cache:
            logger.info(f"[DiagramGenerator] Returning cached sequence diagram for project: {project_id}")
            return self._cache[cache_key]

        summary = self._get_project_symbols_summary(db, project_id)
        prompt = (
            "You are a Mermaid.js diagram generator.\n"
            "Generate a dynamic end-to-end Mermaid sequence diagram (`sequenceDiagram`) tracing request execution from Frontend UI components to Backend Controllers, Services, and Storage:\n\n"
            f"API ROUTES:\n{json.dumps(summary['routes'], indent=2)}\n\n"
            f"CLASSES & SERVICES:\n{json.dumps(summary['classes'], indent=2)}\n\n"
            f"KEY FUNCTIONS:\n{json.dumps(summary['functions'], indent=2)}\n\n"
            "REQUIREMENTS:\n"
            "1. Output ONLY valid Mermaid syntax starting with 'sequenceDiagram'.\n"
            "2. Define participants: Client UI -> API Controller/Router -> Business Service -> Storage/Database.\n"
            "3. Trace realistic end-to-end steps (HTTP Request -> Service Validation -> DB Query -> JSON Response).\n"
            "4. Wrap your code inside a ```mermaid ... ``` markdown block.\n"
            "5. Do NOT include any conversational text before or after the code block."
        )
        markup = self._call_cloud_llm_for_mermaid(prompt, db=db, project_id=project_id, diag_type="sequence")
        self._cache[cache_key] = markup
        return markup

diagram_generator = DiagramGenerator()
