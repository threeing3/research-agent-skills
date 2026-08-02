# Public Reviewer-Pattern Workflow

Build a traceable library of recurring reviewer objections from public records. Use it to retrieve comparable risks and evidence requirements, not to predict acceptance.

## Contents

- Scope and source policy
- Public access and challenge handling
- Coverage probe and collection
- Corpus construction
- Pattern extraction and quality
- Retrieval and idea-stage output
- Training boundary

## Scope and source policy

Prefer official public review records and official venue criteria. OpenReview stores submissions, reviews, rebuttals, meta-reviews, comments, and decisions as related notes. Use only records readable through the public interface or API.

- Restrict collection to the AI venue families and source types in `ai-venue-scope.json`. Reject unrelated venues.
- Prioritize ICLR, NeurIPS, and ICML main conferences for general review patterns; prioritize CVPR and ICCV for VideoQA, video, vision, and multimodal questions. Treat AAAI as complementary.
- Keep workshop, journal, and position-track records in separate source strata. Never merge their scores, severities, or decision rates into main-conference calibration.
- Preserve venue, year, forum/note identifiers, public URL, contribution type, area, and retrieval date.
- Preserve attribution required by the source license.
- Do not ingest private records, infer reviewer identity, or republish complete review text.
- A local source cache may retain the public note content needed for extraction, together with source identifiers, retrieval time, and the OpenReview terms URL. Pattern records and user-facing outputs must use structured paraphrases and only short evidence snippets when necessary; do not republish complete reviews.
- Treat informal experience posts as query inspiration, never as decisive evidence.

Official references:

- OpenReview note model: <https://docs.openreview.net/reference/api-v2/entities/note>
- OpenReview public data retrieval: <https://docs.openreview.net/how-to-guides/data-retrieval-and-modification/how-to-get-all-notes-for-submissions-reviews-rebuttals-etc>
- OpenReview terms: <https://openreview.net/legal/terms>

## Public access and challenge handling

Use guest access first. Public permission and automated access are separate:

- a record is eligible only when its note and retained fields are readable by `everyone`;
- the API may still require an anti-bot browser challenge for an anonymous network session;
- an ordinary account does not grant access to private records;
- never attempt to bypass a challenge or ingest records made visible only through reviewer, author, or chair membership.

If a challenge blocks collection, preserve its URL and the partial checkpoint. Let the user complete the official browser challenge or provide an explicitly authorized token/cookie through local environment variables. Never accept secrets as command-line arguments or write them to logs, manifests, state, or source control.

When verification is isolated to the browser session, prefer browser export plus local ingest over copying cookies:

1. open the exact public API query in the verified browser;
2. save the returned JSON page under `research_state/review_patterns/browser_import/<venue>/`;
3. import it with `openreview_public_corpus.py ingest`;
4. retain the source page and its SHA-256 digest for provenance.

Do not inspect or export browser cookies, local storage, passwords, or session tokens.

Generate a bounded browser plan before exporting multiple pages:

```powershell
python scripts/openreview_public_corpus.py browser-plan <project-root> `
  --venue-id ICLR.cc/2025/Conference `
  --reported-count 3703 --max-submissions 20 `
  --browser-page-size 1
```

Browser plans are deliberately bounded. Do not plan a full multi-thousand-paper crawl through interactive browser tabs. Use browser export for probes and stratified samples; use an authorized API session for full collections.

## Coverage probe and collection

Use the deterministic collector:

```powershell
python scripts/openreview_public_corpus.py probe <project-root> `
  --venue-id ICLR.cc/2025/Conference

python scripts/openreview_public_corpus.py collect <project-root> `
  --venue-id ICLR.cc/2025/Conference `
  --page-size 100 --resume

python scripts/openreview_public_corpus.py ingest <project-root> `
  --venue-id ICLR.cc/2025/Conference `
  --input-json <browser-exported-page.json>
```

For older or unusual venues, query by the verified submission invitation:

```powershell
python scripts/openreview_public_corpus.py probe <project-root> `
  --invitation <verified-submission-invitation>
