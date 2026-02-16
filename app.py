"""
AI-Powered Cyber Report Generator — Gradio app.
M5 — Final UI with text/JSON input, tables, highlighted entities.
M7 — Export (MD/HTML), batch mode.
"""

import tempfile
from pathlib import Path

import gradio as gr

# Authenticate with Hugging Face using huggingface-api.json
from src.hf_auth import login as hf_login

if hf_login():
    pass  # Authenticated for model downloads

from src.export import export_markdown, export_html
from src.inference import format_report_markdown, generate_report as run_inference_report
from src.synthetic_logs import get_sample_json, get_sample_text


def generate_report(raw_input: str) -> tuple[str, list[list[str]], str]:
    """Generate report and return (markdown, entity_table, risk_summary)."""
    report = run_inference_report(raw_input)
    md = format_report_markdown(report)

    # Entity table: Type | Count | Items
    rows: list[list[str]] = []
    for label, items in [
        ("TTPs", report.get("ttps", [])),
        ("IOCs", report.get("iocs", [])[:25]),
        ("CVEs", report.get("cves", [])),
    ]:
        for i, item in enumerate(items):
            rows.append([label, str(i + 1), item])
    if not rows:
        rows = [["—", "—", "No entities extracted"]]

    risk_summary = f"Risk Score: **{report['risk_score']}/100** | Confidence: **{report['confidence']}**"
    return md, rows, risk_summary


def load_uploaded_file(file) -> str:
    """Load content from uploaded JSON/text file."""
    if file is None:
        return ""
    with open(file.name, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


with gr.Blocks(title="Cyber Report Generator") as demo:
    gr.Markdown(
        """
        # AI-Powered Cyber Report Generator
        Generate structured cybersecurity incident reports from logs, alerts, and threat intel feeds.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            inp = gr.Textbox(
                label="Logs / Alerts",
                placeholder="Paste text logs or JSON here...",
                lines=12,
                max_lines=24,
            )
            file_upload = gr.File(
                label="Or upload JSON/log file",
                file_types=[".json", ".jsonl", ".txt", ".log"],
            )
            with gr.Row():
                btn_sample_text = gr.Button("Sample Text", size="sm")
                btn_sample_json = gr.Button("Sample JSON", size="sm")
                btn_generate = gr.Button("Generate Report", variant="primary")
            with gr.Row():
                btn_export_md = gr.Button("Export Markdown", size="sm")
                btn_export_html = gr.Button("Export HTML", size="sm")

        with gr.Column(scale=1):
            with gr.Tabs():
                with gr.Tab("Report"):
                    out_md = gr.Markdown(label="Report", value="*Report will appear here.*")
                with gr.Tab("Entities Table"):
                    out_table = gr.Dataframe(
                        headers=["Type", "#", "Entity"],
                        label="Extracted Entities",
                        interactive=False,
                    )
            out_risk = gr.Markdown(value="")
            export_file = gr.File(label="Download report", visible=False)

    def on_generate(text: str):
        md, rows, risk = generate_report(text)
        return md, rows, risk

    def on_file_upload(file):
        content = load_uploaded_file(file)
        return content

    def export_md_file(text: str):
        report = run_inference_report(text)
        p = Path(tempfile.gettempdir()) / "cyber_report.md"
        export_markdown(report, p)
        return str(p)

    def export_html_file(text: str):
        report = run_inference_report(text)
        p = Path(tempfile.gettempdir()) / "cyber_report.html"
        export_html(report, p)
        return str(p)

    def do_export_md(text: str):
        p = export_md_file(text)
        return gr.update(value=p, visible=True)

    def do_export_html(text: str):
        p = export_html_file(text)
        return gr.update(value=p, visible=True)

    btn_generate.click(fn=on_generate, inputs=inp, outputs=[out_md, out_table, out_risk])
    btn_export_md.click(fn=do_export_md, inputs=inp, outputs=export_file)
    btn_export_html.click(fn=do_export_html, inputs=inp, outputs=export_file)
    btn_sample_text.click(fn=get_sample_text, outputs=inp)
    btn_sample_json.click(fn=get_sample_json, outputs=inp)
    file_upload.change(fn=on_file_upload, inputs=file_upload, outputs=inp)

    gr.Markdown(
        """
        ---
        **Usage:** Paste logs, upload JSON/JSONL, or use sample data. Extracts TTPs, IOCs, CVEs → executive summary, technical notes, risk score.
        """
    )

if __name__ == "__main__":
    demo.launch(
        theme=gr.themes.Soft(primary_hue="slate"),
        server_name="0.0.0.0",  # Allow external access (Hugging Face Spaces)
    )
