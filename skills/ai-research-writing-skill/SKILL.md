---
name: ai-research-writing-skill
description: End-to-end research paper generation, review, and revision for ML/AI/CV/NLP projects from repositories, notes, experiment logs, drafts, and conference templates. Use when building a paper story, mapping claims to evidence, writing or revising sections, producing figures and tables, verifying citations, acting as a skeptical reviewer, running venue or build checks, or preparing a LaTeX/Overleaf/Git submission package.
---

# AI Research Writing Skill

## Mandate

Treat paper writing as claim-evidence engineering, not prose generation.

- Ground claims in repository files, experiment artifacts, notes, or verified citations.
- Never invent citations or numeric results. Mark missing evidence visibly and weaken unsupported claims.
- Keep target-domain novelty, source provenance, transfer/adaptation value, contribution strength, implementation fidelity, and experimental maturity as separate claims. Never use one as a substitute for another.
- For full papers, produce concrete LaTeX, BibTeX, figure, table, review, and build artifacts; do not stop at an outline.
- Keep human judgment in the loop for scientific correctness, visual inspection, reviewer risk, and final submission decisions.

## Route the Task

Choose the smallest route that covers the request. Load only the listed references first.

| Route | Load first |
|---|---|
| Full paper or major revision | `references/workflow.md`, `references/artifacts.md` |
| Empirical evidence assessment or missing experiments | `references/empirical-experiment-design.md`, `references/experiment-requests.md`, `references/artifacts.md` |
| Verified-result ingestion and claim backfill | `references/results-backfill.md`, `references/numeric-evidence.md` |
| Upstream research-system handoff | `references/research-handoff.md`, `references/artifacts.md` |
| Story, thesis, gap, or contribution | `references/paper-story.md` |
| Section writing or revision | `references/README.md`, then the section-specific reference |
| Figures and tables | `references/figure-workflow.md`, `references/figure-spec.md`; for VideoQA or long-video papers also invoke `videoqa-paper-figures` |
| Citation search or repair | `references/citation-workflow.md` |
| Reviewer diagnosis | `references/reviewer-guidelines.md`, `references/reviewer-self-review.md` |
| Submission or camera-ready audit | `references/submission-packaging.md`, `references/citation-checklist.md` |
| Deterministic checks or formatting | `scripts/README.md` |

## Execution Contract

For full-paper and submission work:

1. Create `paper_state.json` from the contract in `references/artifacts.md`; declare mode, stage, venue, main TeX, bibliography, required artifacts, blockers, and build record.
2. If `research_handoff.json` exists, run `check_research_handoff.py --require-unblocked` first. In a shared-state project, accept only handoff v2 after it reconciles the active idea lifecycle, idea-pool and contract hashes, active experiment, plan hash, `paper-ready` state, and v2 verification identity. Otherwise inventory the repository and experiments before drafting. Create one task packet and update `plan/progress.md` at the start and end.
3. Establish the story, claim boundaries, and literature position before long-form prose.
4. For empirical papers, validate the baseline, method-component, experiment-matrix, reproducibility, and long-run logging evidence in `references/empirical-experiment-design.md`. When `research-experiment-lab` state exists, issue a structured experiment request for missing evidence; do not design, launch, debug, or modify experiments from this writing skill.
5. Follow the two-pass drafting order in `references/workflow.md`: write evidence-bearing core sections first, then finalize framing sections.
6. When results arrive, follow `references/results-backfill.md`; never promote `planned` or `placeholder` evidence to `verified` from file presence alone.
7. Run the mode-aware quality gate. A terminal stage is invalid when inputs are missing, claims/citations remain unresolved, verification is pending, blockers remain, or build hashes are stale.

Keep process instructions in plan/review files, never in manuscript prose.

## Gates

- **Evidence**: exact numbers must trace to data, logs, tables, notebooks, or scripts. Quantitative papers maintain numeric-evidence v2 selectors and recomputable aggregates.
- **Experiment evidence**: verify that direct competitors, foundational methods, ablation anchors, robustness, efficiency, and failure analysis support the intended claims. Route missing or invalid evidence to `research-experiment-lab`.
- **Admission**: never use an `exploratory-validation` experiment as paper-ready method evidence. Require a formal plan, focused target-domain novelty review, active contract, and formal paper-ready verification.
- **Long runs**: accept a long experiment only when its experiment package contains readable logs plus structured events, metrics, resource usage, environment, synchronization, and run-verification records.
- **Story**: define thesis, gap, contribution boundary, and claims to avoid before a full draft.
- **Literature**: position close work before writing Related Work.
- **Citation**: scholarly `verified` records require `citation_requests.json` and a fresh `citation_lock.json`; metadata verification and sentence-level support are separate checks.
- **Figures**: generated images may explain concepts but cannot create numeric evidence. For VideoQA and long-video papers, route motivation, method-flow, real-frame qualitative, and quantitative result figures through `videoqa-paper-figures`; it routes numeric charts to `originpro-paper-figures`. For other domains, use built-in image generation as the default concept asset and deterministic plots/tables for results.
- **Review**: resolve high-severity reviewer objections or record them as blockers.
- **Build**: compile the real package with `record_build.py --run` before submission-ready; preserve command, log, tool version, exit code, and hashes.
- **Completion**: do not say "done" until required artifacts and checks pass or explicit blockers are reported.

## Evidence Boundaries

- Treat negative, mixed, missing-seed, or incomplete results as scope constraints, not material to hide.
- Treat `implementation-not-confirmed`, `measurement-inconclusive`, and `mechanism-counterevidence` as different evidence states. Do not write “the idea failed” when only the implementation or measurement failed.
- A positive metric does not prove novelty. A weak adaptation or immature experiment does not prove non-novelty.
- Verify that each citation supports the attached sentence, not merely the topic.
- Save important papers locally only when access and redistribution permit; otherwise record stable metadata and access status.
- Generated diagrams communicate a workflow or idea; they are never experimental evidence.

## Finish

Report the concrete artifacts changed, checks run, and remaining scientific risks. Preserve the author's intent, but not unsupported wording.
