# 22: How the top teams beat us on Autarky (29 Sep 2026)

**Question.** Against top-10 teams we lose Autarky badly (1/7 in the last hour, 3/16 against teams rated ≥1940 since v28). What do they do that we don't, and which parts of it carry over to unseen maps?

**Short answer.**
1. **Our pocket pump makes no length.** A diver goes in at L2 and comes out as an L2 child, and the L3 parent dies. Net per cycle is **−0.2** (79% of our pump parents die at L3).
   - The top teams split at the tip: in at L2 → out at L3, or in at L3 → out at L4, with the L2 parent dying into kelp (93% die at L2). Net **+0.58** per cycle against us, +0.2 to +0.6 elsewhere.
   - This costs us about 6 length by r50, the whole r50 gap (37 v 44). In our wins it costs about 18 length per game (73 cycles × −0.25).
   - The flag that fixes it already exists (`PUMP_TIP_SPLIT`, off). Re-run on 30 real in-pocket L4 splits, it changes 26/30 decisions to "keep eating to the tip". It needs one refinement (§6 F1).
2. **We lose the pocket mouths, and then we're shut out.** On Autarky the 4 dead-end pockets hold essentially all the fast food (8 gap-(1,1) tiles plus 6 gap-(1,5)/(1,10) tips, about 10 pearls/round). The rest of the map spawns about 0.7 pearls/round.
   - From r20 our heads drift away from the mouths: 3.7 → 2.2 → 0.9 heads within 3 of a pocket at r0-20, r60-80 and r140-160. The enemy's go 3.0 → 5.7 → 7.9.
   - Our head-rounds in the barren side zone are 55% (r0-59) and then 77% (r60-199), against 29% and 43% for them.
   - While a pocket is idle, an enemy head sits within 3 of its mouth **85%** of the time, and `pocketWorthPumping()` vetoes every such entry.
   - Result, r60-199: pocket eats **18 v 135**, pocket dives **5.8 v 37**. They also take our *home* pockets: 53 of their 135 pocket eats in r60-199 are in our two pockets.
3. **The snowball.** With more length they split more (normal 2-child splits r60-199: 73 v 30), so they have more heads. With more heads they are locally ahead when trades happen: we were outnumbered in view in 72% of the rams that killed us.
   - Head-ons are always 1 unit for 1 unit, but the denser side eats the corpses: open-field corpse eats r60-199 are 68 v 31.
   - Units go 16/17 (r50) → 16/26 (r100) → 10/43 (r200). **62% of these losses are eliminations** (mean end r371, earliest r182).
4. **Endgame (5 round-limit losses).** By then we have 2-10 units. Our king only forms after r450 (Autarky king seed r380, plus `LATE_SPLIT_ROUND` 450). Final longest 12-21, against 16-92.
   - Two of these games were close (12 v 16 and 14 v 17), with 19-20 units and 43-47 total length at r420 but a longest of only 3.

**What carries over to unseen maps.** Point 1 applies to any map with a dead end and fast tiles: 22/40 `maps/gen` and 22/40 `maps/genhold` maps have pockets. PD, Portals and Slithery show the same L3 pump deaths (notes/19). Point 2 is a valuation problem: we treat a tile that respawns every round as a one-off half-pearl, so our dragons drift to areas with more "stock" and less "flow". Point 3 follows from 1 and 2 and needs no separate fix.

---

## 1. Data and tools

**Games.**
- **Ours (v28 live):** 37 Autarky games, from `replays/auto/games` (7) and `replays/v28` (30). Our side is taken from the ledger `side`.
  - `us-L-strong`: 13 losses vs Elo ≥ 1940 (calc, Sponge, forgot to mention ×2, 中国必须人能飞, 3.14159265, SSS ×2, cheji bt, Peanut Butter, Stockfish, bread first search ×2).
  - `us-W-strong`: 3 wins vs Elo ≥ 1940 (Cutlery, 中国必须人能飞, Stockfish).
  - `us-W-weak`: 15 wins vs Elo < 1940. `us-L-weak`: 6 losses vs Elo < 1940.
