# Novelty and Field-Mapping Workflow

## Baseline search families

Cover task names, benchmark names, dominant method families, recent surveys, current conference/arXiv work, explicit limitations, negative results, and neighboring tasks. Record query, source, date, filters, result count, screened count, retained count, and newly discovered clusters.

## Incremental search

Use the previous `coverage_end` with an overlap window. Search newly published work, new versions of known preprints, citations around closest work, and the saved kill queries of active ideas.

## Core novelty gates

1. Open: adversarial search finds no work occupying the complete claimed combination; absence remains screening evidence, not proof.
2. Contribution: the remaining differentiator creates a meaningful capability, explanation, resource, or empirical finding rather than a cosmetic recombination.
3. Feasible: data, compute, baselines, metrics, and a discriminating pilot are realistically available.
4. Identifiable: the proposed mechanism predicts an observation that the strongest alternative explanation does not.
5. Collision-resistant: discovery of one close paper does not erase every defensible contribution.

For failed attempts, separate:

- `genuinely-open`: no attempt found, with recall caveat;
- `partially-attempted`: attempts exist but outcome is inconclusive;
- `stale-blocker`: a named old limitation has a documented successor technology;
- `fundamental-risk`: multiple sources or a survey identify a problem-level barrier.

An isolated lack of recent papers never proves abandonment or impossibility.

## Evidence sources

Rank evidence:

1. verified primary papers, artifacts, and benchmark documentation;
2. official reviewer criteria and public review/meta-review records;
3. systematic syntheses and surveys;
4. informal experience posts.

Use informal sources to discover objections and search terms, not to establish novelty or venue policy.

For fast-moving industrial topics, run the separate evidence lane in
`industry-to-paper-workflow.md`. Industry sources may establish a production failure,
impact boundary, or reproducibility lead. They do not establish scholarly novelty.
Search public disclosures of allegedly common industry techniques because industry
practice may still be relevant prior art even when it is not a peer-reviewed paper.

## Candidate comparison

Compare candidates with `idea-evaluation-rubric.md`. Keep soundness and excitement separate. Include importance, problem half-life, mechanism identifiability, novelty evidence, closest-work distance, collision resistance, simple-baseline survival, pilot information gain, resource cost, reviewer attacks, and salvage value. Scores summarize evidence; they never replace it or override fatal gates.
