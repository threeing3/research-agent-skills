# Shared Research State Protocol

Store state per project:

```text
research_state.json
research_state/
  literature/field_snapshot.json
  literature/search_history.jsonl
  ideation_sessions/<session-id>/session.json
  ideation_sessions/<session-id>/evidence_packet.json
  ideation_sessions/<session-id>/opportunity_map.yaml
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
  problems/<problem-id>/problem_card.yaml
  problems/<problem-id>/events.jsonl
  ideas/idea_pool.json
  ideas/mechanism_families.json
  ideas/<idea-id>/idea_contract.yaml
  ideas/<idea-id>/lineage_check.json
  ideas/state_consistency.json
  ideas/<idea-id>/validation/<alignment-id>.yaml
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
    "problems": "research_state/problems",
    "idea_pool": "research_state/ideas/idea_pool.json",
    "idea_state_consistency": "research_state/ideas/state_consistency.json",
    "experiments": "research_state/experiments",
    "paper_state": "research_state/paper/paper_state.json",
    "events": "research_state/logs/research_events.jsonl"
  },
  "updated_at": "RFC3339 timestamp"
}
```

Ownership:

- `research-idea-lab`: literature, problem cards, bottleneck and motivation
  hypotheses, problem-to-idea lineage, public reviewer-pattern library, ideation
  sessions, role debate, idea pool, mechanism-family and failure lineage, novelty
  decisions, and idea contracts.
- `research-experiment-lab`: pilot and full experiment plans, immutable runs, logs, synchronization, debugging, aggregation, and verification.
- `ai-research-writing-skill`: paper state, claims, prose, publication assets, review, and submission.

Writers must read the current `revision`, write detailed artifacts first, then atomically update the index only if the expected revision still matches. Append an event for every transition. Never let one stage erase another stage's keys.

## Idea modes and status ownership

Record one work mode in every ideation session:

- `problem-discovery` may create or update problem cards with `problem-seed`,
  `evidence-backed`, `bottleneck-framed`, or `solution-ready` maturity. It does not
  assign an idea status or require a solution.
- `explore` may create provisional seeds and write `raw` or `developing` candidates. It may not write `rejected` or `experiment-ready`.
- `develop` may write `developing`, `screened`, `novelty-risk`, `discussion-active`, `gate-ready`, or `parked`. It may not write `rejected` or `experiment-ready`.
- `novelty` may write `screened`, `novelty-risk`, `gate-ready`, or, after focused novelty, lineage, formal-entry, and explicit user-selection checks pass, `experiment-ready`. It may not write `rejected`.
- `gate` may write any current-state status after running the user-requested full strict checks.

Track problem maturity independently as `problem-seed`, `evidence-backed`,
`bottleneck-framed`, or `solution-ready`. Track idea maturity independently as
`seed`, `developing`, or `validation-ready`.
An incomplete idea is not a rejected idea. Use
`references/iterative-development.md` to classify implementation revisions,
mechanism revisions, and linked derived ideas.

`research_state/ideas/idea_pool.json` is the canonical current status. A candidate may receive a canonical idea ID when it is selected for development or has a stable problem/mechanism signature; provisional exploration seeds remain in the session artifact.

`research_state/problems/<problem-id>/problem_card.yaml` is the evidence-bearing
problem record. A stable idea links to one problem ID and revision; one problem may
link to multiple ideas. A failed implementation or solution does not close the
problem unless the evidence also refutes the observed failure or bottleneck. A
material problem revision stales derived motivation and solution judgments until
they are reconciled.

An idea contract is an evidence-bearing handoff snapshot issued at `experiment-ready`, not the canonical current status. New or materially revised contracts must contain the lifecycle block in `references/idea-contract.md`. When later literature or verified evidence moves the pool entry away from `experiment-ready`:

1. update the pool status;
2. set the contract lifecycle to `invalidated` or `superseded` without rewriting its historical scientific content;
3. append a transition event with the evidence and reason;
4. run `scripts/check_idea_state_consistency.py` and store the report at `ideas/state_consistency.json`.

Legacy contracts without lifecycle metadata remain readable. Do not bulk-rewrite them. The consistency checker must flag a legacy contract whose issued status conflicts with the current pool so it cannot be handed to experiments silently.

Every new v4 experiment handoff uses `contract_profile: problem-led/v1`. The lineage
check reads the referenced problem card, validates its structure and semantics, and
requires its problem ID, revision, maturity, and open/contested/parked status to match
the contract. Missing, closed, invalid, or stale problem cards block handoff. Legacy
profiles remain read-only.

Pre-gate exploratory validation does not require or create an idea contract.
Freeze a user-approved `research-idea/validation-alignment-v3` artifact for new work under
`ideas/<idea-id>/validation/`, and let the experiment plan bind its alignment
ID, parent problem identity, idea revision, and implementation revision. Historical
v1/v2 alignments remain read-only and require migration before a new launch. Do not
require a generic local file hash.
The alignment may move a developing idea forward or backward, but it may not
set novelty, `experiment-ready`, or paper-ready status.

`ideas/state_consistency.json` is the canonical consistency-report name for
all new writes. Readers may accept the legacy
`ideas/idea_state_consistency.json` path when an old index or plan explicitly
references it. Do not delete the legacy file; update new indexes, templates,
and examples to the canonical name.

During multi-role ideation, the Chair is the sole canonical writer. Worker roles return structured artifacts to the Chair or write only to an explicitly bounded temporary path. Use `references/role-artifact-schemas.md` for session and debate artifacts.

Long experimental runs require immutable run IDs; readable persistent logs; and structured event, metric, resource, environment, synchronization, status, summary, and verification records. The writing skill may request missing evidence but must not run experiments.