- **Top teams:** 31 fresh Autarky games of the current top-10 (29 Sep, 8 of them top vs top), downloaded to `notes/replays/autarky/` with GET only. Plus 19 older top-10 Autarky games from `notes/replays/{top10b,midgame}`.
  - Groups: `top-W` (41 team-games), `top-L` (22), `topopp-L` (28).
- **Pockets:** tiles removed by leaf pruning of the kelp graph (as in notes/14). Autarky has four: x=18 and x=35, y 0-2 and 15-17, plus the tips (19,0), (19,17), (34,0), (34,17). The entry tiles are (18,3), (18,14), (35,3) and (35,14).
  - Each team's two **home** pockets are the ones at its L14 starter's column.
- **Zones:** "mouth" = within Manhattan 3 of a pocket tile; "centre" = x 19-34; "side" = the rest. The side is about 2/3 of the tiles but holds only the six 6×6 gap-(1,500) boxes.

**Scripts** (`notes/tools/autarky/`; run from the project root; read-only over replays):

| script | what it does |
|---|---|
| `fetch.py` | list and download top-10 Autarky replays (GET, 1.2 s apart) |
| `collect.py` | per (game, team) metrics, written to `games.pkl` |
| `report.py [list tl eats splits deaths pump sprint pockets rams zone ledger pergame]` | the tables below |
| `windows.py GAME [W r0 r1]` | per-window game view |
| `board.py GAME ROUND [x0 x1 y0 y1]` | ASCII board |
| `trace.py GAME TEAM` | pump episode traces |
| `opening.py GAME` | starter moves in the opening |
| `avgwin.py GROUP` | averaged curves |
| `idle.py` | idle-pocket capacity |
| `entryrisk.py` | child fate by enemy distance at entry |
| `whynot.py BIN` | re-runs the v28 binary on non-entries at the mouth |
| `tipcheck.py BIN0 BIN1` | re-runs v28 with and without `PUMP_TIP_SPLIT` on real in-pocket splits |

Binaries are built in the scratchpad with `c++ -std=c++20 -O2 variants/v28/main.cpp`.

Caveat: `sim2` counts the L14 starters one segment long until their first split (notes/19). Children and death causes are unaffected.

---

## 2. Timelines (units / total length / longest, means; eliminated = 0)

| group | n | r50 | r100 | r200 | r300 | r400 | r500 | eliminated |
|---|---|---|---|---|---|---|---|---|
| **us-L-strong** | 13 | 15.8 / 37 / 3.4 | 15.9 / 37 / 3.2 | 10.4 / 24 / 3.0 | 6.7 / 16 / 2.0 | 6.4 / 16 / 1.5 | 2.4 / 17 / 5.9 | 62% (mean end r371) |
| **their side** | 13 | 17.2 / 44 / 5.5 | 26.2 / 64 / 4.1 | 43.1 / 104 / 4.3 | 51.6 / 138 / 6.8 | 42.0 / 128 / 15.5 | 36.3 / 131 / 22.6 | |
| us-W-strong | 3 | 19.3 / 43 / 3.3 | 21.3 / 49 / 3.3 | 28.0 / 63 / 3.3 | 22.7 / 55 / 3.7 | 31.0 / 72 / 3.7 | 11.0 / 82 / 21.3 | |
| us-W-weak | 15 | 19.3 / 44 / 3.1 | 23.8 / 56 / 3.3 | 34.6 / 81 / 3.5 | 47.5 / 114 / 3.9 | 53.9 / 133 / 5.3 | 44.9 / 130 / 11.7 | |
| top-W | 41 | 17.2 / 42 / 3.9 | 23.4 / 57 / 3.7 | 38.7 / 94 / 4.4 | 43.1 / 109 / 4.8 | 41.1 / 115 / 8.8 | 33.9 / 108 / 17.1 | |
| topopp-L | 28 | 11.6 / 30 / 4.7 | 10.6 / 27 / 4.3 | 7.0 / 19 / 3.4 | 5.4 / 15 / 2.3 | 4.0 / 13 / 2.2 | 0.6 / 7 / 4.4 | 75% |

**20-round curves, strong losses** (`avgwin.py us-L-strong`; us / them):

