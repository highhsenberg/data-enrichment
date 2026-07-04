# Example run

```
$ python enrich.py --input contacts.csv

=== Jordan Blake (northwinddata.com) ===
  Email: jordan@northwinddata.com  [source: hunter.io]
  Verification: valid  [source: neverbounce]
  Tech stack: HubSpot, Clay  [source: builtwith]

=== Alex Kim (fieldworksai.com) ===
  Email: alex@fieldworksai.com  [source: prospeo]
  Verification: valid  [source: neverbounce]
  Tech stack: Smartlead, Clay  [source: builtwith]

=== Priya Shah (ledgerline.io) ===
  Email: priya@ledgerline.io  [source: prospeo]
  Verification: unknown  [source: neverbounce]
  Tech stack: Salesforce  [source: builtwith]

=== Taylor Reed (barrowfinch.com) ===
  Email: not found (hunter.io + prospeo waterfall exhausted)
  Tech stack: none detected  [source: builtwith]

Enriched 3/4 contacts with a verified email source.
```

## Why the waterfall matters

Alex Kim and Priya Shah both show why a single-source lookup isn't enough:
Hunter.io has no record for either of them, but Prospeo does. A pipeline
that only tried Hunter.io would have marked both as "not found" and lost
two verifiable, working emails. Taylor Reed shows the honest failure case
-- when every source in the waterfall comes up empty, the record says so
explicitly instead of guessing.

Every field is tagged with the source that filled it (`hunter.io`,
`prospeo`, `neverbounce`, `builtwith`), so a rep -- or a downstream
scoring system -- can see exactly how confident to be in each piece of
data, rather than treating an enriched record as one opaque blob of truth.
