# Late king growth r350-500 in round-500 losses (v34/v35 vs Stockfish, 3.14159265, PPP, cheji, Cutlery)
Data: 148 API games 30 Sep 07:35 to 1 Oct 04:19 (includes the Sprint PPP Bo7). 72 went to r500: 37 L, 35 W. 42 more losses were eliminations and are excluded.
Every replay was rebuilt with sim2. Scripts: scratchpad q/kan*.py. "Feed" = a reverse-into-neck death that had a free exit, within 4 tiles of our longest dragon, with that dragon >= L+2.
## Where the gap comes from (37 losses, medians, us/them)
- Longest: r300 5/15, r350 12/25, r400 19/33, r450 28/42, r500 27/52. Per game, final gap is 21 and the r350 gap is 8, so about half of the gap already exists at r350.
- Growth r350-500: longest +14/+25. Final king +25/+46. Window gap is >0 in 26/37 games. Adding +5 to our king flips 6/37 losses, +8 flips 9, +10 flips 13.
- King eats in the window (longest at each eat): 24.2/31.6 per game. Natural spawns are similar (8.6/7.9). The difference is own-corpse food: ours 13.4 from neck feeds, theirs 21.3 (6.4 neck + 14.9 NoValidAction feeds; they feed by passing).
## Feeding: we give as much food as they do, but our king eats less of it
- Near-king feeds per game: us 14.9 (49.5 length, 27.5 pearls dropped). Them 12.3 (45 length, 25.3 pearls).
- Share of dropped pearls our king eats: **0.39**. Theirs: 0.61 (NVA) and 0.52 (neck). Other allies take 50% of ours (13.8 pearls/g) against 32-43% of theirs.
- By distance: dk1-2 feeds (5.5/g) give the king 0.50 of the pearls. dk3-4 feeds (9.5/g, the KING_V2_LOOSE path) give it 0.37, and allies take 0.53.
- 10.4 of our 14.9 feeds/g happen within 2 rounds of another feed. The thieves are mostly length 2-3 (188+150 of 512), i.e. queued feeders. Half of them later feed too, so a stolen pearl comes back at about 50%. The king eats with a lag of 2-4 rounds.
- Wins vs losses (us): near-king feeds 23.7 vs 12.8/g. Small units within 10 of the king 6.5 vs 4.3 (out of 32 vs 20.5). Enemy head within 4 of our king in 8% vs 19% of rounds, and the enemyNear gate blocks feeding then.
## Other parts of the task (losses)
- Our deaths r350-500: 126/g carrying 339 length. Only 15/g (15% of the mass) fed the king. Theirs: 112/g, about 14% of mass. Most mass on both sides is lost far away: our median unit is 18 tiles from the king (19 for theirs), and 8% of units are within 6.
- A further 18/g voluntary neck deaths happen more than 4 tiles from the king, next to a bigger non-king ally (about L12 vs king L32). Allies eat 0.91 of those pearls. I could not check whether these come from shouldFeed (a lesser kingId getting past KC_FEED_FRAC) or from fallback moves. That needs a debug-log run.
- Unused mass at r500 (non-king): us 8 units / 52 length (2nd longest 14). Them 12 units / 81 length (2nd 17). It is no worse than theirs, and our L7+ non-king dragons are about 17 tiles from the king, so the reserve and the merge round are not what binds.
- Unknown maps (UNK_KING, feedStart 300, reserve 14->3): only 4 losses, all to PPP in the Sprint. King r300 8.5/23.5, r350 21/34. PPP made 0 feeds and won on early growth and mass (r500: 37 units, 216 spare length). We were down to 7.5 units at r500, so the shrinking reserve was not the limit. UNK_KING_FEED=300 is not shown to be the problem. Local SEED200/FEED250 tested neutral (.513, journal).
## Biggest lever: how much of each feed the king eats (main.cpp:3606-3656, KING_V2 feed block)
- KING_V2_LOOSE=1 lets feeders die at dk2-4 and ignores foodWaiting, and FEED_QUEUE=0, so feeders die together and eat each other's pearls.
- Raising king capture from 0.39 to their about 0.55 on 27.5 pearls/g gives about **+4.5 length/game** (flips about 6/37 r500 losses). It costs no extra units and works on every map.
- Test in order:
  1. Add a CONS_STEAL-style check to the KING_V2 path: do not die while another small ally head is as close to our head as the king is (that check exists today only in tryConsFeed, which is off with CONS_R=0).
  2. FEED_QUEUE=1 (already written). Risk: lower volume, and volume is the other half of the problem (wins 23.7 vs losses 12.8 feeds/g).
- Second lever, outside this window: our king at r300 is 5 vs 15 (8.5 vs 23.5 on unknown maps). Half the final gap exists before feeding starts.
