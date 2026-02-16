"""
Inference module for report generation.
Loads fine-tuned Flan-T5 model or falls back to base model.
"""

import os
from typing import Any
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from .preprocessing import extract_iocs, parse_input, preprocess_for_model
from .risk_scoring import compute_risk_score, extract_severities

# Global variables for model/tokenizer to direct verify
_model = None
_tokenizer = None
MODEL_DIR = "models/flan_t5_report"
BASE_MODEL = "google/flan-t5-base"

def _load_model():
    """Lazy load model and tokenizer."""
    global _model, _tokenizer
    if _model is not None:
        return _model, _tokenizer
    
    # Check if fine-tuned model exists
    path_to_load = MODEL_DIR if os.path.exists(MODEL_DIR) and os.listdir(MODEL_DIR) else BASE_MODEL
    print(f"Loading model from {path_to_load}...")
    
    try:
        _tokenizer = AutoTokenizer.from_pretrained(path_to_load)
        _model = AutoModelForSeq2SeqLM.from_pretrained(path_to_load)
    except Exception as e:
        print(f"Error loading model from {path_to_load}: {e}")
        # Fallback to base model if fine-tuned failed to load
        if path_to_load != BASE_MODEL:
             print(f"Falling back to base model {BASE_MODEL}")
             _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
             _model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL)
        else:
             raise e
             
    return _model, _tokenizer

def generate_report(raw_input: str) -> dict[str, Any]:
    """
    Generate a cybersecurity report from logs/text/JSON using the model.
    """
    parsed = parse_input(raw_input)
    
    if parsed["type"] == "empty":
        return {
            "executive_summary": "No input provided. Paste logs or upload JSON to generate a report.",
            "technical_summary": "",
            "ttps": [],
            "iocs": [],
            "cves": [],
            "threat_actors": [],
            "risk_score": 0,
            "confidence": 0.0,
        }

    # Extract entities using heuristics (still useful for structured data)
    full_text = parsed["content"]
    iocs_raw = extract_iocs(full_text)
    
    # Categorize IOCs
    ttps: list[str] = []
    cves: list[str] = []
    iocs: list[str] = []
    
    for x in iocs_raw:
        if x.startswith("T") and x[1:].replace(".", "").isdigit():
            ttps.append(x)
        elif x.upper().startswith("CVE-"):
            cves.append(x)
        else:
            iocs.append(x)

    # Generate Narrative using Model
    model, tokenizer = _load_model()
    
    # Preprocess input for model
    model_input_text = preprocess_for_model(raw_input)
    
    # Tokenize
    inputs = tokenizer(model_input_text, return_tensors="pt", max_length=512, truncation=True)
    
    # Generate
    # Use standard generation parameters
    outputs = model.generate(
        inputs.input_ids, 
        max_length=128, 
        num_beams=4, 
        early_stopping=True
    )
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Executive summary from model
    num_events = len(parsed["lines"])
    exec_summary = generated_text

    # Technical summary (could also be generated, but let's keep it structured for now)
    tech_summary = (
        f"Input type: {parsed['type']}. {num_events} events processed. "
        f"Detected {len(ttps)} TTPs, {len(cves)} CVEs, and {len(iocs)} IOCs."
    )

    # Risk scoring (M4)
    severities = extract_severities(full_text)
    risk, confidence = compute_risk_score(ttps, cves, iocs, severities, num_events)
    
    return {
        "executive_summary": exec_summary,
        "technical_summary": tech_summary,
        "ttps": ttps,
        "iocs": iocs,
        "cves": cves,
        "threat_actors": [],
        "risk_score": risk,
        "confidence": round(confidence, 2),
    }


def _tag_entity(text: str, tag: str) -> str:
    """Tag entity for highlighting (Markdown inline code)."""
    return f"`{text}`"


def format_report_markdown(report: dict[str, Any]) -> str:
    """Format report dict as Markdown with TTP tagging, IOC highlighting, summary tables."""
    sections = [
        "## Executive Summary",
        report["executive_summary"],
        "",
        "## Technical Summary",
        report["technical_summary"],
        "",
        "## Extracted Entities",
        "| Type | Count | Sample |",
        "|------|-------|--------|",
        f"| **TTPs** | {len(report['ttps'])} | {', '.join(_tag_entity(t, 'ttp') for t in report['ttps'][:5]) or '-'} |",
        f"| **IOCs** | {len(report['iocs'])} | {', '.join(_tag_entity(i, 'ioc') for i in report['iocs'][:5]) or '-'} |",
        f"| **CVEs** | {len(report['cves'])} | {', '.join(_tag_entity(c, 'cve') for c in report['cves'][:5]) or '-'} |",
        "",
        "## Risk Assessment",
        f"- **Risk Score:** {report['risk_score']}/100",
        f"- **Confidence:** {report['confidence']}",
        "",
    ]

    if report["ttps"]:
        sections.extend(["### TTPs (tagged)", ", ".join(_tag_entity(t, "ttp") for t in report["ttps"]), ""])
    if report["iocs"]:
        sections.extend(["### IOCs (highlighted)", ", ".join(_tag_entity(i, "ioc") for i in report["iocs"][:25]), ""])
    if report["cves"]:
        sections.extend(["### CVEs", ", ".join(_tag_entity(c, "cve") for c in report["cves"]), ""])

    # Explainability: contributing entities
    contrib = report.get("ttps", []) + report.get("cves", [])[:5] + report.get("iocs", [])[:5]
    if contrib:
        sections.extend(
            ["## Explainability", "Contributing entities (driving risk score):", ", ".join(_tag_entity(x, "") for x in contrib), ""]
        )

    return "\n".join(sections)
