# Anti-Reskin and Mechanism-Lineage Protocol

Use this protocol before creating a candidate, materially revising an idea, or
handing an idea to experiments. The unit of memory is the mechanism family,
not the title, acronym, model name, or revision number.

## Mechanism family

Assign a stable `family_id` to candidates that share the same:

- target failure and claimed capability;
- state or observation available at decision time;
- action whose value or consequence is predicted;
- learning signal or supervision source;
- causal operator or decision rule;
- intervention that is supposed to identify the mechanism.

Create `research_state/ideas/mechanism_families.json` as the canonical family
registry. Preserve rejected families and failed revisions. A new title never
creates a new family by itself.

Use this minimum registry shape:

```json
{
  "schema_version": "research-idea/mechanism-families-v1",
  "families": [
    {
      "family_id": "",
      "problem_signature": {},
      "mechanism_signatures": [],
      "idea_revisions": [],
      "scientific_failure_count": 0,
      "failures": [],
      "status": "active",
      "reopen_requires_user_review": false
    }
  ]
}
```

For every candidate, record three structured signatures:

```yaml
problem_signature:
  task: ""
  documented_failure: ""
  target_variable: ""
  operating_setting: ""
mechanism_signature:
  state: ""
  observation: ""
  action: ""
  learning_signal: ""
  supervision_source: ""
  causal_operator: ""
  intervention: ""
  claimed_capability: ""
evaluation_signature:
  unit_of_analysis: ""
  dataset_access: []
  primary_outcome: ""
  required_counterfactual: ""
  strongest_simple_baseline: ""
```

Normalize these fields for comparison, but do not treat a text hash as a
semantic novelty judgment. Use `scripts/check_idea_lineage.py` to validate the
contract and compute a reproducible signature hash after the Chair has made
the semantic family decision.

## Classify the relationship

Classify every proposal as exactly one of:

- `new-family`: a different target failure or causal mechanism;
- `same-family-material-revision`: the family is unchanged, but at least one
  causal axis and its discriminating prediction materially change;
- `adjacent-family`: shares the problem but changes the operative mechanism
  and the evidence needed to identify it;
- `cosmetic-variant`: no causal axis or discriminating observation changes.

The following are cosmetic by default unless they change the causal story and
produce a new separating observation:

- renaming the method or acronym;
- swapping backbone, optimizer, prompt template, or dataset;
- adding SFT, preference optimization, or RL around the same target signal;
- renaming a frame, clip, query, tool, or search step as an action;
- adding a module that predicts the same utility from the same observables;
- narrowing the claim without changing the failed mechanism.

Do not add a cosmetic variant to the candidate pool as a new idea. Attach it
to the existing family as an implementation option, fail its
`anti_reskin_gate`, and keep the idea `parked` or `rejected`.

## Inherit failures

Every family keeps a failure ledger. Each entry has a stable `failure_id`,
failure class, evidence path, affected claim, and reopen condition.

| Failure class | What a later revision must add |
| --- | --- |
| novelty occupied | a full-text-verified differentiator that changes the contribution, not wording |
| mechanism non-identifiable | a new intervention or observation that separates the mechanism from the strongest alternative |
| simple baseline wins | a residual claim and matched-resource test that remain valuable after the baseline |
| data infeasible | verified access or a claim-compatible design whose required sample/unit count is attainable |
| scientific negative | a changed causal prediction explaining why the new revision should behave differently |
| benchmark decay | a durable task, metric, or claim that survives the benchmark change |
| technical failure | a bounded child-run fix; it does not erase or support the scientific hypothesis |

Prior scientific failures are active counter-evidence. Do not reset them when
an idea ID or revision changes. An inherited failure may be `resolved`,
`not-applicable`, or `unresolved`; only the first two permit promotion.

## Require a material delta

A same-family revision must name:

- parent idea and revision;
- causal axes changed;
- unchanged axes;
- new discriminating prediction;
- prior failure IDs it claims to resolve;
- evidence or planned observation that would prove each resolution;
- result that would return the family to `rejected` or `parked`.

Changing implementation, compute, or terminology is not a material delta.
When no material delta exists, preserve the proposal as a note under the
parent revision and do not restart novelty review or experiments.

## Cold anti-reskin review

Before promotion, run one cold review from frozen artifacts. Give the reviewer
the candidate contract, family registry entry, closest-work packet, and prior
verification reports. Do not provide proposer discussion history, desired
verdict, or a narrative summary of why the revision is expected to work.

Record:

```yaml
anti_reskin_gate:
  status: pass
  review_context_policy: cold
  proposer_model_family: ""
  reviewer_model_family: ""
  independence_valid: true
  mechanism_signature_sha256: ""
  unresolved_failure_ids: []
  verdict: material-revision
  report: ""
```

Different model families are preferred when available. Independence still
requires a cold evidence view; a different model that receives the proposer's
narrative is not independent.

## Stop rules

- Allow one bounded rebuttal and at most one further material revision after
  new verified evidence changes a premise.
- After two scientifically failed revisions in one family, require explicit
  researcher review before another candidate from that family can proceed.
- Stop when two consecutive revisions change no causal axis or discriminating
  prediction.
- Do not spend GPU compute to decide whether a revision is merely cosmetic.

The researcher may reopen a stopped family, but the ledger and failed evidence
remain attached and the reason for reopening must be recorded.

## Promotion gate

An idea may become `experiment-ready` only when:

- its family relationship is recorded;
- the structured signatures are complete;
- all inherited failures are resolved or explicitly not applicable;
- a cold reviewer marks the change material and `independence_valid=true`;
- the mechanism-signature hash is recorded;
- the proposed pilot's prerequisites are jointly satisfiable under current
  data, compute, budget, and permissions.
