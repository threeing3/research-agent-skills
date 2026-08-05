# Shared Research State Protocol

Store state per project:

```text
research_state.json
research_state/
  literature/field_snapshot.json
  literature/search_history.jsonl
  ideation_sessions/<session-id>/session.json
  ideation_sessions/<session-id>/evidence_packet.json
  ideation_sessions/<session-id>/native_candidates.yaml
  ideation_sessions/<session-id>/cross_domain_candidates.yaml
  ideation_sessions/<session-id>/candidate_clusters.yaml
  ideation_sessions/<session-id>/events.jsonl
  review_patterns/corpus_manifest.jsonl
  review_patterns/patterns.jsonl
  review_patterns/taxonomy.yaml
  review_patterns/extraction_audit.jsonl
  review_patterns/retrieval_index/
  review_patterns/sources/openreview/<venue-id>/forums.jsonl
  review_patterns/checkpoints/<venue-id>.json
  review_patterns/logs/openreview-<venue-id>-<run-id>.log
  review_patterns/browser_import/<venue-id>/page-<offset>.json
  ideas/idea_pool.json
  ideas/mechanism_families.json
  ideas/<idea-id>/idea_contract.yaml
  ideas/<idea-id>/lineage_check.json
  ideas/<idea-id>/debate/debate_state.json
  ideas/<idea-id>/debate/cross_examination.yaml
  ideas/<idea-id>/debate/adversarial_review.yaml
  ideas/<idea-id>/debate/rebuttal.yaml
  ideas/<idea-id>/debate/chair_verdict.yaml
  ideas/<idea-id>/debate/events.jsonl
  experiments/<experiment-id>/experiment_state.json
  paper/paper_state.json
  logs/research_events.jsonl
```

`research_state.json` is a small index, not the full database. It contains:

```json
{
  "schema_version": "research-state/v1",
  "revision": 0,
  "phase": "ideation",
  "active_idea_id": null,
    "paths": {
      "field_snapshot": "research_state/literature/field_snapshot.json",
      "ideation_sessions": "research_state/ideation_sessions",
      "review_patterns": "research_state/review_patterns",
    "idea_pool": "research_state/ideas/idea_pool.json",
    "experiments": "research_state/experiments",
    "paper_state": "research_state/paper/paper_state.json",
    "events": "research_state/logs/research_events.jsonl"
  },
  "updated_at": "RFC3339 timestamp"
}
```

Ownership:

- `research-idea-lab`: literature, public reviewer-pattern library, ideation sessions, role debate, idea pool, mechanism-family and failure lineage, novelty decisions, idea contracts.
- `research-experiment-lab`: pilot and full experiment plans, immutable runs, logs, synchronization, debugging, aggregation, and verification.
- `ai-research-writing-skill`: paper state, claims, prose, publication assets, review, and submission.

Writers must read the current `revision`, write detailed artifacts first, then atomically update the index only if the expected revision still matches. Append an event for every transition. Never let one stage erase another stage's keys.

During multi-role ideation, the Chair is the sole canonical writer. Worker roles return structured artifacts to the Chair or write only to an explicitly bounded temporary path. Use `references/role-artifact-schemas.md` for session and debate artifacts.

Long experimental runs require immutable run IDs; readable persistent logs; and structured event, metric, resource, environment, synchronization, status, summary, and verification records. The writing skill may request missing evidence but must not run experiments.
