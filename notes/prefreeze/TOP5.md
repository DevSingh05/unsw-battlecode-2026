# v34 vs current top-5 (ftm, SSS, cheji bt, Stockfish, Cutlery), 30 Sep 07:35-17:02 UTC
Data: 330 games (170 ranked). Sources: API battles (only the last 200 are served, from 10:52), scratchpad sf/list.json (05:16-10:03), launched.jsonl for 10:03-10:52 (incoming battles in that gap are missing). Excluded battles started 07:40-07:53, 08:28-08:56 and 10:37-11:30 (12 battles). All 330 replays were re-simulated with sim2; winner and side match 330/330. Scripts: scratchpad pf/{collect,lay,lay2,an,dev,dev2,dev3}.py; data pf/rows.json, lay.json.
| map | ftm | SSS | cheji | Stockfish | Cutlery | POOL |
|---|---|---|---|---|---|---|
| Schooltime | 3-10 | 2-1 | 1-2 | 2-11 | 3-4 | **11-28** |
| Devil | 3-10 | 0-0 | 0-1 | 2-5 | 2-4 | **7-20** |
| Queen Of Spades | 4-11 | 0-0 | 0-2 | 4-5 | 4-2 | 12-20 |
| Slithery | 6-11 | 1-0 | 3-1 | 1-3 | 3-6 | 14-21 |
| Autarky | 3-12 | 1-1 | 1-1 | 8-1 | 3-7 | 16-22 |
| Portals / Trophy | 14-5 / 9-3 | 1-0 / 1-1 | 4-0 / 1-2 | 2-11 / 3-3 | 7-1 / 4-3 | 28-17 / 18-12 |
| PD / Default / Trauma | 9-4 / 11-3 / 10-3 | 3-0 total | 4-1 total | 5-0 / 3-1 / 3-1 | 6-2 / 5-3 / 7-0 | 24-6 / 20-8 / 22-4 |
| ALL | 72-72 | 9-3 | 14-10 | 33-41 | 44-32 | **172-158 (.52)** |
Ranked Elo vs top-5 since 07:35: Stockfish 13 series -20, ftm 11 series -14, Cutlery 8 series +18, cheji +3, SSS -4.
Not in the brief: Stockfish Portals 2-11 (the REPORT already covers the late Portals king). Autarky vs ftm 3-12 is the next biggest gap.

## Devil (7-20): we lose the r20-60 centre pearl race; all 27 games ended in elimination (losses median r126)
- Losses: units are 6.0/6.0 at r10 and 6.6/6.5 at r20, then 6.3/8.0 at r30, 6/12 at r50 and 5/18 at r75. Wins mirror this (r50 12.4/6).
- Eats before r60, in the middle columns x12-19 (the hub and pockets): losses us 30 v them 61; wins us 66 v them 21. Splits r25-50: losses 8.6 v 15.2, wins 17.7 v 6.3.
- Head-on trades before r60 are even in losses: we start 4.0/g, they start 5.3/g. From r50 they out-ram us 7.2 v 2.7/g, but that is after they are ahead. So the ram guard (RAM_GUARD_LOCAL=1, on) is not the lever. Pocket and hub control is: this matches forensics RC1 (DEVIL_CLAIM) and RC3 (IDLE_HOT_HOME). **Neither is implemented in v34 or bot/** (grep: 0 hits).
- New: **start side.** Devil tiles and edges are exact mirror images, yet vs top-5 we are left 6-6, right 1-14. Other opponents: left 44-6, right 34-10. Combined: left 50-12, right 35-24.
  - This matches the notes/19 swapped-layout finding (2-6 v 4-0), so the effect has now shown up in two separate samples.
  - The devil.hpp module is empty. Likely causes are move order (left ids act first) or a direction tie-break that favours E. Unverified.
  - Other maps are mixed (Sch left 7-12 / right 4-16, PD 5-5 / 19-1, Portals 18-7 / 10-10), so this is not one global bias.

## Schooltime (11-28): the r300-500 race again (as in REPORT.md and MEASURE.md); new facts from 21 games after 10:03 (5-16)
- 14/16 losses went to r500. Median longest in losses: 14.5/10.5 at r300 (we lead), 24/29 at r400, 29.5/44.5 at the end.
- Losses by map total: r300 115/152 → final 89/187. We eat more (1178 v 929 pearls/g) but burn it: HitSelf 229/g v 30.
- **We keep splitting after r350: 109 splits/g v their 38 (wins 148 v 56).** Our king reaches 16 at r300; theirs at r342.
- Head-on r200-300 is even (us rammed 28.0, them 26.2/g). The losing side dies late and self-inflicted, not in fights.

## Candidates (at most 2; each needs a server A/B; the default recommendation is to keep v34)
1. **Schooltime late dive stop** (one line in applyMapParams, same mechanism as live PM_POR_DIVESTOP=360): `if (n == "Schooltime") RP.diveStopRound = 360;`
   - Targets the 109/g late splits and 229/g self-kills without the full late-split cut. LATE_SPLIT_KING_MAPS=340 was rejected (Sch 2/10 v 4/10); this cut is narrower.
   - Low confidence: wins also split late. A/B on Schooltime only, vs top-10, 20 games per arm.
2. **Devil: no one-line fix is supported by the data.** RAM_GUARD_LOCAL/PM_DEVIL_RG target trades, which are even. The real levers (DEVIL_CLAIM, IDLE_HOT_HOME) are code, not flags, so leave them for the Qualifier. Devil games are short (~r130), so a Devil-only A/B is cheap if one gets written.
