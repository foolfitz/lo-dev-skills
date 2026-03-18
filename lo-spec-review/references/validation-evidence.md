# Validation Evidence Guide

Review validation evidence in layers. Do not treat all tests as equally persuasive.

## Strong Evidence

- headless-safe unit tests for contract semantics
- static assertions for published type shape
- focused tests on virtual devices or simple peers that avoid flaky UI timing
- build outputs that prove generated headers and module wiring are correct

## Weaker But Still Useful Evidence

- interactive macro tests
- manual visual checks in an extension
- log-based confirmation of callback ordering or fallback selection

These are useful, but they should not be the only proof for a stable public contract when a smaller automated test is possible.

## Red Flags

- the only test waits for a repaint callback in headless `svp`
- the test passes because the object exists, not because the contract is correct
- compile success is presented as behavioral validation
- the spec promises more precision than the tests actually prove
- a sequence-returning geometry API is validated only on the first rectangle
- a no-layout or hidden-paragraph contract is tested only through a weaker proxy such as hidden text

## Review Questions

- What exact claim from the spec does each test close?
- Which contract points remain manual-only?
- Is there a smaller headless-safe seam, such as `VirtualDevice`, type assertions, or state round-trip tests, that should have been used?
- Does the evidence distinguish between "feature exists" and "feature is trustworthy enough for the next phase"?
