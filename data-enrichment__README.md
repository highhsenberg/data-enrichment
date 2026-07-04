# Data Enrichment Pipeline

A waterfall enrichment system: for each contact, try each enrichment source
in priority order and stop at the first one that returns a match, so every
prospect record ends up as complete and verified as possible before it's
used for outbound.

See [`example_output.md`](./example_output.md) for a full run, including a
worked example of why a single-source lookup isn't enough.

## Waterfall (in order)

1. **Hunter.io** -- email discovery, tried first.
2. **Prospeo** -- email discovery fallback if Hunter has no match.
3. **NeverBounce** -- verifies whichever email was found.
4. **BuiltWith** -- tech-stack lookup, always attempted independently.

Every source is a static lookup table standing in for the real API --
`lookup_hunter()` / `lookup_prospeo()` / `verify_neverbounce()` /
`lookup_builtwith()` are the seams you'd swap for real HTTP calls in
production. Every field in the output is tagged with the source that
filled it, so nothing pretends to be more certain than it is -- including
an explicit "not found" when the whole waterfall comes up empty.

## Install

No external dependencies beyond the Python standard library.

## Usage

```bash
python enrich.py --input contacts.csv
```

## Project structure

```
enrich.py         -- waterfall enrichment + verification + tech-stack lookup
contacts.csv       -- 4 example contacts covering hunter/prospeo/not-found cases
example_output.md  -- full example run with reasoning
```

## Limitations / next steps

- Lookup tables here stand in for real API calls; swapping in real
  Hunter.io / Prospeo / NeverBounce / BuiltWith clients is a drop-in change
  at each `lookup_*` / `verify_*` function.
- No retry/backoff or rate-limit handling yet -- necessary once these
  become real HTTP calls.
- Only email + tech stack are enriched today; phone number and company
  firmographic waterfalls would follow the same pattern.
