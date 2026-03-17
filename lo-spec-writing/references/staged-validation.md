# Staged Validation Patterns

Use staged validation when a new core capability will be proven through an extension, a UI prototype, or a partial rollout.

## Good Stage Boundaries

Each stage should change one primary variable:

- Stage 1: validate a missing primitive or contract gap
- Stage 2: replace a larger UI or bridge path using the new primitive
- Stage 3: add usability features such as resizing or composition

Avoid stages that mix new API, new layout model, and new interaction model all at once.

## Per-Stage Checklist

- Hypothesis: what specific uncertainty is this stage resolving?
- Entry condition: what previous stage or prerequisite must already hold?
- Fallback: what path remains if the new API is missing or incomplete?
- Evidence: what build output, test, or extension behavior closes the question?
- Exit note: what residual mismatch remains, if any?

## Capability Probe Guidance

If the feature may exist only in patched builds:

- probe type availability explicitly
- probe runtime capability, not just type import
- cache probe results
- define the degraded path in the spec, not only in code comments

## Validation Evidence Mix

Prefer a layered plan:

- build-level proof that generated headers and modules compile
- headless-safe automated tests for stable contracts
- extension-side or manual validation for visual fidelity
- focused logging for residual mismatch instead of vague "looks better" claims

## When To Add Another Phase

Add a new phase when the current contract still leaves a real gap, for example:

- measurement does not match actual rendering inputs
- fallback behavior is still too lossy
- validation reveals a new contract boundary rather than a plain bug

Do not hide that gap inside the current phase summary. Name it and place it deliberately.
