import json
import sys
from pathlib import Path

import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR))

from backend.app.core.config import settings


def _call_version():
    response = requests.get(f"{settings.ollama_base_url}/api/version", timeout=settings.ollama_timeout)
    response.raise_for_status()
    data = response.json()
    print("  /api/version ->", data.get("name") or "version info retrieved")


def _call_chat():
    payload = {
        "model": settings.ollama_chat_model,
        "messages": [
            {
                "role": "user",
                "content": "Return JSON {\"status\":\"online\"} and nothing else.",
            }
        ],
        "stream": False,
        "format": "json",
    }
    response = requests.post(f"{settings.ollama_base_url}/api/chat", json=payload, timeout=settings.ollama_timeout)
    response.raise_for_status()
    data = response.json()
    content = data.get("message", {}).get("content", "")
    json.loads(content)
    print("  /api/chat -> valid JSON response")


def _call_embeddings():
    prompt_text = "hello world"
    print(f"    using model={settings.ollama_embed_model} prompt_len={len(prompt_text)}")
    payload = {"model": settings.ollama_embed_model, "prompt": prompt_text}
    response = requests.post(
        f"{settings.ollama_base_url}/api/embeddings", json=payload, timeout=settings.ollama_timeout
    )
    response.raise_for_status()
    data = response.json()
    vec = data.get("embedding")
    keys = ", ".join(data.keys())
    snippet = response.text[:300]
    if not isinstance(vec, list):
        raise RuntimeError(
            f"Ollama embeddings response missing vector; keys=[{keys}]; sample={snippet}"
        )
    if len(vec) <= 0:
        raise RuntimeError(
            f"Ollama embeddings vector empty; keys=[{keys}]; sample={snippet}"
        )
    if not all(isinstance(v, (float, int)) for v in vec):
        raise RuntimeError(
            f"Ollama embeddings vector contains non-numeric entries; keys=[{keys}]; sample={snippet}"
        )
    print(f"  /api/embeddings -> embeddings retrieved (len={len(vec)})")


def main():
    print("Testing Ollama endpoints at", settings.ollama_base_url)
    tests = (
        ("GET /api/version", _call_version),
        ("POST /api/chat", _call_chat),
        ("POST /api/embeddings", _call_embeddings),
    )
    success = True
    for name, fn in tests:
        try:
            fn()
            print(f"PASS: {name}")
        except Exception as exc:
            print(f"FAIL: {name} -> {exc}")
            success = False
    if success:
        print("All Ollama checks passed.")
        sys.exit(0)
    print("One or more Ollama checks failed.")
    sys.exit(1)


if __name__ == "__main__":
    main()
