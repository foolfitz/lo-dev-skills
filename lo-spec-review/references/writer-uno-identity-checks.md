# Writer UNO Identity Checks

Use this when a new or changed Writer UNO API returns names, styles, or other caller-visible identities.

## First Questions

- Is the API returning the direct style, or the effective resolved style?
- Is the name a localized UI name or a stable UNO programmatic name?
- What existing UNO property should a caller expect this to match?

## Common Writer Cases

- Paragraph style names should usually be compared against `ParaStyleName`, which is a UNO programmatic name.
- Direct collection access such as `GetTextColl()` can be the wrong identity when the public contract is about effective formatting.
- If built-in style names are exposed publicly, check whether `SwStyleNameMapper::FillProgName(...)` is required.

## Review Smells

- Tests only assert the returned string is non-empty.
- IDL says "style name" but never says which identity is promised.
- Implementation uses a UI or internal name even though existing UNO properties use programmatic names.
- Spec relies on reviewer inference instead of naming the identity directly.

## Minimal Review Action

If the intended identity is not explicit, file a finding against both the implementation and the IDL comments. For published UNO, hidden name semantics are compatibility risk, not a wording nit.
