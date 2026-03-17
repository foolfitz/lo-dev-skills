# Spec Template

Use this as a starting structure, then trim sections that do not add value.

## 1. Goal

- What user or extension problem are we solving?
- Why is the current behavior insufficient?
- What is the smallest useful outcome for this phase?

## 2. Background And Precedent

- Current workaround or failure mode
- Closest LibreOffice precedent
- Why the precedent is not enough as-is

## 3. Non-Goals

- Name nearby problems that are intentionally deferred
- Say which later phase or follow-up would own them

## 4. Public Contract

If the spec introduces or changes a public UNO or VCL-facing contract, define:

- Types and signatures
- Units and coordinate system
- Flag values and valid combinations
- State semantics: persistent property, one-shot effect, or callback-only
- Lifetime and ownership
- Listener and event ordering expectations
- Threading assumptions, especially SolarMutex-sensitive code
- Invalid input or boundary behavior
- Compatibility and versioning impact

## 5. Implementation Shape

- Files or modules likely to change
- Reused patterns from existing code
- Internal bridge points or helper objects
- Any implementation constraint that affects the public contract

## 6. Validation Plan

- Compile or build targets
- Headless-safe tests
- Interactive or extension-side validation
- Logging or diagnostics needed to explain residual mismatch
- Capability probe and fallback behavior if the feature may be absent

## 7. Acceptance Criteria

- Specific behaviors that must hold
- Evidence required for each behavior
- What counts as a successful stage completion

## 8. Risks And Deferred Work

- Known contract risk
- What is being accepted for now
- What future phase would address the remaining gap
