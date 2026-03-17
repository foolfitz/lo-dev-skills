---
name: lo-spec-writing
description: Write LibreOffice specs before implementation. Use for spec drafts, phase plans, staged validation, UNO or VCL contract design, fallback paths, capability probes, and compatibility boundaries.
---

# LibreOffice Spec Writing Guide

Use this skill when the main risk is not syntax, but an incomplete or ambiguous contract.

Typical trigger cues:

- "write a spec" or "draft a phase plan"
- "define the UNO contract before coding"
- "figure out fallback or capability detection"
- "design staged validation for an extension-backed rollout"
- "separate goals, non-goals, and deferred work"

This skill is especially useful for:

- new or changed published UNO APIs
- UNO-to-VCL bridge work
- staged extension validation plans
- fallback and capability-probe design
- multi-phase work where follow-up commits would be expensive

## Workflow

1. Start from the user-visible problem, current workaround, and non-goals. Be explicit about what the spec is not solving yet.
2. Identify the closest LibreOffice precedent and explain why it is insufficient. Reuse established patterns whenever possible.
3. Write the public contract before the implementation sketch. For UNO or VCL-facing work, define types, units, flags, lifetime, threading, listener behavior, invalid input, and compatibility expectations.
4. Separate desired contract from current repository state. If code already exists, label status clearly so the spec does not blur design and implementation.
5. Design validation in stages. Each stage should have a narrow hypothesis, a rollback path, and clear evidence that decides whether the next stage is justified.
6. End with acceptance evidence, risks, and deferred work. If a known gap is being postponed, say where it belongs instead of leaving it implicit.

## Output Expectations

Aim for a spec that lets an implementer and a reviewer answer the same questions:

- What exact problem is being solved now?
- What public behavior becomes promised to callers?
- What compatibility burden does that create?
- What evidence will prove the contract is correct?
- What remains out of scope?

## Load These References As Needed

- For a starting structure: [references/spec-template.md](./references/spec-template.md)
- For contract precision questions: [references/contract-questions.md](./references/contract-questions.md)
- For staged rollout, fallback, and extension validation: [references/staged-validation.md](./references/staged-validation.md)

## Scope Boundary

This skill is about design and validation planning. Once the contract is decided and the task becomes implementation mechanics, switch to `lo-uno-api`. Before landing public API changes, run a `lo-spec-review` pass.
