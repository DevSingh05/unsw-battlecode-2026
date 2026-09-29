# Lever: frontier-explore (`EXPLORE_LEARN`)

Patch: `notes/levers/frontier-explore.diff` (against `bot/main.cpp` and `bot/params.hpp`).
Patched copy: `notes/levers/frontier-explore/src/`. Default is off (`EXPLORE_LEARN 0`), and the flag only acts when `!w.known`, so ladder play is unchanged.
Tools: `notes/levers/frontier-explore/firstsight.py` and `metrics.py`. Run both from the project root.

## What it does

On an unknown map, v28 values a never-seen tile at `0.5 * min(1, arrive * UNK_PRIOR)`, which is `0.001 * round / 2`. That value grows with the round whatever the map is like. `EXPLORE_LEARN=1` replaces it with an estimate the dragon learns from its own vision:

- **Sampling.** Every tile that enters this dragon's 7x7 view for the first time (`lastSeen[t] < 0`) counts as one sample of the never-seen population. The sample is a hit if a pearl is there, or if the countdown is `<= EXPLORE_CD` (3). We arrive about 3 steps after first seeing a tile, so a pearl due that soon is food for us.
- **Estimate.** `est = (hits + N0*M0) / (n + N0)`: a Beta-smoothed hit rate with M0=0.03 and N0=30. Both counts decay by 0.98 per turn, a window of about 350 samples. The result is capped at 0.5 and scaled by `EXPLORE_MULT` (1.0).
- **Where it applies.** `pearlValue()` uses `est` for tiles never seen (`ls<0`), with no spawn timer (`spawnAt<0`) and no known gap (`gmax<0`). The value is flat in time. The existing `otherDist` discounts still apply: 0.25 if another head is closer, 0.55 on a tie.
- **Birth view skipped.** A process's first view is not sampled (`round > birthRound`). A split child is born in its parent's picked-over neighbourhood, and those 49 tiles would bias the estimate low.

Everything else is unchanged: seen tiles, spawn timers, `gapSeen`, the UNK_EXPLORE lure, and portals. The patch adds about 30 lines. The only other change is a debug line (`explore est=… n=…`), written only under `BOTDBG`.

## Why: v28's unseen prior is miscalibrated, and differently on every map

`firstsight.py` replays each dragon's own vision: children start with empty memory, and the birth view is excluded. For each first sighting it records whether a pearl was there. That is the empirical P(pearl | this dragon has never seen the tile), which is exactly the quantity the prior is meant to stand for.

Blind v28 against 10 real server peers on Default and Autarky (`replays/ab_blind28`, 20 games):

| rounds | first-sight pearl rate | global density | v28 unseen value (mid-bucket) |
|---|---|---|---|
| 0-99 | 0.017 | 0.015 | 0.025 |
| 100-199 | 0.018 | 0.016 | 0.075 |
| 200-299 | 0.018 | 0.016 | 0.125 |
| 300-399 | 0.019 | 0.019 | 0.175 |
| 400-499 | 0.028 | 0.032 | 0.225 |

Local gen replays (`notes/unseen/replays/king/gen_*`) pool to 0.09-0.12. Per map, the rate ranges from 0.000 (g2026_13, 20, 29) to 0.26 (g2026_37). **Within a map it is nearly constant over time.** For example, g2026_14 reads 0.148, 0.157, 0.148, 0.151 and g2026_21 reads 0.19-0.22.

So there are two errors in the current prior:
1. **The time growth is wrong.** Other dragons eat pearls, so a tile nobody has seen does not keep accumulating food. After r100, v28 overvalues unseen tiles 4-12x against real opponents on sparse maps. The earlier move from 0.01 to 0.001 was a win because it shrank this error (0.01 means 0.5 per tile from r100). 0.001 is still too high late in the game, but too low early on rich maps.
2. **A constant cannot fit maps that differ by more than 100x.** The first-sight rate can be measured cheaply at runtime. About 7 fresh tiles enter view per straight step, so the estimate converges within a few turns.

This is general logic with no per-map tables. It follows what has worked for us so far: estimating from observations (PEARL_ROUTE, UNK_PRIOR, PORTAL_ECHO_GUARD). Abyss uses the same concept, but with a constant `exploreValue` of 0.03 per never-seen tile. This patch is that idea with the constant learned.

### How it covers the other ideas in the brief

- **Decay with team coverage.** This happens implicitly. When allies have harvested the area, the tiles this dragon sees for the first time are empty, so its estimate falls. A split child re-learns in a few turns.
- **Crowd sharing.** The existing `otherDist` discount already cuts unseen tiles that another head reaches first. I added no new crowd term.
- **Information gain on spawners.** This is partly covered: an imminent countdown (≤3) counts as a hit. I did not add a separate value-of-information bonus for "will learn a spawn timer". Such a bonus has no calibration target. It is also the kind of optimism that lost for hunger-valve exploration and UNK_PRIOR 0.04.

### Interaction with PEARL_ROUTE and spawn learning

