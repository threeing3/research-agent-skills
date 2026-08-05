# Industry-to-Paper Workflow

Use this workflow when ideation depends on fast-moving production AI or agent
problems, or when the researcher prioritizes a credible paper submission over a
broad idea list. Industry evidence establishes that a problem occurs in practice;
it does not establish novelty, scientific validity, or likely acceptance.

## Contents

- Two evidence lanes
- Source roles
- Search the problem surface
- Store signal cards
- Quantify without manufacturing a score
- Convert a signal into a scientific candidate
- Apply the publication-first gate
- Integrity and privacy

## Two evidence lanes

Run two linked searches without mixing their evidentiary roles:

1. **Industry lane**: discover recurring failures, constraints, regressions, costs,
   workarounds, and unmet needs in deployed systems.
2. **Scholarly lane**: determine whether the problem has been formalized, whether a
   contribution is occupied, and what evidence a target venue would require.

An industry signal may motivate a candidate only after it is translated into a
bounded scientific question and falsifiable claim. A paper may motivate a method,
but it does not prove that the corresponding production problem is important.

## Source roles

Classify every source before using it:

| Level | Source type | Permitted use |
| --- | --- | --- |
| I0 | public incident report, measured production study, reproducible issue, or released trace/dataset | establish a directly observed failure within the documented boundary |
| I1 | official engineering report with methods, denominators, and limitations | support recurrence, impact, and operational constraints |
| I2 | repository issue or discussion with version, environment, and reproduction details | generate and sometimes corroborate a failure hypothesis |
| I3 | practitioner experience post, forum thread, talk, or survey | discover vocabulary, workarounds, and candidate queries |
| I4 | product announcement, marketing claim, unsourced summary, or repost | query lead only |

Syndicated copies, comments repeating one report, and multiple posts from the same
organization count as one source lineage. Record vendor interest and likely
selection bias. Never infer absence of a problem from a company's silence.

## Search the problem surface

Search at least the applicable families below:

- engineering blogs, reliability reports, incident reviews, and architecture notes;
- changelogs, deprecations, known limitations, and regression notices;
- public issue trackers and discussions with reproduction steps;
- benchmark failure analyses and evaluation-harness reports;
- practitioner forums for repeated failure descriptions and workaround patterns;
- job descriptions or procurement requirements only as weak demand signals;
- production metrics involving task failure, retries, human intervention, latency,
  token or monetary cost, security, privacy, and rollback;
- cross-provider and cross-model reports that test whether a problem survives a
  product or model update.

Use failure-oriented queries, not only topic names. Include combinations such as
`failure`, `regression`, `incident`, `unreliable`, `human handoff`, `rollback`,
`latency`, `cost`, `permission`, `prompt injection`, `memory`, `tool error`, and
`evaluation gap`. Preserve exact queries, dates, filters, screened counts, retained
signals, and inaccessible sources.

Stop an industry scan when two materially different source families add neither a
new failure class nor an independent organization, subject to recorded access and
time limits. This is a stopping heuristic, not proof of complete coverage.

## Store signal cards

Write normalized cards to
`research_state/industry/signals.jsonl` and a scan manifest to
`research_state/industry/scan_manifest.json`. Use this minimum shape:

```yaml
signal_id: IND-001
observed_at: ""
published_at: ""
organization: ""
source_lineage: ""
source_level: I0
source_url: ""
system_boundary:
  model_or_provider: ""
  harness_or_framework: ""
  task: ""
  deployment_setting: ""
failure:
  observable: ""
  denominator: null
  frequency: null
  severity: ""
  workaround: ""
impact:
  task_failure: null
  human_intervention: null
  latency: null
  token_or_monetary_cost: null
  security_or_privacy: null
reproduction:
  public_artifact: ""
  steps_available: false
  reproduced_by_independent_source: false
biases_and_limits: []
candidate_queries: []
```

Use `null`, not zero, for unavailable measurements. Preserve the original unit and
denominator. Do not compare percentages with different units of analysis.

## Quantify without manufacturing a score

