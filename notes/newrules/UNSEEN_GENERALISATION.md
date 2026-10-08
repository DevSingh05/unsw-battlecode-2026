# Unseen-map generalisation: known vs unknown play in v43, Sprint evidence, test-set realism (2026-10-02)
Scope: variants/v43 (read only), the Sprint replays (scratchpad `cutlery/`, 63 Cutlery games + our R16 vs PPP),
server per-map ratings (`tools/permap_ratings.py 10`, one API call), `GET /api/v1/maps` (17 active maps, all already known),
and 16 local single games (2 at a time). Scripts are in the session scratchpad under `ug/`: explore.py, exagg.py, bvk.py, sch.py,
mstats.py. The map-stats validator is saved as `notes/newrules/mapstats.py`.
Qualifier (10 Oct) and Grand Final maps are all unseen, so the v43 unknown-map path is the bot that will play there.

## 1. Headline
1. Map knowledge mostly acts as shared memory. Each dragon is its own process, and a split child starts with nothing
   (notes/01 §1). On a known map every newborn knows all walls, every portal partner and every pearl timer. On an unknown map
   it knows its own 7x7 view. The local blind-vs-known gap comes almost entirely from portal use and early food, and those
   are the two things a newborn cannot learn quickly.
2. **Qualifier risk:** on unseen 64x64 maps v43 can *falsely adopt* a known map. On gen/g2026_16 (64x64, open), 1831
   dragon-turns ran as "Big Empty"/"Around UNSW"/"Australia". While a map is adopted, all `!w.known` logic is off and the bot
   trusts the wrong walls, portals and pearl gaps. `filterByCountdowns()` keeps the wrong map when no candidate fits.
3. Our test sets don't look like the real maps. Gen, genhold and lesson maps put the queens about 10-14 steps apart (official:
   31-46). They have 1/3-1/4 of the corridors, almost no hot tiles and almost no portal-gated food (official: 7/17 maps hold
   >= 20% of food behind portals). The `sprint` set in unseen_eval has also been **known** since v38s/v40 (SPRINT_KNOWN=1),
   so the "unseen" pooled numbers in V41/V43 partly measure known-map play.

## 2. What v43 does only on known maps (and whether it can be learned at runtime)
| known-only machinery (main.cpp) | what an unknown map gets instead | runtime substitute |
|---|---|---|
| `adopt()`: full `nxt` incl. portal partners for every tile | unseen edges assumed open; portals = kelp until both ends seen by *this* process (UNK_EXPLORE knock, UNK_SCARCE_FIX, UPE scouts) | crossing + **sharing** links (G2, G3) |
| `gmin/gmax` gap tables for all tiles (spawn timing of unseen tiles, PEARL_ROUTE values) | `UNK_PRIOR` 0.001 for unseen tiles; observed countdowns; mirror via inferred `sym` | handoff/gossip of hot tiles, block pooling (G5) |
| `sym` from file | `inferSymmetry()` from seen walls (per process) | pass sym in handoff (G2) |
| `applyMapParams`: ram guard, kingDeclare/seed/splitStop/feed per map; KING_V2 table (Sch 200/340/260, Sli 170/370/250, Por 250/360/300, QoS 330/420/400) | UNK_KING seed 250 / feed 300, ramGuard 2 if N <= 750, crown early at 62 units | signals: size, food rate, contact (G6) |
| map modules: Schooltime (yard via portals, keepers, avoid maze band), Portals (tubes/sock, no-contact consolidation), Trauma (pen king, factory cycle), QoS (spade rooms via portal doors) | none (`mapKey()==-1`) | general versions: G3, G6, G7, G8 |
| `pfCompute()` once (pockets from full graph) | recomputed each turn from seen edges; dives need hot evidence (POCKET_UNK_NEEDS_HOT) | handoff of pockets/hot tiles |
| Sprint maps (SPRINT_KNOWN, SPRINT_KING_FULL, SPRINT_ROUTE) | n/a (Qualifier maps are new) | none needed |
| QGUARD/QBOX/QALLY_KEEP/FREE_STEPS | same code on both. FREE_STEPS never steps through unknown portals | none |

## 3. How much knowledge is worth (evidence)
- **Server, same build, Sprint maps unknown vs ranked maps known:** v38m (Sprint maps unknown) went 41-49 (.46) on the 7 Sprint maps
  and 123-73 (.63) on the 10 ranked maps. v41 (Sprint maps known + FREE_STEPS) went 159-106 (.60) on Sprint maps and 268-150
  (.64) on ranked. Knowing the map closed most of a ~17-point gap. Local v38s vs v38m (known vs unknown, nothing else changed): .643.
- **Local, this study: v43 with -DNO_KNOWN_MAPS=1 vs v43, seed 1000, both sides, 12 games: blind 4/12.** Blind won Maze 2/2
  and Schooltime 2/2, and lost Australia, Islands, Around UNSW and Trauma 0/2 each.

