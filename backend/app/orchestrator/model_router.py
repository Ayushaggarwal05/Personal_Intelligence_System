import json
from typing import Optional, Dict, Any
from app.core.settings import settings
from app.core.logging import logger
from app.core.exceptions import LLMProviderException

def make_post_request(url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> str:
    """Helper to perform POST request using httpx if installed, falling back to urllib.request."""
    data = json.dumps(payload).encode("utf-8")
    
    try:
        import httpx
        with httpx.Client(timeout=180.0) as client:
            response = client.post(url, headers=headers, content=data)
            if response.status_code != 200:
                raise LLMProviderException("HTTP Error", f"Status code {response.status_code}: {response.text}")
            return response.text
    except ImportError:
        import urllib.request
        import urllib.error
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=180) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8") if e else ""
            raise LLMProviderException("urllib HTTPError", f"Status {e.code}: {err_body}")
        except Exception as e:
            raise LLMProviderException("urllib ConnectionError", str(e))
    except Exception as e:
         raise LLMProviderException("httpx RequestError", str(e))


class ModelRouter:
    """Central routing engine wrapper for Local and Cloud LLM inference."""
    def __init__(self):
        pass

    def check_local_ollama_health(self) -> bool:
        """Sends a fast health check request to Ollama endpoint to verify if it is running."""
        try:
            import urllib.request
            # Check root Ollama URL with 1-second timeout
            with urllib.request.urlopen(settings.OLLAMA_HOST, timeout=1.0) as response:
                if response.status == 200:
                    return True
        except Exception:
            pass
        return False

    def generate(self, prompt: str, system_prompt: Optional[str] = None, json_format: bool = False, provider: Optional[str] = None) -> str:
        """Executes prompt inference routing between local and cloud providers with auto-fallback policies."""
        if not provider:
            provider = settings.ACTIVE_LLM_PROVIDER.lower()
        else:
            provider = provider.lower()
        
        # Auto fallback check if provider is set to local but Ollama is offline
        if provider == "local" and not self.check_local_ollama_health():
            logger.warning("[ModelRouter] Local Ollama service is offline. Evaluating cloud providers fallback...")
            if settings.GEMINI_API_KEY:
                logger.info("[ModelRouter] Falling back to Gemini Cloud provider.")
                provider = "gemini"
            elif settings.GROQ_API_KEY:
                logger.info("[ModelRouter] Falling back to Groq Cloud provider.")
                provider = "groq"
            else:
                logger.error("[ModelRouter] All providers offline. Routing raw Ollama request...")

        # 1. LOCAL OLLAMA ROUTING
        if provider == "local":
            url = f"{settings.OLLAMA_HOST}/api/generate"
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "keep_alive": "10m"
            }
            if system_prompt:
                payload["system"] = system_prompt
            if json_format:
                payload["format"] = "json"

            try:
                raw_res = make_post_request(url, headers, payload)
                return json.loads(raw_res)["response"]
            except Exception as e:
                logger.warning(f"[ModelRouter] Ollama inference failed: {e}. Yielding mock fallback response.")
                return self._get_fallback_mock_response(prompt, json_format)

        # 2. GEMINI CLOUD ROUTING
        elif provider == "gemini":
            api_key = settings.GEMINI_API_KEY or "MOCK_KEY"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            
            combined_prompt = f"System Instruction: {system_prompt}\n\nUser Prompt: {prompt}" if system_prompt else prompt
            payload = {
                "contents": [{"parts": [{"text": combined_prompt}]}]
            }
            if json_format:
                payload["generationConfig"] = {"responseMimeType": "application/json"}

            try:
                raw_res = make_post_request(url, headers, payload)
                data = json.loads(raw_res)
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                logger.error(f"[ModelRouter] Gemini API failed: {e}")
                return self._get_fallback_mock_response(prompt, json_format)

        # 3. GROQ CLOUD ROUTING
        elif provider == "groq":
            api_key = settings.GROQ_API_KEY or "MOCK_KEY"
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": "llama3-8b-8192",
                "messages": messages,
                "temperature": 0.2
            }
            if json_format:
                payload["response_format"] = {"type": "json_object"}

            try:
                raw_res = make_post_request(url, headers, payload)
                data = json.loads(raw_res)
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"[ModelRouter] Groq API failed: {e}")
                return self._get_fallback_mock_response(prompt, json_format)

        else:
            return self._get_fallback_mock_response(prompt, json_format)

    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None, provider: Optional[str] = None):
        """Streams LLM inference tokens in real-time line-by-line as Ollama generates them."""
        if not provider:
            provider = settings.ACTIVE_LLM_PROVIDER.lower()
        else:
            provider = provider.lower()

        if provider == "local" and self.check_local_ollama_health():
            url = f"{settings.OLLAMA_HOST}/api/generate"
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": True,
                "keep_alive": "10m"
            }
            if system_prompt:
                payload["system"] = system_prompt

            try:
                import httpx
                with httpx.Client(timeout=180.0) as client:
                    with client.stream("POST", url, headers=headers, json=payload) as response:
                        for line in response.iter_lines():
                            if line:
                                try:
                                    data = json.loads(line)
                                    token = data.get("response", "")
                                    if token:
                                        yield token
                                except Exception:
                                    pass
                return
            except Exception as e:
                logger.warning(f"[ModelRouter] Streaming failed: {e}. Yielding fallback stream.")

        # Fallback non-streaming response as single chunk yield
        full_res = self.generate(prompt=prompt, system_prompt=system_prompt, provider=provider)
        yield full_res

    def _get_fallback_mock_response(self, prompt: str, json_format: bool) -> str:
        """Fallback mock response when all LLM providers are unavailable."""
        if json_format:
            return json.dumps({
                "question": "How do you structure database connection pooling in your project?",
                "focus_area": "Database Systems",
                "type": "Technical",
                "score": 85,
                "suggestions": ["Mention connection pool size limits", "Discuss transaction isolation levels"],
                "missing_keywords": ["connection pooling", "transaction isolation"],
                "model_answer": "In production, database connection pooling manages a reusable queue of database connections to minimize overhead."
            })
        
        return "Deterministic local offline placeholder response optimized for technical interview coaching."

def run_llm_generation(prompt: str, system_prompt: Optional[str] = None, json_format: bool = False, provider: Optional[str] = None) -> str:
    """Standalone module function executing prompt generation through ModelRouter."""
    router = ModelRouter()
    return router.generate(prompt=prompt, system_prompt=system_prompt, json_format=json_format, provider=provider)
