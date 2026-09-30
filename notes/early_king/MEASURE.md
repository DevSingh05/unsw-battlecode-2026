# Early king: our longest vs top-10 by round (live v30-v32, 29 Sep 23:50 to 30 Sep ~06:00 UTC)
146 games vs top-13 (cheji, Stockfish, 中国, calc, ftm, 3.14, Sponge, SKKU, Sabotage-d, Cutlery, SSS, PB, bfs); sources: ledger + API battles + ab_v30kc/kc31/v30sch/v31sch/por32/v32base.
Excluded non-live test windows (schb31 00:44-01:02, cons33 03:10-04:33, dv33 05:10-05:45 UTC); por32 window counted as v32. Sides/results checked against each replay (146/146 match).
Cells are medians, us/opp. Longest = longest living dragon; units = living dragons. Scripts: scratchpad ek/{collect,pick,measure,agg}.py (sim2 snapshots).

| map | W/L | n | longest r200 | r300 | r400 | r450 | final | units r300 | r450 | final |
|---|---|---|---|---|---|---|---|---|---|---|
| Sch | W | 16 | 4/4 | 16/6 | 28/15 | 32/26 | 36/26 | 39/37 | 27/16 | 16/10 |
| Sch | L | 24 | 4/4 | **12/4** | 18/22 | 19/28 | **18/36** | 19/54 | 14/26 | 6/17 |
| Por | W | 23 | 4/5 | 5/6 | 20/15 | 28/22 | 38/24 | 33/26 | 13/7 | 9/4 |
| Por | L | 28 | 4/4 | **4/8** | 18/22 | 24/32 | **28/42** | 34/28 | 18/6 | 9/4 |
| Sli | W | 11 | 6/8 | 23/13 | 40/32 | 48/41 | 60/49 | 48/60 | 43/10 | 22/8 |
| Sli | L | 22 | 6/8 | **20/18** | 34/34 | 42/46 | **46/58** | 48/62 | 30/20 | 24/8 |
| QoS | W | 13 | 3/3 | 3/4 | 5/6 | 12/6 | 3/0 | 29/5 | 19/2 | 29/0 |
| QoS | L | 9 | 3/4 | 3/7 | 2/9 | 6/18 | 0/8 | 3/27 | 1/19 | 0/27 |

Share of games with longest >= 17 at r300: Sch us 12/38 vs opp 7/38; Por us 0/51 vs opp 1/51; Sli us 26/32 vs opp 16/32.
Win rate when behind vs ahead on longest: r300 Sch 3/8 vs 13/30, Por 10/28 vs 13/23, Sli 4/13 vs 6/19; r400 Sch 4/16 vs 12/20, Por 7/26 vs 16/25, Sli 3/15 vs 7/17.
Median growth of longest r300 to final, us vs opp: Sch L +7.5 vs +33; Por L +23 vs +33.5; Sli L +28.5 vs +43.5 (wins: Sch +22.5 vs +18, Por +33 vs +17, Sli +36.5 vs +32).
Our longest fell >3 after r400 (king died or was cut): Sch L 6/20, Por L 3/28, Sli L 2/22.
cheji only (small n): Sch L 4 games r300 10/7, r400 14/29, final 4/20; Por L 4 games 4/4, 24/26, 40/51.

## Conclusion
1. No. vs top-10 at r300 we are level or ahead on longest in the losses too: Sch 12 v 4, Por 4 v 8 (both tiny), Sli 20 v 18. The "L17-29 by r300" teams in IMP s5 are the ones beating cheji; our top-10 opponents here are not doing it on these maps (opp >=17 at r300 in only 7/38 Sch and 1/51 Por games).
2. We lose the race from r300 to r500. In losses the opponent's longest grows 1.5-4x faster than ours (Sch +33 v +7.5, Sli +43.5 v +28.5, Por +33.5 v +23). The crossover is r350-400 on every map.
3. Schooltime is the clearest case. Opponents sit at 54 units and a longest of 4 at r300, then consolidate to 26 units and a longest of 28 by r450, while our king stalls at 18-19 (6/20 losses lose the king after r400).
4. Portals is a late build with both kings tiny at r300. The losses split at r400 (18 v 22), so pumping into the king in r330-450 matters more than an early king. Slithery is an even race decided by late feeding (46 v 58 at the end).
5. An earlier king (e.g. KING_V2_FEED6_ROUND < 380) only helps if it raises the r300-450 feed rate into the king. A bigger r300 king alone looks unlikely to help: ahead-at-r300 games still win only 43% (Sch), 57% (Por) and 32% (Sli). Test it by the king's growth from r300 to r450, not by its size at r300.