| window | units | total | pocket eats | open spawn | corpse | our heads within 3 of a pocket |
|---|---|---|---|---|---|---|
| r0-20 | 15.1 / 14.0 | 34 / 36 | 13.2 / 12.5 | 4.4 / 3.6 | 0.8 / 1.5 | 3.7 / 3.0 |
| r20-40 | 15.7 / 16.2 | 36 / 41 | 11.0 / 14.0 | 4.5 / 3.6 | 2.7 / 3.5 | 3.5 / 4.1 |
| r40-60 | 15.5 / 18.5 | 36 / 45 | 8.4 / 15.8 | 4.2 / 5.2 | 4.7 / 4.6 | 2.7 / 4.5 |
| r60-80 | 16.2 / 23.2 | 38 / 57 | **4.8 / 17.2** | 4.2 / 6.5 | 4.1 / 6.1 | **2.2 / 5.7** |
| r100-120 | 14.2 / 30.2 | 33 / 72 | 3.7 / 19.2 | 4.6 / 7.6 | 4.5 / 10.9 | 1.9 / 7.0 |
| r140-160 | 13.0 / 37.7 | 31 / 92 | 1.3 / 22.5 | 4.4 / 7.7 | 5.2 / 8.5 | 0.9 / 7.9 |
| r180-200 | 10.4 / 43.1 | 24 / 104 | 1.8 / 18.3 | 3.0 / 8.5 | 5.5 / 13.2 | 1.0 / 8.0 |

The opening is identical: both bots peel 2-long children off the L14 in r0-4 (`opening.py 602421`). The game is even until r20. From r20 to r60 the pump gap shows (below). From r60 the mouths are theirs.

In our weak wins the same curves stay up: 3-4 heads at the mouths, pocket eats 9-13 per 20 rounds, and units 15 → 35 by r200.

---

## 3. Where the length comes from (per game)

**Eats by phase** (pocket, including corpse pearls inside pockets / open spawn / own corpse / enemy corpse):

| group | r0-59 | r60-199 | r200-349 | r350-500 | total |
|---|---|---|---|---|---|
| **us-L-strong** | 33 / 13 / 5 / 3 | **19** / 28 / 19 / 12 | 5 / 22 / 15 / 10 | 5 / 20 / 14 / 7 | 229 |
| **their side** | 42 / 13 / 6 / 4 | **136** / 54 / 45 / 23 | 108 / 53 / 59 / 19 | 28 / 24 / 42 / 8 | 663 |
| us-W-weak | 43 / 17 / 4 / 3 | 76 / 51 / 29 / 20 | 79 / 59 / 37 / 22 | 31 / 31 / 39 / 12 | 551 |
| top-W | 32 / 15 / 9 / 6 | 88 / 55 / 35 / 21 | 60 / 38 / 35 / 11 | 24 / 21 / 29 / 4 | 482 |

**Length ledger, r60-199** (`report.py ledger`; + eats, − length of the dragons that died):

| group | +pocket | +open spawn | +own corpse | +enemy corpse | −pocket deaths | −head-on deaths | −other | **net** |
|---|---|---|---|---|---|---|---|---|
| **us-L-strong** | 18.5 | 28.1 | 19.3 | 12.2 | 17.3 | 68.3 | 3.5 | **−11** |
| **their side** | 135.5 | 54.4 | 44.9 | 22.7 | 95.3 | 71.2 | 29.2 | **+62** |
| us-W-weak | 76.4 | 50.7 | 28.6 | 20.4 | 70.7 | 65.2 | 6.4 | +34 |
| top-W | 88.3 | 54.7 | 34.5 | 20.7 | 64.2 | 61.1 | 18.5 | +54 |

- **Head-on losses are the same for both sides** (68 v 71). Every head-on kills one of each, so rams don't create the unit gap directly.
- The gap is **pocket net** (+1 v +40) plus the **corpse race** (31 v 68 corpse pearls). There is also a smaller open-spawn gap (28 v 54): they hold the centre, where the scattered slow tiles are.
- **Pocket net ≈ 0 for us even when we hold the pockets:** weak wins show +76 eats against −71 in-pocket deaths. That is the pump bug (§4).

**Splits** (normal 2-child in open / 2-child with ≤1 exit / tip split k=L−2, per game):

