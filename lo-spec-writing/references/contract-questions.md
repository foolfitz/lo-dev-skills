# Contract Questions For Published API Work

Use these questions when the spec touches public UNO APIs, toolkit peers, listeners, or bridge objects.

## Types And Signatures

- Does the signature expose the capability callers are actually expected to use?
- Is each numeric type wide enough and signedness-correct?
- Should the result be a struct, an interface, or an existing UNO type?

## Semantics

- Is this API describing persistent state, a one-shot action, or an event callback?
- Are coordinates in window space, content space, document space, or device space?
- Are flag meanings fixed, documented, and stable enough for extensions to rely on?

## Lifetime And Ownership

- Can the returned object be stored, or is it valid only during a callback?
- What happens after `dispose()` or window replacement?
- Are listeners added and removed symmetrically?

## Threading And Reentrancy

- Does the implementation require `SolarMutexGuard`?
- Will any code call back into UNO while VCL state is held?
- Is reentrancy acceptable, ignored, or forbidden?

## Compatibility

- If this lands in a stable branch, what becomes hard to change later?
- Does the new behavior preserve inherited toolkit contracts such as paint listeners, event forwarding, or base window behavior?
- Are docs and implementation using the same axis, direction, and range wording?

## Validation

- What is the smallest headless-safe test that proves the contract?
- What still requires interactive validation?
- If measurement and drawing are separate APIs, is the contract closed tightly enough that layout code can rely on them being consistent?

## Recent Red Flags

- A property-looking API that is actually a one-shot side effect
- A callback typed too weakly for the intended contract
- Signed and unsigned count mismatches in published structs
- A custom path that accidentally suppresses an inherited listener path
- A measurement API that does not mirror the inputs of the drawing API it is meant to support
