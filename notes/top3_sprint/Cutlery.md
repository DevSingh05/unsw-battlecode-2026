# Cutlery (id 306, rank 1, elo 2127): study for the unseen-map Sprint

Data sources:
- API battles 30 Sep 15:02-21:08 UTC. `/api/v1/battles` has no pagination, so this is the whole window.
- 31 replays parsed with sim2, all winners matched: 15 vs us (battles 742126 and 734700) and 16 vs others (forgot to mention 749002 and 748982, 3.14159265 748893).
- Other teams' games can be found through `api.get('/api/v1/teams/306')['recent']` (its last 6 battles), then `/api/v1/battles/{id}` and `download_replay`.
- Scripts are in scratchpad `t3/`: `dl.py`, `an.py`, `show.py`, `agg.py`, `spr.py`. Results are pickled in `an.pkl`.

## 1. Head-to-head, us vs Cutlery (40 games): 20-20
- By map: Aut 0-3, Por 1-3, Sli 1-3, QoS 1-2, Sch 2-2, Tro 2-2, Def 3-2, Dev 3-2, Tra 3-1, PD 4-0.
- Ranked series: W 5-0 (16:27), L 1-4 (17:48).
- Unranked series: L 4-6 (15:10), W 6-4 (17:13), L 4-6 (19:03).

## 2. Per-game snapshots
Format is `units/longest/total` for Cutlery vs its opponent. Full table: `python3 show.py`.
- **742126 Aut W.** r100 29/4/65 vs 24/4/58, r300 44/5/127 vs 17/3/40, final 14/53/122 vs 3/11/25.
- **742129 Por W.** r200 10/18/57 vs 35/4/78, r300 4/40/68 vs 33/4/80, final 4/50/67 vs 4/47/66.
- **742132 Sch L.** r300 61/15/221 vs 64/14/180, final 34/53/270 vs 13/54/156. They lost on the longest dragon by 1.
- **734701 Dev W.** r200 34/4/84 vs 15/3/32, final 4/48/73 vs 17/5/49. Our longest never reached 16.
- **734702 Tra W, 734704 Sch W.** Same shape: they have 2-4x our units by r200, and our longest never reaches 16.
- **Eliminations vs us.** They won Tro r164, Tro r189, QoS r177 and Def r364. We eliminated them on PD r205.
- **Eliminations vs ftm.** They lost Tro r156/r164, QoS r111/r154 and PD r72. In those games they had only 1-3 units at r50-100.
- **Splits.** They split about as often as we do: 4058 vs 4973 over the 15 games vs us.
- **Portal traversals.** On Portals they cross 67-84 times against the opponent's 487-543.

## 3. Distinctive general behaviours (15 games vs us unless noted)
**A. Eat-sprints.**
- They make 393 sprint moves (2-3 steps) that eat pearls, taking 524 pearls in total. We make 24 (24 pearls). That is 26 vs 1.6 per game.
- 140 of their eat-sprints are by length-2 dragons, and 27 of those go 3 steps. Against other teams: 349 eat-sprints.
- In v35, `EAT_SPRINT 0` (params.hpp:449) is off. `tryEatSprint` (main.cpp:2879) also caps steps at `myLen-1`, so a length-2 dragon could never do this.
- This matches the cheji finding in IMP_FINDINGS.md (24-26 a game).

**B. Sprint rams, including 3 steps and length 2.**
- Head-on kills: 613 for them (1716 of our length) vs 449 for us (1218 of theirs).
- 432 of their kills came from sprints, including 124 three-step kills and 75 by length-2 dragons. 197 of ours did.
- Every one of our sprint kills is 2 steps: 191 by length-3 dragons and 6 by length 4.
- In `tryRam` (main.cpp:2960), a 2-step ram needs `myLen>=3` and a free middle tile. There is no 3-step option.
- Sprint rate: 5.7 vs 1.4 per 1000 moves (6.5 vs 2.9 against other teams).

**C. Early king when behind on units.**
- On portal-heavy Portals, once they trail on units at r100 (18 vs 35), they shrink to 4-10 units and reach longest 16 at r185-216. The opponent gets there at r333-394.
- They mostly stay out of the portals, the king is never rammed, and they won 3/3.
- In the other games reaching r500 they get to longest 16 at about r240-400, similar to us.
- Relevant code: `UNK_KING_SEED 250` and `UNK_KING_FEED 300` (params.hpp:601-608, main.cpp:838-854). These fix the seed round; they do not react to a unit deficit.

## 4. Suggestions (general, not tested)
1. Turn on `EAT_SPRINT`. Change its cap from `myLen-1` to allow a 2-3 step sprint when every extra step lands on a pearl, so length-2 dragons can use it.
2. In `tryRam`, allow 3-step rams, and 2-step rams at length 2 when the path eats a pearl. Keep the `ramGuard`.
3. On unknown maps, trigger an early king when we trail on units by 1.5x or more at about r150, as in C.
