# Writer Public Name Semantics

Use this when a Writer UNO API exposes a caller-visible name.

## Decide The Identity First

For any returned name, decide which of these is promised:

- localized UI name
- UNO programmatic name
- internal pool or collection name
- effective resolved style identity

If the contract does not say which one, reviewers and extension callers will guess, and that guess becomes compatibility burden.

## Practical Rules

- For paragraph style identity, compare against `ParaStyleName` before inventing a new meaning.
- If the public contract is about effective paragraph formatting, prefer `GetAnyFormatColl()` over `GetTextColl()`.
- If the result must be a UNO programmatic name, map it through `SwStyleNameMapper::FillProgName(..., SwGetPoolIdFromName::TxtColl)` or the matching family.
- Do not expose a localized UI name from a new public UNO API unless the UI-facing nature is deliberate and documented.

## Test Expectations

- Do not stop at `!isEmpty()`. Compare against the closest existing UNO property.
- For built-in styles, verify that localized UI naming does not leak into the public result.
