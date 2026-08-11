---
name: research-idea-lab
description: Discover, develop, rescue, compare, and, only when explicitly requested, strictly vet novel ML/AI research ideas, especially for VideoQA and long-video understanding. Use for field mapping, finding directions or open problems, turning rough seeds into testable mechanisms, cross-domain transfer, checking related work, refreshing an idea pool, scoring or ranking ideas, and preparing a selected idea for experimental validation, including requests such as 找方向, 还有没有 idea, 继续想, 救方向, 严格评分, or 选题排序. Default vague direction-finding and rescue requests to exploration; do not enter strict rejection, ranking, or experiment-readiness gates unless the user explicitly asks for them.
---

# Research Idea Lab

Treat ideation as literature-grounded hypothesis discovery. Separate possibility generation from development and strict judgment so early uncertainty does not become premature rejection.

## Interaction Contract

- Return useful candidates before process narration.
- Ask at most one blocking question in a turn. If a bounded assumption permits useful work, state it and continue.
- Do not ask for routine mode changes or skill handoffs. Route silently when the requested work remains within scope.
- Ask before a long or costly experiment, a material scope expansion, use of private text in search, or a choice that would materially change the research target.
- Keep advisory uncertainty in the output; do not require a reply. Request a decision only for a blocking truthfulness, permission, cost, ethics, or venue-compliance issue.
- Never run strict review merely because an idea is rough, crowded, or missing evidence.

## Choose One Work Mode

Select exactly one primary mode per request. When intent is mixed, use the least severe mode that still returns the requested artifact; never silently escalate to `gate`.

### `explore` — default for finding possibilities

Use for vague directions, “find ideas,” “what else can be done,” field scouting, repeated direction search, open problems, and early cross-domain transfer.

- Generate and diversify before judging.
- Do not score, rank, reject, inherit fatal family failures, run full anti-reskin review, or set `experiment-ready`.
- A literature collision creates a differentiation or rescue task, not an automatic dead end.

### `develop` — improve a chosen or rough direction

Use when the user selects a candidate, provides one rough idea, asks to concretize a mechanism, or wants to rescue a crowded or previously failed direction without requesting strict scoring.

- Separate current weakness from development potential.
- Label uncertainty as `needs-search`, `needs-mechanism`, or `needs-evidence`.
- Try a material rescue route before recommending a pivot. Do not write `rejected` in this mode.

### `gate` — strict comparison and experiment admission

Use only when the user explicitly requests scoring, ranking, strict review, an investment decision, an abandon decision, a final novelty verdict, or promotion to experimental validation.

- Run the full literature, anti-reskin, reviewer-pattern, fatal-gate, and lineage workflow.
- Only this mode may set `rejected` or `experiment-ready`.
- A low current-readiness score does not erase development potential. Use `abandon` only when no testable central claim remains after a documented rescue attempt.

## Start

1. Locate the project root. Keep state under `<project-root>/research_state/` and the index at `<project-root>/research_state.json`.
2. Read `references/state-protocol.md` and inspect current state before writing.
3. Choose `explore`, `develop`, or `gate`; record the mode and assumptions in the session artifact.
4. Choose the coverage mode:
   - `baseline`: no trustworthy field snapshot exists, the scope changed materially, or the user requests a remap.
   - `incremental`: a trustworthy snapshot exists; search from its `coverage_end` through today with an overlap window.
5. Load only mode-relevant references:
   - For `explore`: read `references/exploration-workflow.md` and `references/opportunity-map.md`.
   - For `develop`: read those two files plus `references/novelty-workflow.md`; read `references/cross-domain-transfer.md` when transfer is relevant.
   - For `gate`: additionally read `references/idea-evaluation-rubric.md`, `references/anti-reskin-protocol.md`, `references/role-debate-protocol.md`, `references/role-artifact-schemas.md`, and `references/idea-contract.md`.
   - Read `references/research-process-metrics.md` only for strict candidate comparison or pilot-information decisions.
   - Read `references/reviewer-pattern-workflow.md` and `references/ai-venue-scope.json` only when building or querying the public reviewer-pattern corpus or calibrating a target venue.
   - For VideoQA, read `references/videoqa-lenses.md`.

## Workflow

### 1. Define the boundary and opportunity map

Record the target problem, tasks, evidence available, constraints, adjacent fields, date range, exclusions, and compute. Separate user claims from assumptions.

In `explore`, a partial `Background → Motivation → Method` chain is allowed. Record missing links and use them to diversify candidates. Require the complete, falsifiable chain only before `gate-ready` or `experiment-ready`.

Build or update an opportunity map with:

- what existing work covers;
- what settings, mechanisms, evidence, or stakeholders remain under-tested;
- why the gap may be actionable now;
- at least one differentiation or rescue route per close-work cluster;
- the evidence that would close or preserve each opportunity.

Save reusable maps under the current ideation session and update `literature/field_snapshot.json` only with verified evidence.

### 2. Search to the depth required by the mode

For `explore`, search until opportunity sufficiency: the evidence supports 3–5 coherent, materially different candidate cards and another query is unlikely to change which candidates deserve development. If honest constraints support fewer, return the supported candidates plus the exact missing search or evidence route; never return an empty rejection-only answer.

For `develop`, search the selected mechanism, its strongest alternative, close work, failed attempts, and at least one rescue path. Stop when the next decision-relevant uncertainty is explicit.

For `gate`, use full baseline or incremental search. Continue until two consecutive materially different query families add no new close-work cluster, or record the hard time/access limit. Re-run saved kill queries and verify close work through primary sources.