```

The collector:

- defaults to API v2 and supports an explicit `--api-base` for legacy access;
- filters notes and fields to public readers;
- groups official reviews, author responses, meta-reviews, decisions, and public comments;
- keeps full public text only in the local source cache and keeps pattern/output records concise;
- writes an atomic canonical forum corpus and an offset checkpoint;
- imports browser-verified public JSON pages without transferring browser credentials;
- appends a manifest row and research event for complete, blocked, and failed runs;
- writes readable logs under `research_state/review_patterns/logs/`;
- reads optional `OPENREVIEW_ACCESS_TOKEN` or `OPENREVIEW_COOKIE` environment variables without persisting them.

Run `probe` for every venue-year before corpus collection. A successful probe reports the number of sampled submissions containing each public chain type. Do not collect a venue as rejection evidence when reviews, meta-reviews, or decisions are unavailable for the intended analysis.

Coverage output declares four separate eligibility levels:

- review advice: at least one public official review;
- decision-linked patterns: public reviews and decisions;
- fatal/decision-driving patterns: public reviews, decisions, and meta-reviews;
- observed rejection patterns: at least one sampled public rejection decision.

Never infer rejection coverage from an accepted-only sample.

## Source-type boundaries

Use source types as follows:

| Source type | Primary value | Do not use for |
| --- | --- | --- |
| Main conference | reviewer attacks, experimental evidence, decision-linked rejection patterns | acceptance prediction |
| Workshop | emerging topics, speculative mechanisms, cross-domain transfer, early failures | fatal severity or top-conference rejection calibration |
| Journal | soundness, reproducibility, long-form evidence, revision paths | top-conference excitement or acceptance calibration |
| Position track | open problems, research agendas, framing, counterarguments, evaluation critique | method novelty proof, experimental sufficiency, method-paper rejection calibration |

A position paper argues that the field should adopt a view, agenda, policy, evaluation principle, or research direction. Its central evidence is argumentative and synthetic rather than a complete new-method experiment package. Retain it because it is valuable for discovering durable problems and challenging assumptions, but label every derived item as `agenda-and-framing`.

For journals, begin with TMLR because it uses public OpenReview discussion and iterative revision. Add other AI journals only after verifying a public review chain and a stable venue identifier.

For workshops, accept only explicitly scoped workshops under approved AI venue families. A workshop's parent conference does not upgrade its reviewer standards; preserve the exact workshop identity.

## Corpus construction

Sample accepted and rejected papers where both reviews and decisions are publicly available. Match comparisons by:

- venue and year;
- area or task;
- contribution type;
- submission maturity where observable.

Do not treat public rejected papers as an unbiased sample of all rejections. Record coverage gaps, challenge blocks, and access limits in `research_state/review_patterns/corpus_manifest.jsonl`.

For each paper, retrieve:

- title, abstract, keywords, and subject areas;
- official reviews and confidence where public;
- author responses and discussion;
- meta-review or area-chair summary;
- decision.

## Pattern extraction

Extract concerns with a constrained schema:

```yaml
pattern_id: ""
dimension: novelty
subtype: ""
severity: major
reviewer_claim: ""
evidence_requested: []
author_response_status: absent
meta_review_resolution: unknown
decision_role: unknown
paper_area: ""
contribution_type: ""
venue: ""
year: 0
source_note_ids: []
source_url: ""
short_evidence: ""
extraction_confidence: low
human_verified: false
```

Allowed dimensions:

- novelty;
- soundness;
- significance;
- evaluation;
- reproducibility;
- clarity/positioning;
- efficiency;
- data/ethics;
- venue fit.

Allowed response states: `absent`, `addressed`, `partially-addressed`, `unresolved`, `resolved`, `unknown`.

Assign severity:

- `fatal`: the meta-review or decision summary treats the concern as decision-driving and it remains unresolved;
- `major`: substantial evidence or revision is required, but its decision role is unclear or potentially fixable;
- `minor`: clarification or polish without a central claim failure.

Never infer `fatal` from rejection plus a single review comment.

## Extraction quality

Use two passes:

1. extract all distinct reviewer claims, evidence requests, and author-response links;
2. verify each claim against the public source and classify its resolution and decision role.

Audit a stratified sample across venues, years, areas, decisions, and pattern types. Track taxonomy agreement, unsupported extraction rate, missing-concern rate, and severity agreement in `research_state/review_patterns/extraction_audit.jsonl`.

## Retrieval

Build a query from the candidate's:

- problem and intended contribution;
- mechanism and claimed novelty;
- closest work;
- evaluation plan and known weaknesses.

Use hybrid retrieval:

1. keyword retrieval for exact terminology and reviewer phrasing;
2. semantic retrieval for structurally similar concerns;
3. metadata filtering by venue, period, area, and contribution type;
4. reranking by mechanism and evidence gap.

Retrieve matched accepted and rejected cases. Compare which concerns were resolved, tolerated, or decision-driving. Do not claim that a pattern caused rejection unless the meta-review supports that link.

## Idea-stage output

Write to the idea contract:

- matched accepted and rejected cases;
- recurring attacks and their applicability;
- fatal and major risks;
- evidence reviewers previously required;
- whether rebuttals resolved the concern;
- coverage date and retrieval limitations.

Convert applicable patterns into the Reviewer Attack Matrix. Ignore prose-only issues during early ideation unless they reveal an incoherent contribution.

## Training boundary

Begin with retrieval and audited structured extraction. After enough clean labels exist, train only bounded components:

- multi-label concern classification;
- severity or decision-role ranking;
- retrieval reranking;
- domain-specific semantic representations.

Do not train or report a general acceptance-probability model as an idea-quality score. Decisions contain venue, year, area, reviewer, and selection biases; review scores and decision fields also create label leakage.
