# cheji bt (team 70): what generalises to unseen maps (sprint study, 30 Sep ~21:15 UTC / 17:15 EDT)

Builds on notes/top3/cheji_bt/REPORT.txt, which used 40 games from the morning; this note does not redo that work.
Script: notes/top3_sprint/cheji_measure.py. Replays: scratchpad t3/cheji/ (11 games).
Games: 8 cheji games against peers from 20:55-21:11 (5 against 3.14159265 at elo 2108, 3 against "forgot to mention" at 2086), plus our games 742884-6 (Devil, Trophy, PD).

## 1. Head-to-head in our 200-battle window (15:02-21:08 UTC today, all unranked, 6 battles)
We are 12-19 (39%). The morning study had us at 8/34, so this is better.
- Default 0-4, Devil 1-4, Trophy 1-3, Queen of Spades 0-2
- Autarky 1-1, Schooltime 2-2, Slithery 1-1, Trauma 1-1
- Portals 2-0, Prisoners Dilemma 3-1

We lose the small and medium swarm maps, where the game is decided by early elimination. The unseen sprint maps will include maps like these.
Note: the 3.14159265 team beat cheji 3-2 in ranked just now (Trauma, Trophy, Autarky). They are worth a separate look.

## 2. Per-game numbers
Format is units/longest/total, then cheji vs the opponent.
- Devil 742884 (we lose, eliminated at r113). r50: 21/5/53 v 13/4/31. r100: 48/4/110 v 5/3/11.
  - Splits before r100: 84 v 35. Sprints: 81 (61 pearls eaten) v 2. Head-on kills: 13 v 8.
  - Our deaths: 14 HitSelf at L2-3, all before r100. Cheji's deaths: 0 HitSelf and 38 NoValidAction.
- Trophy 742885 (we lose at r141). r100: 45/4/104 v 5/3/13. Splits before r100: 63 v 20. Sprints: 32 v 5. Head-on kills: 19 v 10.
- PD 742886 (we win at r73). Cheji opened with 12->8+4 and 8->4+4 splits, lost 12 units in head-ons and never recovered. Sprints: 9 v 4.
- Peers, round-limit games (Trauma x2, Slithery, Portals). Cheji units at r200/300/400: 44/63/8, 63/64/11, 22/22/2, 47/61/12.
  - Longest stays at 4-6 until r300, then 16-35 at r400 and 24-54 at the end.
  - Cheji's deaths are NoValidAction (voluntary feeds, 229-495 per game) and head-ons. HitWall and HitSelf are both 0.
- Sprints per game against peers: Trauma 130 and 144, Slithery 763 (487 of them eat), Autarky 55, Portals 59. Peers: 1-51.
- Head-on kills: cheji wins the count in 10 of 11 games (Slithery 62 v 45, Autarky 41 v 36, Portals 34 v 18).
- Portal traversals (approximate, measured as head jump > steps): Portals 699 v 479. Similar elsewhere.
- How cheji loses: to 3.14159265 on Trophy (eliminated r166, 0 v 56 units) and Autarky (eliminated r404, a swarm of 48-units). It also loses the round-limit king race to a bigger single king (Trauma 33 v 48, Slithery 54 v 60, Portals 24 v 30).

## 3. Distinctive general behaviours (map-independent)
**A. Opening split rate and swarm width.**
- Every L4+ becomes 2+2 immediately (children are 2 in 90% of pre-r100 splits).
- 60-85 splits before r100 on small maps, giving 45-48 units by r100 on Devil and Trophy against our 5.
- Head-on kills are traded freely: 38-58% of the head-ons cheji initiates (Devil 5/13, Trophy 11/19) are equal-length trades (both die). Being wider, it wins the attrition.
- We split 20-35 times before r100, and 14 of our 36 Devil deaths are L2 HitSelf, meaning we trap ourselves.

**B. Constant cheap 2-step sprints to eat.**
- L3-4 dragons sprint 2 steps onto pearls whenever it pays: 44 (2,L3) sprints in 113 rounds on Devil, 763 per game on Slithery.
- Ours: EAT_SPRINT=0 (params.hpp:448-459). We sprint 2-5 times per game, only to ram.

**C. Wave consolidation at r300-330.**
- Stays wide at the unit cap (longest 4) until about r300, then drops from 60+ to 2-12 units by r400 using NoValidAction feeds next to a longer ally.
- On unseen maps v35 uses the UNK_KING path (main.cpp:838-855): king seed r250, feed r300, SPLIT_STOP_ROUND 350.
- But LATE_SPLIT_ROUND=450 still applies for L<=5, because LATE_SPLIT_KING_MAPS=0 (params.hpp:970, main.cpp:141-143, split gate main.cpp:3820). So we keep splitting small dragons until r450 on unseen maps.

## 4. Code pointers / candidate flags (untested; need a server A/B)
- **A.** Opening/early split cap and the anti-self-trap for L2: split gate at main.cpp:3820 and the RP.splitStopRound logic. The HitSelf deaths come from trapped L2 dragons (see notes/19 on Devil).
- **B.** EAT_SPRINT family: params.hpp:448-459, main.cpp:2886-2942 and 3659-3660. Try a narrow version (L3-4, 2 steps, only with a pearl on the path and a step-safe check).
- **C.** In the UNK block, set RP.lateSplitRound = RP.splitStopRound (or 330). It is one line in main.cpp:~850 and changes nothing on known maps.
