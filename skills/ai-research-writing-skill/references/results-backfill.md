# Verified Results Backfill

Load this reference when planned experiments have produced result files and the paper must transition from conditional placeholders to evidence-bounded factual claims.

## Result discovery

Store machine-readable results under `paper/results/`. Prefer:

- `main_results[_<dataset>].csv`
- `ablation_<component>.csv`
- `robustness_<dataset>.csv`
- `efficiency_<dataset>.csv`
- `<experiment-id>.csv`

Use `templates/result-file-template.csv`. Each observation records method, dataset, metric name, numeric value, seed, timestamp, and notes. Preserve raw logs and aggregation scripts beside or upstream of the summarized result.

Run discovery without mutation first:

```bash
python3 scripts/discover_results.py --project-dir <project> --json
```

File matching is not verification. Before setting `result_status=verified`, confirm schema, expected conditions, seed count, metric implementation, dataset split, protocol equality, log readability, aggregation reproducibility, and consistency with the numeric-evidence selectors.

## State transition

For each accepted experiment:

1. Change its experiment-matrix status from `planned` or `placeholder` to `verified`.
2. Update numeric-evidence records and the claim-evidence map with exact source files and selectors.
3. Replace only placeholders supported by that experiment.
4. Promote introduction or contribution claims only when all evidence required by the claim is verified.
5. Record negative, mixed, or null results and narrow the claim instead of hiding them.

Never infer verification from a filename, non-empty CSV, or successful training exit alone.

## Paper updates

Replace `(hypothesis)`, `[Results pending]`, or provisional figure/table slots with bounded statements and concrete assets. Preserve the distinction between rerun values and paper-reported baseline values.

Generate tables with:

```bash
python3 scripts/generate_results_table.py <results.csv> -o <output.tex> --bold-best
```

Check the metric direction before emphasizing the best value. Generate result plots deterministically from versioned data and scripts. Do not use image generation for axes, values, uncertainty, tables, or benchmark claims.

Write Results before finalizing the Abstract and Conclusion. The final abstract contains only verified outcomes and includes a representative number when the evidence supports one. Keep the abstract within the venue limit rather than assuming a universal word count.

## Backfill QA

- Every promoted number traces to raw results, a readable run log, and a recomputable aggregation.
- Seed counts and uncertainty match the experiment matrix.
- All factual superlatives use the intended comparison set.
- No verified claim still carries hypothesis language.
- No unresolved placeholder is silently removed.
- Figures and tables are defined, referenced, and consistent with the prose.
- Citation keys resolve and sentence-level support remains valid.
- The real LaTeX package compiles; numeric, TODO, citation, venue, and build checks pass.

After substantive backfill, run a targeted skeptical review. If evidence changes the paper story, revise the affected story and framing artifacts before updating the Introduction and Abstract.