| map | portal moves blind / known | eats by r100 blind / known | units/total r100 blind / known |
|---|---|---|---|
| Australia | 1-3 / 179-206 | 75-85 / 315-320 | 35-38/85-90 vs 48-50/117-128 |
| Islands | 1-3 / 466-505 | 176-220 / 276-329 | 23-26/62-66 vs 54-61/128-151 |
| Around UNSW | 1-4 / 46-56 | 236-272 / 386-408 | similar units, total 124-146 vs 144-155 |
| Trauma | 48-81 / 184-229 | **4-12** / 95-103 | **5-8**/12-18 vs 27-28/65 |
| Schooltime | 2-9 / 334-414 | 108-139 / 272-315 | (blind won 2/2: known side churned, 709-800 deaths vs 403-412, HitSelf 341-423) |
| Maze | 48-72 / 151-180 | ~equal | ~equal (blind won 2/2) |

  By r200 blind dragons have seen *more* of the map (0.88-1.00 vs 0.52-0.89), so they do find things. They don't exploit
  them: no crossings, and children forget. On Trauma the blind team sits sealed in the pen, because its exits are portals.
- **Sprint, every team on unseen maps** (explore.py; seen = union of 7x7 views; food% weighted by the rebuilt gaps). Median Cutlery games vs our game vs PPP:

| map | seen r50 (food%) Cutlery / PPP-v-us / us | eats <= r100 C / us | portal-only eats C / us | first head in enemy half C / us |
|---|---|---|---|---|
| Australia | 44% (44) / 41% (54) / 34% (**11**) | 125 / 51 | 42 / **0** | r10 / r9 |
| Islands | 63% (58) / 68% (61) / 36% (45) | 198 / 146 | 0 / 0 (shortcut portals) | r6 / **r26** |
| Around UNSW | 45% (73) / 45% (67) / 32% (46) | 259 / 178 | 0 / 0 | r15 / **r29** |
| Maze | 48% (40) / 38% (25) / 45% (35) | 112 / 91 | 0 / 0 | r54 / r134 |
| Tower Defense | 48% (43) / 50% (43) / 62% (57) | 7 / 73 | - | r126 / r53 (we were better) |
| weakhold | 45% (49) / 40% (41) / 46% (49) | 58 / 90 | - | r140 / r75 (we were better) |

  The top teams reach the middle and the food (including vaults) in the first 25-50 rounds. Where Cutlery stays home
  (TD, weakhold) it does badly. So "push to the contested middle early" generalises, and "wander late" does not.

## 4. Generalisable improvements, ranked (all behind flags, `!w.known` or unconditional; none built here)
**G1. Qualifier build: no known-map adoption (or strict adoption).** Cost ~0, removes a real failure mode.
- Evidence: gen/g2026_16 (64x64) had 1529 turns as Big Empty, 182 as Around UNSW and 120 as Australia (`-DDEBUG_INDICATOR=1`,
  `unswbc run -v`). The lesson maze_a/pockets_a/maze_b (same sizes as Default/Devil/Trauma) had 0. `observeEdges()` adopts
  `candidates.front()` as soon as the seen edges are consistent; an open 7x7 view matches Big Empty. `filterByCountdowns()`
  "keeps what we had" when every candidate contradicts the countdowns. While adopted: UNK_KING isn't set, PEARL_ROUTE runs on
  the Big Empty gap table, and UNK_EXPLORE/USF/UPE are off. A remix of an official map (same walls, new pearls or queen
  spots, as in 1.2.6) would also run the old module with wrong data.
- Rule: for the Qualifier build set `NO_KNOWN_MAPS=1`, since every map is announced unseen. Hedge if wanted: adopt only on an
  exact `identifyByStart` match, drop (not keep) on any countdown contradiction, and turn PEARL_DISTRUST on. Then the Qualifier
  bot is exactly the bot the blind sets measure.

