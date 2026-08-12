# Literature Monitoring

Use `monitor` for dated incremental scans after an idea has a stable ID. This
is competitor maintenance, not a universal novelty proof and not an automatic
rejection gate.

Reuse the idea's declared target-domain boundary and saved query families.
Search from the previous coverage end through today with a short overlap
window. Inspect credible target-domain sources regardless of venue and use
public-safe queries when the idea is unpublished.

Classify each finding across problem, mechanism, evidence, benchmark, claim,
and positioning overlap. Emit one action:

- `RELAX`: no material new overlap in the scanned window;
- `RESEARCH`: partial or uncertain overlap needs full-text retrieval;
- `FOLLOW-UP`: verified material overlap requires focused novelty review,
  differentiation, or claim revision.

Monitoring may update recall confidence, request deeper search, revise a claim,
or create a rescue task. It may not itself set novelty to `occupied`, reject an
idea, or alter the mechanism. Store reports under
`ideas/<idea-id>/literature_monitor/` using
`research-idea/literature-monitor-v1`.
