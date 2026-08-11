# Writing Handoff

Create project-root `research_handoff.json` only after user-approved promotion
and the experiment stage is `paper-ready`.

For a shared-state project, emit
`ai-research-writing/research-handoff-v2`. Include source idea ID, revision,
and contract SHA-256; experiment ID, plan revision, and experiment-plan
SHA-256; and paths to:

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
must repeat the same idea identity, contract hash, experiment identity, plan
revision, and plan hash. Do not copy a verification report or analysis files
from a different experiment directory into the handoff.

The writing skill may issue `experiment_request.json` for missing evidence.
This skill owns the resulting design and execution. Do not let the writing
skill silently run or modify experiments.

