# Research Quality Controls

These controls apply across idea, experiment, and writing skills.

## Direct-output preflight

Before writing a manuscript-facing or publication-facing artifact, classify a
possible concern as:

- `remove`: defensive boilerplate, repeated low-probability cases, duplicated
  checks, internal approval language, or process narration that does not
  change a scientific claim;
- `keep`: information required for scientific correctness, reproducibility,
  ethics, permissions, or venue compliance;
- `warn-only`: a material concern that needs researcher judgment. Report it
  outside the artifact and do not change files for that concern without
  approval.

Internal states such as approved, confirmed, gate-passed, or publication-ready
must not appear in manuscript prose. State the actual method, configuration,
data, and protocol instead.

## Hash necessity

Do not create a digest merely because two local artifacts are related. Prefer
stable IDs, positive revisions, project-relative paths, timestamps, and Git
commits for local workflow identity.

Use a cryptographic digest only when bytes cross an untrusted boundary, an
immutable content-addressed snapshot depends on it, a cache or deduplication
mechanism requires it, or an external system explicitly requires it. Examples
include remote downloads, uploaded archives, official template packages, and
immutable code snapshots.

Legacy digest fields may remain readable for compatibility. New local handoff,
alignment, verification, and writing artifacts must not require or generate
generic digests.

## Confirmation depth

Use partial confirmation by default.

Do not ask again for a read-only local risk scan, a user-named skill, a routine
handoff inside the current stage, or a predeclared task inside an approved
experiment round.

Ask before a new experiment round, a budget or time increase, a stage change
into formal experimentation, a material mechanism change, publication use of
results, external exposure of private text, creation of a reusable external
artifact when not already requested, or deletion of a local file.

## Artifact ownership

Read broadly and write narrowly.

| Artifact | Primary writer | Other skills |
| --- | --- | --- |
| idea pool, idea revisions, novelty and monitoring records | research-idea-lab | read or propose changes |
| validation alignment | research-idea-lab and researcher | experiment skill reads and validates |
| experiment plan, run records, logs, analysis, verification | research-experiment-lab | read or issue structured requests |
| claim-evidence matrix before formal experiments | research-idea-lab | experiment skill updates evidence status |
| manuscript, publication tables, paper claim-evidence matrix | ai-research-writing-skill | other skills supply evidence or requests |
| warnings requiring researcher judgment | owning skill and researcher | never silently inject into other artifacts |

Review and audit work proposes edits unless the user explicitly authorizes
direct changes to the owned artifact.
