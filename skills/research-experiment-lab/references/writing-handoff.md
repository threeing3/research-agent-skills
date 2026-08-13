# Writing Handoff

Create project-root `research_handoff.json` only after user-approved promotion
and the experiment stage is `paper-ready`.

Refuse a writing handoff from `admission_mode: exploratory-validation` even
when its diagnostic result is positive. Route the idea through focused
target-domain novelty review, formal contract issuance, and a formal campaign
first.

For a shared-state project, emit
`ai-research-writing/research-handoff-v2`. Include source idea ID and revision;
experiment ID and plan revision; publication-eligible full method identity; and
paths to:

- project and experiment inventories;
- verified analysis and decision;
- experiment-level verification report;
- run index and metric summary;
- numeric-evidence v2 registry;
- literature inventory when available;
- blockers, contradictory results, and exclusions.

Before emission, re-run idea-state consistency and require the selected
contract lifecycle to remain `active`. The experiment state and its v2
verification report must both say `paper-ready`, and the verification report
must repeat the same idea identity, experiment identity, plan revision, and
method identity. Legacy hashes may be checked when present but are not required
for a new local handoff. Do not copy a verification report or analysis files
from a different experiment directory into the handoff.

The writing skill may issue `experiment_request.json` for missing evidence.
This skill owns the resulting design and execution. Do not let the writing
skill silently run or modify experiments.

