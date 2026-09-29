# Food-route valuation

28 September 2026. Based on frozen `variants/v15`, not the concurrently edited
live `bot/`. The previous symmetry prototype remains intact in
`archive/symmetry-v13-20260928/` and is not enabled in this candidate.

## Problem and change

The original `bfsFrom` sums discounted food over every reachable tile. At a
fork, pearls in both branches count towards the score even though a dragon
can only take one branch. The spatial sum also amplifies a large region of
small speculative food values on an unknown map. It is a useful measure of
regional food density, but does not represent food collected along a route.

The prototype adds a reverse pass through the BFS order. For a tile u:

```
route[u] = pearlValue(u, distance[u])
           + gamma * max(route[v] for neighbours one BFS level farther away)
score = 0.15 * original_region_score + 2.0 * gamma * route[start]
```

Distances strictly increase, so a route never counts a tile twice and only
one continuation at a fork is selected. The original pearl model still
accounts for visible pearls, remembered pearls, spawn timers, and competing
heads. Collision filtering, body-release times, survival search, threat
penalties, splitting, feeding, and map modules are unchanged. The BFS distance
array remains available to feeding logic exactly as before.

`PEARL_ROUTE` defaults to **0**. Enable with `-DPEARL_ROUTE=1`.
`PEARL_ROUTE_SCALE=2.0` and `PEARL_ROUTE_REGION=0.15` were the first values
tested; no parameter sweep or map-specific exceptions have been used.

Limitations: this is an outward shortest-path estimate, not full multi-turn
body simulation. It cannot plan a food tour that returns towards its start.
Growth can delay a tail relative to the BFS's release-time model; the existing
survival search remains responsible for checking the immediate choice. A
small region term retains an incentive to explore when no reliable food is
known.

## Evidence and protocol

The user also asked about the submissions page. A public GET to
https://game.battlecode.au/submissions redirected to sign-in. Browser discovery
found no connected browser, so account submissions could not be inspected.
No API key or browser credentials were accessed. The v15 baseline comes from
the repository snapshot and main journal, not a verified account listing.

Latest main-agent research considered and rejected pearl sprints and reported
an overnight food-harvest deficit; its later 30-game peer sample had similar
harvest to opponents. Therefore that deficit alone is not evidence for this
change. The primary rationale here is the planner's branch-counting model,
tested directly below and then through independent matches.

Correctness test: `tests/pearl_route_test.cpp` verifies mutually exclusive
branches, food collected in sequence, loops, body blocking, and future spawn
timing. It runs the actual Bot BFS and route implementation.

| Stage | Maps | Opponent | Seeds | Score | Wilson 95% |
|---|---|---|---|---:|---:|
| Screening | 40 gen | v15 | 53000 | 55.5/80 (69.4%) | 58.6–78.4% |
| Ranked screen | 10 ranked | v15 | 53000–53001 | 26/40 (65.0%) | 49.5–77.9% |

Both screens had zero harness errors. Ranked results are not yet a proven
gain; Devil was 0/4 and Slithery/Trauma 1/4 each. No per-map changes were made
in response. Settings and strategy hashes were frozen before the independent
50000 and 51000 confirmations against v15 and v13 separately. Do not pool
near-identical opponents to manufacture a narrow interval.

Final holdout plan: if both independent development sets confirm, evaluate
the unchanged candidate once on all 40 `genhold` maps against v15, seed 54000,
both sides. This set has not been inspected or used to choose parameters.
Also run the ranked maps with both bots using `NO_KNOWN_MAPS=1` to check the
generic algorithm separately from the ranked-map modules.

All tests use `tools/pool.py` in this sandbox, one batch at a time, max six
workers. It wraps the existing evaluator and makes our batch visible to the
main agent's documented pool.py process check. Raw match logs retain errors;
builds, caches, and temporary archives stay inside this folder.

Confirmation, holdout, and CPU results will be appended when complete.

## Porting

Add `pearl_route.hpp`, the three default knobs in `params.hpp`, the include
beside `bfsDist/bfsQ`, and the two-line gated score adjustment at the end of
`bfsFrom`. It neither rebuilds map adjacency nor changes portal learning, so
it is independent of the main agent's map-memory work.

Real-opponent confirmation remains necessary before making a ladder claim:
after team review, compare frozen baseline and candidate against the same
varied peer set on balanced sides. Report win rate, r100/r200 unit counts,
spawn harvest, and final longest length, distinguishing known-map modules
from generic/unknown-map mode. This research performs no server submissions
or challenges.
