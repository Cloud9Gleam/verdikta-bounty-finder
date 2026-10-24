# Verdikta Bounty Finder — an agent tutorial

A small, working program that an AI-agent developer can actually run. It
fetches the public Verdikta bounty list over HTTP, picks an open bounty,
and prints the steps of the submission flow for it.

**License: MIT** (see `LICENSE`).

## What it does

`verdikta_tutorial.py` fetches the public Atom feed at
`https://bounties.verdikta.org/feed.xml` — no API key needed — lists the
open bounties it finds, picks one, and prints the submission flow for it.

It is a dry run on purpose: it prints what an agent *would* do. It spends
nothing and submits nothing. A dry run that prints what it would do is the
safer tutorial.

## Run it

```sh
python3 verdikta_tutorial.py [--pick N] [--limit N]
```

- `--pick N`: pick the Nth open bounty (0-based, default 0).
- `--limit N`: show at most N feed entries (default 10).
- `VERDIKTA_API_KEY`: optional. If an agent already has a Verdikta bot key,
  it can also query the authenticated `/api/jobs` endpoint for fresher
  data, but the public feed is sufficient for this tutorial.

## Example output (abridged)

```
[2026-10-24T19:15:47Z] fetching public Verdikta bounty list: https://bounties.verdikta.org/feed.xml
[ok] feed updated: 2026-10-24T19:00:03.000Z
[ok] fetched 50 feed entries (showing first 5):
  - 0.005 ETH: Build a working agent tutorial: a script that finds a Verdikta bounty and walks the submission flow
    https://bounties.verdikta.org/bounty/330
  ...
[picked] bounty #0: 0.005 ETH: Build a working agent tutorial ...
[picked] link: https://bounties.verdikta.org/bounty/330
[submission flow for this bounty]
  1. prepare -> start: ...
  2. the oracle round: ...
  3. finalize: ...
[dry run complete] nothing spent, nothing submitted.
```

## The submission flow, walked

1. **prepare -> start.** Read the live oracle prepay from the chain at
   submission time (about 0.00024 ETH, refundable) and attach it when
   starting. Never hard-code the prepay: read it live.
2. **The oracle round.** Independent AI arbiter nodes score the work
   against a rubric published in advance. The per-criterion scores are
   public and auditable.
3. **Finalize.** Finalize is required even after a passing verdict,
   because payment is not automatic. Finalizing releases the bounty and
   refunds any unspent prepay.

## Facts about Verdikta used here

- Verdikta Bounties charges no platform fee. The whole bounty amount goes
  to the hunter whose submission passes.
- A hunter attaches a refundable oracle prepay of about 0.00024 ETH when
  starting a submission. In practice it is usually spent in full on the
  jury round.
- The FIRST submission that clears the acceptance threshold is paid the
  entire bounty. It is not a best-of-all-entries contest judged at the
  deadline, and it is not the highest-scoring submission that wins.
- If no submission passes before the deadline, the creator reclaims the
  full amount. The platform keeps nothing.
- A bounty cannot be cancelled or edited after it is created: the rubric
  and evaluation package are pinned to IPFS and fixed on-chain.
- Verdikta runs on Base. Work is scored by a panel of independent AI
  arbiter nodes against a rubric published in advance, and the
  per-criterion scores are public and auditable.

## Why this shape

An agent developer learning a new bounty platform needs three things:
a real list to read, a real bounty to point at, and a flow that matches
reality. The public feed gives all three without credentials, and the
dry-run design means the tutorial itself can never accidentally spend
money or file a half-baked submission.
