---
title: Cyber Report Generator
emoji: 🔐
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: "4.44.1"
python_version: "3.10"
app_file: app.py
pinned: false
license: mit
---

# Cyber Report Generator

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/unit731/cyber-report-generator)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Executive Summary

The **Cyber Report Generator** is an AI-driven automated reporting solution designed to streamline the analysis of cybersecurity incidents. Leveraging a fine-tuned **Google Flan-T5** model, the system ingests raw logs, threat intelligence feeds, and JSON alerts to produce structured, actionable executive and technical summaries.

By automating the correlation of Indicators of Compromise (IOCs), CVEs, and MITRE ATT&CK TTPs, this tool significantly reduces the mean time to report (MTTR) for security operations centers (SOCs) and incident response teams.

---

## Key Capabilities

*   **Automated Incident Narration**: Transforms unstructured logs and raw JSON data into coherent, professional-grade incident reports.
*   **Intelligent Entity Extraction**:
    *   **IOCs**: Identifies IP addresses, domains, and file hashes.
    *   **TTPs**: Maps observed behaviors to MITRE ATT&CK techniques (e.g., T1021.002).
    *   **CVEs**: Highlights relevant Common Vulnerabilities and Exposures.
*   **Risk Quantification**: Computes a dynamic risk score (0-100) based on the severity of detected entities and the confidence of the analysis.
*   **Multi-Format Export**: Generates reports in Markdown (for documentation) and HTML (for presentation/email).
*   **Explainable AI**: Provides a transparency layer showing which specific entities contributed to the risk assessment.

---

## Technical Architecture

The solution is built on a robust, containerized architecture deployed on Hugging Face Spaces:

1.  **Ingestion Layer**: A Gradio-based frontend accepts direct text input or file uploads (JSON/JSONL/LOG).
2.  **Preprocessing Engine**: Normalizes input data and performs heuristic extraction of IOCs using regex patterns.
3.  **Inference Engine**:
    *   Uses a fine-tuned `google/flan-t5-base` sequence-to-seqauence model for text generation.
    *   Falls back to the base model if custom weights are unavailable.
4.  **Post-Processing & Scoring**:
    *   Calculates risk scores based on weighted entity severity.
    *   Formats the output into a structured report with Markdown highlighting.

---

## Getting Started

### Prerequisites

*   Python 3.10+
*   Git

### Installation (Local)

1.  **Clone the Repository**
    ```bash
    git clone https://huggingface.co/spaces/unit731/cyber-report-generator
    cd cyber-report-generator
    ```

2.  **Environment Setup**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Launch the Application**
    ```bash
    python app.py
    ```
    Access the interface at `http://127.0.0.1:7860`.

---

## Configuration

The application supports the following environment variables:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `HF_TOKEN` | Hugging Face User Access Token (Required for model download if private) | `None` |
| `MODEL_DIR` | Local directory for fine-tuned model weights | `models/flan_t5_report` |

---

## Usage

1.  **Input Data**:
    *   Paste raw security logs (Syslog, JSON) into the "Logs / Alerts" text box.
    *   OR upload a `.json`, `.jsonl`, or `.txt` file.
    *   Use the **Sample Text** or **Sample JSON** buttons to load demo data.
2.  **Generate Report**: Click **Generate Report**. The system will process the input and display:
    *   **Executive Summary**: A high-level overview for stakeholders.
    *   **Technical Summary**: Detailed analysis for engineers.
    *   **Entities Table**: A categorized list of extracted TTPs, IOCs, and CVEs.
    *   **Risk Score**: A calculated 0-100 risk metric.
3.  **Export**: Use the **Export Markdown** or **Export HTML** buttons to download the report for distribution.

---

## Security & Disclaimer

This tool is intended for **cybersecurity analysis and reporting purposes only**.

*   **Data Privacy**: When running locally, all data remains on your machine. When using the Hugging Face Space, data is processed within the transient container environment. Avoid uploading PII or highly sensitive secrets to public Spaces.
*   **Accuracy**: AI-generated reports should be reviewed by a human analyst for accuracy. The "Confidence" score provides a heuristic reliability metric but does not guarantee correctness.

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

*Developed by Unit 731 Research.*
