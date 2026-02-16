"""
Risk scoring module: normalize severity, impact, confidence.
M4 — Ensemble & scoring.
"""

from typing import Any


# Weights for risk components
SEVERITY_WEIGHTS = {"low": 1, "medium": 2, "high": 3, "critical": 4}
TTP_WEIGHT = 15
CVE_WEIGHT = 20
IOC_WEIGHT = 5
IMPACT_WEIGHT = 0.3


def extract_severities(text: str) -> list[str]:
    """Extract severity keywords from text."""
    import re

    matches = re.findall(
        r"\b(?:severity|criticality)\s*[=:]\s*['\"]?(\w+)['\"]?",
        text,
        re.I,
    )
    return [m.lower() for m in matches if m.lower() in SEVERITY_WEIGHTS]


def compute_risk_score(
    ttps: list[str],
    cves: list[str],
    iocs: list[str],
    severities: list[str],
    num_events: int,
) -> tuple[int, float]:
    """
    Compute risk score (0–100) and confidence (0–1).
    Returns (risk_score, confidence).
    """
    base = 10
    risk = base

    # Entity counts
    risk += len(ttps) * TTP_WEIGHT
    risk += len(cves) * CVE_WEIGHT
    risk += min(len(iocs), 10) * IOC_WEIGHT

    # Severity from text
    for sev in severities:
        risk += SEVERITY_WEIGHTS.get(sev, 1) * 5

    # Event volume
    risk += min(num_events // 5, 10)

    risk = min(100, risk)

    # Confidence: higher when we have more extracted entities
    confidence = 0.3
    if ttps or cves:
        confidence = 0.6
    if ttps and (cves or iocs):
        confidence = 0.85
    if ttps and cves and iocs:
        confidence = 0.95

    return risk, round(confidence, 2)


def normalize_report_for_ui(report: dict[str, Any]) -> dict[str, Any]:
    """
    Add risk scoring and post-processing to report.
    Includes structured tables for UI display.
    """
    # Extract severities from raw content if available
    content = report.get("_raw_content", "")
    severities = extract_severities(content) if content else []

    risk, conf = compute_risk_score(
        ttps=report.get("ttps", []),
        cves=report.get("cves", []),
        iocs=report.get("iocs", []),
        severities=severities,
        num_events=report.get("_num_events", 0),
    )
    report["risk_score"] = risk
    report["confidence"] = conf

    # Summary table
    report["entity_table"] = [
        {"Type": "TTPs", "Count": len(report.get("ttps", [])), "Items": report.get("ttps", [])},
        {"Type": "IOCs", "Count": len(report.get("iocs", [])), "Items": report.get("iocs", [])[:20]},
        {"Type": "CVEs", "Count": len(report.get("cves", [])), "Items": report.get("cves", [])},
    ]

    return report
