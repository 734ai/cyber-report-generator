"""Tests for evaluation metrics."""

from src.evaluation import precision_recall_f1, rouge_n, bleu_simple


def test_precision_recall_f1():
    pred = {"a", "b", "c"}
    gold = {"b", "c", "d"}
    m = precision_recall_f1(pred, gold)
    assert abs(m["precision"] - 2 / 3) < 0.01
    assert abs(m["recall"] - 2 / 3) < 0.01
    assert abs(m["f1"] - 2 / 3) < 0.01


def test_rouge_n():
    ref = "the quick brown fox"
    hyp = "the quick fox"
    m = rouge_n(ref, hyp, n=2)
    assert m["rouge_recall"] > 0


def test_bleu_simple():
    ref = "the quick brown fox"
    hyp = "the quick"
    b = bleu_simple(ref, hyp)
    assert b > 0
    assert b <= 1.0