**G2. Share map knowledge across processes: SPLIT_HANDOFF + MAP_GOSSIP** (notes/13 #4-5, pearl-inference P4; never built).
- Why it is first among the behaviour changes: it turns one dragon's learning into the team's. That is the core of the known
  advantage in §3. fm_portalknow (notes/unseen/failure-mining.md): the team union knew 10/12 portal pairs while 22-78% of
  living dragons knew none.
- Mechanism: after `SPLIT k` the parent's ray *opposite its facing* leaves from its new tail straight into the child's body.
  The child has the highest id, so it reads the message on its first turn, the same round. One 64-bit word per split costs
  nothing. Gossip: idle rays carry a rotating fact.
- Payload priority: (1) a portal link (two 13-bit canonical edges + tag/checksum); (2) symmetry (2 bits) + "home sealed"
  flag; (3) best hot tile / food cluster + rate class; (4) dead-end pocket mouth. Apply only facts consistent with the
  receiver's own view, and use the existing SECRET checksum (enemies hear rays).
- Test: blindvk17 + qgen (section 6). Mechanism metric: share of living dragons that know >= 1 portal pair at r100.

**G3. Portal-first foraging by expendable units (general form of the Portals/Schooltime/QoS/Trauma modules).**
- Evidence: 7/17 official maps hold >= 20% of food behind portals (ranked 5/10: Default .50, Portals .46, QoS .60, Sch .33,
  Trauma .99; Sprint: Australia .52, Stripes .89). Sprint crossings by r100: Cutlery Aus 34, Isl 64, Stripes 60 vs our 0.
  Vault eats 437/game vs 0. Blind v43 makes 1-9 portal moves/game on Aus/Isl/Around/Sch vs 46-505 known (section 3).
  Blind Trauma: 4-12 eats by r100 vs 95-103.
- Rules: (a) sealed-home detector: if the walkable region around our start (seen edges + inferred sym) has no unseen frontier
  and the tiles we have seen are under ~0.3 N, cross the nearest portal at once with L2-4 non-queens. That is the Trauma pen,
  the Portals halves and the Schooltime box neighbourhood. (b) From about r10-40, 1 in 3-4 L2-4 non-queens knocks and crosses
  any unknown portal whose far side is unseen. UPE exists but fires rarely; lower UPE_HUNGER and drop the slot/mod gate early.
  (c) The queen never crosses blind. (d) Learned links go into `nxt`, so PORTAL_WARN etc. apply, and are shared (G2).
- Why earlier portal flags "failed": they were judged on gen/holdout, where 37/40 maps are walk-connected (portal-only food
  2/40 and 1/40). There crossing can only cost. See section 5.

**G4. Early frontier push to the contested middle (r0-50), then exploit.**
- Evidence: in Sprint we saw 11% of Australia's food by r50 (Cutlery 44%, PPP 54%), 36% of Islands vs 63-68%, and reached the
  enemy half at r26-29 vs r6-15 on Islands/Around. Where we pushed early (TD, weakhold) we beat Cutlery's numbers.
- Rule: at birth, an unknown-map unit values unseen tiles *toward the map centre / mirror axis* above UNK_PRIOR for the
  first ~50 rounds (on a symmetric map the centre is where both halves' food meets). After that use observed food only.
  The weakhold note (V43) shows the side that takes the centre field at r1 wins the economy. This is the same thing.

**G5. Pearl-timer inference to replace gap tables.** Neighbouring tiles share a gap range 92-96% of the time
(pearl-inference.md), mirror tiles share one countdown, and official maps have clustered classes (`1 1`, 1-4, 10-30,
40-200). Pool countdowns per 3x3 block, mirror them, hand them off (G2). HOT_LEARN/EXPLORE_LEARN were rejected on gen sets,
which have **0 hot tiles at the median** (official 8-20), so they were never really tested.

**G6. King/queen timing from runtime signals (general KING_V2 table + Portals "no contact" rule).**
UNK_KING's fixed 250/300 replaced a per-map table ranging from 170/250 to 330/400. Cutlery's longest reached >= 16 at r216-365.
Signals: board size, observed food per round, and first enemy contact. If no ally has seen an enemy head by about r150
(beacons), the halves are separated (Portals-like): consolidate earlier and stop splitting. UNK_SIZE_PARAMS was "neutral"
only on gen. Retest on qgen/blind17.

**G7. Protected-queen spawn = stay home and be fed (general Trauma pen / Trophy cup / Schooltime box).** Organisers say Qualifier
queens spawn in "much safer, more consistent spots". NEWMAPS: a living queen won 87/87 single-queen r500 games. Rule: if the
queen's start region has <= 2 entrances (ring6 small) and no enemy head is seen nearby, she stays inside. Allies keep the
entrances clear (QALLY_KEEP already does part of this) and feed her from r~250. Never split her below QG_MIN.

**G8. Corridor-aware king (Schooltime "avoid maze band" generalised).** Sprint corridor share is 0.21 (median) vs gen 0.06.
Big non-queen dragons and the queen penalise 1-wide corridor tiles (degree 2 from seen edges) when an open alternative exists.
Low priority. Maze/weakhold losses are already queen-boxing, which v43 addresses.

Not worth generalising: SPRINT_* per-map params (Qualifier maps are new), and Schooltime-style pumps. Known Schooltime churned
2x the deaths for no gain in local games, and known Maze played the same as blind. Single seed, so re-check the Schooltime
module on the server data before trusting it.

## 5. Are our unseen sets realistic? (`python3 notes/newrules/mapstats.py --summary ranked sprint gen genhold lesson`, q25/median/q75)
| metric | official ranked (10) | official Sprint (7) | gen (40) | genhold (40) | lesson (24) |
|---|---|---|---|---|---|
| tiles N | 512/924/1150 | 512/1152/4096 | 252/442/900 | 352/668/1730 | 640/960/1150 |
| symmetry | xy 7, y 3 | xy 6, y 1 | xy 18, y 9, **x 7, none 6** | xy 13, **x 10, none 10**, y 7 | xy 11, y 9, x 4 |
| queen length | 3/3.5/4 | 2/4/4 | 4/**6/12** (flagship queens) | 3/4/16 | 4 |
| queen<->enemy queen BFS | 26/31.5/80 (2 unreachable) | 23/46/72 | **8/10.5/17** | 9/14/23 | 9/14/28 |
| ring6 (low = enclosed spawn) | 11/14.5/20 | 9/11/22 | 14/19.5/24 | 11/15.5/24 | 22/24/24 |
| kelp share of edges | .11/.16/.24 | .11/.25/.27 | .05/.13/.16 | .06/.12/.19 | 0/.03/.11 |
| corridor tiles | .08/.15/.19 | .09/.21/.35 | .02/.06/.11 | .02/.07/.15 | 0/.005/.04 |
| dead-end tiles | .005/.025/.04 | .02/.08/.09 | 0/.01/.04 | 0/.008/.03 | 0 |
| portal pairs | 2/5/12 | 0/4/12 | 0/2/6 | 2/4/8 | 0/0/2 |
| maps with >= 20% food portal-only | **5/10** | **2/7** | 2/40 | 1/40 | 5/24 (vault/islands) |
| spawn-tile share | .16/.20/.50 | .08/.15/.29 | .26/.55/.97 | .23/.33/.70 | .49/.94/1 |
| hot tiles (mean gap <= 5) | 0/8/12 | 4/20/24 | **0/0/2** | 0/0/36 | 0/4/16 |
| open wrap borders | 0/.08/.94 | 0/.39/.92 | .12/.72/1 | .05/.34/.91 | 1/1/1 |

Verdict: **no**. Gen/genhold (Loong generator) put both queens in a brawl 10-14 steps apart, often make the queen the big
flagship, smear slow food over half the tiles, have few corridors/dead ends/hot pockets, and almost never gate food behind
portals. They also use x/none symmetry, which no official map does. Lesson maps are open boxes. These sets reward close-range
brawling and punish portal crossing and exploration, which is the opposite of what the Sprint data says matters.

## 6. Proposed test-set changes
1. **Fix `sprint` now.** In `tools/unseen_eval.py` the sprint set runs v40+ with the maps known. Run it with `-DNO_KNOWN_MAPS=1`
   on both sides (or `-DSPRINT_KNOWN=0`). Treat the sprint numbers in V41/V43 pooled scores as known-map results.
2. **`blind17` as the primary unseen set:** the 10 ranked + 7 Sprint maps (the organisers' own designs, current 1.2.6+ queen
   spots) with `NO_KNOWN_MAPS=1` on both sides, 2 seeds x 2 sides = 68 games. The old `blind` set (10 maps) was missing from
   every eval since V38.
3. **`blindvk17` (asymmetric):** candidate blind vs map-aware v43. That is the real-opponent view: Sprint opponents crossed
   portals and found vaults whether or not they knew the map. Baseline here: v43-blind 4/12 vs v43. Report win rate plus
   portal moves, eats <= r100, queen alive, and r500 queen/longest. Mechanism changes (G2, G3) show up there first.
4. **New generator `qgen` (40 tuning + 40 holdout)**, validated against section 5 with mapstats.py. Each set's quartiles must
   overlap the official ones. Targets:
   - Size: W 24-64, H 12-64, N 500-4100 (median ~1100). Symmetry xy 75% / y 25% (a few x for robustness, no none).
   - Kelp .12-.27 of edges, corridor tiles .10-.30, dead-end tiles .02-.09, 4-12 portal pairs on 80% of maps.
   - Food: 8-30% of tiles spawn. Rate classes clustered in blocks: a few `1 1`, hot 1-4 pockets/fountains (5-25 tiles),
     10-30 regions, 40-200 bulk, rare 400-500 late tiles. Mirror classes.
   - Motifs, mixed per map with weights, built from the official designs:
     - portal-only vault/yard holding 20-90% of food (Australia, Schooltime yard, QoS rooms) on ~40% of maps;
     - sealed home pen with portal exits (Trauma, Portals) ~15%;
     - poor home / rich contested middle (weakhold, TD, Maze) ~40%;
     - maze band of 1-wide corridors ~30%;
     - band/stripe links via portals (Stripes) ~10%;
     - open 64x64 with sparse kelp (Around UNSW/Big Empty-like; also exercises G1) ~10%.
   - Dragons: 2-4 per team (rarely up to 10), lengths 2-6, sometimes one big non-queen; the queen (first DRAGON pair) L3-5,
     once in a while a big spiral queen (Slithery).
   - **Queen spawn protected** (new-map style): a sealed 2x2-4x4 box with a pearl tile, a cup/pocket with 1-2 entrances, or the
     back of the home region. Queen-to-queen BFS 25-80 or unreachable on foot. Nearest enemy head >= 15.
5. **Weighting / gate for unseen changes:** pooled = blind17 50% + qgen 30% + gated/lesson 20%. Keep blindvk17 as a mechanism
   report. Holdout only at the end. Retire gen/genhold as tuning sets, or keep them as a brawl-robustness check only. Old
   rejections tested only on gen/lesson should be re-run on blind17/qgen before being called dead: LEARN_PORTALS, the
   hunger-45 valve, HOT_LEARN, EXPLORE_LEARN, UNK_SIZE_PARAMS, UNK_SEALED_FOOD.

## 7. Suggested order
G1 (one flag, Qualifier build) -> test-set fixes 1-3 (no new code) -> qgen generator -> G2 handoff -> G3 sealed-home + early
scouts on top of G2 -> G4 -> G7 -> G5/G6. Every step behind a flag, judged on blind17 + blindvk17 + qgen, never on gen alone.

## 8. Build: variants/v45 = v43 + MATCH_STRICT (G1 hedge), 2026-10-02. Default MATCH_STRICT=1. Not submitted.
Flags (end of params.hpp): MATCH_STRICT, MS_EVID 8, MS_EV_DIR 1, MS_HANDOFF 1, MS_GOSSIP 1, MS_DEBUG 0 (MS_TRACE=file logs one line per turn).
`-DMATCH_STRICT=0` gives v43 exactly (same actions on devil and sprint/maze, seed 1000).
- **Starting dragons** (round 0, first turn, recognised by the missing ECHOES line): a map is accepted only if our id has
  this start tile and length in it, and every not-yet-moved higher-id start head in view sits on its start tile. Every map
  that passes stays a candidate (Maze and Trauma share their start tiles), and the countdown filter picks between them as in v43.
  If nothing passes: unseen for life, and children get told "unseen" (only when same-size maps exist).
- **Children/restarts:** they adopt the map index a confirmed ally sends by sonar (on split turns and idle turns,
  only when no other sonar is going out, so the echo/probe logic is untouched). Otherwise they adopt on their own only when
  one map family is left with zero pearl misfits and >= 8 distinct non-border kelp/portal edges match.
- A wall/portal contradiction removes that map for good. Switching only happens inside the start-matched list / one family, never
  to an unrelated same-size map. Pearl contradictions (>= 3) keep the walls and drop the gap table (PEARL_DISTRUST
  fallback, which also covers the Sprint maps' rebuilt gaps on the server).

Checks (seed 1000, scratchpad ms/tr.py traces):
- (a) 17 official maps: share of turns with the right map adopted, 99.0-100% (Devil 99.0, QoS 99.5, Trophy 99.5, the rest
  99.7-100). Swapped-side Default/Schooltime/Trauma 99.7-99.8%, pearl variants var/devil_pv1 99.0 and schooltime_pv1 89.4
  (distrust fallback; v43 drops these to wrong maps/unknown). The leftover <1% is first-turn children the handoff ray
  missed. Self-play replays are not byte-identical to v43 (first divergence r0-r150; chaos from those turns and the
  extra sonar), but identification matches.
- (b) False matches: v43 (strict off) was "known" on look-alike unseen maps: g2026_16 3.9% of turns (Big Empty/Around
  UNSW/Australia), peel_a 4.1% (Default), g2026_08 (Arena), g2026_26 (Trophy), webs_a (Default). **v45: 0 turns on all
  25 look-alike maps** (7 gen/genhold + 6 lesson maps that share an official size, and the 12 new real_gen/samesize maps).
  On maps whose size matches no official map nothing changes (g2026_00 and open_a are action-identical to v43).
- (c) unseen_eval vs v43, --jobs 3: seed 451000: every set .500 (gen, lesson, gated, real, realhold, samesize, holdout),
  ladder .475, sprint .500, pooled 216/432 = .500. Seed 461000: gen .487, lesson/gated/real/realhold/samesize/holdout .500,
  ladder .525, sprint .571, pooled .499. Neutral, as expected: these sets have no look-alikes except those listed in (b), and
  there both v43 sides fooled themselves equally. The gain is against map-aware opponents on look-alike Qualifier maps.
- (d) Sandbox (v45 vs v43, seed 1000): australia v45 max 33.6M (p99 30.4M), v43 32.4M; g2026_16 v45 35.7M (p99 32.7M),
  v43 35.5M. Under 40M, no change.

Test-set changes made: tools/realmapgen.py (spec 6.4; validates with mapstats and loads every map in the engine).
maps/real_gen/tune (40, seed 2028), hold (40, seed 2029), samesize (12, official W x H, look-alike stress test). First drafts
are in archive/real_gen_draft/. Their stats match the official quartiles: queens 33-35 BFS apart, kelp .19, corridor .14-.15, spawn
share .19, portal pairs 4-6, portal-only food median .11-.14. tools/unseen_eval.py has new sets real, realhold, samesize,
blind17. `sprint` is no longer pooled (it is known since v40).

Recommendation: merge MATCH_STRICT into v44 (it touches only identification and sonar output on idle/split turns, so it
should not interact with WH_CENTRE). It is neutral locally, prevents wrong-map play on Qualifier maps that share an
official size, and holds up on the server's pearl variants.

## 9. v49 = v44 + MATCH_STRICT (merge of v45), 2026-10-02. Default MATCH_STRICT=1. Not submitted.
Built by applying the v45-vs-v43 diff to a copy of v44. One main.cpp hunk (the header) and the params tail were applied by hand;
the reject/orig files are in archive/v49_build/. v49-only changes to the child rule:
- Several known maps fitting with zero pearl misfits: take the first, as v43 does (Queen Of Spades and its "Ages" twin
  share walls). The evidence bar still guards against unseen maps.
- One-orientation wall evidence is accepted at >= 2 x MS_EVID (Devil's columns).
- MS_SPAWN_EV (spawning tiles as evidence) was tried and is off: it brought back false matches on all-spawn maps
  (peel_a as Default 4.7%, g2026_16 as Big Empty).

Checks:
- Compiles. `-DMATCH_STRICT=0` gives the same actions as v44 (sprint/weakhold, devil, sprint/maze, seed 1000).
- WH_CENTRE: on weakhold (seeds 1000-1002), ids 2-7 had the map adopted on 100% of their turns in r0-59 (1042/1042),
  including split children. WH_CENTRE reads w.gmax. The pearl-distrust fallback would wipe it, but the server's weakhold
  file is the 1.2.7 bundled one, identical to ours, so no distrust (0 events in the traces).
- Identification, seed 491001: Devil, QoS 100%, weakhold 100%, Schooltime 99.9%, Australia 99.8%, Trophy 99.0%.
  False matches on the 25 look-alike maps: 0.
- v49 vs v44: weakhold 13/24 (.54, seeds 495000 x12). An earlier run of the first port was 3/12 + 9/20; the strict-off
  control was 10/20. The divergences traced to single first-turn children whose parent's handoff ray missed (bent
  tail), so chaos rather than a mechanism. Ranked devil/schooltime/portals/trauma/autarky/default x2 seeds: 15/24 (.625).
  real .500 (40/80), samesize .500 (12/24).
- Sandbox (main.cpp touched, seed 1000): australia v49 max 33.6M (p99 30.4M) vs v44 32.4M; schooltime 27.4M vs 27.2M.

## 10. v49 server regression and v51 (2026-10-03)
Server (coordinator): v49 lost ground against v44 on Stripes (1635 vs 1926), Devil, QoS, Portals and Maze. v44 was restored.
What 20 v49 + 9 v44 server replays (replays/v49_srv/, Stripes/Devil/QoS/Portals/Maze) show:
- The server maps are identical to ours (walls, portals, DRAGON starts). Identification worked: decoding our sonar
  (scratchpad ms/mapwords.py) shows v49's handoff words naming the right map (Stripes=17, Devil=6, QoS=12, Portals=9,
  Maze=8) from round 0, so the ECHOES-line original detection works on the judge too.
- No TLE or budget overrun events.
- The visible difference from v44: MS_GOSSIP. Every confirmed dragon sent the map word on 4 rays on every otherwise idle
  turn, 2,100-47,500 extra rays per game where v44 sends none early. Rays that hit enemies land in their inbox and give
  away our direction, and opponents that read sonar can use that. Not proven, but it is the only systematic behaviour change on official maps (the
  pearl-distrust fallback can't be checked: server replays strip countdowns).
v51 (variants/v51; files from v49, main.cpp/params.hpp = v44 + a small patch; MATCH_STRICT=1, MS_GOSSIP_R=500):
- Official maps: v44's own matching, untouched. Only new rule: a starting dragon (round 0, no ECHOES line) whose start
  fits no same-size known map marks the map unseen for its process (no adoption, candidates cleared). Such dragons
  pass "unseen" to children (split turns, plus idle turns while round < MS_GOSSIP_R). Children that hear it drop
  any known-map guess. No known-map gossip, no strict child rules, no pearl distrust.
- On all 17 official maps (seed 1000, self-play, so both sides) actions are identical to v44. Sonar is identical too
  (checked QoS, Stripes, Devil, Portals).
- Look-alike maps (25): wrong-map turns 0-0.4% (g2026_16 0.3%, peel_a 0.2%, webs_a 0.1%, g2026_08 0.4%,
  g2026_26 0.03%), vs v44's 0.2-4.1%. With split-turn-only words (MS_GOSSIP_R=0) it was 0.2-3.9%. Zero is not reachable
  without changing children's adoption on official maps, which is what v49 did. The gossip only fires on look-alike
  unseen maps (dead originals exist only there).
- Sandbox: g2026_16 v51 max 35.5M (p99 32.8M), australia 34.1M (p99 30.3M). Under 40M.

## Status (paused 2026-10-02 at the coordinator's request)
Done: everything above. No games, API calls or downloads are running; the 16 local games and 2 API reads finished before the pause.
Left, if resumed:
- More seeds for blind-vs-known v43 (only 1 seed per map so far). Check the Schooltime-module churn on server data.
- Build the qgen generator (spec in 6.4) and validate it with mapstats.py.
- G1 hedge: done as v45 MATCH_STRICT (section 8). qgen: done as tools/realmapgen.py.

## 11. qf1 Qualifier build (8 Oct, ~12:10 EDT): variants/qf1 = bot/ + `QE_KR 2` + `UNK_PORTAL_SIDES 2`. Not submitted.
variants/qf1 is bot/ (minus .unswbc-build, *.orig, .DS_Store) with `#define QE_KR 2` and `#define UNK_PORTAL_SIDES 2`
prepended to params.hpp. bot/ keeps every new flag at 0. KW_QID stays 0. Scripts and logs are in work/qf/ (gitignored).
- **QE_KR** (notes/top5/TOP4_HORSE_OCT8.md 4; diff notes/top5/new_rules_tools/QE_KR_horse8.diff, applied unchanged): before
  QS_FROM the queen floods each visible enemy head's kamikaze reach. Each visible pearl on the path refunds one paid step.
  The flood is capped at 4, gives `threatAt`, and adds a 60 penalty.
- **Gate:** QE_KR acts only while the new sticky per-process `World::neverKnown()` holds:
  - `everKnown` is set in `adopt()` and never cleared, so it covers split children that adopt the map, a mid-game drop
    (Schooltime B doors) and a MATCH_STRICT reset;
  - `nkBirth` is set once, at the end of the process's first `analyse()`, to `!known && candidates.empty()`;
  - live `!w.known` is not used. `QE_KR_ANYMAP=1` removes the gate (that is horse's ungated prototype).
- **UNK_PORTAL_SIDES=2** (new value): the Codex reverse-face portal fix, applied only while `neverKnown()`. Value 1 is the
  old ungated form. It acts inside observeEdges' `if (!known)` block, so with 1 a known map dropped mid-game would also
  change; 2 rules that out.

Checks (sandbox, seed 1000 unless noted):
- **Identity on the 17 known maps.** The check compares the full `-v` transcript (every dragon's stdout, deaths and the
  result) with CPU lines dropped. qf1 vs b4, both sides, against b4 vs b4, on maps/server_live (17 maps) plus
  schooltime_b/b2/b3: **40/40 identical**.
  - Positive control: the ungated build (QE_KR_ANYMAP=1 + UPS=1) differs in 11/12 games on Trophy, Devil, TD, Autarky and
    Schooltime B/B2. Trophy ends at r29-30 instead of r93, and the Schooltime B queen diverges at r29/r50. So the gate is
    what keeps the 17 identical.
  - UPS=1 alone was also 12/12 identical on schooltime_b/b2/b3, Schooltime, Portals and Trauma at this seed.
  - Flags off: bot/ vs b4 on Trophy, Devil, Portals and Schooltime B, both sides: 8/8 identical.
- **Fixture** maps/targeted/unknown_neck.map (copied from codex-battlecode), seed 121000:
  - b4 as A: the queen moves N into her neck through the unknown portal, dies at r0 and loses at r1.
  - qf1 / UPS=2 / UPS=1 as A: MOVE E, the queen lives, draw at r500.
  - QE_KR alone does not fix it.
- **Unseen strength vs b4** (`tools/unseen_eval.py --seeds 1 --jobs 6 --sets real,realhold,blind17`; blind17 =
  -DNO_KNOWN_MAPS=1 on both sides, so QE_KR is live there):

| seed base | real | realhold | blind17 | pooled |
|---|---|---|---|---|
| 951000 | 46/80 .575 | 50/80 .625 | 34/68 .500 | 130/228 **.570** |
| 961000 | 37/80 .463 | 46/80 .575 | 35/68 .515 | 118/228 **.518** |
| both | 83/160 .519 | 96/160 .600 | 69/136 .507 | 248/456 **.544** |

  Both seed bases are above the .48 bar, so QE_KR stays in. The base (b4) does not lunge like horse, so this checks for
  regressions and cannot show the horse-specific gain. The per-flag-alone runs were skipped because the result was not
  ambiguous.
- **CPU, judge sandbox** (judge limit 100M):
  - **Australia (known, flags inactive):** qf1 p99 27.8-31.2M, max 32.6-32.7M, equal to b4 in the same game. **Pass.**
  - **Known-map identity runs:** qf1 max 34.0M over the 20 maps.
  - **rt2028_24 (64x64, unseen):** p99 32.3-32.5M (b4 32.2-32.4M). **Over the 40M bar on max:** single-turn spikes of 40.1M
    and 46.2M at seed 1000, and 54.4M and 42.5M at seed 1001.
    - Each spike is one turn by a late non-queen dragon at r112-484, not a queen turn before r100.
    - They match b4's REPLY_SEARCH budget (`REPLY_BUDGET_M 45`, hard stop at +10 = 55M).
    - b4 spikes the same way on this map (40.1M in b4 self-play, 46.3M as the base side of a UPS game). Over 40M:
      b4 2 of 24 team-games, UPS-carrying builds 9 of 12 (8 of them on rt2028_24). So UPS may make these spikes more frequent, but they stay
      inside b4's own budget.
    - The QE_KR flood itself is cheap: queen turns before r100 max 30.5-32.3M (b4 29.7-30.6M).
  - **Other unseen maps:** g2026_16 (64x64) 35.7/40.0M (b4 35.6-37.4M); rh2029_26 (64x63) 35.1/35.3M.
- **Robustness:** 12 sandbox games and the fixture, with return code 0 and no invalid/timeout/error lines. Maps: Australia,
  rt2028_24, g2026_05 (10x8), g2026_32 (x-symmetry, 12 portal edges), rs7_00 (63x27, 18 dragons, same-size look-alike)
  and g2027_22 (12x12 x-symmetry), both sides. Maxima on the small and odd maps were 4.6-29.2M.

Verdict:
- qf1 plays exactly as b4 on the 17 known maps and on Schooltime B, so seeding autoscrims are unaffected.
- On unseen maps it fixes the deterministic unknown-portal neck suicide and adds QE_KR. Pooled .544 vs b4 over 456 games.
- Open item: the rt2028_24 single-turn CPU maxima of 40-54M are above our 40M bar. They are b4's own reply-search
  budget, well under the judge's 100M.

## 12. QNO_UNKPORTAL: the queen stays off unknown portals on unseen maps (8 Oct, 15:35-17:00 EDT). Not shipped.
Hypothesis (notes/top5/DEEP_CUTLERY_OCT8.md side finding): on maps the bot never identified, the queen should never knock on
or cross a portal she doesn't know. In b4 blind self-play she crossed by r100 in 8 of 36 team-games, and all 8 died by r150.

The flag is in bot/ with default 0, gated on `amQueen() && w.neverKnown()` (`Bot::qNoUnkPortal()`):
- **1:** her explore desire is forced off, so she gets no door lure and makes no UNK_EXPLORE crossing. Her sonar knock on
  unknown portals is dropped, so her beacons are not displaced. The explore-crossing branch also checks the gate.
  Unknown portals are already kelp in `nxt`, so normal moves and sprints can't enter them. Pair-linked portals
  (UNK_SCARCE_FIX `portalUse`) and the all-lethal UNK_PORTAL_ESCAPE fallback are unchanged.
- **2:** as 1, and the queen's process also skips `scarceFixCheck`, so she never links seen pairs. Every portal is then kelp
  to her except in the all-lethal fallback.

Staging: work/qf2 = bot/ + `QE_KR 2`, `UNK_PORTAL_SIDES 2` and `QNO_UNKPORTAL 1`. work/qf2_scratch/qf2v2 is the same with
`QNO_UNKPORTAL 2`. Scripts and logs are in work/qf2_scratch/ (gitignored).

Checks (sandbox, seed 1000, full `-v` transcripts):
- **Flags off** (bot/ + the qf1 defines vs variants/qf1): Trophy, Schooltime B, rt2028_00 and rt2028_05, both sides,
  8/8 identical. Blind (NO_KNOWN_MAPS on both) Portals, Stripes, Islands and Trauma: 8/8. After the value-2 line was
  added: 12/12 again.
- **qf2 vs qf1 on the 17 server_live maps + schooltime_b/b2/b3, both sides: 40/40 identical**, max CPU 34.0M.
  - Positive control (both blind): Portals and rt2028_00 differ at the queen's turn (r13, r2). Stripes is identical.
- **CPU:**
  - Australia known: 32.6/32.7M, the same as qf1.
  - Australia blind: 35.0/35.1M, the same as qf1.
  - rt2028_05 blind: 19.9M.
- **Sandbox cache pitfall:** unswbc's judge-clang wasm cache key is the directory name plus the .c/.cpp contents. Headers
  are not part of it (`clangtool.build`, `sources()`).
  - So a stage dir that keeps its name and changes only params.hpp reuses the old wasm.
  - Every stage here had a new name or a changed main.cpp, so every build was fresh.
  - Give stage dirs a new name for each define set.

Mechanism: 10 blind head-to-head games against qf1 (NO_KNOWN_MAPS on both sides, seed 975000) on Portals, Stripes, Trauma,
rt2028_00 and rt2028_05, both sides. Counts are per team-game, from the replays (`work/qf2_scratch/mech.py`).

| | queen crossed a never-crossed pair before r100 | queen crossings before r100 | queen alive at r150 | cand result |
|---|---|---|---|---|
| qf1 (base; value-1 run / value-2 run) | 8/10 / 8/10 | 31 / 46 | 4/10 / 5/10 | |
| qf2 (value 1) | 3/10 (all pair links: Portals r72, Stripes r13/r17) | 25 | **8/10** | 8 W 2 L |
| value 2 | **0/10** | 0 | **8/10** | 7 W 3 L |

- On rt2028_00 and rt2028_05 the qf1 queen knocks and crosses at r5-18 and dies at r28-50, head-on.
  - The value-1/2 queen stays home and wins on the longer queen at r500, 4/4.
- On Portals and Stripes the value-1 games were move-for-move the same as qf1: those crossings use pair links, not explore.

Unseen strength vs qf1 (`tools/unseen_eval.py --seeds 1 --jobs 5 --sets real,realhold,blind17`):

| build | seed base | real | realhold | blind17 | pooled |
|---|---|---|---|---|---|
| qf2 (1) | 981000 | 43/80 .537 | 40/80 .500 | 35/68 .515 | 118/228 **.518** |
| qf2 (1) | 982000 | 40/80 .500 | 41/80 .512 | 33/68 .485 | 114/228 **.500** |
| qf2 (1) | both | 83/160 .519 | 81/160 .506 | 68/136 .500 | 232/456 **.509** |
| value 2 | 981000 | 45/80 .562 | 40/80 .500 | 34/68 .500 | 119/228 **.522** |
| value 2 | 982000 | 42/80 .525 | 42/80 .525 | 31/68 .456 | 115/228 **.504** |
| value 2 | both | 87/160 .544 | 82/160 .512 | 65/136 .478 | 234/456 **.513** |

Verdict:
- **Not shipped.** The bar was pooled >= .52 and blind17 >= .48 on both seed bases.
  - Value 1 fails on pooled at both seed bases (.518 and .500).
  - Value 2 fails at 982000 on pooled (.504) and on blind17 (.456).
- The flag does what it is meant to do. In the targeted games it removes the queen's knocks and explore crossings, and
  8/10 queens are alive at r150 (qf1: 4/10 and 5/10). But the broad sets show no gain beyond noise (.509 and .513 over
  456 games).
  - Most unseen games probably never put the queen at an unknown portal, so any effect is diluted.
  - These sets cannot tell whether it helps in the games where it does act.
- bot/ keeps `QNO_UNKPORTAL 0`. variants/qf1 stays the Qualifier build. No variants/qf2 was made.
