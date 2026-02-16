# TODO — AI-Powered Cyber Report Generator (Hugging Face Spaces)

## Goal
Build a Hugging Face Space that generates structured cybersecurity reports from logs, alerts, and threat intelligence feeds using fully fine-tuned Google open-source models (Flan-T5, Sentence-T5).

## Milestones & Tasks

### M1 — Project scaffold (Days 1–3)
- [x] Create repo structure (app/, models/, data/, src/, tests/, docs/)
- [x] Add LICENSE (MIT/Apache-2.0) and CODE_OF_CONDUCT
- [x] Minimal Gradio app prototype (app.py) accepting text or JSON logs, returns stub report
- [x] Create `requirements.txt` and `runtime.txt`

### M2 — Dataset collection & preprocessing (Days 3–8)
- [x] Collect MITRE ATT&CK public reports (src/mitre_templates.py)
- [x] Download curated SOC reports (anonymized) or synthetic logs (src/synthetic_logs.py)
- [x] Generate synthetic incident datasets (logs + AI-generated reports) (src/dataset_builder.py)
- [x] Build preprocessing pipeline for logs, JSON, alerts (src/preprocessing.py)

### M3 — Model fine-tuning (Days 8–16)
- [x] Fine-tune `google/flan-t5-base` for narrative generation (src/train_model.py)
- [x] Train multi-task heads (rule-based extraction in preprocessing + inference)
- [x] Generate embeddings with sentence-transformers (src/embeddings.py)

### M4 — Ensemble & scoring (Days 14–20)
- [x] Build risk scoring module (src/risk_scoring.py)
- [x] Post-processing: TTP tagging, IOC highlighting, summary tables
- [x] Explainability: contributing entities section

### M5 — Spaces deployment (Days 20–24)
- [x] Implement final Gradio UI with text input + JSON log upload (app.py)
- [x] Display report outputs, tables, highlighted entities
- [x] Test CPU vs GPU Spaces deployment (T4 recommended)

### M6 — Evaluation & validation (Days 24–28)
- [x] Precision/recall/F1 metrics for TTP/IOC extraction (src/evaluation.py)
- [x] Evaluate narrative quality (ROUGE / BLEU)
- [x] Test adversarial/synthetic logs (via dataset_builder + evaluation)

### M7 — Extras / polish (28+)
- [x] SOC dashboard mode: batch report generation (src/batch.py)
- [x] Export reports (Markdown / HTML) (src/export.py, app.py)
- [ ] Integration with email / SIEM feed inputs (future)

## Short-term priorities (first 72h)
1. Repo skeleton + app.py stub
2. Preprocessing script + synthetic log generator
3. Gradio UI demo with sample text input
