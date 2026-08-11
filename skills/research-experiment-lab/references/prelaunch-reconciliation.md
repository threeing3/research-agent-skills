# Prelaunch Lineage and Gate Reconciliation

Use this protocol before creating a novel-method run, allocating a GPU, or
starting an autonomous task graph. It prevents a renamed failed mechanism or
an impossible experimental gate from consuming compute.

## Required handoff

Read the canonical idea contract, idea-state consistency report, and
lineage-check report. Copy these immutable identifiers into
`experiment_plan.json`:

```json
{
  "idea_id": "",
  "idea_revision": 1,
  "idea_contract_sha256": "",
  "mechanism_family_id": "",
  "mechanism_signature_sha256": "",
  "inherited_failure_ids": []
}
```

Reject the handoff when:

- the contract lifecycle is missing, `invalidated`, or `superseded`;
- the idea or current idea-pool state is not `experiment-ready`, or the idea
  was not explicitly selected;
- the `research-idea/state-consistency-v2` report is absent, failed, or its
  idea-contract or idea-pool SHA-256 no longer matches current files;
- the anti-reskin gate did not pass;
- any inherited failure is unresolved;
- the idea revision, family, contract hash, or mechanism hash differs;
- the proposed experiment does not test the recorded discriminating prediction.

Historical runs remain valid evidence for their original revision. They do not
become evidence for a new mechanism merely because files, weights, or datasets
are reused.

## Declare satisfiable prerequisites

Add a `prelaunch` object to the plan:

```json
{
  "required_gates": [
    "anti-reskin",
    "mechanism-identifiability",
    "simple-baseline-survival",
    "data-feasibility"
  ],
  "constraints": [
    {
      "constraint_id": "independent-video-count",
      "description": "video-disjoint units available to the formal test",
      "available": 16,
      "op": ">=",
      "required": 64,
      "unit": "videos",
      "evidence": "path/to/manifest.json",
      "resolution": "expand the frozen replay",
      "resolution_authorized": false
    }
  ],
  "lineage_check_report": "research_state/ideas/example/lineage_check.json",
  "idea_state_consistency_report": "research_state/ideas/idea_state_consistency.json",
  "last_reconciled_at": ""
}
```

Declare every prerequisite that can make the scientific gate impossible:
sample count, independent unit count, label class support, required action
coverage, dataset access, model access, disk, GPU memory, wall time, and budget.
Use actual available values and evidence paths, not optimistic estimates.

Run `scripts/prelaunch_reconcile.py` and preserve its JSON report. An unmet
constraint is a blocked gate even when a possible resolution exists. If the
resolution requires a hypothesis, dataset, metric, permission, or budget
change, return to the owning stage or user; do not launch a smaller run that
cannot possibly satisfy the declared scientific threshold.

## Check the task graph

Every task dependency must refer to an existing task, and the dependency graph
must be acyclic. A task may depend only on declared gates and artifacts. Do not
create a cycle such as:

```text
novelty pass -> expand data -> run pilot -> establish novelty pass
```

When a gate needs evidence from a cheap diagnostic, explicitly classify that
diagnostic as permitted before the gate. Otherwise the graph is unsatisfiable
and must be revised before execution.

## Reconcile before every launch

Freshly recompute:

- idea-contract SHA-256;
- mechanism-signature SHA-256;
- inherited failure set;
- constraint values backed by current manifests or preflight records;
- task dependency eligibility;
- current idea revision and user selection.
- current idea lifecycle, pool status, contract hash, and pool hash against the
  referenced state-consistency report.

Store the report under the experiment directory and reference it from the run
manifest. A stale or failed report blocks `new-run`, snapshot deployment, and
AutoDL lifecycle actions for novel-method work.

## Distinguish blockers

- `lineage-blocked`: same mechanism family still carries an unresolved failure;
- `scientifically-unsatisfiable`: current assets cannot meet a frozen gate;
- `permission-blocked`: a valid resolution exists but is not authorized;
- `technically-blocked`: implementation or infrastructure failed while the
  scientific design remains satisfiable;
- `stale-by-idea-revision`: the canonical idea changed after reconciliation.
- `stale-by-idea-lifecycle`: the contract is no longer active or the referenced
  idea-state consistency report no longer represents current files.

Do not reclassify a scientific or lineage blocker as technical to keep an
autonomous campaign moving.
