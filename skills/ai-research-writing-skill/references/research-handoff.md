# Research-System Handoff

Use this when an upstream system has already completed research planning, experiments, or analysis and this skill should own paper writing from that point onward.

The upstream system must export evidence, not writing prompts. The skill remains the canonical source for story construction, drafting, figures, citations, review, revision, LaTeX, and completion gates.

When the project-root `research_state.json` exists, read it before accepting a
handoff and require `ai-research-writing/research-handoff-v2`. Reconcile the
source idea with `active_idea_id`, its v4 contract revision and SHA-256, its
`active` lifecycle, the current experiment-ready idea-pool row, and a fresh
passed `research-idea/state-consistency-v2` report. Reconcile the experiment
with `active_experiment_id`, plan revision and SHA-256, `paper-ready` state, and
a passed `research-experiment/experiment-verification-v2` report carrying the
same identities and hashes. Treat any mismatch, lifecycle invalidation,
incomplete verification, or unresolved kill condition as a blocker.

Require the experiment plan and verification report to use
`admission_mode: formal`; an exploratory validation cannot enter a writing
handoff. For a `staged-novelty/v1` idea contract, require
`novelty_review.status: supported` plus its target-domain boundary, coverage
end, and recall confidence. Preserve source provenance, transfer/adaptation
value, contribution strength, implementation fidelity, and experimental
maturity as separate evidence fields; do not collapse them into novelty.

## Handoff Contract

Create `research_handoff.json` using `research-handoff.schema.json`. Paths are relative to the handoff project.

```json
{
  "schema_version": "ai-research-writing/research-handoff-v2",
  "source_idea_id": "videoqa-example",
  "source_idea_revision": 1,
  "source_idea_contract_sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
  "experiment_id": "videoqa-example-full",
  "experiment_plan_revision": 1,
  "experiment_plan_sha256": "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
  "research_question": "Does method X improve metric Y under condition Z?",
  "paper_type": "empirical ML paper",
  "target_venue": "ICML",
  "quantitative": true,
  "artifacts": {
    "project_inventory": "evidence/project_inventory.md",
    "analysis": "evidence/analysis.md",
    "decision": "evidence/decision.md",
    "experiment_inventory": "evidence/experiment_inventory.md",
    "experiment_verification": "research_state/experiments/videoqa-example-full/verification_report.json",
    "run_index": "research_state/experiments/videoqa-example-full/analysis/run_index.csv",
    "metric_summary": "research_state/experiments/videoqa-example-full/analysis/metric_summary.csv",
    "numeric_evidence": "numeric_evidence.json",
    "literature_inventory": "literature/paper_inventory.md",
    "figure_inventory": "figures/figure_inventory.md"
  },
  "blockers": []
}
```

For quantitative work, `experiment_inventory` and numeric-evidence v2 are
required. A handoff may retain blockers for inspection, but full-paper drafting
must use `--require-unblocked`. Exploratory partial writing must carry every
blocker into `paper_state.json` and weaken affected claims. Standalone projects
without `research_state.json` may still read the legacy v1 handoff; the presence
of shared state always activates the stricter v2 reconciliation.

Validate before drafting:

```bash
python3 scripts/check_research_handoff.py /path/to/handoff-project --require-unblocked
```

## Ownership Boundary

The upstream system owns the truth of exported evidence and stable file paths. It must not summarize away negative runs, failed conditions, missing baselines, uncertainty, or contradictory outcomes.

It must also preserve whether a negative result was
`implementation-not-confirmed`, `measurement-inconclusive`, or
`mechanism-counterevidence`. Only the last directly challenges the mechanism,
and even then the manuscript must bind the conclusion to the tested idea and
implementation revisions.

This skill owns all manuscript decisions after handoff. It creates `paper_state.json`, the paper story, claim map, prose, figures/tables, citation records, reviews, LaTeX, and build record. Never copy upstream writing prompts into the skill contract.

When shared research state exists, store or mirror paper state at `research_state/paper/paper_state.json`, append transitions to `research_state/logs/research_events.jsonl`, and link rather than duplicate idea or experiment artifacts. Do not rewrite literature, idea, or experiment-owned state. Missing evidence becomes an `experiment_request.json`; this skill never launches or modifies the requested experiment.

## Acceptance Procedure

1. Validate the handoff and inspect every declared artifact.
2. Reconcile contradictions between analysis, decision, raw evidence, and blockers.
3. Create the paper project contract and copy blockers without weakening them.
4. Build the story and claim map from evidence, not from an upstream proposed title.
5. Continue with `workflow.md` from the evidence-bearing core draft.
