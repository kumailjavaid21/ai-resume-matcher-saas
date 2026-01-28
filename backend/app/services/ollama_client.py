import json
import logging
from typing import Any

import requests

from backend.app.core.config import settings

logger = logging.getLogger("ollama")


class OllamaClient:
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.chat_model = settings.ollama_chat_model
        self.embed_model = settings.ollama_embed_model
        self.timeout = settings.ollama_timeout
        self.session = requests.Session()

    def generate_json(self, prompt: str, schema_hint: str) -> dict[str, Any]:
        payload = {
            "model": self.chat_model,
            "messages": [
                {
                    "role": "user",
                    "content": f"{schema_hint}\n\n{prompt}\n\nRespond with strict JSON and nothing else.",
                }
            ],
            "stream": False,
            "format": "json",
        }
        response = self.session.post(f"{self.base_url}/api/chat", json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content", "")
        if not isinstance(content, str):
            raise ValueError("Ollama chat response did not include a textual message.")
        try:
            return json.loads(content.strip())
        except json.JSONDecodeError as exc:
            snippet = content.strip()[:300]
            error_message = f"Ollama returned invalid JSON (first 300 chars: {snippet})"
            logger.warning(error_message)
            raise ValueError(error_message) from exc

    def embed(self, text: str) -> list[float]:
        payload = {"model": self.embed_model, "input": text}
        response = self.session.post(f"{self.base_url}/api/embeddings", json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        vec = data.get("embedding")
        if not isinstance(vec, list):
            snippet = response.text[:300]
            raise RuntimeError(
                f"Ollama embeddings response missing vector (first 300 chars: {snippet})"
            )
        return vec
