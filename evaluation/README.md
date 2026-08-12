# Customer Support Evaluation

The versioned synthetic set exercises the repository's real deterministic intent router and escalation policy. It also includes atomic answer claims and approved evidence for a transparent faithfulness check.

Metrics:

- **Intent accuracy:** correctly routed messages divided by all labeled messages.
- **Escalation recall:** correctly escalated positive cases divided by all cases requiring escalation.
- **RAG faithfulness:** normalized answer claims found in the supplied evidence divided by all evaluated claims.

Run:

```bash
python evaluation/evaluate.py
```

The script prints JSON and enforces regression thresholds. The fixture is intentionally small and synthetic; expand it with de-identified, independently labeled traffic before making production-quality claims.
