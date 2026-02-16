"""
Evaluation metrics for TTP/IOC extraction and narrative quality.
M6 — Evaluation & validation.
"""

from typing import Any


def extract_entities_from_text(text: str) -> set[str]:
    """Extract TTPs, CVEs, and generic IOCs from text for evaluation."""
    from .preprocessing import extract_iocs

    iocs = extract_iocs(text)
    return set(iocs)


def precision_recall_f1(pred: set[str], gold: set[str]) -> dict[str, float]:
    """Compute precision, recall, F1 for entity extraction."""
    if not pred and not gold:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    if not pred:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    if not gold:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    tp = len(pred & gold)
    p = tp / len(pred) if pred else 0.0
    r = tp / len(gold) if gold else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    return {"precision": round(p, 4), "recall": round(r, 4), "f1": round(f1, 4)}


def rouge_n(reference: str, hypothesis: str, n: int = 2) -> dict[str, float]:
    """ROUGE-N: n-gram overlap recall."""
    ref_tokens = reference.lower().split()
    hyp_tokens = hypothesis.lower().split()

    def ngrams(tokens: list[str], n: int) -> set[tuple[str, ...]]:
        return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}

    ref_ng = ngrams(ref_tokens, n)
    hyp_ng = ngrams(hyp_tokens, n)

    if not ref_ng:
        return {"rouge_precision": 0.0, "rouge_recall": 0.0, "rouge_f1": 0.0}

    overlap = len(ref_ng & hyp_ng)
    prec = overlap / len(hyp_ng) if hyp_ng else 0.0
    rec = overlap / len(ref_ng)
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0

    return {
        "rouge_precision": round(prec, 4),
        "rouge_recall": round(rec, 4),
        "rouge_f1": round(f1, 4),
    }


def bleu_simple(reference: str, hypothesis: str) -> float:
    """Simplified BLEU: 1-gram precision."""
    ref_words = reference.lower().split()
    hyp_words = hypothesis.lower().split()
    if not hyp_words:
        return 0.0
    matches = sum(1 for w in hyp_words if w in ref_words)
    return round(matches / len(hyp_words), 4)


def evaluate_extraction(pred_entities: list[str], gold_entities: list[str]) -> dict[str, float]:
    """Evaluate entity extraction: precision, recall, F1."""
    pred_set = set(pred_entities)
    gold_set = set(gold_entities)
    return precision_recall_f1(pred_set, gold_set)


def evaluate_narrative(reference: str, hypothesis: str) -> dict[str, float]:
    """Evaluate narrative quality: ROUGE-2, BLEU."""
    r2 = rouge_n(reference, hypothesis, n=2)
    bleu = bleu_simple(reference, hypothesis)
    return {
        "rouge2_recall": r2["rouge_recall"],
        "rouge2_f1": r2["rouge_f1"],
        "bleu_simple": bleu,
    }


def run_eval_on_dataset(csv_path: str) -> dict[str, Any]:
    """
    Run evaluation on a CSV with input_text, target_report.
    Uses rule-based extraction; gold entities from target_report.
    """
    import pandas as pd

    df = pd.read_csv(csv_path, encoding="utf-8")
    from .inference import generate_stub_report

    all_p = []
    all_r = []
    all_f1 = []
    all_rouge = []
    all_bleu = []

    for _, row in df.head(100).iterrows():
        inp = row.get("input_text", "")
        gold_report = str(row.get("target_report", ""))
        report = generate_stub_report(inp)
        pred = set(report.get("ttps", []) + report.get("cves", []) + report.get("iocs", []))
        gold = extract_entities_from_text(gold_report)
        m = precision_recall_f1(pred, gold)
        all_p.append(m["precision"])
        all_r.append(m["recall"])
        all_f1.append(m["f1"])
        nr = evaluate_narrative(gold_report, report.get("executive_summary", ""))
        all_rouge.append(nr["rouge2_f1"])
        all_bleu.append(nr["bleu_simple"])

    def avg(x):
        return round(sum(x) / len(x), 4) if x else 0.0

    return {
        "extraction": {"precision": avg(all_p), "recall": avg(all_r), "f1": avg(all_f1)},
        "narrative": {"rouge2_f1": avg(all_rouge), "bleu_simple": avg(all_bleu)},
        "n_samples": len(all_p),
    }


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/val.csv")
    args = ap.parse_args()
    results = run_eval_on_dataset(args.data)
    print("Evaluation results:", results)