| group | r0-59 | r60-199 | r200-349 |
|---|---|---|---|
| us-L-strong | 5 / 21 / 0 | 17 / 12 / 0 | 14 / 4 / 0 |
| their side | 11 / 10 / **12** | 44 / 29 / **37** | 37 / 18 / **33** |
| us-W-weak | 6 / 26 / 0 | 27 / 40 / 0 | 32 / 40 / 0 |

Split parent length: ours is 94-97% L4. Theirs is 59% L4, 24% L5, 13% L6; the L5-6 splits are tip splits.

---

## 4. Pump cycles (a head enters a pocket tile → split or death)

| group | dives/g | entry L | split L | child | **net/cycle** (child − entry) | parent dies at L2 / L3 | rounds entry→split | net/g |
|---|---|---|---|---|---|---|---|---|
| **us-L-strong** | **18.5** | 2.20 | 4.00 | 2.00 | **−0.20** | 50 / **190** | 3 (78%) | −3.6 |
| **their side** | **85.5** | 2.77 | 5.47 | 3.42 | **+0.58** | **1015** / 62 | 4 (81%) | +49.5 |
| us-W-weak | 73.5 | 2.23 | 4.00 | 2.00 | −0.25 | 244 / 834 | 3 | −18.3 |
| top-W | 60.3 | 2.59 | 4.96 | 2.91 | +0.20 | 2035 / 295 | 4 (60%) | +12.1 |
| top-L | 28.8 | 2.70 | 5.08 | 3.06 | +0.35 | 444 / 188 | 4 | +10.0 |

**Cycle shapes** (entry L, split L, child, parent death L), share of cycles:
- **Ours:** (2, 4, 2, 3) 78%; (3, 4, 2, 2) 18%.
- **Theirs vs us:** (2, 5, 3, 2) 40%; (3, 6, 4, 2) 33%; (3, 4, 2, 2) 11%.

**Our cycle (trace, 565513 diver 91, r105-110):**
- The diver enters (18,2) at L2. It eats (18,1) and (18,0) and reaches L4.
- The **normal split branch fires**: `SPLIT 2` at (18,0), 1 exit, and an L2 child leaves.
- The L2 parent steps to the tip (19,0), eats, reaches L3, and dies HitSelf. Its 2 corpse pearls land on hot tiles that would have spawned anyway.

**Their cycle (e.g. calc 500988 id31 in notes/14):** L2 in → eat, eat, eat to the tip (L5) → `SPLIT 3` → the L3 child leaves facing out, and the L2 parent dies into kelp (1 pearl).

**Pearls eaten per cycle are the same (about 2.7-2.8).** The difference is only *where the split happens*: one tile before the tip (ours) or at the tip (theirs). That is worth +1 length per cycle, and from r0 it costs us 6-7 length by r50 in strong games.

The top teams' own −1 cycles, (3, 4, 2, 2), come when the pocket was half-eaten by a previous diver, so they don't always hit +1 either.

**Risk of diving near enemies** (`entryrisk.py`; child dies within 8 rounds of the split):

| nearest enemy head at entry | top-W: child rammed / net | their side vs us | ours (weak wins) |
|---|---|---|---|
| ≤ 2 | 23% / −0.18 | 27% / −0.27 | n=2 |
| 3-4 | 23% / −0.28 | 23% / −0.10 | 11% / −0.49 |
| ≥ 5 | **2.7%** / +0.14 | 4.6% / +0.34 | 3.3% / −0.32 |

The top teams dive with an enemy head within 4 only 13% of the time, the same as we do (9%), and those dives lose even for them. **Our "no enemy head within 3" veto is right. Don't relax it.** The fix is to keep enemies away from the mouths by being there, not to dive under their noses.

---

## 5. Pocket access, presence and rams

**Home and away pocket eats (per game; `report.py pockets`):**
- r60-199 strong losses: we eat 17.8 in our home pockets and 0.7 in theirs. They eat 82.9 in their home pockets and **52.6 in ours**.
- r200-349: we eat 5.4 / 0; they eat 60 / 48.
- In our 3 strong wins we held our home pockets (60, then 49) and they got almost nothing away.

**Idle capacity** (`idle.py`, r60-349): pockets have no head inside 55-62% of pocket-rounds in *every* group, including the top teams' games. Capacity is not the limit; the queue at the mouth is.

