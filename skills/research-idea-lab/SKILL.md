---
name: research-idea-lab
description: Discover evidence-backed ML/AI research problems, separate competing bottleneck explanations, derive methods only when the problem supports them, control low-information iteration, inspect related work, and prepare selected ideas for validation. Use for finding directions, diagnosing why a method or benchmark fails, developing or rescuing a research idea, discussing novelty, or deciding what evidence is needed next, especially for VideoQA and long-video understanding. Use strict scoring, rejection, ranking, or experiment-readiness only when the user explicitly requests that decision.
---

# Research Idea Lab

Treat research ideation as movement from uncertainty to discriminating evidence. The skill supplies a minimal reusable decision loop, not a mandatory end-to-end process. Expand the workflow only when the task, risk, or requested deliverable needs it.

## Core distinction

Keep four layers separate:

1. observed failure: what repeatedly happens and under which conditions;
2. bottleneck hypothesis: a possible explanation for that failure;
3. method hypothesis: an intervention expected to change the bottleneck;
4. implementation realization: the concrete program, prompt, data flow, or model change.

A low benchmark score does not identify a bottleneck. A working implementation does not prove the problem exists. A method improvement may support the method hypothesis only after the problem and comparison are independently measurable.

## Minimal evidence loop

Use only the parts needed for the current request:

1. **Observe** — state the failure in ordinary language and identify inspectable evidence.
2. **Separate** — name credible competing explanations, including the strongest simple explanation.
3. **Discriminate** — find the smallest observation or intervention that makes those explanations predict different outcomes. Prefer a check independent of the full proposed method; when pure observation is insufficient, use a minimal diagnostic intervention rather than the complete method.
4. **Derive** — after one bottleneck is sufficiently supported, derive the required behavior, mechanism, and simplest implementation.
5. **Learn** — bind each result to the layer it informs, then continue, return to diagnosis, revise the mechanism, pivot, or park.

These are decision aids, not a fixed sequence. A narrow discussion may need only one or two. A formal experiment handoff needs the full chain.

Read references/problem-and-diagnosis.md when the problem or bottleneck is uncertain. Read references/iteration-control.md before recommending another implementation or experimental round after a negative, inconclusive, or repeated failure.

When an experiment supplies a verified
`diagnostic_evidence_handoff.json`, read it during **Learn**. Check its evidence
references, scope, and limitations before deciding whether to keep or weaken a
bottleneck, narrow the problem, or return to diagnosis. Treat
`recommended_update` as an experiment-owned recommendation, not an automatic
canonical state transition. Read references/state-protocol.md before persisting
the decision.

## Choose a primary intent, not a rigid mode

Infer the user's main intent and use adjacent capabilities when useful:

- **Find a problem**: establish observed failures, competing explanations, value, and feasibility before proposing methods.
- **Explore solutions**: generate materially different routes for a selected or user-supplied problem.
- **Develop an idea**: strengthen a rough mechanism, implementation path, prediction, or rescue route.
- **Inspect related work**: search for close mechanisms, evidence, collisions, and changed assumptions.
- **Make a strict decision**: score, rank, reject, or admit an idea only when the user explicitly asks.
- **Monitor**: refresh an existing evidence map without silently changing an idea's status.

Do not force a request into exactly one isolated workflow. Do not escalate ordinary discussion into strict review or formal experiment admission.

## Start lightly

- Locate the project root and inspect research state only when the work needs continuity, revision, or durable artifacts.
- Do not write state for ordinary discussion unless the user asks or the result will be reused.
- State bounded assumptions and continue when they do not materially change the research target.
- Search to resolve the next decision-relevant uncertainty. Broaden or saturate search only for a requested novelty review, strict gate, or durable field map.
- Load only references relevant to the current decision.

## Establish the problem before building the method

Before treating a direction as method-ready, make the following understandable without invented terminology:

- one-sentence research problem;
- observed failure and conditions;
- evidence and meaningful counter-evidence;
- at least one credible competing explanation;
- a separating observation that does not require the proposed method to succeed;
- scientific or practical value;
- feasibility blockers in data, measurement, compute, supervision, or access.

When these are incomplete, return a problem seed and the next evidence task. Do not invent modules to make an uncertain problem appear complete.

Do not use the full proposed method's performance to establish the existence of its target bottleneck. First diagnose the bottleneck with existing data, controls, analysis, or a method-independent probe. When the bottleneck is identifiable only through intervention, a minimal diagnostic intervention such as evaluator-side oracle information or component substitution is allowed, provided it does not instantiate the complete proposed solution. If no feasible separating observation or minimal intervention exists, label the mechanism not identifiable and revise or park it.

## Derive methods from supported bottlenecks

Use the chain:

observed failure → supported bottleneck → required behavior change → mechanism → simplest implementation → distinguishing prediction

A candidate may remain incomplete while missing links are explicit. Do not require a fixed number of candidates. Diversify until additional routes become cosmetic, unsupported, or irrelevant.

Explain a developing method first in one ordinary sentence:

