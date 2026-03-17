---
name: lo-spec-review
description: Review LibreOffice patches against specs. Use for spec-driven review, published UNO API review, UNO-to-VCL bridge checks, lifecycle and compatibility risks, and missing validation evidence.
---

# LibreOffice Spec-Driven Review Guide

Use this skill when the right review question is "does this patch faithfully implement the intended contract?" rather than "does the code look clean?"

Typical trigger cues:

- "review this patch against the spec"
- "do a spec-driven code review"
- "check the published UNO contract"
- "look for lifecycle, listener, or compatibility regressions"
- "tell me what tests are still missing"

This skill is especially useful for:

- published UNO API reviews
- toolkit or VCL bridge work
- staged feature branches with explicit specs
- follow-up commits that may reveal missed contract gaps

## Review Order

1. Read the spec first and extract concrete claims: promised behavior, non-goals, compatibility burden, and validation expectations.
2. Review the public contract next: IDL, comments, struct field types, flags, service names, and callback signatures.
3. Review the bridge and lifecycle path after that: state persistence, disposal, listener symmetry, base behavior preservation, window replacement, and threading.
4. Review tests and validation evidence last. Prefer tests that prove contract semantics, not just smoke that the code compiles.

## What To Prioritize

Look for:

- contract mismatches between spec, IDL, and implementation
- public type choices that will be painful to fix later
- state that is documented like a property but implemented like a one-shot effect
- broken inherited toolkit behavior such as listener paths
- lifecycle, `dispose()`, or `SolarMutexGuard` mistakes
- validation gaps, especially when only visual or manual evidence exists

Ignore pure style nits unless they hide one of the risks above.

## Output Format

Findings first. For each finding, include:

- severity
- file and contract area
- what behavior or guarantee is violated
- why it matters to callers, compatibility, or maintenance
- the minimal fix or missing test that would close it

If the spec is missing or ambiguous, say so and review against the strongest observable intent you can justify.

## Load These References As Needed

- For a concrete review checklist: [references/published-api-review-checklist.md](./references/published-api-review-checklist.md)
- For judging tests and manual evidence: [references/validation-evidence.md](./references/validation-evidence.md)

## Scope Boundary

This skill is about review strategy and issue finding. If the task becomes implementation work, switch to `lo-uno-api` or the relevant code-level skill after the review pass.