| while a pocket is idle | own L≤3 head within 3 / 6 / 10 of the mouth | enemy head within 3 of the mouth | own head closer than the enemy's |
|---|---|---|---|
| us-L-strong | 25 / 38 / 54% | **85%** | 18% |
| us-W-weak | 53 / 74 / 88% | 60% | 45% |
| top-W | **67 / 85 / 95%** | 33% | 67% |

**Why our dragons at the mouth don't go in** (`whynot.py`, v28 binary re-run on 40 real non-entries at a mouth tile in strong losses):
- 19: the first pocket tile holds our own just-born L2 child's neck, so we wait in our own queue.
- 11: `POCKET enemy` (enemy head within 3), candidate score −15 to −23.
- 10: the bot says YES but the replay differs. 9 of these 10 are from one game (reconstruction or memory mismatch).

**Why our dragons aren't at the mouth.** `pearlValue()` gives an unseen gap-(1,1) tile at most 0.5, the same as a slow tile unseen for about 250 rounds. It then multiplies by 0.25 if any other head (ally or enemy) is closer, and discounts by γ = 0.82 per step.
- A full pocket 8-11 steps away is worth about 0.75 score points, less than the 0.3 straight-ahead bonus plus noise.
- Nothing pulls a free L2 back to the only real food source. The side zone's 6×6 slow boxes look richer (36 tiles × up to 0.5 each) than they are (0.14 pearls/round per box, against about 3/round per pocket).

**Rams against us** (`report.py rams`; enemy moved into our head):

| group | per game | victim L / killer L | within 3 of a pocket | we were outnumbered in view | even |
|---|---|---|---|---|---|
| us-L-strong | 39.8 | 2.66 / 2.88 | 21% | **72%** | 17% |
| us-W-weak | 17.3 | 2.56 / 2.81 | 19% | 59% | 20% |
| top-W (as victims) | 18.5 | 2.82 / 2.61 | 20% | 47% | 27% |

Rams happen all over the map, not at the mouths. They follow local numbers. Our own rams in strong losses (8.5 in r60-199 against their 17.8) are limited by `RAM_GUARD` (units ≥ 8, allies ≥ enemies + 1).

**Deaths per game, r60-199** (we rammed / rammed by enemy / self / wall + no valid action / in pocket):
- us-L-strong: 8.5 / 17.8 / 7.0 / 0 / 6.3.
- Their side: 17.8 / 8.5 / 10.6 / 38.8 / 46.1. Their "wall/nva" deaths are the L2 tip parents.
- Our pump parents die HitSelf (into their own neck), so our "self" column is the pump.

**Sprints:** they make 0.8 eat sprints and 3-4 escape or "other" sprints per phase; we make 0 of either (all our sprints are rams). This is small (notes/14).

---

## 6. King / endgame

Only 5 of the 13 strong losses reach r500:

| game | us r400 / r450 / r500 (units u, longest L) | them r400 / r450 / r500 |
|---|---|---|
| 608206 Sponge | 35u 5L / 16u 17L / 9u **18L** | 9u 39L / 6u 48L / 2u **58L** |
| 608231 中国必须人能飞 | 12u 3L / 14u 8L / 10u **21L** | 9u 37L / 3u 49L / 1u **57L** |
| 607992 3.14159265 | 17u 3L / 19u 3L / 8u **12L** | 30u 6L / 32u 8L / 12u **16L** |
| 602421 SSS | 5u 3L / 3u 8L / 2u **12L** | 20u 60L / 11u 73L / 4u **92L** |
| 590350 Stockfish | 13u 3L / 5u 7L / 2u **14L** | 42u 5L / 27u 12L / 26u **17L** |

- The top kings start at r300-350 (Sponge 10 → 18 → 39 at r300/350/400).
- On Autarky our king declares from r380 (`PM_AUT_KS`), and `LATE_SPLIT_ROUND` 450 keeps every dragon ≤ 5 splitting. So in 607992 we sat at 19-20 units and 43-47 total with a longest of 3 until r450, and lost 12 v 16.
- This is a second-order problem: the first three rows are lost on units long before r400. It is worth a cheap per-map test (§7 F4).

---

