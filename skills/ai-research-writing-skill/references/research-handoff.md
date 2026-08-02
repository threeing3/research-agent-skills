# Research-System Handoff

Use this when an upstream system has already completed research planning, experiments, or analysis and this skill should own paper writing from that point onward.

The upstream system must export evidence, not writing prompts. The skill remains the canonical source for story construction, drafting, figures, citations, review, revision, LaTeX, and completion gates.

When the project-root `research_state.json` exists, read it before accepting a handoff. Require `source_idea_id`, `source_idea_revision`, `experiment_id`, and `experiment_plan_revision` to match active state. Require the linked experiment stage to be `paper-ready` and its verification report to pass. Treat revision mismatch, `novelty-risk`, incomplete experiment verification, and unresolved kill conditions as blockers.

## Handoff Contract

Create `research_handoff.json` using `research-handoff.schema.json`. Paths are relative to the handoff project.

```json
{
  "schema_version": "ai-research-writing/research-handoff-v1",
  "source_idea_id": "videoqa-example",
  "source_idea_revision": 1,
  "experiment_id": "videoqa-example-full",
  "experiment_plan_revision": 1,
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

For quantitative work, `experiment_inventory` and numeric-evidence v2 are required. A handoff may retain blockers for inspection, but full-paper drafting must use `--require-unblocked`. Exploratory partial writing must carry every blocker into `paper_state.json` and weaken affected claims.

Validate before drafting:

```bash
python3 scripts/check_research_handoff.py /path/to/handoff-project --require-unblocked
```

## Ownership Boundary

The upstream system owns the truth of exported evidence and stable file paths. It must not summarize away negative runs, failed conditions, missing baselines, uncertainty, or contradictory outcomes.

This skill owns all manuscript decisions after handoff. It creates `paper_state.json`, the paper story, claim map, prose, figures/tables, citation records, reviews, LaTeX, and build record. Never copy upstream writing prompts into the skill contract.

When shared research state exists, store or mirror paper state at `research_state/paper/paper_state.json`, append transitions to `research_state/logs/research_events.jsonl`, and link rather than duplicate idea or experiment artifacts. Do not rewrite literature, idea, or experiment-owned state. Missing evidence becomes an `experiment_request.json`; this skill never launches or modifies the requested experiment.

## Acceptance Procedure

1. Validate the handoff and inspect every declared artifact.
2. Reconcile contradictions between analysis, decision, raw evidence, and blockers.
3. Create the paper project contract and copy blockers without weakening them.
4. Build the story and claim map from evidence, not from an upstream proposed title.
5. Continue with `workflow.md` from the evidence-bearing core draft.
