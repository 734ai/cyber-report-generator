"""
Batch report generation (SOC dashboard mode).
M7 — Extras.
"""

from typing import Any

from .inference import generate_stub_report


def batch_generate(texts: list[str]) -> list[dict[str, Any]]:
    """Generate reports for multiple log inputs."""
    return [generate_stub_report(t) for t in texts]


def batch_generate_from_chunks(raw: str, chunk_sep: str = "\n\n") -> list[dict[str, Any]]:
    """
    Split input by chunk_sep and generate one report per chunk.
    Useful for multiple incidents in one paste.
    """
    chunks = [c.strip() for c in raw.split(chunk_sep) if c.strip()]
    return batch_generate(chunks)


def batch_report_summary(reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate batch reports into summary."""
    total_ttps = sum(len(r.get("ttps", [])) for r in reports)
    total_iocs = sum(len(r.get("iocs", [])) for r in reports)
    total_cves = sum(len(r.get("cves", [])) for r in reports)
    max_risk = max(r.get("risk_score", 0) for r in reports) if reports else 0
    return {
        "n_reports": len(reports),
        "total_ttps": total_ttps,
        "total_iocs": total_iocs,
        "total_cves": total_cves,
        "max_risk_score": max_risk,
    }
