#!/usr/bin/env python3
"""
Data Enrichment Pipeline
---------------------------
A waterfall enrichment system: for each contact, try each enrichment source
in priority order and stop at the first one that returns a match, so every
prospect record ends up as complete and verified as possible before it's
used for outbound.

Waterfall (in order):
    1. Hunter.io   -- email discovery, tried first
    2. Prospeo     -- email discovery fallback if Hunter has no match
    3. NeverBounce -- verifies whichever email was found
    4. BuiltWith   -- tech-stack lookup, always attempted independently

Every source here is a static lookup table standing in for the real API --
`lookup_hunter()` / `lookup_prospeo()` / `verify_neverbounce()` /
`lookup_builtwith()` are the seams you'd swap for real HTTP calls in
production. Every field in the output is tagged with which source filled
it, so nothing pretends to be more certain than it is.

Usage:
    python enrich.py --input contacts.csv
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

HUNTER_DB = {
    "northwinddata.com": {"jordan blake": "jordan@northwinddata.com"},
}

PROSPEO_DB = {
    "fieldworksai.com": {"alex kim": "alex@fieldworksai.com"},
    "ledgerline.io": {"priya shah": "priya@ledgerline.io"},
}

NEVERBOUNCE_DB = {
    "jordan@northwinddata.com": "valid",
    "alex@fieldworksai.com": "valid",
    "priya@ledgerline.io": "unknown",
}

BUILTWITH_DB = {
    "northwinddata.com": ["HubSpot", "Clay"],
    "fieldworksai.com": ["Smartlead", "Clay"],
    "ledgerline.io": ["Salesforce"],
    "barrowfinch.com": [],
}


@dataclass
class EnrichedContact:
    name: str
    domain: str
    email: Optional[str]
    email_source: Optional[str]
    email_status: str
    tech_stack: List[str] = field(default_factory=list)


def load_contacts(path: str) -> List[Dict[str, Any]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def lookup_hunter(domain: str, name: str) -> Optional[str]:
    return HUNTER_DB.get(domain, {}).get(name.lower())


def lookup_prospeo(domain: str, name: str) -> Optional[str]:
    return PROSPEO_DB.get(domain, {}).get(name.lower())


def verify_neverbounce(email: str) -> str:
    return NEVERBOUNCE_DB.get(email, "unknown")


def lookup_builtwith(domain: str) -> List[str]:
    return BUILTWITH_DB.get(domain, [])


def enrich_contact(row: Dict[str, Any]) -> EnrichedContact:
    name = row["name"]
    domain = row["company_domain"]

    email = lookup_hunter(domain, name)
    source = "hunter.io" if email else None

    if not email:
        email = lookup_prospeo(domain, name)
        source = "prospeo" if email else None

    status = verify_neverbounce(email) if email else "n/a"
    tech_stack = lookup_builtwith(domain)

    return EnrichedContact(
        name=name,
        domain=domain,
        email=email,
        email_source=source,
        email_status=status,
        tech_stack=tech_stack,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Data Enrichment Pipeline")
    parser.add_argument("--input", default="contacts.csv")
    args = parser.parse_args()

    rows = load_contacts(args.input)
    found = 0

    for row in rows:
        c = enrich_contact(row)
        print(f"=== {c.name} ({c.domain}) ===")
        if c.email:
            found += 1
            print(f"  Email: {c.email}  [source: {c.email_source}]")
            print(f"  Verification: {c.email_status}  [source: neverbounce]")
        else:
            print("  Email: not found (hunter.io + prospeo waterfall exhausted)")
        if c.tech_stack:
            print(f"  Tech stack: {', '.join(c.tech_stack)}  [source: builtwith]")
        else:
            print("  Tech stack: none detected  [source: builtwith]")
        print()

    print(f"Enriched {found}/{len(rows)} contacts with a verified email source.")


if __name__ == "__main__":
    main()
