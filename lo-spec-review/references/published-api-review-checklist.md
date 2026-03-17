# Published API Review Checklist

Use this checklist when reviewing new or changed UNO APIs, toolkit peers, listener contracts, or bridge classes.

## 1. Contract Surface

- Do the IDL signatures match the capability described by the spec?
- Are docs precise about units, axes, coordinate system, and valid flag combinations?
- Are field types correct for range and signedness?
- Is there any promise that became visible to extensions without being deliberately designed?

## 2. Bridge And Lifecycle

- Is `SolarMutexGuard` used where VCL access requires it?
- Does the implementation preserve inherited toolkit behavior such as paint notifications?
- Does state survive resize, orientation changes, window replacement, or peer rebinding when the contract implies persistence?
- Are listeners disposed and callback sources kept alive correctly?
- Is there any callback path that can outlive the underlying VCL object?

## 3. Compatibility Risk

- Would changing this later break Python, Java, Basic, or extension callers?
- Is a new interface revision needed, or is a direct change still acceptable because the API is not yet hardened?
- Are docs and implementation aligned closely enough that external callers will not learn the wrong behavior?

## 4. Validation Evidence

- Is there at least one automated test for the core contract?
- Does the test assert semantics rather than only getter or setter round-trips?
- If UI repaint or plugin-specific behavior is involved, is the test stable in headless `svp`, or clearly separated from headless-safe checks?

## Common Failure Patterns

- Property documented as durable, implemented as one-shot side effect
- Bridge exposes richer runtime object than the published type admits
- New feature bypasses base event path and silently regresses old listeners
- Doc wording reverses axis or orientation relative to VCL behavior
- Metric struct uses the wrong signedness and can report nonsense values
- First API closes only part of the contract, forcing a quick follow-up method to make layout code trustworthy
