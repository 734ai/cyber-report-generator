"""
Export reports to PDF and Markdown.
M7 — Extras.
"""

from pathlib import Path
from typing import Any


def report_to_markdown(report: dict[str, Any]) -> str:
    """Convert report dict to Markdown string."""
    from .inference import format_report_markdown

    return format_report_markdown(report)


def export_markdown(report: dict[str, Any], path: str | Path) -> Path:
    """Export report to Markdown file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    md = report_to_markdown(report)
    path.write_text(md, encoding="utf-8")
    return path


def export_html(report: dict[str, Any], path: str | Path) -> Path:
    """Export report to HTML file (print-friendly, convertible to PDF via browser)."""
    try:
        import markdown
    except ImportError:
        raise ImportError("Install markdown: pip install markdown") from None

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    md = report_to_markdown(report)
    html_content = markdown.markdown(md, extensions=["tables"])
    full_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>Cyber Report</title>
    <style>body{{font-family:sans-serif;margin:2em;line-height:1.6;max-width:800px}}
    table{{border-collapse:collapse;width:100%;margin:1em 0}} td,th{{border:1px solid #ccc;padding:8px}}
    h2{{margin-top:1.5em}} code{{background:#f4f4f4;padding:2px 6px}}
    @media print {{ body {{ margin:1em }} }}
    </style></head><body>{html_content}</body></html>"""
    path.write_text(full_html, encoding="utf-8")
    return path