## 7. Fixes (new flags, default 0; code locations in `bot/main.cpp` = v28 + off flags)

### F1 `PUMP_TIP_SPLIT=1` + new `PUMP_TIP_DEADEND` (general; highest confidence)

**Where.** `decide()`, the splitting block (~line 2507-2545: `holdTile`, the split-size branch).

**Existing flag.** With `PUMP_TIP_SPLIT=1` the bot keeps eating while a pearl or a gap-(1,1) tile lies ahead in a dead end. `tipcheck.py` on 30 real in-pocket L4 splits:
- v28 (flag off) reproduces `SPLIT 2` in **30/30**.
- The flag build plays `MOVE` deeper in **26/30** and still splits at the 4 tip tiles.

**Gap.** On Autarky the tip tiles (19,0), (19,17), (34,0) and (34,17) are gap (1,5)/(1,10), not (1,1). With no visible pearl on the tip, `holdTile` stays −1 at (18,0) with L5. Then the split fires with `exits == 1` (the tip counts as an exit), so k = 2 again, and the L3 parent dies at the tip. **Count a free neighbour as an exit only if it leads somewhere:**

```cpp
// params.hpp
#ifndef PUMP_TIP_DEADEND   // 1: a neighbour that is itself a 1-2 tile dead end is not an exit when sizing a pump split
#define PUMP_TIP_DEADEND 0
#endif
// decide(), inside `if (PUMP_TIP_SPLIT)` of the split-size block
int exits = 0;
for (int d = 0; d < 4; d++)
{
    int t = step(myHead, d);
    if (t < 0 || (occId[t] >= 0 && freeT[t] > 1))
        continue;
    if (PUMP_TIP_DEADEND)
    {
        double pp; int ar;
        bfsFrom(t, pp, ar, 4);          // area counts tiles we reach first; a tip has 1-2
        if (ar < 3)
            continue;                   // stepping there only goes deeper into the pocket
    }
    exits++;
}
if (exits == 0 && tailHasExit(myLen - 2))
    k = myLen - 2;                      // child takes L-2 out; a 2-long head stays and dies
```

(`bfsFrom` overwrites `bfsDist`, and the candidate loop recomputes it per candidate, so this is safe here.)

**Also:** allow the hold at `myLen == 4..6` even when the next tile is a gap ≤ `POCKET_FAST_GAP` pocket tile whose `spawnAt` is ≤ 1 round away. That covers the tips on unseen maps with `gapSeen`.

**Expected effect.**
- Net per cycle moves from −0.2 to about +0.5-0.8. With 18 (strong losses) to 73 (weak wins) cycles per game, that is **+10 to +55 length per game**.
- r50 total rises about +7 in strong games, which closes the gap at r50.
- The children come out at L3-4, so each re-dive at L3 or a quick 2+2 split adds units (their pipeline).
- The same fix applies to the L3 pump deaths on PD, Portals, Slithery and unseen pocket maps (notes/19: 34, 116 and 188 per game).

**Mechanism check** (server A/B on Autarky vs peers):
- Pump parent death length should go from 79% L3 to ≥ 80% L2 (`report.py pump`).
- Net per cycle should be > 0.
- Pocket net (pocket eats − in-pocket death length) should go from +1-6 to +25 or more.

### F2 `HOT_PULL` (general; the presence fix)

**Where.**
- A new member `std::vector<int> hotMouth`, filled at map identification (and refreshed when `gapSeen` learns a fast tile on unknown maps).
- A target pick before the candidate loop in `decide()`, and one term inside the loop next to the `feeding && target` pull (~line 2655).

