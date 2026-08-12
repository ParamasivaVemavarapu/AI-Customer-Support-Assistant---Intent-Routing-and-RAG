"""Offline routing, escalation, and RAG faithfulness evaluation."""

import argparse
import json
import re
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))
from app.intent import route_intent  # noqa: E402


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def normalize(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def evaluate(rows: list[dict], escalation_threshold: float) -> dict[str, float]:
    intent_hits = escalation_tp = escalation_fn = 0
    supported = claims = 0
    for row in rows:
        route = route_intent(row["message"])
        intent_hits += route.intent == row["expected_intent"]
        predicted_escalation = bool(route.urgent_reason) or row["retrieval_score"] < escalation_threshold
        escalation_tp += predicted_escalation and row["expected_escalation"]
        escalation_fn += (not predicted_escalation) and row["expected_escalation"]
        evidence = normalize(" ".join(row["evidence"]))
        for claim in row["answer_claims"]:
            claims += 1
            supported += normalize(claim) in evidence
    return {
        "examples": len(rows),
        "intent_accuracy": intent_hits / len(rows),
        "escalation_recall": escalation_tp / (escalation_tp + escalation_fn),
        "rag_faithfulness": supported / claims if claims else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path(__file__).with_name("support_eval.jsonl"))
    parser.add_argument("--escalation-threshold", type=float, default=0.35)
    args = parser.parse_args()
    metrics = evaluate(load_jsonl(args.dataset), args.escalation_threshold)
    print(json.dumps(metrics, indent=2))
    assert metrics["intent_accuracy"] >= 0.80
    assert metrics["escalation_recall"] >= 0.90
    assert metrics["rag_faithfulness"] >= 0.90


if __name__ == "__main__":
    main()
