# Published UNO Contract Checklist

Use this when a spec introduces or changes a published UNO interface, method, struct, or callback.

## Scope And Ordering

- Is the supported scope explicit?
- If the API walks content, what ordering does it use?
- Are excluded areas named directly instead of implied from implementation?

## Out-Of-Scope Behavior

- Does the spec say whether callers get a sentinel, `FALSE`, empty sequence, or exception?
- Is the same behavior mirrored in the IDL comments?

## Identity Semantics

- If a result is a name, is it a UI name, UNO programmatic name, pool name, or resolved effective identity?
- Does it match the closest existing UNO property or service contract?

## Flag Semantics

- Does each flag reuse an existing Writer or UI behavior, or invent a new model?
- Is `Select=true` or similar wording concrete enough that reviewers can compare it to existing behavior?

## Geometry Semantics

- Are units and origin explicit?
- If multiple rectangles or fragments are returned, is their order part of the contract?
- Is empty-sequence behavior documented for hidden, filtered, or no-layout cases?

## IDL Visibility

- Could a Python or Basic caller infer the key behavior from the IDL comments alone?
- If not, the contract is still too hidden in spec prose or C++.

## Validation

- What is the smallest automated test that proves each frozen contract edge?
- Which parts still require extension-side or manual validation?