The venue list in `references/ai-venue-scope.json` limits reviewer-pattern and venue-calibration evidence only. It must not exclude high-quality primary literature from adjacent fields used for mechanism discovery, cross-domain transfer, datasets, or theory.

Record source, date, query, evidence depth, and recall limits. Never claim that search proves nobody has done an idea.

### 3. Explore a diverse candidate portfolio

Follow `references/exploration-workflow.md`.

- Target at least six raw seeds internally, then return 3–5 coherent candidates that differ materially across problem, mechanism, supervision, evidence, contribution type, or source domain.
- Use problem-first, contradiction, boundary/failure, simplicity, composition/decomposition, abstraction shift, changed assumption, stakeholder, and cross-domain lenses.
- Use provisional seed labels in session artifacts. Do not assign a canonical idea ID merely to test a possibility.
- Run a lightweight signature comparison to merge obvious duplicates and label likely family collisions. Do not inherit fatal failures or run the cold anti-reskin protocol yet.
- For a crowded or weak seed, produce at least one narrower problem, mechanism change, evidence route, benchmark/setting change, or minimum viable research question before pivoting.
- Store shortlisted candidates as `raw` or `developing`; exploration may not set `rejected`.

Multi-role generation is optional in `explore`. If used, keep proposing and rescue passes separate from adversarial review, and reserve canonical state writes for the Chair. Do not require a full debate merely to return candidates.

### 4. Develop a selected candidate

Normalize the candidate into problem, documented failure, root challenge, insight, mechanism, assumptions, differentiating prediction, strongest alternative, evidence plan, and limitation.

Compare problem, mechanism, and evaluation signatures against `ideas/mechanism_families.json`. Treat inherited failures as repair obligations and search clues, not automatic rejection. State the material delta required to survive the closest family failure.

Produce:

- the current weakness and development potential separately;
- closest-work deltas and remaining novelty unknowns;
- at least one material rescue route;
- the minimum discriminating pilot question, without designing or running the experiment;
- a recommendation to continue development, park, pivot, search, or request strict review.

Set `gate-ready` only when the central claim is testable, the mechanism is specified, a strongest alternative exists, and the required evidence is identifiable. Do not score or reject unless the user explicitly enters `gate`.

### 5. Run the strict gate

Load every strict reference listed under `Start`. Use the structured debate and anti-reskin protocols for shortlisted candidates, not the whole raw portfolio.

Require:

- closest-work subtraction and novelty/recall confidence;
- problem, mechanism, supervision, data, evaluation, and contribution comparison;
- contribution-type fit, problem and benchmark half-life;
- mechanism identifiability and a separating observation;
- strongest-simple-baseline survival and collision resistance;
- a cheapest discriminating pilot with satisfiable prerequisites;
- reviewer attack and required-evidence matrices;
- a passed cold anti-reskin gate with no unresolved inherited family failure;
- all applicable fatal gates and triggered process diagnostics.

Send factual disputes back to search. Keep `soundness` and `excitement` separate. Scores summarize evidence and may not compensate for a fatal gate.

The Chair may decide `survive`, `revise`, `park`, `reject`, or `novelty-risk`. Before `reject`, record at least one attempted material rescue route unless the claim is non-testable, unethical, permission-blocked, or impossible under explicit hard constraints.

### 6. Return the mode-appropriate artifact

For `explore`, return in this order:

1. assumptions and opportunity snapshot;
2. 3–5 candidate cards;
3. material-diversity summary;
4. rescue routes and minimum viable research questions;
5. recommended candidates to develop;
6. at most one optional next question.

For `develop`, return the optimized candidate, current weakness, development potential, closest-work delta, rescue route, minimum discriminating question, and recommended next state.

For `gate`, return the verdict first, then search basis, closest-work table, strict risks, scores, confidence, repair conditions, rescue attempt, and promotion decision.

The researcher chooses what to pursue. Promote only an explicitly selected, sufficiently specified idea with a passed gate to `experiment-ready`. Create `ideas/<idea-id>/idea_contract.yaml` from `references/idea-contract.md`, run `scripts/check_idea_lineage.py`, then run `scripts/check_idea_state_consistency.py` before experiment handoff.

### 7. Coordinate state and downstream work

Use these current-state statuses: `raw`, `developing`, `screened`, `novelty-risk`, `discussion-active`, `gate-ready`, `experiment-ready`, `parked`, and `rejected`.

Treat `ideas/idea_pool.json` as the canonical current status. Treat an idea contract as an evidence-bearing handoff snapshot. When later literature or verified experiments move an `experiment-ready` idea to another status, invalidate or supersede the contract lifecycle, append an event, and run `scripts/check_idea_state_consistency.py`. Preserve historical scientific content; do not bulk-rewrite old contracts.

`research-experiment-lab` owns experiment design, execution, debugging, aggregation, and verification. Handoff the family ID, mechanism-signature hash, lineage report, inherited failure IDs, and active contract lifecycle. Do not run experiments in this skill.

## Integrity

- Distinguish metadata-only, abstract-level, and full-text-verified evidence.
- Prefer primary papers and artifacts, official criteria and public reviews, then systematic syntheses. Use informal posts only to generate hypotheses or search terms.
- Do not fabricate papers, identifiers, quotes, results, reviewer reactions, or novelty certainty.
- Use only publicly readable reviewer records; preserve source identifiers, do not infer reviewer identities, and do not republish full reviews.
- Never pass OpenReview credentials on the command line or store them in project state. Record access challenges; never bypass access controls.
- Do not overwrite another stage's detailed state or store private chain-of-thought.
- Let only the Chair write canonical ideation/debate state when multiple roles or agents are active.
- Use `scripts/research_state.py` for initialization and revision-safe index updates.
