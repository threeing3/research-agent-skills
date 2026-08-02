# Experiment Requests

Use this contract when manuscript claims need evidence that is missing,
invalid, underpowered, unfair, or not paper-ready.

Create `research_state/paper/experiment_requests/<request-id>.json`:

```json
{
  "schema_version": "ai-research-writing/experiment-request-v1",
  "request_id": "robustness-cross-dataset-001",
  "source_claim_ids": ["C3"],
  "reason": "The robustness claim lacks cross-dataset evidence.",
  "question": "Does method X retain its gain on dataset Z?",
  "required_comparisons": ["method X", "baseline Y"],
  "required_datasets": ["dataset Z"],
  "required_metrics": ["accuracy", "latency"],
  "acceptance_evidence": [
    "verified run records for all declared seeds",
    "recomputed aggregate with uncertainty"
  ],
  "priority": "blocking",
  "status": "requested"
}
```

Do not prescribe implementation patches, remote commands, or result values.
`research-experiment-lab` owns the plan, budget, runs, debugging, and
verification. When results return, validate that the response links this
request and satisfies every acceptance-evidence item before revising claims.

