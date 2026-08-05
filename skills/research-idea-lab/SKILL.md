---
name: research-idea-lab
description: Discover, discuss, score, and adversarially vet novel research ideas for ML/AI, especially VideoQA and long-video understanding. Use when mapping a field, running structured multi-role brainstorming and debate, finding open problems, transferring mechanisms from other disciplines, checking whether an idea has already been done, comparing an idea against real reviewer rejection patterns, refreshing an existing idea pool with newly published work, or preparing an idea for pilot or full experimental validation.
---

# Research Idea Lab

Treat ideation as literature-grounded hypothesis discovery, not free-form brainstorming.

## Start

1. Locate the project root. Keep all state under `<project-root>/research_state/` and the index at `<project-root>/research_state.json`.
2. Read `references/state-protocol.md` and inspect existing state before searching.
3. Select the search mode:
   - `baseline`: no trustworthy field snapshot exists, the scope changed materially, or the user requests a complete remap.
   - `incremental`: a deep snapshot exists; search from its `coverage_end` through today, plus backward citation checks for any new close work.
4. Read `references/novelty-workflow.md` and `references/idea-evaluation-rubric.md`.
5. Read `references/cross-domain-transfer.md` when generating or evaluating transferred ideas. For VideoQA work also read `references/videoqa-lenses.md`.
6. Read `references/reviewer-pattern-workflow.md` when building, refreshing, or querying the rejection-pattern library.
7. Read `references/ai-venue-scope.json` and reject sources outside its approved AI venue families. Preserve its source-type roles: main conferences calibrate reviewer attacks; workshops scout emerging ideas; journals inform soundness and revision; position tracks inform agendas and framing.
8. Use `scripts/openreview_public_corpus.py` for OpenReview coverage probes, public-corpus collection, browser-safe page plans, and browser-verified JSON ingest. Probe before collecting a new venue or year.
9. When generating, substantially revising, or debating ideas, read `references/role-debate-protocol.md` and `references/role-artifact-schemas.md`.
10. Before creating a candidate, revising a failed idea, or promoting an idea,
    read `references/anti-reskin-protocol.md`. Treat mechanism families and
    inherited failures as canonical state; titles and acronyms are not lineage.

## Workflow

### 1. Define the search boundary

Record the target problem, tasks, datasets, method families, adjacent fields, date range, exclusions, and available compute. Separate the user's claims from assumptions.

### 2. Search before converging

In `baseline` mode, build a field map and the first candidate pool in the same run:

- Search surveys, seminal work, direct competitors, current papers, negative results, limitations, and relevant benchmarks.
- Search multiple scholarly indexes when available. Record unavailable sources and reduced recall.
- Expand terminology, abbreviations, task aliases, mechanism names, and adversarial phrasings.
- Follow backward and forward citations around the closest papers.
- Search adjacent disciplines for structurally matching problems and mechanisms, not merely shared vocabulary.
- Continue until query saturation: two consecutive materially different query families add no new close-work cluster. A hard time or access limit must be recorded, never hidden.

In `incremental` mode:

- Search from the last trustworthy `coverage_end`, with a small overlap window.
- Re-run saved high-risk novelty queries and inspect newly citing/cited close work.
- Re-score affected ideas. Do not silently preserve a novelty verdict after conflicting work appears.

Save search provenance and update `literature/field_snapshot.json` plus `literature/search_history.jsonl`.

### 3. Generate candidates continuously

Generate candidates while mapping the field. Do not impose a fixed count. Stop only when additional lenses yield duplicates, trivial variants, or ideas dominated by existing work.

Use problem-first, contradiction, boundary/failure, simplicity, composition/decomposition, abstraction-shift, changed-assumption, stakeholder, and cross-domain transfer lenses. Treat cross-domain transfer as a first-class innovation source, but follow `references/cross-domain-transfer.md`: require a structural mapping, a target-domain adoption search, broken-assumption analysis, and a falsifiable prediction. A renamed source method or surface analogy is not innovation.

For a new candidate pool, follow `references/role-debate-protocol.md`:

- let the Native Innovator and Cross-Domain Transfer Researcher generate independently from permission-scoped evidence;
- preserve proposer isolation until first-round outputs are fixed;
- let the Chair cluster by problem, mechanism, and claimed capability before discussion;
- use isolated agents when callable and isolated role passes otherwise, with identical artifacts in both modes;
- reserve canonical state writes for the Chair.

Preserve all candidates in `ideas/idea_pool.json`, including rejected and parked ideas. Use statuses:
`raw`, `screened`, `novelty-risk`, `discussion-active`, `experiment-ready`, `parked`, `rejected`.

Before assigning a new idea ID, compare its problem, mechanism, and evaluation
signatures against `ideas/mechanism_families.json`. Classify it as a new
family, material same-family revision, adjacent family, or cosmetic variant.
Do not admit a cosmetic variant as a new candidate. Inherit all family-level
scientific failures and require the exact material delta specified in
`references/anti-reskin-protocol.md`.

### 4. Run structured debate and adversarial novelty review

For every serious candidate:

- run cross-examination, then give the Adversarial Reviewer both proposer artifacts, closest-work evidence, kill-query results, and matched reviewer patterns;
- allow one bounded rebuttal; allow one additional round only when new verified evidence changes a factual premise;
- send factual disputes back to search rather than resolving them through rhetoric;
- Write the strongest anticipated rejection: “This is already known because…”.
- Search the exact proposed mechanism, weaker and stronger variants, synonyms, component combinations, source-domain terms, target-domain terms, and the claimed outcome.
- Identify the closest work and compare problem, mechanism, supervision, data, evaluation, and claimed contribution.
- Search failed attempts and limitations; distinguish genuinely open, partially attempted, stale-tool dead end, and plausibly fundamental barrier.
- Classify contribution as capability-unlocking, problem-solving, empirical discovery, resource/benchmark, reframing, or incremental extension.
- Separate `soundness` from `excitement`; a plausible method can still be unimportant, and an exciting claim can still be unsupported.
- Test mechanism identifiability: specify an observation that distinguishes the proposed mechanism from capacity, data, compute, prompting, retrieval, and implementation confounders.
- Run the simple-baseline survival test and collision-resistance check in `references/idea-evaluation-rubric.md`.
- Query the reviewer-pattern library when available. Compare matched accepted and rejected work at the same venue, period, area, and contribution type; never infer quality from decision alone.
- For a shortlisted new family or revision of a failed family, run a cold
  anti-reskin review from frozen artifacts. Do not expose proposer discussion
  history or the desired verdict. Record reviewer independence, the mechanism
  signature hash, inherited failures, and the material-delta verdict.

Never claim proof that nobody has done an idea. Report `novelty_confidence`, `recall_confidence`, occupied components, remaining differentiator, and kill queries. Verify identifiers and any quoted evidence.

The Chair adjudicates with `survive`, `revise`, `park`, `reject`, or `novelty-risk`. Do not decide by majority vote or average away a fatal gate. For shortlisted or costly candidates, instantiate temporary novelty, mechanism, evaluation, and venue-review lenses; do not turn them into permanent roles by default.

### 5. Score evidence, not enthusiasm

Apply the gates and scoring anchors in `references/idea-evaluation-rubric.md`. Record evidence and uncertainty for each dimension; never hide a fatal gate behind a high average.

Require:

- a contribution-type fit judgment;
- problem half-life and benchmark half-life;
- mechanism identifiability;
- simple-baseline survival;
- collision resistance;
- the information gain of the cheapest pilot;
- reviewer attack and required-evidence matrices.
- a passed anti-reskin gate with no unresolved inherited family failure;
- a prerequisite satisfiability statement showing that the cheapest pilot can
  meet its minimum data, compute, budget, and permission requirements.

Use scores to compare candidates, not to manufacture precision. A candidate with unresolved fatal novelty, feasibility, ethics, or mechanism gates cannot become `experiment-ready`.

### 6. Discuss and promote

Present the field map and provisional candidates together. For each candidate state:

- two-sentence problem and mechanism;
- why it matters;
- closest prior work and exact distinction;
- cross-domain source, if any;
- soundness, excitement, novelty, feasibility, and impact risks;
- cheapest discriminating pilot;
- top reviewer attacks and evidence that would neutralize them;
- conditions that would kill or revise it.

The researcher chooses what to pursue. Promote only an explicitly selected,
sufficiently specified idea with a passed anti-reskin gate to
`experiment-ready`, then create `ideas/<idea-id>/idea_contract.yaml` using
`references/idea-contract.md`. Run `scripts/check_idea_lineage.py` and preserve
its report before handoff. Recommend a `pilot` or `full` entry mode without
designing or running the experiment.

### 7. Coordinate downstream

Append state transitions to `logs/research_events.jsonl`.
`research-experiment-lab` owns all experiment design, execution, debugging,
aggregation, and verification. Handoff the family ID, mechanism-signature hash,
lineage-check report, and inherited failure IDs with the idea revision. If
verified experimental evidence contradicts the mechanism, add a family failure
entry before reviewing a revision request and move the idea back to
`discussion-active` or `rejected`. If new literature occupies the
differentiator, set `novelty-risk` and block new long experiments until the
user reviews it.

## Integrity

- Distinguish metadata-only evidence, abstract-level evidence, and full-text-verified evidence.
- Rank evidence sources: primary papers, official reviewer criteria and public reviews, systematic syntheses, then informal experience posts. Use experience posts only to generate hypotheses or queries, never as decisive novelty evidence.
- Do not fabricate papers, identifiers, quotes, results, or novelty certainty.
- Use only publicly readable reviewer records; preserve source identifiers and attribution, do not infer reviewer identities, and do not republish full review text.
- Never pass OpenReview credentials on the command line or store them in project state. If anti-bot verification blocks guest access, record the challenge and use an explicitly authorized local environment token or browser session; never bypass access controls.
- Do not run experiments in this skill.
- Do not overwrite another stage's detailed state.
- Store structured claims, evidence, attacks, concessions, and decisions; never store private chain-of-thought.
- Let only the Chair write canonical ideation and debate state when multiple roles or agents are active.
- Use `scripts/research_state.py` for initialization and revision-safe index updates.