Keep these diagnostics separate; do not sum them into an industry-opportunity or
acceptance score.

### Independent recurrence count

```text
IRC = number of independent organizations reporting the same normalized failure
```

Also report source levels and source lineages. One I0 report with a public trace can
be stronger than many I3 anecdotes. As a default screening rule, `IRC >= 2` is
needed to call a problem recurring. An `IRC = 1` candidate may proceed only when the
single source includes strong public evidence and the claim is explicitly bounded.

### Production-impact vector

Report a vector rather than blending incomparable harms:

```text
PIV = [task_failure, human_intervention, latency, cost, security_or_privacy]
```

Each dimension contains the raw estimate, denominator, observation window, source
IDs, and missingness. A severe security incident is not averaged down by unknown
latency, and a latency improvement does not establish task correctness.

### Cross-system persistence

Create a matrix over model/provider, harness, task, and deployment setting. Mark each
cell `observed`, `not_observed`, `not_tested`, or `incomparable`. A production problem
is more durable when it survives relevant system changes. Never treat `not_tested`
as `not_observed`.

### Reproduction readiness

Rate the public reproduction path:

- `0`: private anecdote with no observable specification;
- `1`: observable failure described, but no public inputs or environment;
- `2`: public inputs or traces exist, with important missing dependencies;
- `3`: a public approximation can reproduce the failure;
- `4`: independent public reproduction exists and supports a controlled study.

This rating measures research access, not problem severity.

### Academic-gap status

Record one of `unsearched`, `occupied`, `partially-addressed`, `open-with-caveats`,
or `translation-gap`. A translation gap means scholarly methods exist but their
assumptions or evaluations do not cover the production boundary. Verify this status
with the full novelty workflow; industry novelty claims are not sufficient.

## Convert a signal into a scientific candidate

Require this chain before candidate admission:

```text
observed production failure
  -> normalized failure class and system boundary
  -> evidence that the failure is recurring or strongly documented
  -> scholarly gap or invalid assumption
  -> scientific question
  -> falsifiable mechanism or empirical claim
  -> public approximation or evaluation environment
  -> target contribution type and minimum paper package
```

Reject or park candidates that remain vendor-specific bug fixes, depend on private
telemetry that cannot be approximated, disappear under a likely model update, or
offer only an engineering workaround without new transferable knowledge. A negative
result, benchmark, dataset, measurement study, or failure taxonomy may be the right
contribution when a new method is not justified.

## Apply the publication-first gate

Before a serious candidate can become `experiment-ready`, write a publication case
using current official criteria for the intended venue and track. Record:

- target venues or tracks and submission horizon;
- contribution type recognized by each target;
- one-sentence knowledge claim, not a product feature claim;
- closest work and the exact defensible difference;
- minimum publishable evidence package;
- public reproduction and artifact plan;
- required baselines, generalization settings, and failure analysis;
- the two strongest likely reviewer attacks and evidence needed to answer them;
- the claim that survives a close contemporaneous paper;
- fallback contribution and venue only when supported before outcomes are known.

Mark the gate `pass`, `unresolved`, or `fail`. It passes only when the contribution is
legible to a target venue, the central evidence package is feasible within the stated
time and resources, and the primary claim remains worthwhile without proprietary
access. Do not predict acceptance probability. Venue fit cannot compensate for failed
novelty, soundness, ethics, mechanism, or feasibility gates.

Use current official reviewer criteria rather than remembered norms. Useful anchors
include the current NeurIPS, ICLR, CVPR, and ACL/ARR reviewer guidance. Industry
practice can establish significance, but claims that a technique is common in
industry still require a public disclosure or publication when used as prior art.

## Integrity and privacy

- Use only public or explicitly authorized material.
- Do not upload private logs, code, prompts, customer data, or incident details.
- Do not infer confidential architecture from symptoms.
- Separate observed facts, practitioner interpretations, and the researcher's
  proposed explanation.
- Refresh time-sensitive signals before promotion; record the refresh date.
- Treat experience posts as hypothesis generators unless corroborated by stronger
  evidence.
