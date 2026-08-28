# Diagnostic Evidence Handoff

Use `diagnostic_evidence_handoff.json` to carry verified diagnostic evidence
back to research ideation without letting the experiment skill rewrite
idea-owned state.

## When to write it

Write the handoff only after `verify_experiment.py` produces a passing
`verified-diagnostic` report. Start from
`assets/diagnostic_evidence_handoff.json.template` and conform to
repository-root `schemas/diagnostic-evidence-handoff.schema.json`.

Do not create this artifact for a blocked, technically incomplete, or merely
promising run. Preserve inconclusive evidence explicitly instead of forcing a
positive or negative conclusion.

## Evidence boundary

- Copy the frozen research question, experiment ID, plan revision, observed
  failure, and competing explanations from the verified plan.
- Classify only claims reached by inspectable evidence as `supports`, `weakens`,
  or `inconclusive`.
- Point `evidence_refs` to the verification report and the smallest result
  artifacts needed to audit each interpretation.
- State the supported sample, model, dataset, subgroup, or condition in
  `scope`; do not generalize beyond it.
- Record limitations even when the separating prediction succeeds.
- Choose one `recommended_update`, but keep it advisory.

The handoff does not establish novelty, method validity, superiority,
`experiment-ready`, or `paper-ready`.

## Ownership boundary

The experiment skill writes and preserves the handoff under the immutable
experiment directory. It does not edit the idea pool, bottleneck hypothesis,
idea contract, or canonical research state.

The idea skill reads the handoff during **Learn**, verifies its evidence
references and scope, and makes the canonical decision. That decision may keep
or weaken the bottleneck, narrow the problem, or return to diagnosis. Record
the decision separately so the original experimental receipt remains intact.
