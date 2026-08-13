# Motivation-led Solution Design

Use this reference only after the user supplies a concrete problem or selects a
problem card. Generate multiple solution routes from the selected motivation rather
than attaching familiar modules to the baseline.

## Derivation chain

Build every serious solution through this chain:

```text
verified failure
  -> bottleneck hypothesis
  -> distinctive motivation insight
  -> required behavior change
  -> mechanism principle
  -> module or system operation
  -> implementation location
  -> measurable prediction
  -> mechanism, quantitative, and qualitative evidence
```

Every arrow needs a short justification. If an arrow is missing, keep the solution
as a seed and name the missing link.

## One problem, multiple routes

Generate 3–5 materially different routes for one selected problem when possible.
Include mechanism invention, baseline modification, mechanism combination,
cross-domain transfer, simplification, or diagnostic/evaluation contributions as
appropriate. Do not force every problem into a new-module paper.

Compare routes by:

- directness against the bottleneck;
- dependence on disputed assumptions;
- mechanism identifiability;
- simplest credible implementation;
- expected information gain of the first test;
- value if the main aggregate metric does not improve;
- likely qualitative behavior change;
- resource and integration risk.

## Module derivation

For every proposed module or baseline change, record:

- `motivation_requirement`: the behavior the bottleneck says must change;
- `design_principle`: the abstract operation needed to create that change;
- `module_operation`: what information or control flow the module changes;
- `location`: the exact pipeline boundary;
- `why_existing_components_are_insufficient`;
- `minimal_form`: the simplest implementation that preserves the mechanism;
- `strongest_alternative`: capacity, extra data, retrieval, prompting, optimization,
  or another simple explanation;
- `isolating_control`: removal, replacement, shuffle, oracle, or matched-budget
  comparison;
- `predicted_quantitative_change`;
- `predicted_qualitative_change`;
- `failure_signature`: what would contradict the design rationale.

Do not accept “add module X” as a derivation. Reusing a known module is allowed when
the problem interpretation, adaptation, complete mechanism, or evidence contribution
is meaningful and target-domain novelty remains unoccupied.

## Evidence triad

Before validation, predeclare three evidence families:

1. `mechanism`: activation and intervention evidence showing that the intended
   module is implemented, used, and responsible for the targeted behavior;
2. `quantitative`: aggregate and targeted metrics under fair, matched comparisons,
   with uncertainty appropriate to the claim;
3. `qualitative`: predeclared failure-case categories or representative examples
   selected by a non-cherry-picking protocol, showing how behavior changes and where
   it still fails.

Qualitative evidence cannot be a gallery of hand-picked successes. Quantitative gain
without mechanism evidence supports a system result but not the claimed causal
explanation. Mechanism evidence without task improvement supports diagnosis but not
an effectiveness claim.

## Output

Return the selected problem and motivation first, then the alternative solution
routes. For the recommended route, show the complete derivation chain, exact baseline
change, evidence triad, current unknowns, and cheapest discriminating validation.
