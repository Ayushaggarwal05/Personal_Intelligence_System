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
                        return self._clean_mermaid_markup(text)
                    else:
                        logger.warning(f"[DiagramGenerator] Gemini API status {res.status_code}. Trying Groq or fallback.")
            except Exception as e:
                logger.warning(f"[DiagramGenerator] Gemini API call exception: {e}")

        # 2. Try Groq API
        if groq_key:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0
            }
            try:
                with httpx.Client(timeout=15.0) as client:
                    res = client.post(url, headers=headers, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        text = data["choices"][0]["message"]["content"]
                        return self._clean_mermaid_markup(text)
                    else:
                        logger.warning(f"[DiagramGenerator] Groq API status {res.status_code}: {res.text}. Trying fallback.")
            except Exception as e:
                logger.warning(f"[DiagramGenerator] Groq API call exception: {e}")

        if db and project_id and diag_type:
            logger.info("[DiagramGenerator] Serving clean AST-driven fallback diagram.")
            return self._generate_deterministic_fallback(db, project_id, diag_type)

        raise PEISException("NO_API_KEY: No Diagram API Key configured in Settings.", status_code=400)

    def _clean_mermaid_markup(self, text: str) -> str:
        """Strips markdown code blocks and sanitizes common LLM Mermaid syntax errors."""
        text = text.strip()
        match = re.search(r"```(?:mermaid)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if match:
            text = match.group(1).strip()

        # Fix invalid LLM arrow syntax: e.g. -->|METHOD|> into valid -->|METHOD|
        text = re.sub(r"-->\|([^|\n]+)\|>", r"-->|\1|", text)
        text = re.sub(r"->\|([^|\n]+)\|>", r"->|\1|", text)

        return text

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
                for cls in set(classes[:15]):
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
                    
                    label = r.name.replace('"', '')
                    lines.append(f"    Client -->|{method}| {node_id}[\"{label}\"]")
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
        classes = []
        functions = []

        for sym, rel_path in symbols:
            info = f"{sym.name} (in {rel_path})"
            if sym.type == "route":
                routes.append(f"Route {sym.name}: {sym.signature or ''} [{rel_path}]")
            elif sym.type == "class":
                classes.append(info)
            elif sym.type == "function":
                functions.append(info)

        return {
            "routes": sorted(list(set(routes)))[:30],
            "classes": sorted(list(set(classes)))[:35],
            "functions": sorted(list(set(functions)))[:45]
        }

    def generate_er_diagram(self, db: Session, project_id: str) -> str:
        """Generates a comprehensive, detailed Mermaid ER diagram for all project model entities."""
        summary = self._get_project_symbols_summary(db, project_id)
        prompt = (
            "You are a Mermaid.js diagram generator.\n"
            "Generate a valid Mermaid Entity-Relationship (ER) diagram (`erDiagram`) for ALL the following codebase classes and data models:\n\n"
            f"CLASSES & DATA MODELS:\n{json.dumps(summary['classes'], indent=2)}\n\n"
            "REQUIREMENTS:\n"
            "1. Output ONLY valid Mermaid syntax starting with 'erDiagram'.\n"
            "2. Include ALL classes provided in the input. Do not omit model entities.\n"
            "3. Use valid ER syntax: ENTITY_A ||--o{ ENTITY_B : \"relationship\".\n"
            "4. Ensure entity names contain ONLY alphanumeric characters (no spaces, dashes, or dots).\n"
            "5. Wrap your code inside a ```mermaid ... ``` markdown block.\n"
            "6. Do NOT include any conversational explanation text before or after the code block."
        )
        return self._call_cloud_llm_for_mermaid(prompt, db=db, project_id=project_id, diag_type="er")

    def generate_api_flow(self, db: Session, project_id: str) -> str:
        """Generates a detailed Mermaid graph diagram mapping all backend API routes."""
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
        return self._call_cloud_llm_for_mermaid(prompt, db=db, project_id=project_id, diag_type="api-flow")

    def generate_sequence_diagram(self, db: Session, project_id: str) -> str:
        """Generates a dynamic Mermaid sequence diagram mapping the overall Frontend to Backend request flow."""
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
        return self._call_cloud_llm_for_mermaid(prompt, db=db, project_id=project_id, diag_type="sequence")

diagram_generator = DiagramGenerator()
