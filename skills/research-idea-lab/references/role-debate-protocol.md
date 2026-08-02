# Multi-Role Ideation and Debate Protocol

Use this protocol when generating a new candidate pool, reopening an idea for substantial revision, or adversarially comparing serious candidates. Do not invoke it for a narrow citation lookup or a simple status question.

## Contents

- Architecture
- Evidence and permissions
- Execution modes
- Debate stages
- Dynamic review panel
- Stop and escalation rules
- Integrity constraints

## Architecture

Use three working roles and one chair:

1. **Native Innovator**: generate target-domain mechanisms from documented failures, contradictions, constraints, and unmet capabilities.
2. **Cross-Domain Transfer Researcher**: retrieve structurally analogous mechanisms from other fields and adapt them under the transfer requirements in `cross-domain-transfer.md`.
3. **Adversarial Reviewer**: attack novelty, mechanism, significance, simple-baseline survival, feasibility, evaluation, and venue fit; every rejection must include a repair path or counterproposal when one is credible.
4. **Chair**: prepare evidence, enforce isolation, verify disputed facts, apply fatal gates, maintain canonical state, and present decisions to the researcher.

The human researcher retains final selection authority. A vote or model score cannot promote an idea.

Do not create a permanent experiment-designer role in ideation. The Adversarial Reviewer may check whether a discriminating pilot is possible, but `research-experiment-lab` owns experiment design and execution.

## Evidence and permissions

The Chair creates an evidence packet with stable evidence IDs and a freeze timestamp before divergent generation.

| Capability or evidence | Native Innovator | Cross-Domain Researcher | Adversarial Reviewer | Chair |
| --- | --- | --- | --- | --- |
| Research boundary and compute constraints | read | read | read | read/write |
| Target-domain field snapshot | full | bottlenecks and key clusters | full | full |
| Adjacent-field mechanism library | limited | full | candidate-triggered | full |
| Other proposer's first-round output | hidden | hidden | not applicable | full |
| Closest-work and kill-query results | after first round | after first round | full | full |
| Reviewer-pattern library | hidden during generation | hidden during generation | full | full |
| Canonical project state | read | read | read | read/write |
| Experiments or external mutations | forbidden | forbidden | forbidden | forbidden |

Workers return structured artifacts to the Chair. Only the Chair writes canonical shared state. This prevents concurrent agents from overwriting one another.

The Chair may refresh evidence after the freeze only when:

- a factual dispute cannot be resolved from the packet;
- a candidate introduces a previously uncovered mechanism or source field;
- a newly published close paper changes the novelty judgment.

Record every refresh and identify which earlier judgments became stale.

## Execution modes

Prefer **isolated-agent mode** when independent agents are callable:

- run the Native Innovator and Cross-Domain Researcher independently;
- give each only its permitted evidence view;
- return structured outputs rather than private reasoning;
- let the Adversarial Reviewer inspect both only after first-round outputs are fixed.

Use **isolated-pass fallback** when independent agents are unavailable:

- execute the same roles sequentially with separate prompts and context views;
- do not expose first-round outputs across proposer roles;
- preserve the same artifacts and state transitions as isolated-agent mode.

The output contract must not depend on which execution mode was used. Record the mode in the session manifest.

## Debate stages

### 0. Frame and freeze evidence

The Chair:

- records the research question, target contribution types, exclusions, compute, target venue assumptions, and literature coverage;
- separates user claims from system assumptions;
- creates the session manifest and evidence packet;
- assigns stable candidate IDs as proposals arrive.

### 1. Divergent generation

Run both proposer roles independently.

The Native Innovator must derive candidates from a named target-domain failure and specify:

- problem and why it persists;
- mechanism, causal story, and falsifiable prediction;
- nearest native baseline;
- simple pilot concept and kill condition;
- expected reviewer objection.

The Cross-Domain Researcher must produce a complete transfer card for every candidate. Reject surface analogies, renamed source methods, and transfers without a target-adoption search.

Do not impose a fixed candidate count. Stop a role when new lenses yield only duplicates, cosmetic variants, or candidates dominated by existing work.

### 2. Cluster before discussion