```cpp
// params.hpp
#ifndef HOT_PULL            // score per BFS step towards the nearest free hot-pocket mouth, for L<=3 (try 0.6)
#define HOT_PULL 0.0
#endif
#ifndef HOT_PULL_RANGE
#define HOT_PULL_RANGE 14
#endif
// once per map: leaf-prune the static graph (as pockets.py), keep components holding a tile with
// gmax <= POCKET_FAST_GAP (or gapSeen <= POCKET_FAST_GAP), store their entry tiles in hotMouth.
// decide(), before scoring:
int hotTarget = -1;
if (HOT_PULL > 0 && myLen <= 3 && !feeding && !iAmKing())
{
    int bestD = HOT_PULL_RANGE + 1;
    for (int mt : hotMouth)
    {
        int dd = wrapDist(myHead, mt);
        if (dd >= bestD) continue;
        int alliesAt = 0;
        for (auto& o : segs)
            if (o.head && o.id != w.myId && o.team == w.myTeam && wrapDist(o.tile, mt) <= 2)
                alliesAt++;
        if (alliesAt >= 2) continue;       // enough of us queued there already
        bestD = dd, hotTarget = mt;        // an enemy head there does NOT cancel the pull: presence is the point
    }
}
// candidate loop, after bfsFrom(t, ...):
if (hotTarget >= 0 && !pump)
    score -= HOT_PULL * std::min(bfsDist[hotTarget], HOT_PULL_RANGE);
```

- `pocketWorthPumping()` keeps its enemy veto: F2 brings us *near* the mouth, not into a guarded pocket.
- The pull competes with `SMALL_THREAT_PEN`, so dragons still sidestep enemy reach.

**Evidence.**
- Our mouth presence falls from 3.7 to 0.9 heads, theirs rises from 3.0 to 7.9, and pocket eats follow (§2).
- In weak wins we keep 3-4 heads at the mouths and win the pockets.
- Top teams keep an own small head within 6 of 85% of idle mouths; we manage 38% in strong losses.

**Expected effect.** It stops the side-zone drift: head-rounds on the side from 77% toward the top teams' 43-51%. Pocket dives in strong games from 5.8 toward 20-30 in r60-199. More corpse share because of more local numbers.

**Risk.** Clumping at mouths feeds enemy rams if we are the thinner side. The cap of 2 allies per mouth limits this.

**Mechanism check.** `avgwin.py` mouth-heads column ≥ 3 through r200. `idle.py` "enemy head within 3 while idle" should fall from 85% toward 50%.

### F3 `HOT_VALUE` (general, smaller alternative or complement to F2)

**Where.** `pearlValue()` (~line 1029).

**Change.** For tiles with `w.gmax[t] > 0 && w.gmax[t] <= 2` (or learned `gapSeen <= 2`):
- use `v = max(v, HOT_VALUE /*0.9*/)` for an unseen tile;
- apply the "someone closer" discount as `v *= 0.6` instead of 0.25, since the tile refills every round and another head takes one pearl, not the stream.

**Why.** It is a flow-versus-stock fix inside the existing valuation. It is cheaper than F2 but weaker, because γ = 0.82 still makes anything beyond 8 steps worthless. Test F2 first.

### F4 `PM_AUT_KS` 380 → 320 (Autarky only; cheap)

- It lets a king declare while `LATE_SPLIT_ROUND` still splits the small dragons.
- It only matters in round-limit games (5/13 strong losses, 2 of them lost by 4 and 3 length).
- Pair it with the existing notes/16 `FEED_EAGER` idea if that is ever built.

### Not recommended

- **Relaxing the "enemy within 3" pocket veto.** Dives with an enemy head within 4 lose the child to a ram 23% of the time and net negative even for the top teams (§4).
- **Mouth guarding / killing their divers.** Head-ons within 3 of a pocket are about 20% of rams for every group, with no edge (notes/14 agrees).
- **More ram aggression.** Head-ons are 1:1 in units. The corpse race follows local numbers, which F1 and F2 address. `SMALL_SPRINT_THREAT` (the timid direction) was already rejected at 0.20.

---

## 8. Test plan (ask before server games)

1. **F1 alone** (`-DPUMP_TIP_SPLIT=1 -DPUMP_TIP_DEADEND=1`).
   - Server A/B: 10 peers × Autarky plus 10 top-15 × Autarky.
   - Judge on mechanism first: pump parent death L2 share, net per cycle, pocket net, total at r50/r100.
   - Then check the unseen suites for regressions on pocket-free maps. It should not fire there (no dead ends with food).
2. **F1 + F2** (`HOT_PULL=0.6`) with the same batch. Judge on mouth heads, pocket dives vs strong, and units at r100/r200.
3. **F4** only after 1-2, on Autarky round-limit games.

Self-play can't show F2: both sides would have it. F1's gain shows in self-play only as symmetric growth, so it needs real opponents.
