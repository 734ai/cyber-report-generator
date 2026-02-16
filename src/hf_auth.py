"""
Load Hugging Face API key from huggingface-api.json and authenticate.
"""

import json
import os
from pathlib import Path


def _config_path() -> Path:
    """Path to huggingface-api.json (project root)."""
    return Path(__file__).resolve().parent.parent / "huggingface-api.json"


def get_hf_token() -> str | None:
    """
    Get HF token from huggingface-api.json or HF_TOKEN env var.
    Returns None if not found.
    """
    # Prefer env (for Spaces / CI)
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if token:
        return token

    path = _config_path()
    if path.exists():
        try:
            data = json.loads(path.read_text())
            return data.get("key") or data.get("token")
        except (json.JSONDecodeError, KeyError):
            pass
    return None


def login() -> bool:
    """
    Log in to Hugging Face Hub using token from huggingface-api.json or env.
    Returns True if login succeeded.
    """
    token = get_hf_token()
    if not token:
        return False
    try:
        from huggingface_hub import login

        login(token=token)
        return True
    except ImportError:
        os.environ["HF_TOKEN"] = token
        return True
