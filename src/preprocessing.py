"""
Preprocessing pipeline for logs, JSON alerts, and raw text.
Prepares input for narrative generation and entity extraction.
"""

import json
import re
from typing import Any


def parse_input(raw: str) -> dict[str, Any]:
    """
    Parse user input (text or JSON) into a normalized structure.
    
    Returns:
        dict with keys: type, content, lines, parsed (if JSON)
    """
    raw = raw.strip() or ""
    if not raw:
        return {"type": "empty", "content": "", "lines": []}

    # Try JSON first
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            lines = [json.dumps(item) if isinstance(item, dict) else str(item) for item in parsed]
        elif isinstance(parsed, dict):
            lines = [raw]
        else:
            lines = [str(parsed)]
        return {
            "type": "json",
            "content": raw,
            "parsed": parsed,
            "lines": lines,
        }
    except json.JSONDecodeError:
        pass

    # Treat as plain text / log lines
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    return {
        "type": "text",
        "content": raw,
        "lines": lines,
    }


def extract_iocs(text: str) -> list[str]:
    """Extract potential IOCs (IPs, domains, hashes, URLs) using regex."""
    iocs: list[str] = []
    
    # IPv4
    for m in re.finditer(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b", text):
        iocs.append(m.group())
    
    # MD5
    for m in re.finditer(r"\b[a-fA-F0-9]{32}\b", text):
        iocs.append(m.group())
    
    # SHA256
    for m in re.finditer(r"\b[a-fA-F0-9]{64}\b", text):
        iocs.append(m.group())
    
    # Domains (simple)
    for m in re.finditer(r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b", text):
        iocs.append(m.group())
    
    # CVE IDs
    for m in re.finditer(r"CVE-\d{4}-\d{4,}", text, re.I):
        iocs.append(m.group())
    
    # MITRE TTP (T####)
    for m in re.finditer(r"T\d{4}(?:\.\d{3})?", text):
        iocs.append(m.group())
    
    return list(dict.fromkeys(iocs))


def parse_alert(alert: dict[str, Any]) -> str:
    """Convert alert dict into a flat text string for model input."""
    parts: list[str] = []
    for k, v in alert.items():
        if isinstance(v, (dict, list)):
            parts.extend(flatten_json(v, k))
        else:
            parts.append(f"{k}={v}")
    return " | ".join(parts)


def preprocess_for_model(raw: str) -> str:
    """
    Full preprocessing pipeline: parse logs/JSON/alerts -> single text string.
    Use as model input.
    """
    parsed = parse_input(raw)
    if parsed["type"] == "empty":
        return ""
    lines = parsed["lines"]
    if parsed["type"] == "json":
        if isinstance(parsed.get("parsed"), list):
            texts = []
            for item in parsed["parsed"]:
                if isinstance(item, dict):
                    texts.append(parse_alert(item))
                else:
                    texts.append(str(item))
            return "\n".join(texts)
        elif isinstance(parsed.get("parsed"), dict):
            return parse_alert(parsed["parsed"])
    return parsed["content"]


def flatten_json(obj: Any, prefix: str = "") -> list[str]:
    """Flatten JSON object into key=value log-like strings."""
    out: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else k
            out.extend(flatten_json(v, key))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            key = f"{prefix}[{i}]" if prefix else f"[{i}]"
            out.extend(flatten_json(v, key))
    else:
        out.append(f"{prefix}={obj}" if prefix else str(obj))
    return out