The Chair clusters proposals by problem, operative mechanism, and claimed capability. Merge only true duplicates; preserve distinct causal mechanisms even when titles or tasks are similar.

Keep rejected and dominated candidates with reasons. Do not show proposer identity during comparative scoring when it is not needed.

### 3. Cross-examination

Reveal the clustered proposals to both proposer roles.

The Native Innovator evaluates cross-domain candidates for target necessity, native alternatives, broken assumptions, and whether the transfer adds a real capability.

The Cross-Domain Researcher evaluates native candidates for equivalent mechanisms in other fields, missing invariants, and possible stronger abstractions.

For each serious candidate, each role must return one of:

- `support`: preserve the mechanism and add evidence;
- `revise`: name the exact change and what it fixes;
- `challenge`: state a falsifiable objection;
- `replace`: provide a materially different counterproposal.

Agreement without an evidence-bearing reason is not useful output.

### 4. Adversarial review

The Adversarial Reviewer receives the proposals, cross-examination, closest work, kill-query results, and matched reviewer patterns. It must:

- write the strongest plausible rejection;
- distinguish occupied components from the remaining differentiator;
- test mechanism identifiability and alternative explanations;
- construct simple and matched-budget baselines;
- test problem and benchmark half-life;
- assess collision resistance and salvage value;
- fill the Reviewer Attack Matrix;
- label each fatal gate `pass`, `unresolved`, or `fail`;
- offer a repair path or counterproposal when credible.

Do not infer a fatal issue from a single review comment or from rejection status alone.

### 5. Bounded rebuttal and revision

The originating proposer receives only the structured attacks and supporting evidence. It may:

- concede and narrow the claim;
- revise the mechanism;
- add a discriminating prediction;
- provide counter-evidence;
- withdraw the candidate.

Default to one rebuttal. Permit one additional round only if new verified evidence changes a factual premise. A second round that merely restates arguments must terminate.

A material mechanism revision creates a new candidate revision and invalidates stale novelty, reviewer, and pilot judgments.

### 6. Chair adjudication

The Chair verifies citations and disputed factual claims, then decides:

- `survive`: no fatal gate remains and discussion may continue;
- `revise`: potentially valuable but specified evidence or mechanism work remains;
- `park`: currently blocked by timing, access, compute, or unresolved external facts;
- `reject`: occupied, non-identifiable, trivial, infeasible, or not meaningful;
- `novelty-risk`: new close work may occupy the differentiator.

Do not average away fatal gates. Record majority and minority arguments, but do not use voting as the decision rule.

### 7. Researcher decision

Present surviving and revisable candidates with:

- mechanism and importance;
- exact closest-work distinction;
- cross-domain source when applicable;
- unresolved attacks and required evidence;
- cheapest discriminating pilot concept;
- kill conditions and fallback contribution.

Only an explicit researcher selection may set `experiment-ready` or create the downstream handoff.

## Dynamic review panel

For shortlisted or high-cost candidates, the Chair may instantiate independent review lenses:

- novelty and collision;
- mechanism and soundness;
- evaluation and feasibility;
- venue contribution and excitement.

Treat these as temporary reviewers, not permanent roles. Use separate evidence views where practical, then let the Adversarial Reviewer synthesize disagreements. Add a specialist from a source discipline only when the transfer depends on non-obvious domain assumptions.

## Stop and escalation rules

Stop debate when:

- all fatal gates have stable outcomes;
- two consecutive turns add no new evidence, attack, revision, or candidate;
- the remaining dispute is a user preference;
- the question requires an experiment rather than more argument.

Escalate to search rather than debate for factual novelty disputes. Escalate to the user for a target, risk, resource, or contribution choice that would materially change the direction.

## Integrity constraints

- Cite evidence IDs in every consequential claim.
- Store claims, evidence, attacks, concessions, and decisions; do not store private chain-of-thought.
- Never claim proof that no prior work exists.
- Do not reward winning, rhetorical confidence, or refusal to concede.
- Reward useful disagreement, correct concession, information gain, and repair quality.
- Do not let roles message external parties, run experiments, change remote systems, or write outside the Chair-controlled state.
