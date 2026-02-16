---
title: Cyber Report Generator
emoji: 🔐
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: "4.36.0"
python_version: 3.10
app_file: app.py
pinned: false
license: mit
---

# AI-Powered Cyber Report Generator

Generate structured cybersecurity incident reports from logs, alerts, and threat intelligence feeds. Extracts TTPs, CVEs, IOCs, produces executive and technical summaries, and computes risk scores.

## Features

- **Text & JSON input** — Paste logs or upload JSON/JSONL files
- **Entity extraction** — TTPs, CVEs, IOCs, threat actors
- **Executive & technical summaries** — Structured report output
- **Risk scoring & explainability** — Normalized severity, confidence, contributing entities
- **Export** — Markdown and HTML downloads
- **Batch processing** — Multiple log chunks supported

## Try it

1. Paste sample logs or upload a JSON file
2. Click **Generate Report**
3. View the report, entity table, and risk assessment
4. Use **Export Markdown** or **Export HTML** to download

## Local setup

```bash
git clone https://huggingface.co/spaces/<username>/cyber-report-generator
cd cyber-report-generator
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open the URL shown in the console (typically http://127.0.0.1:7860).

## Project structure

```
.
├── app.py              # Gradio app
├── requirements.txt
├── runtime.txt
├── src/
│   ├── preprocessing.py   # Log/JSON parsing, IOC extraction
│   ├── synthetic_logs.py  # Sample data generator
│   ├── mitre_templates.py # MITRE ATT&CK templates
│   ├── dataset_builder.py # Train/val dataset builder
│   ├── train_model.py     # Flan-T5 fine-tuning
│   ├── inference.py       # Report generation
│   ├── risk_scoring.py    # Risk & confidence
│   ├── evaluation.py      # F1, ROUGE, BLEU
│   ├── export.py          # Markdown/HTML export
│   └── batch.py           # Batch report generation
├── data/
│   ├── train.csv
│   └── val.csv
└── tests/
```

## Scripts

| Command | Description |
|---------|-------------|
| `python app.py` | Launch the Gradio app |
| `python -m src.dataset_builder --train 500 --val 100` | Generate train/val datasets |
| `python -m src.synthetic_logs -n 50 -o data/synth/sample.jsonl` | Generate synthetic logs |
| `python -m src.train_model --model_name google/flan-t5-base ...` | Fine-tune Flan-T5 |
| `python -m src.evaluation --data data/val.csv` | Run evaluation metrics |

## Fine-tuning (optional)

```bash
python -m src.train_model \
  --model_name google/flan-t5-base \
  --train data/train.csv \
  --val data/val.csv \
  --output_dir models/flan_t5_report \
  --epochs 3 \
  --batch_size 8
```

## Deployment to Hugging Face Spaces

1. Create a new Space (Gradio SDK)
2. Push your code to the Space repo
3. Choose hardware: CPU (default) or GPU (T4) for fine-tuned models

**Before pushing:** Ensure `huggingface-api.json`, `.env`, and any API keys are not committed. See [SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).
