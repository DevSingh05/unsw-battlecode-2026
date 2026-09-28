# Schooltime pass 2 (28 Sep 2026)

Code: `variants/wip_sch2/maps/schooltime.hpp` (new flags, all default 0; old SCH_* untouched).
Test maps: `maps/schooltime_b3.map` (best estimate of layout B, used for all B numbers), plus the earlier drafts `maps/schooltime_b.map` and `maps/schooltime_b2.map`.
Scratch scripts are in the session scratchpad (`sch2..sch10.py`, `first*.py`, `waits.py`, `rp.py`, `agg.py`).

## 1. Main finding: Schooltime has two spawn layouts on the server

The ladder runs **two different pearl layouts** under map id 9. The walls, portals and starts are identical. The replay map text hides gaps, so we only saw this from spawn events.

- **Layout A** is `maps/schooltime.map`: 326 spawn tiles, including the [1,20] pool (26 tiles). Total income is about 7.6 pearls/round.
- **Layout B** has 178 spawn tiles and **no pool**. It is identical in all 10 ch9 B games (171 tiles in 10/10 games, 7 in 9/10), and it is mirror-symmetric.
  - 18 tiles at [20,50]. These are A's [20,50] tiles in the top strip and at the maze entries.
  - 2 tiles at [20,80]: (8,16) and (51,16).
  - 158 tiles at [20,200], including 22 in the yard corners and the 4 inside mouths.
  - That is about **2 pearls/round**, a starved map.
  - The classes come from first-spawn timing across 51 B games: the [20,80] tiles of A have median first spawn 50 in A games but 102 in B games, and A's [20,200] tiles have median 107.
- **How often B comes up:** ch9 10/15 games, ch7 15/30, ch6 8/15, v13 5/8, kings 7/11. Overall it is about half of all Schooltime games.
- **This rewrites the ch9 diagnosis.** In the "enemy holds the yard" games the enemy did *not* hold the yard (their yard eats r0-100 were 0). Those were B games:
  - Our 2 rushers reached an empty yard at r21/r25.
  - Our pearl model believed A's gaps.
  - We fell behind outside: units at r100 were 5-16 against 18-19.
- On A games (5 of 15) we owned the yard. Most in-yard HitSelf deaths were len-2/3 dragons with 0 free exits at the 64-unit cap (recycling), and the games were lost on the king race.

## 2. Flags

| flag | what it does |
|---|---|
| `SCH_LAYOUT` | Every turn, compares the visible countdowns (`in.tin`) with both layouts. On B it overwrites `w.gmin/gmax` with the B table (`SCH_LAYOUT_PATCH`, default 1) and switches off all yard behaviour (`SCH_LAYOUT_NOYARD`, default 1). All 6 starters detect at r0, and 95% of 7x7 windows contain a distinguishing tile. |
| `SCH_CROWD` | (a) Inside the yard: penalty for tiles near ally heads and near-dead-end tiles. Length ≥4 dragons don't walk in after r60. |
| `SCH_CONTEST` | (b) Length ≤3 dragons near or inside the yard chase enemy heads 3-6 away. Length ≥6 dragons don't enter the yard within 40 rounds of seeing ≥2 enemy heads in it. |
| `SCH_FALLBACK` | (c) Length ≥8 dragons and the king stay out of the maze band y 8-21. Always active on B (with `SCH_LAYOUT`); on A only when ≥3 enemy heads were seen in the yard. |
| `SCH_NORUSH_KID` | (d) Only the r≤3 starters rush. This is a no-op: children inherit the parent's state. |

## 3. Results

Setup: pool v13,v12, `--jobs 6`, 10 seeds, maps schooltime + schooltime_b3. Each flag was run alone and then in combos. v12 and v13 play identically here, so each map has only about 20 distinct games.

| config | A (30000) | B3 (30000) | overall | A (31000) | B3 (31000) | overall |
|---|---|---|---|---|---|---|
| baseline | 0.50 | 0.50 | 0.500 | | | |
| LAYOUT | 0.50 | 0.75 | 0.625 | | | |
| CONTEST | 0.65 | 0.35 | 0.500 | | | |
| FALLBACK | 0.50 | 0.50 | 0.500 | | | |
| CROWD (b1 map) | 0.25 | 0.60 | 0.425 | | | |
| LAYOUT+FALLBACK | 0.50 | 0.80 | 0.650 | | | |
| LAYOUT+CONTEST | 0.65 | 0.75 | 0.700 | 0.50 | 0.65 | 0.575 |
| **LAYOUT+CONTEST+FALLBACK** | 0.65 | 0.80 | **0.725** | 0.50 | 0.65 | **0.575** |

Extra runs, vs v13 only, 30 seeds (base 30100):
- **A:** CONTEST 0.533, CROWD 0.367.
- **B3:** LAYOUT 0.617, LAYOUT+FALLBACK 0.650, CONTEST 0.433, and no-rush without the gap patch 0.567.

**Local B results depend on how accurate the B map is.**
- On `schooltime_b.map`, where I wrongly made the yard corners [20,80] (a rich yard), LAYOUT scored 0.33.
- On b2, where most tiles are [20,200], it scored 0.78.
- b3 is the calibrated version (see §1).

## 4. Conclusions

- **SCH_LAYOUT is the real fix.** It is positive on B on both seed sets (0.75 and 0.65) and changes nothing on A.
- **FALLBACK** adds a little on B.
- **CONTEST** is +0.15 on A for seeds 30000 but 0.50 on fresh seeds, and 0.533 over 30 seeds. Treat it as neutral to slightly positive.
- **CROWD** hurts on A, so leave it off. Yard congestion deaths are unit-cap churn, not the cause of the losses.
- **Integrate:** `SCH_LAYOUT=1 SCH_FALLBACK=1`, plus `SCH_CONTEST=1` if you accept a neutral A-side change.
- **Before trusting the numbers:** validate with ladder challenges. Check that B-game units at r100 reach ≥18 and that the rushers no longer go to the yard.