> Because the system fails at ___, make it ___; if the explanation is correct, ___ should change, not merely the aggregate score.

If this sentence is unclear to a domain reviewer, clarify the problem and causal mechanism before naming or expanding the method.

For an existing baseline, state what is added, removed, replaced, rewired, or combined; where the change occurs; why existing behavior is insufficient; and what control isolates the proposed mechanism.

## Control iteration by information gain

Before recommending another implementation or experiment, answer:

1. What uncertainty changed after the previous round?
2. What new variable or behavior will the next round observe?
3. Which competing explanations predict different outcomes?
4. If the result repeats, what will stop, narrow, or change?

If these cannot be answered, do not create another scientific revision. Return to problem diagnosis, repair the measurement, materially revise the mechanism, or park the route.

Separate:

- **engineering repair**: makes a predeclared mechanism or measurement actually run;
- **scientific iteration**: changes a bottleneck hypothesis, causal operator, control, measured variable, or distinguishing prediction.

Engineering repairs do not become new scientific evidence merely because the version number changes. After the intended implementation is confirmed active, failure of its distinguishing prediction is mechanism counterevidence; do not continue prompt, parser, fallback, or threshold tuning under the same claim without a material reason.

Use two consecutive low-information rounds as a default warning, not a universal ban. Continuing is reasonable only when new evidence, a newly verified engineering blocker, or a material mechanism change makes the next round informative. State the reason and stopping condition.

When a method depends on generated traces, retrieved evidence, pseudo-labels, annotations, or another intermediate artifact, check that the artifact can occur naturally at useful quality and coverage before a long run. Choose thresholds from the claim and intended analysis; do not use a universal pass rate.

## Interpret results at the right layer

Use these meanings as guidance, not a rigid state machine:

- implementation not established: the intended mechanism did not actually run;
- measurement inconclusive: the observation cannot distinguish the explanations;
- mechanism counterevidence: realization succeeded but the distinguishing prediction failed;
- supportive signal: realization succeeded and the predicted behavior appeared;
- problem counterevidence: evidence weakens or refutes the observed failure or bottleneck itself.

A negative result does not automatically erase the parent problem. A code repair does not automatically preserve the mechanism. Update only the layer the evidence reaches.

## Literature and novelty

Prefer primary papers and inspectable artifacts. Distinguish metadata, abstract, full text, code, and reproduced evidence. Literature absence is not proof of novelty or of a research problem.

For early work, run only enough collision search to avoid obvious duplication and identify the closest alternative. Read references/novelty-workflow.md for a focused novelty review. Read the strict references only when the user requests comparison, rejection, ranking, or formal admission:

- references/idea-evaluation-rubric.md
- references/anti-reskin-protocol.md
- references/role-debate-protocol.md
- references/role-artifact-schemas.md
- references/idea-contract.md
- references/research-process-metrics.md

Read references/cross-domain-transfer.md for a real transfer. Read references/videoqa-lenses.md for VideoQA or long-video work. Read references/reviewer-pattern-workflow.md and references/ai-venue-scope.json only for public reviewer-pattern or venue-calibration work.

## State and artifacts

Match artifact weight to the decision:

- ordinary discussion: concise answer, usually no state write;
- reusable problem or idea: a small revisioned card with evidence and open uncertainties;
- experimental handoff: freeze the claim, comparison, distinguishing prediction, realization check, outcome meanings, budget, logs, and stopping conditions;
- strict decision: use the full novelty, lineage, and review artifacts.

Read references/state-protocol.md before canonical state writes. Preserve historical evidence and do not bulk-rewrite earlier records. Use scripts/research_state.py for revision-safe index updates when required.

The research-experiment-lab skill owns experiment design, execution, debugging, aggregation, and verification. This skill may prepare the decision and handoff, but does not launch experiments.

For a bounded user-approved validation campaign, the approval may cover the declared model, data, cost, objective, and expected engineering repairs. Request renewed approval when those boundaries change materially, rather than treating every small repair as a new scientific round.

## Output

Lead with the useful research conclusion, not workflow narration. Adapt structure and length to the request.

For problem discovery, return the supported problems or honest smaller set, their evidence, competing explanations, value, feasibility, and next discriminating checks.

For solution exploration or development, return the parent problem first, then the motivation-to-mechanism derivation, alternatives, unknowns, feasibility, predicted evidence, and recommended next decision.

For strict review, return the verdict first, then search basis, closest-work subtraction, fatal risks, uncertainty, repair conditions, and decision.

The researcher chooses what to pursue. Do not convert advisory uncertainty into a blocking question unless truthfulness, permission, cost, ethics, or scope requires a decision.

## Integrity

- Do not fabricate papers, identifiers, quotes, results, reviewer reactions, or novelty certainty.
- Do not hide contradictory or inconclusive evidence.
- Use only publicly readable reviewer records; do not infer reviewer identities or bypass access controls.
- Never store credentials or private chain-of-thought in research state.
- Preserve authorization boundaries for external actions and paid resources.