- **PEARL_ROUTE.** With γ=0.82, an all-unseen route is worth about `2.0 * est / (1-0.82) ≈ 11 * est`:

  | map type | v28 route value | EXPLORE_LEARN route value |
  |---|---|---|
  | sparse, real opponents | about 1.1 at r200, 2.5 at r500 | about 0.2-0.3 |
  | rich gen maps | — | about 1-2 from r0 (v28 only reaches that late) |

  So the route's pull toward the unknown now tracks the map instead of the clock. A visible pearl 3 steps away is worth about 1.1, so on sparse maps real food wins almost every comparison against imagined food.
- **Spawn learning.** `spawnAt` and `gapSeen` are untouched and take precedence: the flag only affects tiles with `spawnAt<0`. HOT_LEARN and LEARN_GAPS are unaffected.

## Mechanism checks (10 single games, `--jobs 1`)

Candidate is `src:-DEXPLORE_LEARN=1`, opponent is `variants/v28`. Replays are in `notes/levers/frontier-explore/replays/`.

**Calibration (the main mechanism).** On lesson/open_a with `BOTDBG`, the in-bot estimate averaged over all candidate dragon-turns tracks what the replay says is actually there:

| rounds | in-bot estimate | replay truth (pearl only) |
|---|---|---|
| 0-99 | 0.045 | 0.048 |
| 100-199 | 0.037 | 0.022 |
| 200-299 | 0.045 | 0.041 |
| 300-399 | 0.044 | 0.049 |
| 400-499 | 0.049 | 0.055 |

v28 used 0.025 → 0.225 over the same rounds.

**Behaviour** (candidate side listed first; c = team-union share of the map seen):

| map | result | eats <100 (cand / v28) | eats all (cand / v28) | coverage c50 (cand / v28) | longest (cand / v28) |
|---|---|---|---|---|---|
| gen/g2026_14 (rich) | W, W | 1782 / 1809, 1870 / 1843 | 9565 / 9624, 9756 / 9540 | .76 / .77, .78 / .76 | 33 / 17, 27 / 23 |
| blind default | L, W | 24 / 32, 30 / 32 | 173 / 292, 313 / 153 | .67 / .82, .81 / .75 | side-decided (B won both) |
| lesson/open_a | W, L | 444 / 474, 457 / 390 | 4404 / 4404, 4338 / 4235 | .18 / .19, .20 / .17 | 89 / 86, 97 / 105 |
| lesson/rush_b (food away from spawn) | L, W | 1528 / 1528, 1509 / 1419 | 8373 / 8650, 8453 / 8695 | .96 / .89, .92 / .90 | 27 / 34, 45 / 42 |
| gen/g2026_09 (famine) | L, W | 2 / 5, 5 / 2 | 5 / 19, 18 / 11 | — | side-decided |

Total 6/10. That count is noise, not evidence.

What the checks show:
- **The estimator is calibrated.**
- **Early exploration is not starved.** On rush_b, where spawn is empty and the food lies in a band away from it, coverage at r50 is equal or higher (.96/.92 against .89/.90). Across all 10 games, eats before r100 are mixed: equal or higher in 5 of 10. One reason early exploration holds up is the prior mean M0=0.03, which is above v28's `0.0005*r` in the first 60 rounds.
- **Late eats on rush_b are about 3% lower** (8.4k against 8.7k). This is worth watching in the batch.
- **No behavioural win is visible at this sample size.** The value has to come from the main agent's batch.

## CPU cost

In the judge sandbox on lesson/open_b (64x40, the largest map, 28k turns per team):

| | p50 | mean | p99 | max |
|---|---|---|---|---|
| candidate | 10.9M | 10.9M | 13.2M | 29.0M |
| v28 | 12.0M | 11.0M | 13.2M | 25.8M |

Per turn the patch adds 49 comparisons and 2 multiplies. `pearlValue` on never-seen tiles gets cheaper. The difference in max is turn-to-turn noise, and everything is well under 100M.

## Risks

- **Clustered food.** If food sits in one far region and the home area is barren, first sightings near home drive the estimate toward 0 and dragons stop drifting outward. It is bounded two ways. Every step still samples about 7 new tiles, and the decay forgets the old ones, so the estimate rises as soon as a dragon starts seeing the rich area. And UNK_EXPLORE's sealed-in portal gate does not depend on this value. rush_b, the closest lesson map, showed no starvation.
- **Rich maps.** The estimate is higher than v28's early prior, up to about 0.15-0.26, so unseen routes pull harder early on. This is correct in expectation, but it could pull dragons away from contested visible food. Watch gen maps with rates above 0.1 (g2026_14, 21, 37, 39).
- **A tiny effect.** When the sparse map's value is close to 0, unseen space barely matters, and the change may do nothing on maps where v28 was already fine.
- **The prior is never tuned per map.** M0 and N0 wash out after a few turns, so there is no route to overfitting through them.

## Suggested test (main agent)

1. Run `unseen_eval 'bot:-DEXPLORE_LEARN=1' --sets gen,blind,lesson,gated` against v28, then the holdout once.
2. Arms: `EXPLORE_MULT` 0.5 / 1 / 2, which tests whether the calibrated value is too cautious for route planning; and `EXPLORE_CD` 0 against 3.
3. `-DUNK_PRIOR=0.0005` as a zero-code control. If that alone matches the gain, the benefit comes from lower late values rather than from the learning.
4. If it passes locally, run a server blind A/B (blind28 was 11/20; eats on Default 348, Autarky 395). That is where the 4-12x late overvaluation was measured.
