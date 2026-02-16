"""
Dataset builder: synthetic logs + AI-generated report targets.
Produces train.csv and val.csv for model fine-tuning.
"""

import csv
import json
import random
from pathlib import Path
from typing import Optional

from .mitre_templates import ATTACK_WRITEUPS, INCIDENT_TEMPLATES
from .synthetic_logs import generate_single_log


def logs_to_text(logs: list[str]) -> str:
    """Convert list of JSON log strings to single text block."""
    return "\n".join(logs)


def generate_report_target(logs_text: str, ttps: list[str], cves: list[str]) -> str:
    """Generate a target report summary from logs and extracted entities."""
    parts: list[str] = []
    if ttps:
        for t in ttps[:3]:
            if t in ATTACK_WRITEUPS:
                parts.append(ATTACK_WRITEUPS[t])
    if not parts and INCIDENT_TEMPLATES:
        _, summary = random.choice(INCIDENT_TEMPLATES)
        parts.append(summary)
    if not parts:
        parts.append(
            f"Incident involving {len(ttps)} TTP(s), {len(cves)} CVE(s). "
            "Further analysis recommended."
        )
    return " ".join(parts)


def build_dataset(
    num_train: int = 500,
    num_val: int = 100,
    samples_per_example: int = 5,
    output_dir: str = "data",
) -> tuple[Path, Path]:
    """
    Build train and validation CSV datasets.
    Format: input_text, target_report
    """
    from .preprocessing import extract_iocs

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    train_path = output_path / "train.csv"
    val_path = output_path / "val.csv"

    def _generate_split(n: int) -> list[tuple[str, str]]:
        rows: list[tuple[str, str]] = []
        for _ in range(n):
            logs = [generate_single_log() for _ in range(samples_per_example)]
            text = logs_to_text(logs)
            iocs = extract_iocs(text)
            ttps = [x for x in iocs if x.startswith("T") and x[1:].replace(".", "").isdigit()]
            cves = [x for x in iocs if x.upper().startswith("CVE-")]
            target = generate_report_target(text, ttps, cves)
            rows.append((text, target))
        return rows

    for path, n in [(train_path, num_train), (val_path, num_val)]:
        rows = _generate_split(n)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["input_text", "target_report"])
            w.writerows(rows)
        print(f"Wrote {len(rows)} rows -> {path}")

    return train_path, val_path


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--train", type=int, default=500)
    ap.add_argument("--val", type=int, default=100)
    ap.add_argument("--output", default="data")
    args = ap.parse_args()
    build_dataset(num_train=args.train, num_val=args.val, output_dir=args.output)
