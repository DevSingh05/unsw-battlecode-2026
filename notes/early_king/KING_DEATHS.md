# King deaths and slow growth in losses vs top-13 (Sch/Por/Sli, v30-v32, 124 games from meas.json)
Scripts and pickles: scratchpad `kd/{kd,ram,ram2,safe,sp,exp,bigself}.py` (sim2 replay reconstruction). "King" = our longest dragon.
Engine note: a body is never cut. A king only shrinks by dying, splitting, or multi-step moves. Head-to-head kills both dragons, whatever their lengths.

## A. Drops (longest falls >=3 after r350): 51/74 losses (Por 25/28, Sch 15/24, Sli 11/22), but also 29/50 wins
- In 32/51 the only cause is reverse splits (king SPLIT L-2, costs 2 each; KING_ESCAPE or the trapped branch). Wins have the same rate (1.4 rsplits/game), so it is a tax, not the thing that separates W from L.
- 18/51 are real king deaths. By map, losses with a king death: Sch 10/24 (wins 1/16), Por 5/28, Sli 3/22.
- King deaths from r340 (longest >=6): losses 27, wins 5. Causes in losses:
  - 18 rammed by an enemy head (3 in wins).
  - 4 moved into an ally body through a blind portal crossing, boxed in with 0 free exits (all Portals).
  - 4 fed themselves: a fresh reverse-split child (L19-57) suicided as a feeder to its parent's stale crown (v30/v31 only, 0 in v32 with CROWN_INHERIT=5).
  - 1 trapped.
  - 0 hit kelp, 0 were cut.
- Rams (19 in losses from r300):
  - Rammers are small: median length 4-5, range 2-11. They are usually recent split children.
  - 15/19 were multi-step sprints of 2-5 steps. 2 got their extra reach by eating pearls from our feeder corpses on the way.
  - The king was being fed (>=1 feed suicide in the prior 15 rounds) in only 5/18. Nearest ally was median ~8 tiles away, length 2.
  - Every king moved 1 step on its last turn. KING_ESCAPE never produced a sprint or reverse split.
  - Geometry of that last turn (rebuilt from the replay with threat reach = min(len-1,4), 7x7 vision):
    - 8/19 had no safe step (kelp/bodies plus threatened tiles).
    - 2/19 had a safe step but took a threatened one.
    - 9/19 took a step that looked safe: 5 rammers were out of vision, 2 had pearl-extended reach, 2 unclear.
  - Exposure r300-450: on Sch losses our king has an enemy head within 4 in 18% of rounds (opponent king 9%) and 1.6 allies within 8 (opponent 2.4).

## B. Slow growth r300-450 in losses without a king death (Sch 14, Por 23, Sli 19); medians, us vs opp
- Sch: longest grows +6.5 vs +21.
  - Units at r300: 18.5 vs 45.5 (in wins 39 vs 37). We had lost the army before r300.
  - Feed suicides r300-450: 4/game (wins 16).
  - King eats 14.6 pearls (6 from our own corpses) vs opponent 22 (15).
  - Small allies within 8 tiles of the king at r350: 0.5. Median distance 24.
  - So: few feeders, and they are far away.
- Por: longest grows +20 vs +27, although our king eats more (35.6 vs 31.6).
  - The king reverse-splits 6.7x/game in r340-450 (~13 segments). 2.7 of those had 0 free exits.
  - Feed pearls leak: pearls from feed suicides go 33.5/game to other allies vs 15.6 to the king.
  - Small allies eat 26/game pearls within 4 tiles of the king.
- Sli: longest grows +22 vs +34. King eats 27 vs 38.
  - Consolidation lags: 31 units at r450 (28 of them small) vs opponent 17.
  - Feed pearls go 28 to allies vs 20 to the king.
- Code: shouldFeed() before r420 feeds only myLen <= KING_V2_FEED_LEN (3). A feeder that eats a king pearl grows to 4, stops feeding, and returns at most half of it (a death drops ceil(L/2)).
- Not the cause: king multi-step moves (median 0), king not moving, escape splits costing extra.

## Fixes (general)
1. **King safety before contact.**
   - Evidence: 18/27 king deaths in losses are enemy rams vs 3 in wins; Sch king deaths 10/24 losses vs 1/16 wins; 8/19 were cornered; 15/19 rams were sprints.
   - Change: in computeThreats (king), add +1 reach for each pearl on the enemy's path. Make the king move score avoid tiles with <=1 free exit whenever an enemy head is within reach+2. Fire tryKingEscape when the chosen tile is within reach+1, not only when bestD is already threatened (by then 8/19 had no safe tile).
2. **Keep king food for the king.**
   - Evidence: small allies eat 26/25/6.5 pearls/game within 4 of the king (Por/Sli/Sch), about as much as the king. 55-68% of feed-corpse pearls go to allies on Por/Sli.
   - Change: non-king dragons within ~4 of the king in feedPhase() should give pearls ~0 value. Also let a feeder that grew stay a feeder: raise the length cap in shouldFeed() before r420; KING_V2_FEED6_ROUND=380 exists in bot/ but was not in v30-v32.
3. **Crown and reverse-split hygiene.**
   - Keep CROWN_INHERIT on. All 6 fresh-child self-feeds (239 segments) were in losses, 0 in wins, 0 in v32.
   - Caution: bot/params.hpp now defaults CROWN_INHERIT 0, KING_CONSENSUS 0, ECHO_EXIT_HOLD 0 (v32 had 5/1/15). Make sure the build still sets them.
   - Only reverse-split the king when an enemy threat is real, not when it is boxed in by its own feeders (Por 2.7/game with 0 exits). This does not separate W from L; it is growth on every map.
