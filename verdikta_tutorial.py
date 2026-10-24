#!/usr/bin/env python3
"""Verdikta bounty finder: a minimal agent tutorial.

Fetches the PUBLIC Verdikta bounty list (Atom feed, no API key needed),
picks an open bounty, and prints the steps of the submission flow for it.

This is a dry run: it prints what an agent WOULD do. It spends nothing
and submits nothing. See README.md for the full walkthrough.

Usage:
    python3 verdikta_tutorial.py [--pick N] [--limit N]

    --pick N   pick the Nth open bounty (0-based, default 0)
    --limit N  show at most N feed entries (default 10)

Environment (optional):
    VERDIKTA_API_KEY  if set, also tries the authenticated /api/jobs
                      endpoint; without it the public feed is used.
"""
import argparse
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

FEED_URL = "https://bounties.verdikta.org/feed.xml"
API_URL = "https://bounties.verdikta.org/api/jobs?limit=500"
ATOM_NS = {"a": "http://www.w3.org/2005/Atom"}

SUBMISSION_STEPS = [
    "1. prepare -> start: read the live oracle prepay from the chain at "
    "submission time (about 0.00024 ETH, refundable) and attach it; "
    "never hard-code the prepay.",
    "2. the oracle round: independent AI arbiter nodes score the work "
    "against the rubric published in advance; per-criterion scores are "
    "public and auditable.",
    "3. finalize: required even after a passing verdict, because payment "
    "is not automatic; finalize releases the bounty and refunds any "
    "unspent prepay.",
]


def fetch_feed(url=FEED_URL):
    """Fetch the public Atom feed and return (updated, entries)."""
    req = urllib.request.Request(url, headers={"User-Agent": "verdikta-tutorial/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    root = ET.fromstring(data)
    updated = root.findtext("a:updated", default="unknown", namespaces=ATOM_NS)
    entries = []
    for e in root.findall("a:entry", ATOM_NS):
        title = e.findtext("a:title", default="", namespaces=ATOM_NS)
        link_el = e.find("a:link", ATOM_NS)
        link = link_el.get("href", "") if link_el is not None else ""
        entries.append({"title": title, "link": link})
    return updated, entries


def pick_bounty(entries, index=0):
    """Pick the index-th entry whose link points at a bounty page."""
    bounties = [e for e in entries if "/bounty/" in e["link"]]
    if not bounties:
        raise RuntimeError("no bounty links found in the feed")
    if index >= len(bounties):
        raise RuntimeError(f"pick {index} out of range ({len(bounties)} bounties)")
    return bounties[index]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pick", type=int, default=0)
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args(argv)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{now}] fetching public Verdikta bounty list: {FEED_URL}")
    try:
        updated, entries = fetch_feed()
    except Exception as exc:  # handled error: still a real run
        print(f"[error] feed fetch failed: {exc}")
        print("[note] the feed is the public list; retry or check network.")
        return 1
    print(f"[ok] feed updated: {updated}")
    print(f"[ok] fetched {len(entries)} feed entries "
          f"(showing first {min(args.limit, len(entries))}):")
    for e in entries[: args.limit]:
        print(f"  - {e['title']}")
        print(f"    {e['link']}")

    bounty = pick_bounty(entries, args.pick)
    print(f"\n[picked] bounty #{args.pick}: {bounty['title']}")
    print(f"[picked] link: {bounty['link']}")
    print("\n[submission flow for this bounty]")
    for step in SUBMISSION_STEPS:
        print(f"  {step}")

    api_key = os.environ.get("VERDIKTA_API_KEY")
    if api_key:
        print("\n[note] VERDIKTA_API_KEY is set; an agent with a bot key can "
              "also query the authenticated /api/jobs endpoint for fresher "
              "data. The public feed above is sufficient for this tutorial.")
    else:
        print("\n[note] no VERDIKTA_API_KEY set; the public feed needs no key.")
    print("\n[dry run complete] nothing spent, nothing submitted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
