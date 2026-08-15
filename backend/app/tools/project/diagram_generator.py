import json
import re
import httpx
from sqlalchemy.orm import Session
from app.database.models.symbol import Symbol
from app.database.models.file import File
from app.core.settings import settings
from app.core.exceptions import PEISException

class DiagramGenerator:
    """Tool generating dynamic Mermaid.js diagrams using scoped Gemini/Groq API keys."""

    def _call_cloud_llm_for_mermaid(self, prompt: str) -> str:
        """Helper to invoke Gemini or Groq exclusively for diagram generation."""
        gemini_key = settings.GEMINI_API_KEY
        groq_key = settings.GROQ_API_KEY

        if not gemini_key and not groq_key:
            raise PEISException("NO_API_KEY: No Diagram API Key configured in Settings.", status_code=400)

        # 1. Try Gemini API
        if gemini_key:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            try:
                with httpx.Client(timeout=15.0) as client:
                    res = client.post(url, json=payload)
                    if res.status_code == 429:
                        raise PEISException("RATE_LIMITED: Gemini API key rate limit exceeded.", status_code=429)
                    elif res.status_code in {400, 401, 403}:
                        raise PEISException("INVALID_KEY: Invalid Gemini API key in Settings.", status_code=401)
                    elif res.status_code != 200:
                        raise PEISException(f"Gemini API returned status {res.status_code}", status_code=500)
                    
                    data = res.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return self._clean_mermaid_markup(text)
            except PEISException:
                raise
            except Exception as e:
                raise PEISException(f"Failed to generate diagram via Gemini API: {str(e)}", status_code=500)

        # 2. Try Groq API
        if groq_key:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
            try:
                with httpx.Client(timeout=15.0) as client:
                    res = client.post(url, headers=headers, json=payload)
                    if res.status_code == 429:
                        raise PEISException("RATE_LIMITED: Groq API key rate limit exceeded.", status_code=429)
                    elif res.status_code in {401, 403}:
                        raise PEISException("INVALID_KEY: Invalid Groq API key in Settings.", status_code=401)
                    elif res.status_code != 200:
                        raise PEISException(f"Groq API returned status {res.status_code}: {res.text}", status_code=500)
                    
                    data = res.json()
                    text = data["choices"][0]["message"]["content"]
                    return self._clean_mermaid_markup(text)
            except PEISException:
                raise
            except Exception as e:
                raise PEISException(f"Failed to generate diagram via Groq API: {str(e)}", status_code=500)

        raise PEISException("NO_API_KEY: No Diagram API Key configured in Settings.", status_code=400)

    def _clean_mermaid_markup(self, text: str) -> str:
        """Strips markdown fenced code blocks to extract raw Mermaid syntax."""
        text = text.strip()
        match = re.search(r"```(?:mermaid)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return text

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
            "routes": routes[:25],
            "classes": classes[:30],
            "functions": functions[:40]
        }

    def generate_er_diagram(self, db: Session, project_id: str) -> str:
        """Generates a Mermaid ER diagram illustrating project models schemas using cloud LLM."""
        summary = self._get_project_symbols_summary(db, project_id)
        prompt = (
            "You are a Mermaid.js diagram generator.\n"
            "Generate a valid Mermaid Entity-Relationship (ER) diagram (`erDiagram`) for the following codebase classes and data models:\n\n"
            f"CLASSES / MODELS:\n{json.dumps(summary['classes'], indent=2)}\n\n"
            "REQUIREMENTS:\n"
            "1. Output ONLY valid Mermaid syntax starting with 'erDiagram'.\n"
            "2. Wrap your code inside a ```mermaid ... ``` markdown block.\n"
            "3. Ensure all entity names use alphanumeric characters only (no spaces or special chars).\n"
            "4. Do not include any conversational explanation text before or after the code block."
        )
        return self._call_cloud_llm_for_mermaid(prompt)

    def generate_api_flow(self, db: Session, project_id: str) -> str:
        """Generates a Mermaid graph diagram mapping API routes flow configurations using cloud LLM."""
        summary = self._get_project_symbols_summary(db, project_id)
        prompt = (
            "You are a Mermaid.js diagram generator.\n"
            "Generate a valid Mermaid flowchart diagram (`graph LR` or `graph TD`) illustrating the API routes and component flow for this codebase:\n\n"
            f"API ROUTES:\n{json.dumps(summary['routes'], indent=2)}\n\n"
            f"CLASSES / SERVICES:\n{json.dumps(summary['classes'], indent=2)}\n\n"
            "REQUIREMENTS:\n"
            "1. Output ONLY valid Mermaid syntax starting with 'graph LR' or 'graph TD'.\n"
            "2. Wrap your code inside a ```mermaid ... ``` markdown block.\n"
            "3. Use double quotes around node labels containing spaces or special characters.\n"
            "4. Do not include any conversational explanation text before or after the code block."
        )
        return self._call_cloud_llm_for_mermaid(prompt)

    def generate_sequence_diagram(self, db: Session, project_id: str) -> str:
        """Generates a dynamic Mermaid sequence diagram mapping controller-service lifecycle using cloud LLM."""
        summary = self._get_project_symbols_summary(db, project_id)
        prompt = (
            "You are a Mermaid.js diagram generator.\n"
            "Generate a dynamic Mermaid sequence diagram (`sequenceDiagram`) tracing the request-response flow through these routes and service components:\n\n"
            f"API ROUTES:\n{json.dumps(summary['routes'], indent=2)}\n\n"
            f"CLASSES & SERVICES:\n{json.dumps(summary['classes'], indent=2)}\n\n"
            f"FUNCTIONS:\n{json.dumps(summary['functions'], indent=2)}\n\n"
            "REQUIREMENTS:\n"
            "1. Output ONLY valid Mermaid syntax starting with 'sequenceDiagram'.\n"
            "2. Define realistic sequence steps: Client -> Controller/Router -> Service -> Repository/Database.\n"
            "3. Wrap your code inside a ```mermaid ... ``` markdown block.\n"
            "4. Do not include any conversational explanation text before or after the code block."
        )
        return self._call_cloud_llm_for_mermaid(prompt)

diagram_generator = DiagramGenerator()
